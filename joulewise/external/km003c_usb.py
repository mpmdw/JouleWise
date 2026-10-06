"""POWER-Z KM003C over USB: libusb and AES through ctypes, standard library only.

Why ctypes and not pyusb/pycryptodome.  pyusb is itself a ctypes wrapper over
the same native ``libusb-1.0`` library, so calling libusb directly needs the
same native library and no Python package; the repository stays
standard-library-only.  The meter's StreamingAuth and MemoryRead requests are
AES-128-ECB encrypted; macOS ships AES in CommonCrypto (``CCCrypt`` in
libSystem), so pycryptodome is not needed either.  Native requirement: the
Homebrew ``libusb`` (``brew install libusb``); without it the meter reads as
absent, never as an error.

Protocol (okhsunrog/km003c-protocol-research, archived at
``~/night-archive/km003c-tools-20260923``; the wall-meter probe of 2026-10-06
ran it on this unit, firmware 2.0.5):

- USB vendor 0x5FC9, product 0x0063; interface 0 is vendor bulk, endpoint
  0x01 OUT and 0x81 IN.
- Every command starts with a 4-byte little-endian control word: packet type
  in bits 0-6, transaction id in bits 8-15, an "attribute" in bits 17-31.
- Streaming: Connect (type 0x02, answered by Accept 0x05) -> MemoryRead
  (0x44) of the 12-byte HardwareID at 0x40010450 -> StreamingAuth (0x4C:
  AES of [8-byte millisecond time][HardwareID][12 random bytes]) ->
  StartGraph (0x0E, rate index as the attribute) -> repeated GetData (0x0C,
  attribute 0x0002 = AdcQueue) -> StopGraph (0x0F) -> Disconnect (0x03).
- A GetData answer is PutData (0x41): 4-byte control word, 4-byte extended
  header (attribute in bits 0-14, sample count in bits 16-21), then that many
  20-byte samples.  At most 63 samples come back per answer; the rest wait in
  the meter's queue for the next poll.  A 4-byte PutData means the queue was
  empty.
- MemoryRead returns a 20-byte confirmation (0xC4) and then the block.  The
  research documents the block as AES encrypted; firmware 2.0.5 returns it in
  plaintext, so both readings are tried (plaintext first).
"""

from __future__ import annotations

import binascii
import ctypes
import ctypes.util
import os
import struct
import sys
import time
from typing import Any

VID, PID = 0x5FC9, 0x0063
INTERFACE = 0
EP_OUT, EP_IN = 0x01, 0x81
MEMORY_KEY = b"Lh2yfB7n6X7d9a5Z"
AUTH_KEY = b"Fa0b4tA25f4R038a"
HWID_ADDR = 0x40010450
DEVICE_INFO_ADDR = 0x00000420     # model, hardware version, manufacturing date
FIRMWARE_INFO_ADDR = 0x00004420   # firmware version and date
RATES_SPS = {0: 2, 1: 10, 2: 50, 3: 1000}
RESPONSE_CAP = 63                 # samples per GetData answer
SAMPLE_BYTES = 20
LIBUSB_ERROR_TIMEOUT = -7
LIBUSB_ERROR_NOT_FOUND = -5
LIBUSB_CANDIDATES = ("/opt/homebrew/lib/libusb-1.0.dylib", "/usr/local/lib/libusb-1.0.dylib")


class MeterAbsent(Exception):
    """No meter to talk to: libusb missing, or no device with this vendor/product id."""


class UsbError(OSError):
    def __init__(self, what: str, code: int) -> None:
        super().__init__(f"{what} failed: libusb error {code}")
        self.code = code


# --------------------------------------------------------------------------
# AES-128-ECB through CommonCrypto


_CC_ENCRYPT, _CC_DECRYPT, _CC_AES, _CC_ECB = 0, 1, 0, 2
_commoncrypto = None


def _cccrypt():
    global _commoncrypto
    if _commoncrypto is None:
        if sys.platform != "darwin":
            raise OSError("CommonCrypto requires macOS")
        lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        fn = lib.CCCrypt
        fn.restype = ctypes.c_int32
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p,
                       ctypes.c_size_t, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                       ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        _commoncrypto = fn
    return _commoncrypto


