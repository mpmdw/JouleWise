"""AppleSMC key reader: battery current, battery voltage and the power keys.

Why this exists.  The AppleSmartBattery registry values the battery hazard
used to judge (``InstantAmperage`` and the ``PowerTelemetryData`` block) are
republished only once every 60 s.  The wall-meter probe of 2026-10-06
(``~/night-archive/wallmeter-probe``) read the System Management Controller
(SMC, the chip that runs the battery charger and the power sensors) directly
and found that its key ``B0AC`` (battery current) refreshes once a second,
reads without root in about 75 microseconds, and showed battery-discharge
bursts down to -865 mA during inference that the 60 s registry values missed
entirely (they read 0 throughout).  So the battery hazard measures the current
here instead.

What is read.  An SMC key is a four-character name; the SMC answers a key
with a data type (also four characters) and up to 32 bytes.  On Apple Silicon
the numeric types are little-endian.  The keys read here:

======  ======  =====  ==================================================
key     type    unit   meaning
======  ======  =====  ==================================================
B0AC    si16    mA     battery current; negative = discharging, positive =
                       charging (the sign convention of InstantAmperage)
B0AV    ui16    mV     battery voltage
PDTR    flt     W      DC-in power (adapter input); agreed with the KM003C
                       meter within about 1.4 % in the probe
PSTR    flt     W      system total power
PPBR    flt     W      battery power
======  ======  =====  ==================================================

How a key is read.  The process opens a user client on the ``AppleSMC`` IOKit
service and calls its struct method 2 twice per key: once with command 9
(get key info: the data size and type, cached per key) and once with command
5 (read key: the bytes).  The request and reply are one 80-byte
``SMCKeyData`` structure.  A nonzero kernel return or SMC result code (0x84
means the key does not exist) is an error for that key.

Errors never raise out of :class:`Reader`: every read returns
``{"values": {key: value or None}, "errors": {key: reason}}`` so the monitor
and the arm journal a failed read as data.  Imports nothing outside the
standard library.
"""

from __future__ import annotations

import ctypes
import struct
import sys
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

KEYS: tuple[str, ...] = ("B0AC", "B0AV", "PDTR", "PSTR", "PPBR")
UNITS: Mapping[str, str] = {"B0AC": "mA", "B0AV": "mV", "PDTR": "W", "PSTR": "W", "PPBR": "W"}
SERVICE = b"AppleSMC"
SELECTOR = 2            # kSMCHandleYPCEvent
CMD_READ_KEY = 5        # kSMCReadKey
CMD_GET_KEY_INFO = 9    # kSMCGetKeyInfo
RESULT_KEY_NOT_FOUND = 0x84
IOKIT_PATH = "/System/Library/Frameworks/IOKit.framework/IOKit"
LIBC_PATH = "/usr/lib/libSystem.B.dylib"


class _Vers(ctypes.Structure):
    _fields_ = [("major", ctypes.c_uint8), ("minor", ctypes.c_uint8), ("build", ctypes.c_uint8),
                ("reserved", ctypes.c_uint8), ("release", ctypes.c_uint16)]


class _PLimit(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint16), ("length", ctypes.c_uint16),
                ("cpuPLimit", ctypes.c_uint32), ("gpuPLimit", ctypes.c_uint32),
                ("memPLimit", ctypes.c_uint32)]


class _KeyInfo(ctypes.Structure):
    _fields_ = [("dataSize", ctypes.c_uint32), ("dataType", ctypes.c_uint32),
                ("dataAttributes", ctypes.c_uint8)]


class SMCKeyData(ctypes.Structure):
    """The 80-byte request/reply of the AppleSMC user client."""

    _fields_ = [("key", ctypes.c_uint32), ("vers", _Vers), ("pLimitData", _PLimit),
                ("keyInfo", _KeyInfo), ("result", ctypes.c_uint8), ("status", ctypes.c_uint8),
                ("data8", ctypes.c_uint8), ("data32", ctypes.c_uint32),
                ("bytes", ctypes.c_uint8 * 32)]


def fourcc(text: str) -> int:
    """A four-character SMC name as the big-endian 32-bit integer the SMC uses."""

    raw = text.encode("ascii")
    if len(raw) != 4:
        raise ValueError(f"SMC key or type {text!r} is not four characters")
    return struct.unpack(">I", raw)[0]


def type_name(code: int) -> str:
    return struct.pack(">I", code).decode("ascii", errors="replace")


_FORMATS = {"flt ": "<f", "si8 ": "<b", "ui8 ": "<B", "si16": "<h", "ui16": "<H",
            "si32": "<i", "ui32": "<I", "si64": "<q", "ui64": "<Q"}


def decode(data_type: str, raw: bytes) -> int | float:
    """One SMC value from its type and bytes (Apple Silicon: little-endian).

    Raises ValueError for an unsupported type or too few bytes.
    """

    fmt = _FORMATS.get(data_type)
    if fmt is None:
        raise ValueError(f"unsupported SMC data type {data_type!r}")
    size = struct.calcsize(fmt)
    if len(raw) < size:
        raise ValueError(f"SMC type {data_type!r} needs {size} bytes, got {len(raw)}")
    return struct.unpack(fmt, raw[:size])[0]


class Transport(Protocol):
    """One call of the AppleSMC user client's struct method; tests replace it."""

    def call(self, request: SMCKeyData) -> SMCKeyData: ...

    def close(self) -> None: ...


