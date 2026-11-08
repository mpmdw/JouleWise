"""Pre-GO native sources and an injectable bounded R16 runner.

Nothing starts on import. This is a between-window tool, not a telemetry source
inside a member. Native channels/overhead remain PROVISIONAL until CW-1.
"""
from __future__ import annotations

from collections import deque
from datetime import timezone
import json
import os
import plistlib
import subprocess
import threading
import time

from joulewise.align.apple import condition_waits as cw
from joulewise.hazards import contention
from joulewise.hazards.base import Context


class PowerStream:
    """One bounded NUL-plist stream, watts only. Never integrates energy.

    Native timestamp maps through one wall/monotonic anchor, not arrival time.
    A delivery stall therefore cannot manufacture a fresh power observation.
    """
    ARGV = ('sudo', '-n', '/usr/bin/powermetrics', '--samplers', 'cpu_power,gpu_power,thermal',
            '-i', '1000', '-f', 'plist')

    def __init__(self, ctx, *, popen=subprocess.Popen):
        self.ctx, self.popen = ctx, popen
        self.process = self.thread = None
        self.pending = deque(maxlen=4096)
        self.lock = threading.Lock()
        self.error = self.pm = self.pm_ns = None
        self.last_end = None

    def start(self):
        self.anchor = self.ctx.stamp()
        self.process = self.popen(self.ARGV, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  start_new_session=True)
        self.thread = threading.Thread(target=self._read, daemon=True, name='cw-pre-go-power')
        self.thread.start()
        return self

    def accept(self, document):
        timestamp = document['timestamp']
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        native_end = self.anchor.monotonic_ns + round(timestamp.timestamp()*cw.NS)-self.anchor.wall_ns
        duration, w = document['elapsed_ns'], document['processor']['combined_power']/1000
        if type(duration) is not int or duration <= 0 or not cw.finite(w) or w < 0:
            raise ValueError('invalid native power duration/watts')
        # D-078 endpoint/cumulative-elapsed convention; native timestamp drift
        # remains checked rather than replacing a stalled source with arrival.
        end = native_end if self.last_end is None else self.last_end+duration
        if abs(end-native_end) > cw.NS//10:
            raise ValueError('native power timestamp discontinuity')
        self.last_end = end
        with self.lock:
            if len(self.pending) == self.pending.maxlen:
                raise ValueError('power delivery queue overflow')
            self.pending.append({'start_ns': end-duration, 'end_ns': end, 'watts': w})
            self.pm, self.pm_ns = document.get('thermal_pressure'), end

    def _read(self):
        frame = bytearray()
        try:
            while True:
                value = self.process.stdout.read1(65536)
                if not value:
                    raise ValueError('powermetrics stream ended')
                frame.extend(value)
                while (end := frame.find(b'\0')) >= 0:
                    document = bytes(frame[:end])
                    del frame[:end+1]
                    if document.strip():
                        self.accept(plistlib.loads(document))
                if len(frame) > 8*1024*1024:
                    raise ValueError('power frame exceeds bound')
        except Exception as exc:
            self.error = f'{type(exc).__name__}:{exc}'

    def sample(self):
        with self.lock:
            out = list(self.pending)
            self.pending.clear()
            return {'power_intervals': out, 'pm_state': self.pm if self.error is None else None,
                    'pm_observed_ns': self.pm_ns, 'power_error': self.error}

    def close(self):
        if self.process is not None:
            import signal
            try:
                os.killpg(self.process.pid, signal.SIGTERM)
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=5)
            except ProcessLookupError:
                pass
            if self.thread is not None:
                self.thread.join(timeout=5)
            self.process.stdout.close()


def command(argv):
    return subprocess.run(argv, capture_output=True, check=False, timeout=2)


def display_state(run):
    """Qualified aggregate display power source; unknown refuses, HID is unused."""
    result = run(('/usr/sbin/ioreg', '-a', '-r', '-n', 'IODisplayWrangler'))
    if result.returncode:
        return None
    rows = plistlib.loads(result.stdout)
    if not isinstance(rows, list) or len(rows) != 1:
        return None
    value = rows[0].get('IOPowerManagement', {}).get('CurrentPowerState')
    return value <= 1 if type(value) is int and value >= 0 else None