def _aes_ecb(operation: int, key: bytes, data: bytes) -> bytes:
    if len(key) != 16 or len(data) % 16:
        raise ValueError("AES-128-ECB needs a 16-byte key and whole 16-byte blocks")
    out = ctypes.create_string_buffer(len(data))
    moved = ctypes.c_size_t(0)
    status = _cccrypt()(operation, _CC_AES, _CC_ECB, key, 16, None, data, len(data), out,
                        len(data), ctypes.byref(moved))
    if status != 0 or moved.value != len(data):
        raise OSError(f"CCCrypt returned {status}")
    return out.raw


def aes_encrypt(key: bytes, data: bytes) -> bytes:
    return _aes_ecb(_CC_ENCRYPT, key, data)


def aes_decrypt(key: bytes, data: bytes) -> bytes:
    return _aes_ecb(_CC_DECRYPT, key, data)


# --------------------------------------------------------------------------
# libusb


class _DeviceDescriptor(ctypes.Structure):
    _fields_ = [("bLength", ctypes.c_uint8), ("bDescriptorType", ctypes.c_uint8),
                ("bcdUSB", ctypes.c_uint16), ("bDeviceClass", ctypes.c_uint8),
                ("bDeviceSubClass", ctypes.c_uint8), ("bDeviceProtocol", ctypes.c_uint8),
                ("bMaxPacketSize0", ctypes.c_uint8), ("idVendor", ctypes.c_uint16),
                ("idProduct", ctypes.c_uint16), ("bcdDevice", ctypes.c_uint16),
                ("iManufacturer", ctypes.c_uint8), ("iProduct", ctypes.c_uint8),
                ("iSerialNumber", ctypes.c_uint8), ("bNumConfigurations", ctypes.c_uint8)]


def load_libusb(path: str | None = None):
    """The libusb-1.0 library with the prototypes used here; MeterAbsent when missing."""

    candidates = [path] if path else [*LIBUSB_CANDIDATES, ctypes.util.find_library("usb-1.0")]
    for candidate in candidates:
        if candidate and (os.path.exists(candidate) or not os.path.isabs(candidate)):
            try:
                lib = ctypes.CDLL(candidate)
                break
            except OSError:
                continue
    else:
        raise MeterAbsent(f"libusb-1.0 not found (tried {[c for c in candidates if c]})")
    p, i, u8, u16, uint = ctypes.c_void_p, ctypes.c_int, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint
    for name, restype, argtypes in (
            ("libusb_init", i, [ctypes.POINTER(p)]),
            ("libusb_exit", None, [p]),
            ("libusb_open_device_with_vid_pid", p, [p, u16, u16]),
            ("libusb_get_device", p, [p]),
            ("libusb_get_device_descriptor", i, [p, ctypes.POINTER(_DeviceDescriptor)]),
            ("libusb_get_string_descriptor_ascii", i, [p, u8, ctypes.c_char_p, i]),
            ("libusb_set_configuration", i, [p, i]),
            ("libusb_claim_interface", i, [p, i]),
            ("libusb_release_interface", i, [p, i]),
            ("libusb_reset_device", i, [p]),
            ("libusb_close", None, [p]),
            ("libusb_bulk_transfer", i, [p, ctypes.c_ubyte, ctypes.c_char_p, i,
                                         ctypes.POINTER(i), uint])):
        fn = getattr(lib, name)
        fn.restype, fn.argtypes = restype, argtypes
    return lib


