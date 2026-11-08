"""Pre-GO in-process macOS status reads. No subprocesses or host mutations.

Native bindings remain PROVISIONAL until the MBP dry arm. IOKit objects and
CoreFoundation values are released on every read. No admission is memoized.
"""
from __future__ import annotations

import ctypes as C
import os
import plistlib
import sys


def profile_mode(profile):
    """pmset's unified enum, or the explicit underlying IOPM mode switches."""
    mode = profile.get('powermode')
    if type(mode) is int and mode in (0, 1, 2):
        return mode
    low, high = profile.get('LowPowerMode'), profile.get('HighPowerMode')
    if (type(low) not in (int, bool) or type(high) not in (int, bool)
            or low not in (0, 1) or high not in (0, 1) or low and high):
        return None
    return 2 if high else 1 if low else 0


def battery_record(properties, wall):
    """Normalize typed IOKit properties, independently of the frozen ioreg grammar."""
    p = properties
    for key in ('ExternalConnected', 'IsCharging'):
        if type(p.get(key)) is not bool:
            raise ValueError('battery boolean unavailable: '+key)
    for key in ('InstantAmperage', 'UpdateTime', 'CurrentCapacity'):
        if type(p.get(key)) is not int:
            raise ValueError('battery integer unavailable: '+key)
    current = p['InstantAmperage']
    if current >= 2**63:
        current -= 2**64
    age = wall-p['UpdateTime']
    passed = p['ExternalConnected'] and not p['IsCharging'] and abs(current) <= 200 and 0 <= age <= 180
    return {'schema': 'joulewise.battery_float.v1', 'probe_error': False, 'passed': passed,
            'wall_time_s': wall, 'external_connected': p['ExternalConnected'],
            'is_charging': p['IsCharging'], 'instant_amperage_ma': current,
            'current_capacity_pct': p['CurrentCapacity'], 'update_time_s': p['UpdateTime'],
            'update_age_s': age, 'source': 'IORegistryEntryCreateCFProperties:AppleSmartBattery'}


class StatusReader:
    def __init__(self):
        if sys.platform != 'darwin':
            raise RuntimeError('native condition status requires macOS')
        self.io = C.CDLL('/System/Library/Frameworks/IOKit.framework/IOKit')
        self.cf = C.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        self.cg = C.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
        self.libc = C.CDLL('/usr/lib/libSystem.B.dylib')
        self.proc = C.CDLL('/usr/lib/libproc.dylib')
        def bind(lib, name, result, args):
            f = getattr(lib, name); f.restype = result; f.argtypes = args
            return f
        ptr, u32, i32 = C.c_void_p, C.c_uint32, C.c_int32
        bind(self.io, 'IOServiceMatching', ptr, [C.c_char_p])
        bind(self.io, 'IOServiceGetMatchingService', u32, [u32, ptr])
        bind(self.io, 'IORegistryEntryCreateCFProperties', i32, [u32, C.POINTER(ptr), ptr, u32])
        bind(self.io, 'IOObjectRelease', i32, [u32])
        bind(self.io, 'IOPMCopyCustomPowerProfiles', ptr, [])
        bind(self.cf, 'CFPropertyListCreateData', ptr, [ptr, ptr, C.c_long, C.c_ulong, C.POINTER(ptr)])
        bind(self.cf, 'CFDataGetLength', C.c_long, [ptr])
        bind(self.cf, 'CFDataGetBytePtr', ptr, [ptr])
        bind(self.cf, 'CFRelease', None, [ptr])
        bind(self.cg, 'CGSessionCopyCurrentDictionary', ptr, [])
        bind(self.libc, 'sysctlbyname', i32, [C.c_char_p, ptr, C.POINTER(C.c_size_t), ptr, C.c_size_t])
        bind(self.proc, 'proc_listpids', i32, [u32, u32, ptr, i32])
        bind(self.proc, 'proc_name', i32, [i32, ptr, u32])
        # Boot identity is immutable within this process/boot; no per-tick sysctl.
        data = C.create_string_buffer(128); size = C.c_size_t(len(data))
        if self.libc.sysctlbyname(b'kern.bootsessionuuid', data, C.byref(size), None, 0):
            raise OSError('boot identity unavailable')
        self.boot = data.value.decode('ascii')

    def decode(self, value):
        if not value:
            raise ValueError('native CF property unavailable')
        error = C.c_void_p()
        data = None
        try:
            data = self.cf.CFPropertyListCreateData(None, value, 100, 0, C.byref(error))
            if not data:
                raise ValueError('native CF property serialization failed')
            return plistlib.loads(C.string_at(self.cf.CFDataGetBytePtr(data), self.cf.CFDataGetLength(data)))
        finally:
            if data: self.cf.CFRelease(data)
            if error.value: self.cf.CFRelease(error)
            self.cf.CFRelease(value)

    def properties(self, name):
        service = self.io.IOServiceGetMatchingService(0, self.io.IOServiceMatching(name.encode('ascii')))
        if not service:
            raise ValueError('native service unavailable: '+name)
        value = C.c_void_p()
        try:
            if self.io.IORegistryEntryCreateCFProperties(service, C.byref(value), None, 0):
                raise ValueError('native properties unavailable: '+name)
            return self.decode(value.value)
        finally:
            self.io.IOObjectRelease(service)

    def screensaver(self):
        # The session dictionary covers locked/login sessions as well. A missing
        # state stays unknown unless the process census also succeeds.
        session = self.decode(self.cg.CGSessionCopyCurrentDictionary())
        if session.get('CGSSessionScreenIsLocked') is True:
            return True
        size = self.proc.proc_listpids(1, 0, None, 0)
        if size <= 0:
            raise ValueError('screensaver census unavailable')
        pids = (C.c_int32 * (size//4+256))()
        used = self.proc.proc_listpids(1, 0, pids, C.sizeof(pids))
        if used <= 0 or used >= C.sizeof(pids):
            raise ValueError('screensaver census incomplete')
        for pid in pids[:used//4]:
            if pid <= 0: continue
            name = C.create_string_buffer(256)
            if self.proc.proc_name(pid, name, len(name)) > 0 and name.value == b'ScreenSaverEngine':
                return True
        return False

    def sample(self, wall):
        battery = battery_record(self.properties('AppleSmartBattery'), wall)
        display = self.properties('IODisplayWrangler').get('IOPowerManagement', {}).get('CurrentPowerState')
        profiles = self.decode(self.io.IOPMCopyCustomPowerProfiles())
        mode = profile_mode(profiles.get('AC Power', {}))
        return {'battery': battery, 'display_asleep': display <= 1 if type(display) is int and display >= 0 else None,
                'ac_powermode': mode if type(mode) is int else None, 'screensaver_engaged': self.screensaver()}

    def close(self):
        pass