class NativeSampler:
    """Read native SMC, pmset, ioreg, notify and the same native ps guard.

    setup_check includes volume/meter/support/cooler checks selected by the
    caller; no static setup digest is itself a physical check. topup_reader
    derives completion from v4_topup logs; a manually supplied timestamp is
    never inferred here. Each source can be injected without macOS or MLX.
    """
    def __init__(self, policy, *, ctx=None, smc=None, notify=None, power=None,
                 run=command, topup_reader, setup_check, obc_off_attested_by,
                 battery_reader=None, guard_reader=None, boot_reader=None, channel_template=None):
        self.policy = cw.validate_policy(policy)
        # A prospectively approved CW-1 reference capture may select channels
        # before numeric Q exists. It supplies candidates, never an active Q.
        self.channels = self.policy['q'] or channel_template
        self.ctx = ctx or Context()
        self.smc, self.notify, self.power = smc, notify, power
        self.run, self.topup_reader, self.setup_check = run, topup_reader, setup_check
        self.obc = obc_off_attested_by
        self.battery_reader, self.guard_reader, self.boot_reader = battery_reader, guard_reader, boot_reader
        self.previous = None
        self.previous_over, self.root_identities = {}, {}
        self.index = 0

    def start(self):
        from joulewise.align.apple.smc_reader import Reader
        from joulewise.hazards.thermal import NotifyReader
        try:
            if self.smc is None:
                self.smc = Reader()
            if self.notify is None:
                self.notify = NotifyReader()
            if self.power is None:
                self.power = PowerStream(self.ctx)
            self.power.start()
        except BaseException:
            self.close()
            raise
        return self

    def boot_id(self):
        if self.boot_reader:
            return self.boot_reader()
        result = self.run(('/usr/sbin/sysctl', '-n', 'kern.bootsessionuuid'))
        if result.returncode:
            raise ValueError('boot identity unavailable')
        return result.stdout.decode('ascii').strip()

    def _guard(self):
        if self.guard_reader:
            return self.guard_reader()
        # Same native interval evaluator, aggregate threshold, root identities,
        # counter-regression handling and 30 s cadence as the arm.
        now = self.ctx.clocks.monotonic_ns()
        if self.previous is not None and now-self.previous.midpoint_ns < 30*cw.NS:
            return []
        current = contention.take_snapshot(self.ctx, raw_name=f'cw-{self.index:04d}-ps.txt', compress=True,
                                           host_reader=contention.read_host_cpu)
        self.index += 1
        roots = (os.getpid(),)
        contention.pin_roots(current, roots, self.root_identities)
        rows = []
        if self.previous is not None:
            limits = self.policy['guard']
            value = contention.interval(self.previous, current, tree_roots=roots, include_kernel_task=True,
                limit=limits['cpu_limit_s_per_s'], previous_over=self.previous_over,
                aggregate_limit=contention.aggregate_limit(limits), root_identities=self.root_identities)
            self.previous_over = contention.over_limit(value)
            rows.append(value)
        self.previous = current
        return rows

    def sample(self, *, attempt_id, boot_id):
        from joulewise import battery_float
        from joulewise.align.apple import thermal, powermode
        a = self.ctx.stamp()
        q = self.channels
        selected = ([c['key'] for c in q['temperatures'].values()] + list(q['fans'])) if q else []
        smc = thermal.sample(self.smc, selected)
        decoder_ok = all(smc['readings'][k].get('data_type') == c['decoder']
                         for k, c in ([(c['key'], c) for c in q['temperatures'].values()]
                                      + list(q['fans'].items()))) if q else True
        battery, _raw = (self.battery_reader() if self.battery_reader else battery_float.observe(
            phase='arm_check', runner=self.run, wall_time_s=a.wall_ns/cw.NS,
            monotonic_ns=self.ctx.clocks.monotonic_ns))
        batt_ns = self.ctx.clocks.monotonic_ns()
        custom = self.run(('/usr/bin/pmset', '-g', 'custom'))
        mode = powermode.parse_ac_powermode(custom.stdout.decode('ascii')) if not custom.returncode else None
        asleep = display_state(self.run)
        saver = self.run(('/usr/bin/pgrep', '-x', 'ScreenSaverEngine'))
        screensaver = False if saver.returncode == 1 and not saver.stdout.strip() else True if saver.returncode == 0 else None
        setup = self.setup_check()
        power = self.power.sample()
        intervals = self._guard()
        os_level = self.notify.read()
        b = self.ctx.stamp()
        # Filter only the initial partial PM interval (it precedes this attempt).
        return {'schema': cw.SAMPLE, 'attempt_id': attempt_id, 'boot_id': self.boot_id(),
                'started': a.to_json(), 'finished': b.to_json(), 'sensors': smc['sensors'],
                'smc_readings': smc['readings'], 'smc_units': smc['units'],
                'raw_ioreg': _raw.decode('ascii', errors='backslashreplace'),
                'source_errors': smc['errors'], 'ac_powermode': mode, 'display_asleep': asleep,
                'screensaver_engaged': screensaver, 'os_level': os_level, **power,
                'battery': battery, 'battery_observed_ns': batt_ns,
                'topup': self.topup_reader(b.wall_ns/cw.NS), 'obc_off_attested_by': self.obc,
                'setup_sha256': setup.get('setup_sha256'),
                'final_checks_passed': setup.get('passed') is True and decoder_ok,
                'guard_intervals': intervals}

    def close(self):
        errors = []
        for source in (self.power, self.notify, self.smc):
            if source is not None:
                try:
                    source.close()
                except Exception as exc:
                    errors.append(exc)
        if errors:
            raise errors[0]