class UsbDevice:
    """One opened, claimed device: bulk write/read with millisecond timeouts."""

    def __init__(self, lib, *, vid: int = VID, pid: int = PID, reset: bool = False) -> None:
        self.lib = lib
        self.ctx = ctypes.c_void_p()
        rc = lib.libusb_init(ctypes.byref(self.ctx))
        if rc != 0:
            raise UsbError("libusb_init", rc)
        self.handle = None
        self.claimed = False
        try:
            self._open(vid, pid)
            if reset:
                rc = lib.libusb_reset_device(self.handle)
                # After a reset the device may re-enumerate under a new handle.
                if rc != 0:
                    lib.libusb_close(self.handle)
                    self.handle = None
                time.sleep(1.5)
                if self.handle is None:
                    self._open(vid, pid)
            lib.libusb_set_configuration(self.handle, 1)  # already configured is fine
            rc = lib.libusb_claim_interface(self.handle, INTERFACE)
            if rc != 0:
                raise UsbError("libusb_claim_interface", rc)
            self.claimed = True
        except BaseException:
            self.close()
            raise
        self.buffer = ctypes.create_string_buffer(4096)
        self.transferred = ctypes.c_int(0)

    def _open(self, vid: int, pid: int) -> None:
        self.handle = self.lib.libusb_open_device_with_vid_pid(self.ctx, vid, pid)
        if not self.handle:
            self.handle = None
            raise MeterAbsent(f"no USB device {vid:04x}:{pid:04x}")

    def descriptor(self) -> dict[str, Any]:
        """bcdDevice and the three descriptor strings; None for any that cannot be read."""

        out: dict[str, Any] = {"bcd_device": None, "manufacturer": None, "product": None,
                               "serial": None}
        desc = _DeviceDescriptor()
        if self.lib.libusb_get_device_descriptor(self.lib.libusb_get_device(self.handle),
                                                 ctypes.byref(desc)) != 0:
            return out
        out["bcd_device"] = f"{desc.bcdDevice >> 8:x}.{desc.bcdDevice & 0xFF:02x}"
        for key, index in (("manufacturer", desc.iManufacturer), ("product", desc.iProduct),
                           ("serial", desc.iSerialNumber)):
            if index:
                buf = ctypes.create_string_buffer(256)
                n = self.lib.libusb_get_string_descriptor_ascii(self.handle, index, buf, 256)
                if n > 0:
                    out[key] = buf.raw[:n].decode("ascii", errors="replace")
        return out

    def write(self, data: bytes, timeout_ms: int = 2000) -> None:
        rc = self.lib.libusb_bulk_transfer(self.handle, EP_OUT, data, len(data),
                                           ctypes.byref(self.transferred), timeout_ms)
        if rc != 0:
            raise UsbError("bulk write", rc)
        if self.transferred.value != len(data):  # a partial command is not a command
            raise UsbError(f"bulk write sent {self.transferred.value} of {len(data)} bytes;", 0)

    def read(self, timeout_ms: int = 2000) -> bytes:
        rc = self.lib.libusb_bulk_transfer(self.handle, EP_IN, self.buffer, len(self.buffer),
                                           ctypes.byref(self.transferred), timeout_ms)
        if rc != 0:
            raise UsbError("bulk read", rc)
        return self.buffer.raw[:self.transferred.value]

    def close(self) -> None:
        if self.handle is not None:
            if self.claimed:
                self.lib.libusb_release_interface(self.handle, INTERFACE)
                self.claimed = False
            self.lib.libusb_close(self.handle)
            self.handle = None
        if self.ctx:
            self.lib.libusb_exit(self.ctx)
            self.ctx = ctypes.c_void_p()


# --------------------------------------------------------------------------
# The KM003C protocol


def control(ptype: int, tid: int, attribute: int = 0) -> bytes:
    return struct.pack("<I", (ptype & 0x7F) | ((tid & 0xFF) << 8) | ((attribute & 0x7FFF) << 17))


def _text(block: bytes, start: int, stop: int) -> str | None:
    raw = block[start:stop].split(b"\x00")[0]
    if raw and all(32 <= c < 127 for c in raw):
        return raw.decode("ascii")
    return None