class IOKitTransport:
    """The production transport: a user client on the AppleSMC service.

    Raises OSError when the service cannot be opened (not macOS, no AppleSMC,
    IOServiceOpen refused) and on a nonzero kernel return from a call.
    """

    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise OSError("AppleSMC requires macOS")
        iokit = ctypes.CDLL(IOKIT_PATH)
        libc = ctypes.CDLL(LIBC_PATH)
        iokit.IOServiceMatching.restype = ctypes.c_void_p
        iokit.IOServiceMatching.argtypes = [ctypes.c_char_p]
        iokit.IOServiceGetMatchingService.restype = ctypes.c_uint32
        iokit.IOServiceGetMatchingService.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        iokit.IOServiceOpen.restype = ctypes.c_int
        iokit.IOServiceOpen.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                        ctypes.POINTER(ctypes.c_uint32)]
        iokit.IOServiceClose.restype = ctypes.c_int
        iokit.IOServiceClose.argtypes = [ctypes.c_uint32]
        iokit.IOObjectRelease.restype = ctypes.c_int
        iokit.IOObjectRelease.argtypes = [ctypes.c_uint32]
        iokit.IOConnectCallStructMethod.restype = ctypes.c_int
        iokit.IOConnectCallStructMethod.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_size_t)]
        self._iokit = iokit
        self._conn = ctypes.c_uint32(0)
        matching = iokit.IOServiceMatching(SERVICE)
        if not matching:
            raise OSError("IOServiceMatching(AppleSMC) failed")
        service = iokit.IOServiceGetMatchingService(0, matching)  # consumes ``matching``
        if not service:
            raise OSError("no AppleSMC service in the IO registry")
        try:
            task = ctypes.c_uint32.in_dll(libc, "mach_task_self_").value
            kr = iokit.IOServiceOpen(service, task, 0, ctypes.byref(self._conn))
        finally:
            iokit.IOObjectRelease(service)
        if kr != 0:
            raise OSError(f"IOServiceOpen(AppleSMC) returned {kr:#x}")

    def call(self, request: SMCKeyData) -> SMCKeyData:
        reply = SMCKeyData()
        size = ctypes.c_size_t(ctypes.sizeof(SMCKeyData))
        kr = self._iokit.IOConnectCallStructMethod(
            self._conn.value, SELECTOR, ctypes.byref(request), ctypes.sizeof(SMCKeyData),
            ctypes.byref(reply), ctypes.byref(size))
        if kr != 0:
            raise OSError(f"IOConnectCallStructMethod returned {kr:#x}")
        return reply

    def close(self) -> None:
        if self._conn.value:
            self._iokit.IOServiceClose(self._conn.value)
            self._conn = ctypes.c_uint32(0)


class Reader:
    """Reads SMC keys; never raises.

    ``transport``: an object with ``call`` and ``close`` (tests pass a fake);
    None opens :class:`IOKitTransport` on the first read, and again on a later
    read if opening failed or a call on it failed (a user client the kernel
    invalidated is not reused).  ``read()`` returns
    ``{"values": {key: int | float | None}, "errors": {key: reason}}``; a key
    is in ``errors`` exactly when its value is None.
    """

    def __init__(self, transport: Transport | None = None) -> None:
        self._transport = transport
        self._owned = transport is None
        self._info: dict[str, tuple[int, str]] = {}

    def _open(self) -> Transport:
        if self._transport is None:
            self._transport = IOKitTransport()
        return self._transport

    def _drop(self) -> None:
        """After a failed call: an owned transport is closed and reopened on the next read."""

        if self._owned and self._transport is not None:
            transport, self._transport = self._transport, None
            try:
                transport.close()
            except Exception:
                pass

    def read_key(self, key: str) -> tuple[int | float | None, str | None]:
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
            request = SMCKeyData(key=code, data8=CMD_READ_KEY)
            request.keyInfo.dataSize = size
            reply = transport.call(request)
            if reply.result != 0:
                self._info.pop(key, None)
                return None, _result_text(key, reply.result, "read")
            value = decode(data_type, bytes(reply.bytes[:size]))
            if isinstance(value, float) and value != value:  # NaN is not a reading
                return None, f"{key}: {data_type!r} value is NaN"
            return value, None
        except OSError as exc:  # the transport failed (or could not open): data, never a raise
            self._info.pop(key, None)
            self._drop()
            return None, f"{key}: {type(exc).__name__}: {exc}"
        except Exception as exc:  # a decode failure is data too
            self._info.pop(key, None)
            return None, f"{key}: {type(exc).__name__}: {exc}"

    def read(self, keys: Sequence[str] = KEYS) -> dict[str, Any]:
        values: dict[str, int | float | None] = {}
        errors: dict[str, str] = {}
        for key in keys:
            value, error = self.read_key(key)
            values[key] = value
            if error is not None:
                errors[key] = error
        return {"values": values, "errors": errors}

    def close(self) -> None:
        transport, self._transport = self._transport, None
        if transport is not None:
            try:
                transport.close()
            except Exception:  # closing never raises either
                pass


def _result_text(key: str, result: int, what: str) -> str:
    if result == RESULT_KEY_NOT_FOUND:
        return f"{key}: SMC {what} result {result:#x} (key not found)"
    return f"{key}: SMC {what} result {result:#x}"


def read_once(keys: Sequence[str] = KEYS) -> dict[str, Any]:
    """Open the SMC, read ``keys`` once, close it.  Never raises."""

    reader = Reader()
    try:
        return reader.read(keys)
    finally:
        reader.close()


__all__ = ["CMD_GET_KEY_INFO", "CMD_READ_KEY", "IOKitTransport", "KEYS", "Reader",
           "RESULT_KEY_NOT_FOUND", "SMCKeyData", "Transport", "UNITS", "decode", "fourcc",
           "read_once", "type_name"]