def run_attempt(policy, header, sampler, *, journal, trace, final_checks,
                incumbent_ready=lambda: False, cancelled=lambda: False, on_receipt=lambda r: None,
                at_go=False):
    """One native attempt, final re-read then GO; no extra sleep after READY.

    By default this makes the preliminary install receipt (no GO marker).
    Caller supplies already-open journals and native final clock/battery/census
    checks. It owns the actual GO/chain launch. Returning a receipt never caches
    an admission for a later process. Missing/failed final reads resume the same
    bounded attempt. All sources close on cancellation, exceptions and success.
    """
    attempt = cw.Attempt(policy, **header)
    cw.marker(journal, 'quiet_start', {**header['started'], 'monotonic_ns': header['quiet_start_ns'],
        'wall_ns': header['started']['wall_ns']-(header['started']['monotonic_ns']-header['quiet_start_ns'])})
    result = None
    try:
        sampler.start()
        while True:
            if cancelled():
                raise InterruptedError('condition-waits cancelled before GO')
            tick = sampler.ctx.clocks.monotonic_ns()
            row = observation(sampler, header)
            row['power_intervals'] = [p for p in row.get('power_intervals', []) if p['start_ns'] >= attempt.start]
            incumbent = incumbent_ready() is True
            row['incumbent_ready'] = incumbent
            trace.write(cw.canonical(row).decode()+'\n')
            result = attempt.feed(row, incumbent_ready=incumbent)
            if result['status'] == 'not_ready':
                cw.marker(journal, 'not_ready', result['finished'])
                on_receipt(result)
                return result
            if result['status'] == 'released':
                # Final native reads may disturb readiness. Always re-sample;
                # the final row remains in the same stamped trace/attempt.
                final_ok = final_checks() is True
                row = observation(sampler, header)
                row['final_checks_passed'] = row.get('final_checks_passed') is True and final_ok
                row['incumbent_ready'] = incumbent_ready() is True
                row['go'] = at_go
                trace.write(cw.canonical(row).decode()+'\n')
                result = attempt.feed(row, go=at_go, incumbent_ready=row['incumbent_ready'])
                if result['status'] == 'released':
                    on_receipt(result)
                    cw.marker(journal, 'release', result['finished'])
                    if result['go']:
                        cw.marker(journal, 'GO', result['finished'])
                    return result
                if result['status'] == 'not_ready':
                    cw.marker(journal, 'not_ready', result['finished'])
                    on_receipt(result)
                    return result
            elapsed_tick = (sampler.ctx.clocks.monotonic_ns()-tick)/cw.NS
            sampler.ctx.clocks.sleep(max(0, 1-elapsed_tick))
    except BaseException as exc:
        failed = dict(attempt.last_result or {
            'schema': cw.RECEIPT, **attempt.identity, 'policy_sha256': cw.digest(policy),
            'trace_sha256': attempt.hash.hexdigest(), 'samples': attempt.samples,
            'finished': sampler.ctx.stamp().to_json()})
        failed.update(status='cancelled' if isinstance(exc, (InterruptedError, KeyboardInterrupt)) else 'error',
                      go=False, error=f'{type(exc).__name__}:{exc}')
        cw.marker(journal, 'not_ready', failed['finished'])
        on_receipt(failed)
        raise
    finally:
        sampler.close()