class Meter:
    """The KM003C on an opened :class:`UsbDevice`."""

    def __init__(self, usb: UsbDevice) -> None:
        self.usb = usb
        self.tid = 0

    def next_tid(self) -> int:
        self.tid = (self.tid + 1) & 0xFF
        return self.tid

    def xfer(self, packet: bytes, timeout_ms: int = 2000) -> bytes:
        self.usb.write(packet, timeout_ms)
        return self.usb.read(timeout_ms)

    def drain(self) -> None:
        """Discard answers left in the IN endpoint by an earlier session."""

        for _ in range(64):
            try:
                self.usb.read(50)
            except UsbError as exc:
                if exc.code == LIBUSB_ERROR_TIMEOUT:
                    return
                raise

    def connect(self) -> None:
        reply = self.xfer(control(0x02, self.next_tid()))
        if not reply or (reply[0] & 0x7F) != 0x05:
            raise RuntimeError(f"connect rejected: {reply.hex()}")

    def memory_read(self, address: int, size: int) -> list[bytes]:
        """One MemoryRead; returns [plaintext reading, decrypted reading] of the block."""

        tid = self.next_tid()
        body = struct.pack("<III", address, size, 0xFFFFFFFF)
        plain = body + struct.pack("<I", binascii.crc32(body) & 0xFFFFFFFF) + b"\xff" * 16
        self.usb.write(bytes([0x44, tid, 0x01, 0x01]) + aes_encrypt(MEMORY_KEY, plain))
        confirmation = self.usb.read()
        if len(confirmation) != 20 or confirmation[0] != 0xC4:
            raise RuntimeError(f"memory read confirmation bad: {confirmation.hex()}")
        padded = (size + 15) // 16 * 16
        block = b""
        while len(block) < padded:
            chunk = self.usb.read(3000)
            if not chunk:
                break
            block += chunk
        block = block[:padded]
        decrypted = aes_decrypt(MEMORY_KEY, block) if len(block) == padded else b""
        return [block[:size], decrypted[:size]]

    def hardware_ids(self) -> list[bytes]:
        return self.memory_read(HWID_ADDR, 12)

    def device_info(self) -> dict[str, Any]:
        """Hardware and firmware version strings from the two info blocks (null when unreadable)."""

        info: dict[str, Any] = {"model": None, "hardware_version": None, "manufacture_date": None,
                                "firmware_version": None, "firmware_date": None,
                                "info_error": None}
        try:
            for candidate in self.memory_read(DEVICE_INFO_ADDR, 64):
                if _text(candidate, 0x10, 0x1C):
                    info["model"] = _text(candidate, 0x10, 0x1C)
                    info["hardware_version"] = _text(candidate, 0x1C, 0x28)
                    info["manufacture_date"] = _text(candidate, 0x28, 0x40)
                    break
            for candidate in self.memory_read(FIRMWARE_INFO_ADDR, 64):
                if _text(candidate, 0x1C, 0x28):
                    info["firmware_version"] = _text(candidate, 0x1C, 0x28)
                    info["firmware_date"] = _text(candidate, 0x28, 0x38)
                    break
        except Exception as exc:  # the versions are recorded, never required
            info["info_error"] = f"{type(exc).__name__}: {exc}"
        return info

    def auth(self, hardware_id: bytes) -> int:
        """StreamingAuth; returns the granted level (0 = refused)."""

        plain = struct.pack("<Q", time.time_ns() // 1_000_000) + hardware_id + os.urandom(12)
        reply = self.xfer(bytes([0x4C, self.next_tid(), 0x00, 0x02]) + aes_encrypt(AUTH_KEY, plain))
        if len(reply) < 4 or (reply[0] & 0x7F) != 0x4C:
            return 0
        return (int.from_bytes(reply[2:4], "little") >> 1) & 3

    def start_graph(self, rate_idx: int) -> None:
        reply = self.xfer(control(0x0E, self.next_tid(), rate_idx))
        if not reply or (reply[0] & 0x7F) != 0x05:
            raise RuntimeError(f"StartGraph rejected: {reply.hex()}")

    def stop_graph(self) -> None:
        try:
            self.xfer(control(0x0F, self.next_tid()), timeout_ms=500)
        except Exception:
            pass

    def disconnect(self) -> None:
        try:
            self.xfer(control(0x03, self.next_tid()), timeout_ms=300)
        except Exception:
            pass

    def poll_request(self) -> bytes:
        return control(0x0C, self.next_tid(), 0x0002)


def parse_put_data(reply: bytes) -> tuple[bytes, int, bool]:
    """(sample bytes, sample count, ok) of one GetData answer.

    ok is False for anything that is not an AdcQueue PutData of exactly the
    declared length (8 header bytes + 20 per sample: what the meter sent on
    every one of 40 live polls on 10-06; surplus bytes would be samples the
    count does not cover); an empty queue is (b"", 0, True).
    """

    if len(reply) == 4 and (reply[0] & 0x7F) == 0x41:
        return b"", 0, True
    if len(reply) < 8 or (reply[0] & 0x7F) != 0x41:
        return b"", 0, False
    ext = struct.unpack("<I", reply[4:8])[0]
    if ext & 0x7FFF != 0x0002:
        return b"", 0, False
    n = (ext >> 16) & 0x3F
    if len(reply) != 8 + n * SAMPLE_BYTES:
        return b"", 0, False
    payload = reply[8:]
    return payload, n, True


__all__ = ["AUTH_KEY", "EP_IN", "EP_OUT", "LIBUSB_ERROR_TIMEOUT", "MEMORY_KEY", "Meter", "MeterAbsent",
           "PID", "RATES_SPS", "RESPONSE_CAP", "SAMPLE_BYTES", "UsbDevice", "UsbError", "VID",
           "aes_decrypt", "aes_encrypt", "control", "load_libusb", "parse_put_data"]
