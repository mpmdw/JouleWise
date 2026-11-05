"""ALIGN-local decoding and key census over the unchanged hazard SMC reader.

Private Reader transport/cache seams are inherited; no second IOKit protocol or
native client is installed. #KEY alone is big-endian ui32 on Apple Silicon.
"""
from __future__ import annotations

import math
import struct
from typing import Any

from joulewise.hazards import smc
from joulewise.hazards.smc import (CMD_GET_KEY_INFO, CMD_READ_KEY, SMCKeyData,
                                 fourcc, type_name, _result_text)

CMD_GET_KEY_BY_INDEX = 8


def decode(data_type: str, raw: bytes, *, key: str | None = None) -> int | float:
    formats = {"sp78": (">h", 256), "fpe2": (">H", 4), "ioft": ("<q", 65536)}
    if key == "#KEY":
        if data_type != "ui32" or len(raw) != 4:
            raise ValueError("#KEY must be a four-byte big-endian ui32")
        return struct.unpack(">I", raw)[0]
    if data_type in formats:
        fmt, scale = formats[data_type]
        size = struct.calcsize(fmt)
        if len(raw) < size:
            raise ValueError(f"SMC type {data_type!r} needs {size} bytes")
        return struct.unpack(fmt, raw[:size])[0] / scale
    return smc.decode(data_type, raw)


class Reader(smc.Reader):
    """Extra ALIGN types/enumeration; normal integer keys keep their byte order.

    read/read_key/close retain the base API. read additionally retains raw
    bytes/type for per-bundle thermometry evidence; failed reads remain data.
    """
    def __init__(self, transport=None):
        super().__init__(transport)
        self.raw: dict[str, dict[str, Any]] = {}

    def read_key(self, key: str) -> tuple[int | float | None, str | None]:
        self.raw.pop(key, None)
        try:
            transport = self._open()
            code = fourcc(key)
            info = self._info.get(key)
            if info is None:
                request = SMCKeyData(key=code, data8=CMD_GET_KEY_INFO)
                reply = transport.call(request)
                if reply.result != 0:
                    return None, _result_text(key, reply.result, "key info")
                info = (int(reply.keyInfo.dataSize), type_name(reply.keyInfo.dataType))
                if not 0 < info[0] <= 32:
                    return None, f"{key}: key info gives data size {info[0]}"
                self._info[key] = info
            size, data_type = info
            self.raw[key] = {"data_type": data_type, "data_size": size, "raw_hex": None}
            request = SMCKeyData(key=code, data8=CMD_READ_KEY)
            request.keyInfo.dataSize = size
            reply = transport.call(request)
            if reply.result != 0:
                self._info.pop(key, None)
                return None, _result_text(key, reply.result, "read")
            self.raw[key] = {"data_type": data_type, "data_size": size,
                             "raw_hex": bytes(reply.bytes[:size]).hex()}
            value = decode(data_type, bytes(reply.bytes[:size]), key=key)
            if isinstance(value, float) and not math.isfinite(value):  # NaN/inf is not a reading
                return None, f"{key}: {data_type!r} value is {value}"
            return value, None
        except OSError as exc:  # the transport failed (or could not open): data, never a raise
            self._info.pop(key, None)
            self._drop()
            return None, f"{key}: {type(exc).__name__}: {exc}"
        except Exception as exc:  # a decode failure is data too
            self._info.pop(key, None)
            return None, f"{key}: {type(exc).__name__}: {exc}"

    def read(self, keys=smc.KEYS) -> dict[str, Any]:
        result = super().read(keys)
        result["raw"] = {key: dict(self.raw.get(key, {})) for key in keys}
        return result

    def enumerate_sensors(self) -> dict[str, Any]:
        """Enumerate the SMC index, retaining every readable T* and F* key.

        Names are candidates, not assertions about anatomical location. Failed
        index lookups and unreadable candidates are retained in ``errors``.
        No hardcoded model-specific key list is used.
        """
        sensors, errors, unsupported = [], {}, {}
        count, why = self.read_key("#KEY")
        if why or type(count) is not int or not 0 < count <= 65536:
            return {"keys": [], "errors": {"#KEY": why or f"invalid key count {count!r}"},
                    "complete": False}
        complete = True
        for index in range(count):
            try:
                reply = self._open().call(SMCKeyData(data8=CMD_GET_KEY_BY_INDEX, data32=index))
                if reply.result:
                    raise OSError(f"index result {reply.result:#x}")
                key = type_name(reply.key)
            except Exception as exc:
                errors[f"index:{index}"] = str(exc)
                complete = False
                continue
            unit = "degC" if key.startswith("T") else (
                "rpm" if key.startswith("F") and key[2:] == "Ac" else
                "raw" if key.startswith("F") else None)
            if unit is None:
                continue
            value, why = self.read_key(key)
            if why is not None:
                errors[key] = why
                if "unsupported SMC data type" in why:
                    unsupported[key] = {**self.raw.get(key, {}), "error": why}
            elif (unit == "degC" and not -40 <= value <= 150) or (unit == "rpm" and value < 0):
                errors[key] = f"implausible {unit} value {value}"
            else:
                size, data_type = self._info[key]
                sensors.append({"key": key, "unit": unit, "data_type": data_type,
                                "data_size": size, "initial_value": value})
        return {"keys": sorted(sensors, key=lambda item: item["key"]),
                "errors": errors, "unsupported_types": unsupported, "complete": complete}