def observation(sampler, header):
    """Failed source reads are unobserved rows, never stale successful values."""
    started = sampler.ctx.stamp().to_json()
    try:
        return sampler.sample(attempt_id=header['attempt_id'], boot_id=header['boot_id'])
    except Exception as exc:
        return {'schema': cw.SAMPLE, 'attempt_id': header['attempt_id'], 'boot_id': header['boot_id'],
                'started': started, 'finished': sampler.ctx.stamp().to_json(),
                'source_error': f'{type(exc).__name__}:{exc}', 'final_checks_passed': False}


class ArmWait:
    """Adapter for hazards.arm.ArmConfig.start_state (one shared native dwell).

    The arm still owns final clock, battery, thermal and agent-census checks.
    This adapter adds the fresh R16 recheck at GO and closes before the caller
    launches any member. No journal or collector survives the arm.
    """
    def __init__(self, policy, header, sampler, *, journal, trace,
                 incumbent_ready=lambda: False, on_receipt=lambda r: None):
        self.policy = cw.validate_policy(policy)
        self.attempt = None
        self.header, self.sampler = header, sampler
        self.journal, self.trace = journal, trace
        self.incumbent_ready, self.on_receipt = incumbent_ready, on_receipt
        self.pending = []
        self.receipt = None
        self.closed = False
        self.sampler.guard_reader = lambda: []

    def start(self):
        try:
            self.sampler.start()
            if self.sampler.boot_id() != self.header['boot_id']:
                raise ValueError('boot changed before native R16 guard')
        except Exception:
            if self.policy['mode'] == 'condition':
                raise
        # Cadence/collectors and all heavy arm preparation precede this point.
        # Their completion is a disruptive boundary, not part of a quiet suffix.
        self.header['started'] = self.sampler.ctx.stamp().to_json()
        self.header['quiet_start_ns'] = self.header['started']['monotonic_ns']
        self.attempt = cw.Attempt(self.policy, **self.header)
        cw.marker(self.journal, 'quiet_start', {**self.header['started'],
            'monotonic_ns': self.header['quiet_start_ns'],
            'wall_ns': self.header['started']['wall_ns']-(
                self.header['started']['monotonic_ns']-self.header['quiet_start_ns'])})

    def interval(self, result):
        self.pending.append(result)

    def tick(self, *, go=False):
        row = observation(self.sampler, self.header)
        row['guard_intervals'], self.pending = self.pending, []
        row['power_intervals'] = [p for p in row.get('power_intervals', [])
                                  if p['start_ns'] >= self.attempt.start]
        row['go'], row['incumbent_ready'] = go, self.incumbent_ready() is True
        self.trace.write(cw.canonical(row).decode()+'\n')
        self.receipt = self.attempt.feed(row, go=go, incumbent_ready=row['incumbent_ready'])
        return self.receipt

    def ready(self):
        return self.receipt is not None and self.receipt['status'] == 'released'

    def binding(self):
        r = self.receipt or {}
        return {'receipt_sha256': cw.digest(r) if r else None,
                'policy_sha256': cw.digest(self.policy), 'attempt_id': self.header['attempt_id'],
                'boot_id': self.header['boot_id']}

    def stop(self):
        return self.receipt is not None and self.receipt['status'] == 'not_ready'

    def at_go(self):
        result = self.tick(go=True)
        if result['go']:
            cw.marker(self.journal, 'release', result['finished'])
        return result['go']

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.sampler.close()
            finally:
                if self.receipt is not None:
                    if self.receipt['status'] == 'not_ready':
                        cw.marker(self.journal, 'not_ready', self.receipt['finished'])
                    self.on_receipt(self.receipt)


