"""ALIGN-local numeric decoders and enumeration over the unchanged SMC transport."""
from __future__ import annotations
import struct
from typing import Any

from joulewise.hazards import smc
from joulewise.hazards.smc import SMCKeyData, fourcc, type_name

CMD_GET_KEY_BY_INDEX = 8


def decode(data_type, raw):
    if data_type in ('sp78', 'fpe2'):
        if len(raw) < 2:
            raise ValueError(f'SMC type {data_type!r} needs 2 bytes')
        return struct.unpack('>h' if data_type == 'sp78' else '>H', raw[:2])[0] / (256 if data_type == 'sp78' else 4)
    return smc.decode(data_type, raw)


class Reader(smc.Reader):
    def read_key(self, key):
        info = self._info.get(key)
        if info is None or info[1] not in ('sp78', 'fpe2'):
            value, error = super().read_key(key)
            if error is None or not any(f"unsupported SMC data type '{kind}'" in error for kind in ('sp78', 'fpe2')):
                return value, error
        try:
            transport = self._open()
            code = fourcc(key)
            if info is None:
                reply = transport.call(SMCKeyData(key=code, data8=smc.CMD_GET_KEY_INFO))
                if reply.result:
                    return None, smc._result_text(key, reply.result, 'key info')
                info = int(reply.keyInfo.dataSize), type_name(reply.keyInfo.dataType)
                if not 0 < info[0] <= 32:
                    raise ValueError(f'invalid data size {info[0]}')
                self._info[key] = info
            request = SMCKeyData(key=code, data8=smc.CMD_READ_KEY)
            request.keyInfo.dataSize = info[0]
            reply = transport.call(request)
            if reply.result:
                self._info.pop(key, None)
                return None, smc._result_text(key, reply.result, 'read')
            return decode(info[1], bytes(reply.bytes[:info[0]])), None
        except Exception as exc:
            self._info.pop(key, None)
            if isinstance(exc, OSError):
                self._drop()
            return None, f'{key}: {type(exc).__name__}: {exc}'

    def enumerate_sensors(self) -> dict[str, Any]:
        """Enumerate the SMC index, retaining readable T*** and F?Ac keys.

        Names are candidates, not assertions about anatomical location. Failed
        index lookups and unreadable candidates are retained in ``errors``.
        No hardcoded model-specific key list is used.
        """
        sensors, errors = [], {}
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
                "rpm" if len(key) == 4 and key[0] == "F" and key[2:] == "Ac" else None)
            if unit is None:
                continue
            value, why = self.read_key(key)
            if why is not None:
                errors[key] = why
            elif (unit == "degC" and not -40 <= value <= 150) or (unit == "rpm" and value < 0):
                errors[key] = f"implausible {unit} value {value}"
            else:
                size, data_type = self._info[key]
                sensors.append({"key": key, "unit": unit, "data_type": data_type,
                                "data_size": size, "initial_value": value})
        return {"keys": sorted(sensors, key=lambda item: item["key"]),
                "errors": errors, "complete": complete}