def arm_with_start_state(config, policy, header, sampler, *, journal, trace,
                         incumbent_ready=lambda: False, on_receipt=lambda r: None, seams=None):
    """Prospective native entry: start state and guard release at their max.

    Registered callers use this entry instead of serial evaluator + arm calls.
    Native smoke/replay and registration are required before enabling it.
    """
    import dataclasses
    from joulewise.hazards import arm
    if any(config.thresholds['contention'].get(k) != v for k, v in policy['guard'].items()):
        raise ValueError('R16 shared native guard differs from the frozen policy thresholds')
    gate = ArmWait(policy, header, sampler, journal=journal, trace=trace,
                   incumbent_ready=incumbent_ready, on_receipt=on_receipt)
    try:
        result = arm.run(dataclasses.replace(config, start_state=gate), seams)
        if result.go:
            cw.marker(journal, 'GO', sampler.ctx.stamp().to_json())
        return result
    finally:
        gate.close()


def registered_arm(config, policy, *, attempt_id, seams=None):
    """Launchd binding for a prospectively registered ALIGN cohort.

    Load only explicitly installed inputs; policy comes from the bound pack.
    The install receipt is never reused for GO. Failed attempts keep their
    native trace and receipt. No directory search or model/data read occurs.
    """
    from pathlib import Path
    from joulewise.align.apple import external_volume, v4_topup
    policy = cw.validate_policy(policy)
    custody = Path(config.custody_dir)
    inputs = json.loads((custody/'condition_waits_inputs.json').read_bytes())
    if (inputs.get('schema') != 'joulewise.align.condition_waits.native_inputs.v1'
            or inputs.get('policy_sha256') != cw.digest(policy) or inputs.get('attempt_id') != attempt_id):
        raise ValueError('R16 installed inputs do not bind this plan/policy')
    if policy['q'] is not None and not inputs.get('setup_attested_by'):
        raise ValueError('R16 registered support/cooler/setup attestation missing')
    directory = custody/'hazards'
    directory.mkdir(parents=True, exist_ok=True)
    ctx = Context(raw_dir=directory/'condition-waits-raw', custody_root=custody)

    def topup(now):
        observed = v4_topup.derive_from_file(inputs['battery_log'], now)
        if observed and observed['admissible']:
            return {'completed_at_epoch_s': observed['completed_at_epoch_s'], 'source': observed['source']}
        return None

    def setup():
        census = external_volume.census(external_volume.run_command)
        result = external_volume.arm_check(external_volume.validate_config(None), census,
                                          run=external_volume.run_command)
        return {'passed': result['verdict'] == external_volume.PASS,
                'setup_sha256': policy['q']['setup_sha256'] if policy['q'] else None}

    sampler = NativeSampler(policy, ctx=ctx, topup_reader=topup, setup_check=setup,
                            obc_off_attested_by=inputs['obc_off_attested_by'])
    # Retry is never automatic: the magistrate provides a fresh ambient check
    # and the first failure's digest through a new install after disposal.
    try:
        boot = sampler.boot_id()
    except Exception:
        if policy['mode'] == 'condition':
            raise
        boot = 'unobserved'
    h = dict(attempt_id=attempt_id, boot_id=boot, started=ctx.stamp().to_json(),
             quiet_start_ns=ctx.clocks.monotonic_ns(),
             attempt_number=inputs.get('attempt_number', 1), ambient_check=inputs.get('ambient_check'))
    # Keep first construction ordered: quiet_start is no later than started.
    h['quiet_start_ns'] = h['started']['monotonic_ns']
    def save(receipt):
        with (directory/'condition-waits-receipt.json').open('x') as handle:
            json.dump({'header': h, 'receipt': receipt}, handle, sort_keys=True, allow_nan=False)
            handle.write('\n')
    timing = custody/'night'/'chain-stages.jsonl'
    timing.parent.mkdir(parents=True, exist_ok=True)
    with timing.open('a') as journal, (directory/'condition-waits-trace.jsonl').open('x') as trace:
        return arm_with_start_state(config, policy, h, sampler, journal=journal, trace=trace,
                                    # Incumbent setup/cooldown was admitted at install;
                                    # the unchanged native arm still owns its clean run.
                                    incumbent_ready=lambda: True, on_receipt=save, seams=seams)
