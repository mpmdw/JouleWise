#!/usr/bin/env python3
"""Cloud patch runner with v3 report and write-scope semantics (stdlib only).

Use --cx-bin for a test CLI. SOL_CLOUD_TEST_RATE_LIMIT_WAIT overrides the 900s
backoff; SOL_CLOUD_TEST_POLL_FLOOR overrides the default 0.1s polling floor.
--record-dir saves each CLI argv, return code and raw stdout/stderr separately.
Continuation finds <out>.state.json in the current directory (or
SOL_CLOUD_STATE_DIR); --state-file identifies an explicit state file. No global
registry is maintained. Cloud model/effort selection remains unverified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

GENRE_TEMPLATE = """
RUNNER-OWNED REPORT CONTRACT — mandatory for this out-file
ADAPTER: claude-codex-report/v1
GENRE: $1

Start the response with exactly one fenced JSON object and no introductory prose. The object must be UTF-8 and at most 8192 bytes. Follow it only with applicable prose sections below.

ENVELOPE SCHEMA:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "$1",
  "status": "clean|findings|blocked",
  "completion": "complete|partial|none",
  "summary": "nonempty one-line summary",
  "workspace": {"base_requested":"string|null","base_mode":"exact|descendant|informational|null","head_start":"string|null","head_end":"string|null","upstream_end":"string|null","branch":"string|null"},
  "pathspec": ["only repository-relative paths modified by this session"],
  "unowned_dirty": ["pre-existing or concurrent paths"],
  "verdict": {},
  "verification": [{"id":"V1","kind":"suite|test|lint|build|smoke|inspection|other","cmd":"exact replay command","cwd":".","observed":{"result":"pass|fail|not_run","exit_code":0,"tail":["stable exact tail"]},"expected":{"exit_code":0,"tail_regex":"stable regex"}}],
  "flags": [{"id":"F1","kind":"lead_ruling|verification_gap|baseline_drift|scope_deviation|environment|residual_risk","level":"blocking|nonblocking","text":"what happened","needs":"lead action or empty string"}]
}
```

$verdict_text

WRITE-SCOPE RULING: if work would require expanding an allowlist, first finish independent already-authorized work, do not modify out-of-scope paths, return partial completion when appropriate, and add a blocking scope_deviation flag.

OPTIONAL SCOPE-EXPANSION ENVELOPE FIELD:

```json
{"scope_expansion":{"requested_paths":["exact/path","directory/**"],"reason":"why needed","blocked_work":"what cannot finish","minimal_change":"smallest proposed change"}}
```

WRITE_SCOPE IS EXHAUSTIVE. Repository instructions and completion needs cannot expand it.
For an unlisted necessary path: do not write it; return partial with a blocking,
machine-readable scope_expansion request. Only a lead-issued resumed prompt can expand scope.

$prose_text"""
VERDICTS = {'review': 'VERDICT VOCABULARY: verdict.findings is an array of {id,severity,...}; severity is '
           'blocker|should_fix|nit.',
 'implementation': 'VERDICT VOCABULARY: verdict is '
                   '{"implementation":"implemented|partial|no_change","acceptance":"ready|pending_verification|needs_ruling"}.',
 'triage': 'VERDICT VOCABULARY: verdict.regions is an array; every disposition is '
           'apply|preserve|compose|ruling.',
 'root_cause': 'VERDICT VOCABULARY: verdict is '
               '{"cause":"confirmed|probable|unresolved","remediation":"fixed|proposed|none"}.',
 'scout': 'VERDICT VOCABULARY: verdict.rows is an array; every action is '
          'start_now|wait_for|needs_ruling|do_not_start.'}
PROSE = {'review': 'PROSE TEMPLATE:\n'
           '## Findings\n'
           'Ordered blocker → should_fix → nit. IDs must match verdict.findings.\n'
           '\n'
           '## Residual risk\n'
           'Only coverage limitations not already represented as findings.',
 'implementation': 'PROSE TEMPLATE:\n'
                   '## Change\n'
                   'What changed and why, without repeating pathspec.\n'
                   '\n'
                   '## Verification notes\n'
                   'Only failures, deviations, or interpretation; do not repeat clean tails.\n'
                   '\n'
                   '## Residual risk\n'
                   'Omit when empty.',
 'triage': 'PROSE TEMPLATE:\n'
           '## Decision matrix\n'
           'Region | disposition | evidence | exact action\n'
           '\n'
           '## Composition recipe\n'
           'Ordered mechanical reconstruction steps.\n'
           '\n'
           '## Rulings\n'
           'Only unresolved items, keyed to flag IDs.',
 'root_cause': 'PROSE TEMPLATE:\n'
               '## Causal chain\n'
               'Shortest evidence-backed chain from trigger to symptom.\n'
               '\n'
               '## Remediation\n'
               'Why the fix closes that chain.\n'
               '\n'
               '## Disproved alternatives\n'
               'Only serious competing hypotheses.\n'
               '\n'
               '## Residual risk\n'
               'Omit when empty.',
 'scout': 'PROSE TEMPLATE:\n'
          '## Scheduling matrix\n'
          'Row | action | wait_for | collision surface\n'
          '\n'
          '## Critical path\n'
          'Only cross-row dependencies.\n'
          '\n'
          '## Delegation contracts\n'
          'Include only when explicitly requested.'}

def genre_contract(genre):
    return (GENRE_TEMPLATE.replace('$1', genre)
            .replace('$verdict_text', VERDICTS[genre])
            .replace('$prose_text', PROSE[genre]) + '\n')


def parse_report(text, genre):
    """Python validator from v3, with file I/O replaced by parameters."""
    raw = text if isinstance(text, bytes) else text.encode('utf-8')
    genre_requested = genre or None
    report_bytes = len(raw)
    metrics = {
        "report_parse": "missing", "semantic_status": "unknown", "completion": "unknown",
        "finding_counts": {"blocker": 0, "should_fix": 0, "nit": 0},
        "blocking_flag_count": 0, "pathspec_count": 0, "unowned_dirty_count": 0,
        "scope_violation_count": 0, "verification_counts": {"pass": 0, "fail": 0, "not_run": 0},
        "header_bytes": 0, "report_bytes": report_bytes, "reported_changed_paths": [],
        "scope_expansion": None, "scope_expansion_valid": False,
    }
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = ""

    match = re.search(r"(?m)^```json[ \t]*\r?\n(.*?)^```[ \t]*$", text, re.S)
    if match:
        metrics["report_parse"] = "invalid"
        payload = match.group(1)
        payload_bytes = payload.encode("utf-8")
        metrics["header_bytes"] = len(payload_bytes)
        valid = text[:match.start()].strip() == "" and len(payload_bytes) <= 8192
        parsed = None
        if valid:
            try:
                if valid:
                    def no_duplicates(pairs):
                        result = {}
                        for key, value in pairs:
                            if key in result:
                                raise ValueError("duplicate key")
                            result[key] = value
                        return result
                    parsed = json.loads(
                        payload,
                        object_pairs_hook=no_duplicates,
                        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
                    )
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                valid = False

        def string_or_none(value):
            return value is None or isinstance(value, str)

        def validate(data):
            required = {"schema", "genre", "status", "completion", "summary", "workspace",
                        "pathspec", "unowned_dirty", "verdict", "verification", "flags"}
            if not isinstance(data, dict) or not required.issubset(data): return False
            if data["schema"] != "claude-codex-report/v1": return False
            genres = {"review", "implementation", "triage", "root_cause", "scout"}
            if data["genre"] not in genres or (genre_requested and data["genre"] != genre_requested): return False
            if data["status"] not in {"clean", "findings", "blocked"}: return False
            if data["completion"] not in {"complete", "partial", "none"}: return False
            if not isinstance(data["summary"], str) or not data["summary"].strip(): return False
            workspace = data["workspace"]
            workspace_keys = {"base_requested", "base_mode", "head_start", "head_end", "upstream_end", "branch"}
            if not isinstance(workspace, dict) or not workspace_keys.issubset(workspace): return False
            if workspace["base_mode"] not in {"exact", "descendant", "informational", None}: return False
            if not all(string_or_none(workspace[key]) for key in workspace_keys - {"base_mode"}): return False
            if not isinstance(data["pathspec"], list) or not all(isinstance(x, str) for x in data["pathspec"]): return False
            if any(not x or x.startswith("/") or ".." in x.split("/") for x in data["pathspec"]): return False
            if not isinstance(data["unowned_dirty"], list) or not all(isinstance(x, str) for x in data["unowned_dirty"]): return False
            verdict = data["verdict"]
            if not isinstance(verdict, dict): return False
            if data["genre"] == "implementation":
                if verdict.get("implementation") not in {"implemented", "partial", "no_change"}: return False
                if verdict.get("acceptance") not in {"ready", "pending_verification", "needs_ruling"}: return False
            elif data["genre"] == "root_cause":
                if verdict.get("cause") not in {"confirmed", "probable", "unresolved"}: return False
                if verdict.get("remediation") not in {"fixed", "proposed", "none"}: return False
            elif data["genre"] == "review":
                findings = verdict.get("findings")
                if not isinstance(findings, list): return False
                if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or x.get("severity") not in {"blocker", "should_fix", "nit"} for x in findings): return False
            elif data["genre"] == "triage":
                regions = verdict.get("regions")
                if not isinstance(regions, list): return False
                if any(not isinstance(x, dict) or x.get("disposition") not in {"apply", "preserve", "compose", "ruling"} for x in regions): return False
            elif data["genre"] == "scout":
                rows = verdict.get("rows")
                if not isinstance(rows, list): return False
                if any(not isinstance(x, dict) or x.get("action") not in {"start_now", "wait_for", "needs_ruling", "do_not_start"} for x in rows): return False
            if not isinstance(data["verification"], list): return False
            for item in data["verification"]:
                if not isinstance(item, dict) or not {"id", "kind", "cmd", "cwd", "observed", "expected"}.issubset(item): return False
                if not all(isinstance(item[key], str) for key in ("id", "kind", "cmd", "cwd")): return False
                observed, expected = item["observed"], item["expected"]
                if not isinstance(observed, dict) or not {"result", "exit_code", "tail"}.issubset(observed): return False
                if observed["result"] not in {"pass", "fail", "not_run"}: return False
                if observed["exit_code"] is not None and (not isinstance(observed["exit_code"], int) or isinstance(observed["exit_code"], bool)): return False
                if not isinstance(observed["tail"], list) or not all(isinstance(x, str) for x in observed["tail"]): return False
                if not isinstance(expected, dict) or not {"exit_code", "tail_regex"}.issubset(expected): return False
                if expected["exit_code"] is not None and (not isinstance(expected["exit_code"], int) or isinstance(expected["exit_code"], bool)): return False
                if not isinstance(expected["tail_regex"], str): return False
            kinds = {"lead_ruling", "verification_gap", "baseline_drift", "scope_deviation", "environment", "residual_risk"}
            if not isinstance(data["flags"], list): return False
            for flag in data["flags"]:
                if not isinstance(flag, dict) or not {"id", "kind", "level", "text", "needs"}.issubset(flag): return False
                if flag["kind"] not in kinds or flag["level"] not in {"blocking", "nonblocking"}: return False
                if not all(isinstance(flag[key], str) for key in ("id", "text", "needs")): return False
            if "scope_expansion" in data:
                expansion = data["scope_expansion"]
                expansion_keys = {"requested_paths", "reason", "blocked_work", "minimal_change"}
                if not isinstance(expansion, dict) or set(expansion) != expansion_keys: return False
                if not isinstance(expansion["requested_paths"], list) or not expansion["requested_paths"]: return False
                if not all(isinstance(x, str) for x in expansion["requested_paths"]): return False
                if not all(isinstance(expansion[x], str) and expansion[x].strip() for x in ("reason", "blocked_work", "minimal_change")): return False
            return True

        try:
            valid = valid and validate(parsed)
        except (TypeError, KeyError):
            valid = False
        if valid:
            metrics["report_parse"] = "valid"
            metrics["semantic_status"] = parsed["status"]
            metrics["completion"] = parsed["completion"]
            metrics["pathspec_count"] = len(parsed["pathspec"])
            metrics["reported_changed_paths"] = sorted(set(parsed["pathspec"]))
            metrics["unowned_dirty_count"] = len(parsed["unowned_dirty"])
            metrics["blocking_flag_count"] = sum(f["level"] == "blocking" for f in parsed["flags"])
            for item in parsed["verification"]:
                metrics["verification_counts"][item["observed"]["result"]] += 1
            if parsed["genre"] == "review":
                for finding in parsed["verdict"]["findings"]:
                    metrics["finding_counts"][finding["severity"]] += 1
            if "scope_expansion" in parsed:
                metrics["scope_expansion"] = parsed["scope_expansion"]
                blocking_scope = any(f["kind"] == "scope_deviation" and f["level"] == "blocking" for f in parsed["flags"])
                verdict_ready = parsed["genre"] != "implementation" or parsed["verdict"].get("acceptance") == "needs_ruling"
                metrics["scope_expansion_valid"] = parsed["status"] == "blocked" and parsed["completion"] == "partial" and blocking_scope and verdict_ready

    return metrics

class Refusal(Exception):
    def __init__(self, message, rc=64):
        super().__init__(message)
        self.rc = rc


def normalize_scope(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError as exc:
            raise Refusal(f'invalid scope JSON: {exc}') from exc
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise Refusal('scope must be a JSON array of strings')
    seen = set()
    for entry in value:
        exact = entry[:-3] if entry.endswith('/**') else entry
        if (not exact or exact in {'.', '..'} or exact.startswith(('/', './')) or
                exact.endswith('/') or '//' in exact or '\\' in exact or
                any(part in {'', '.', '..'} for part in exact.split('/')) or
                exact.split('/')[0] == '.git' or any(ch in exact for ch in '*?[]{}') or
                entry.count('**') > (1 if entry.endswith('/**') else 0)):
            raise Refusal(f'invalid scope entry: {entry!r}')
        if entry in seen:
            raise Refusal(f'duplicate scope entry: {entry!r}')
        seen.add(entry)
    return list(value)


def allowed(path, scope):
    return any(path == entry or (entry.endswith('/**') and
               path.startswith(entry[:-3] + '/')) for entry in scope)


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def report_path(job):
    return f'.codex-report/{job}.md'


def build_prompt(prompt, genre, scope, job):
    return (prompt + '\n' + genre_contract(genre) +
            '\nRUNNER AUTHORITATIVE WRITE_SCOPE (JSON; exhaustive): ' +
            compact(scope + [report_path(job)]) + '\n' +
            'Before you finish, write your complete final report, starting with the fenced JSON envelope,\n'
            f'to `{report_path(job)}`. The runner reads only that file. Do not commit it.')


def utc():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def git(repo, *args, check=True):
    proc = subprocess.run(['git', '-C', str(repo), *map(str, args)],
                          capture_output=True)
    if check and proc.returncode:
        raise Refusal(proc.stderr.decode('utf-8', 'replace').strip(), 74)
    return proc


def git_value(repo, *args):
    return git(repo, *args, check=False).stdout.decode('utf-8', 'replace').strip() or None


def remote_sha(repo, branch):
    proc = git(repo, 'ls-remote', 'origin', f'refs/heads/{branch}', check=False)
    rows = proc.stdout.decode().splitlines()
    if proc.returncode or not rows:
        raise Refusal('branch absent from origin; push first')
    return rows[0].split()[0]


def log(state, message):
    with open(state['out'] + '.log', 'ab') as stream:
        stream.write((utc() + ' ' + message + '\n').encode())


class Transport:
    def __init__(self, state, deadline):
        self.state, self.deadline = state, deadline
        self.calls = 0

    def call(self, *args):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        argv = [self.state['cx_bin'], 'cloud', *map(str, args)]
        self.calls += 1
        try:
            proc = subprocess.run(argv, capture_output=True, timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            self.record(argv, 143, exc.stdout or b'', exc.stderr or b'')
            raise TimeoutError from exc
        except OSError as exc:
            self.record(argv, 1, b'', str(exc).encode())
            raise Refusal(f'cloud CLI could not start: {exc}', 1) from exc
        self.record(argv, proc.returncode, proc.stdout, proc.stderr)
        return proc

    def record(self, argv, rc, stdout, stderr):
        with open(self.state['out'] + '.log', 'ab') as stream:
            stream.write((utc() + f' cloud {argv[2]} rc={rc}\n').encode())
            stream.write(stdout)
            stream.write(stderr)
        if self.state.get('record_dir'):
            root = Path(self.state['record_dir'])
            root.mkdir(parents=True, exist_ok=True)
            # Exclusive files keep earlier continuation recordings intact.
            prefix = root / f'{self.state["run_key"]}-{self.state["attempt"]}-{self.calls:04d}'
            for suffix, data in [('.stdout', stdout), ('.stderr', stderr),
                                 ('.json', compact({'argv': argv, 'rc': rc}).encode())]:
                with open(str(prefix) + suffix, 'xb') as stream:
                    stream.write(data)

    def wait(self, seconds):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        time.sleep(min(seconds, remaining))
        if time.monotonic() >= self.deadline:
            raise TimeoutError


def rate_limited(proc):
    return bool(re.search(rb'429|rate limit', proc.stdout + proc.stderr, re.I))


def rate_wait():
    return float(os.environ.get('SOL_CLOUD_TEST_RATE_LIMIT_WAIT', '900'))


def parse_task_id(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    match = re.search(r'/codex/tasks/([A-Za-z0-9_-]+)|\b(task_[A-Za-z0-9_-]+)', text)
    return (match.group(1) or match.group(2)) if match else None


def list_tasks(transport):
    tasks, cursor = [], None
    for _ in range(5):
        argv = ['list', '--env', transport.state['cloud_env'], '--json', '--limit', '20']
        if cursor:
            argv += ['--cursor', cursor]
        proc = transport.call(*argv)
        if rate_limited(proc):
            transport.wait(rate_wait())
            return None, 'rate_limit'
        if proc.returncode:
            return None, 'failed'
        try:
            data = json.loads(proc.stdout)
            page = data['tasks']
            cursor = data.get('cursor')
            if not isinstance(page, list) or not all(isinstance(t, dict) for t in page):
                raise ValueError('invalid tasks')
            if cursor is not None and not isinstance(cursor, str):
                raise ValueError('invalid cursor')
        except (ValueError, KeyError, TypeError):
            return None, 'failed'
        tasks.extend(page)
        if not cursor or any(t.get('id') == transport.state.get('session_id') for t in page):
            break
    return tasks, None


def submit(transport, prompt):
    state = transport.state
    submitted = dt.datetime.now(dt.timezone.utc)
    argv = ['exec', '--env', state['cloud_env'], '--branch', state['cloud_branch']]
    if state['model']:
        argv += ['-c', 'model=' + json.dumps(state['model'])]
    if state['effort']:
        argv += ['-c', 'model_reasoning_effort=' + json.dumps(state['effort'])]
    argv += [prompt]
    for attempt in range(state['retries'] + 1):
        proc = transport.call(*argv)
        with open(state['out'] + '.submit.txt', 'ab') as stream:
            stream.write(proc.stdout)
            stream.write(proc.stderr)
        if rate_limited(proc):
            if attempt < state['retries']:
                transport.wait(rate_wait())
                continue
            raise Refusal('rate limit; retries exhausted', 1)
        if proc.returncode:
            raise Refusal('cloud submit failed', 1)
        task_id = parse_task_id(proc.stdout + proc.stderr)
        if task_id:
            return task_id
        tasks, failure = list_tasks(transport)
        candidates = []
        for task in tasks or []:
            try:
                updated = dt.datetime.fromisoformat(task['updated_at'].replace('Z', '+00:00'))
                if updated >= submitted and isinstance(task.get('id'), str):
                    candidates.append((updated, task['id']))
            except (KeyError, TypeError, ValueError, AttributeError):
                pass
        if candidates:
            return max(candidates)[1]
        raise Refusal(f'cannot identify submitted task ({failure or "not listed"})', 1)


def poll(transport):
    failures = 0
    while True:
        tasks, failure = list_tasks(transport)
        if failure == 'failed':
            failures += 1
            if failures >= 5:
                raise Refusal('five consecutive list failures', 1)
        elif failure is None:
            failures = 0
            task = next((t for t in tasks if t.get('id') == transport.state['session_id']), {})
            status = task.get('status', 'not_listed')
            if not isinstance(status, str):
                status = 'unknown'
            log(transport.state, f'poll task={transport.state["session_id"]} status={status}')
            if task.get('url'):
                transport.state['cloud_task_url'] = task['url']
            if status in {'ready', 'applied'}:
                return
            if status == 'error':
                raise Refusal('cloud task error', 1)
        log(transport.state, f'poll list={failure or "ok"}')
        transport.wait(max(transport.state['poll'], float(os.environ.get('SOL_CLOUD_TEST_POLL_FLOOR', '0.1'))))


def fetch_patch(transport):
    proc = transport.call('diff', '--attempt', '1', transport.state['session_id'])
    Path(transport.state['patch_path']).write_bytes(proc.stdout)
    if proc.returncode or proc.stdout.lstrip().startswith(b'*** Begin Patch'):
        raise Refusal('diff capture failed', 1)
    return proc.stdout


def unquote_path(value):
    """Decode git's C quoting, including octal UTF-8 bytes."""
    if not value.startswith(b'"'):
        return value.decode('utf-8', 'surrogateescape')
    if not value.endswith(b'"'):
        raise ValueError('unterminated quoted path')
    data, i = bytearray(), 1
    escapes = {ord(k): ord(v) for k, v in [('a', '\a'), ('b', '\b'), ('t', '\t'),
               ('n', '\n'), ('v', '\v'), ('f', '\f'), ('r', '\r'), ('"', '"'), ('\\', '\\')]}
    while i < len(value) - 1:
        ch = value[i]
        i += 1
        if ch != 92:
            data.append(ch)
        elif i < len(value) - 1 and value[i] in b'01234567':
            match = re.match(rb'[0-7]{1,3}', value[i:])
            data.append(int(match[0], 8))
            i += len(match[0])
        else:
            if i >= len(value) - 1 or value[i] not in escapes:
                raise ValueError('invalid quoted escape')
            data.append(escapes[value[i]])
            i += 1
    return data.decode('utf-8', 'surrogateescape')


def diff_pair(raw):
    if raw.startswith(b'"'):
        token = re.match(rb'"(?:[^"\\]|\\.)*"', raw)
        if not token:
            raise ValueError('invalid diff header')
        return unquote_path(token[0]), unquote_path(raw[token.end():].lstrip())
    if b' "b/' in raw:
        a, b = raw.split(b' "b/', 1)
        return unquote_path(a), unquote_path(b'"b/' + b)
    # Git leaves spaces unquoted. Prefer equal paths, then a unique separator.
    candidates = [(raw[:m.start()], raw[m.start()+1:]) for m in re.finditer(rb' b/', raw)]
    for a, b in candidates:
        if a[2:] == b[2:]:
            return unquote_path(a), unquote_path(b)
    if len(candidates) == 1:
        return tuple(unquote_path(x) for x in candidates[0])
    raise ValueError('ambiguous diff header')


def patch_details(patch_bytes):
    paths, modes, new_files, sections = set(), {}, set(), []
    section = None
    for line in patch_bytes.splitlines():
        if line.startswith(b'diff --git '):
            a, b = diff_pair(line[11:])
            if not a.startswith('a/') or not b.startswith('b/'):
                raise ValueError('invalid diff prefixes')
            section = {'a': a[2:], 'b': b[2:], 'new': False}
            sections.append(section)
            paths.update((a[2:], b[2:]))
        elif section is not None:
            if line.startswith((b'rename from ', b'copy from ')):
                source = unquote_path(line.split(b' ', 2)[2])
                paths.add(source)
                if line.startswith(b'copy from '):
                    section['copy_from'] = source
            elif line.startswith((b'rename to ', b'copy to ')):
                paths.add(unquote_path(line.split(b' ', 2)[2]))
            elif line.startswith((b'--- ', b'+++ ')):
                path = unquote_path(line[4:].split(b'\t', 1)[0])
                if path != '/dev/null':
                    paths.add(path[2:] if path.startswith(('a/', 'b/')) else path)
            elif line.startswith(b'index ') and len(line.split()) == 3:
                modes[section['b']] = line.split()[-1].decode('ascii')
            elif line.startswith((b'new file mode ', b'new mode ')):
                mode = line.split()[-1].decode('ascii')
                modes[section['b']] = mode
                if line.startswith(b'new file mode '):
                    new_files.add(section['b'])
                    section['new'] = True
    return paths, modes, new_files, sections


def patch_paths_headers(patch_bytes):
    return patch_details(patch_bytes)[0]


def patch_paths_git(patch_path):
    with tempfile.TemporaryDirectory(prefix='sol-patch-') as root:
        proc = subprocess.run(['git', 'apply', '--numstat', '--summary', '-z',
                               '--allow-empty', str(Path(patch_path).resolve())],
                              cwd=root, capture_output=True)
    if proc.returncode:
        raise ValueError('git patch parser rejected patch: ' + proc.stderr.decode('utf-8', 'replace'))
    paths = set()
    raw = proc.stdout
    # --numstat -z uses a blank third column followed by old\0new\0 for moves.
    while raw and re.match(rb'(?:\d+|-)\t(?:\d+|-)\t', raw):
        record, raw = raw.split(b'\0', 1)
        name = record.split(b'\t', 2)[2]
        if name:
            paths.add(name.decode('utf-8', 'surrogateescape'))
        else:
            for _ in range(2):
                name, raw = raw.split(b'\0', 1)
                paths.add(name.decode('utf-8', 'surrogateescape'))
    for line in raw.splitlines():
        match = re.match(rb' (?:create|delete) mode \d+ (.*)', line)
        if match:
            paths.add(unquote_path(match[1]))
        match = re.match(rb' mode change \d+ => \d+ (.*)', line)
        if match:
            paths.add(unquote_path(match[1]))
        match = re.match(rb' (?:rename|copy) (.*) \(\d+%\)$', line)
        if match:
            summary = match[1]
            candidates = []
            for arrow in re.finditer(rb' => ', summary):
                left, right = summary[:arrow.start()], summary[arrow.end():]
                candidates.append((unquote_path(left), unquote_path(right)))
                # Git compresses a shared prefix/suffix: dir/{old => new}.txt.
                for opening in re.finditer(rb'\{', left):
                    for closing in re.finditer(rb'\}', right):
                        prefix, suffix = left[:opening.start()], right[closing.end():]
                        candidates.append((unquote_path(prefix + left[opening.end():] + suffix),
                                           unquote_path(prefix + right[:closing.start()] + suffix)))
            matched = [pair for pair in candidates if pair[1] in paths]
            if len(set(matched)) != 1:
                raise ValueError('ambiguous git rename/copy summary')
            paths.update(matched[0])
    return paths


def check_scope(paths, scope, job, modes=None, apply_base=None):
    violations, kinds = set(), {}
    report = report_path(job)
    for path in paths:
        kind = None
        if path.startswith('/') or '..' in path.split('/') or path.split('/')[0] == '.git':
            kind = 'unsafe_path'
        elif path.startswith('.codex-report/') and path != report:
            kind = 'report_path'
        elif (modes or {}).get(path) in {'120000', '160000'}:
            kind = 'unsafe_mode'
        elif path != report and not allowed(path, scope):
            kind = 'outside_scope'
        if kind:
            violations.add(path)
            kinds[path] = kind
    if apply_base:
        for entry in scope:
            current = Path(apply_base)
            for part in (entry[:-3] if entry.endswith('/**') else entry).split('/'):
                current /= part
                if current.is_symlink():
                    violations.add(entry)
                    kinds[entry] = 'symlink_ancestor'
                    break
    return sorted(violations), kinds


def extract_report(patch_path, job):
    with tempfile.TemporaryDirectory(prefix='sol-report-') as root:
        proc = subprocess.run(['git', 'apply', '--include=' + report_path(job).replace('codex', '[c]odex'),
                               str(Path(patch_path).resolve())], cwd=root, capture_output=True)
        report = Path(root) / report_path(job)
        if proc.returncode or not report.is_file() or report.is_symlink():
            return b''
        return report.read_bytes()


def decide(metrics, violations=(), transport_rc=0):
    if transport_rc:
        return 'FAILED', transport_rc, 'failed_preserved'
    if violations:
        return 'SCOPE_VIOLATION', 77, 'failed_preserved'
    if metrics['report_parse'] != 'valid' or (metrics['scope_expansion'] is not None and
                                             not metrics['scope_expansion_valid']):
        return 'ACCEPTANCE_FAILED', 65, 'acceptance_failed'
    if metrics['scope_expansion'] is not None:
        return 'NEEDS_SCOPE', 79, 'needs_scope'
    return 'OK', 0, 'passed'


def staged_paths(repo):
    fields = git(repo, 'diff', '--cached', '--name-status', '-z').stdout.split(b'\0')
    paths, index = set(), 0
    while index < len(fields) and fields[index]:
        count = 2 if fields[index].startswith((b'R', b'C')) else 1
        for raw in fields[index+1:index+1+count]:
            paths.add(raw.decode('utf-8', 'surrogateescape'))
        index += count + 1
    return paths


def apply_patch(state, checked, existing=False):
    repo, target = state['cdir'], state['apply_worktree']
    created = False
    if not existing:
        stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        state['apply_branch'] = f'cloud/{state["job"]}-{stamp}'
        proc = git(repo, 'worktree', 'add', '-b', state['apply_branch'], target,
                   state['base_sha'], check=False)
        if proc.returncode:
            raise Refusal('worktree add failed: ' + proc.stderr.decode('utf-8', 'replace'), 74)
        created = True
    proc = git(target, 'apply', '--index', '--allow-empty',
               '--exclude=' + report_path(state['job']).replace('codex', '[c]odex'), state['patch_path'], check=False)
    # A pure copy's source is scope-checked (conservatively) but is not staged,
    # because the copy leaves it unchanged: allow exactly those to be absent.
    copy_sources = {s['copy_from'] for s in patch_details(Path(state['patch_path']).read_bytes())[3]
                    if s.get('copy_from')}
    staged, expected = (staged_paths(target) if not proc.returncode else set()), set(checked)
    if proc.returncode or not (staged <= expected and expected - staged <= copy_sources):
        if created:
            git(repo, 'worktree', 'remove', '--force', target, check=False)
            git(repo, 'branch', '-D', state['apply_branch'], check=False)
        else:
            # The resume preflight guaranteed clean HEAD; roll back only the
            # staged patch this invocation just applied if comparison fails.
            if not proc.returncode:
                git(target, 'apply', '--reverse', '--index', '--allow-empty',
                    '--exclude=' + report_path(state['job']).replace('codex', '[c]odex'), state['patch_path'], check=False)
        raise Refusal('patch apply failed or staged path set disagreed', 74)


def append_manifest(state, row):
    Path(state['manifest']).parent.mkdir(parents=True, exist_ok=True)
    with open(state['manifest'], 'a', encoding='utf-8') as stream:
        stream.write(compact(row) + '\n')


def cloud_keys(state):
    return {k: state.get(k) for k in ('cloud_env', 'cloud_branch', 'cloud_task_id',
            'cloud_task_url', 'base_sha', 'patch_path', 'apply_worktree', 'apply_branch')} | {
            'transport': 'codex-cloud', 'model_verified': False}


def prompt_value(prompt, key):
    match = re.search(r'(?m)^' + re.escape(key) + r':[ \t]*(.*)$', prompt)
    return match[1].strip() if match else None


def started_row(state, prompt):
    original = state['original_prompt']
    baseline = (prompt_value(original, 'BASELINE') or '').split(' ', 1)
    mode = baseline[0] if baseline[0] in {'exact', 'descendant', 'informational'} else None
    profile = prompt_value(original, 'VERIFICATION_PROFILE')
    if not profile:
        match = re.search(r'(?m)^REQUIRED_VERIFICATION:[ \t]*\n\s*-\s*(.*)', original)
        profile = match[1] if match else None
    return {'schema_version': 3, 'event': 'run_started', 'run_key': state['run_key'],
            'task_id': prompt_value(original, 'TASK_ID'), 'attempt': state['attempt'],
            'parent_run_key': prompt_value(original, 'PARENT_RUN_KEY'), 'genre': state['genre'],
            'prompt_contract': 'claude-codex-report/v1', 'report_contract': 'claude-codex-report/v1',
            'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(), 'prompt_bytes': len(prompt.encode()),
            'base_requested': baseline[1] if mode and len(baseline) > 1 else None, 'base_mode': mode,
            'head_start': git_value(state['cdir'], 'rev-parse', 'HEAD'),
            'upstream_start': git_value(state['cdir'], 'rev-parse', '@{upstream}'),
            'branch_start': git_value(state['cdir'], 'branch', '--show-current'),
            'write_scope': state['write_scope'], 'verification_profile': profile,
            'model': state['model'], 'reasoning_effort': state['effort'], 'sandbox': state['sandbox'],
            'cwd': state['cdir'], 'out': state['out'], 'role_or_lens': state.get('role'),
            'parent_report': state.get('parent'), 'started_at': state['started_at'], **cloud_keys(state)}


def write_outputs(state, metrics, rc, transport_rc, error_stage, started, paths, violations):
    out = Path(state['out'])
    size = out.stat().st_size if out.exists() else 0
    status = (f'TIMEOUT after {state["timeout"]:g}s' if transport_rc == 143 else
              f'FAILED rc={transport_rc}' if transport_rc else
              f'OK (WARN: thin output, {size} bytes — verify via git diff/artifacts)' if size < 400 else 'OK')
    evidence = state.get('evidence_bundle')
    if violations:
        metrics['semantic_status'] = 'blocked'
        metrics['completion'] = 'partial' if set(paths) - set(violations) else 'none'
    rows = [status, 'semantic_status=' + metrics['semantic_status'],
            'completion=' + metrics['completion'], 'run_status=' + state['run_status'],
            'scope_action=' + state['scope_action']]
    if evidence:
        rows += ['evidence_bundle=' + evidence]
        meta = {'run_key': state['run_key'], 'write_scope': state['write_scope'],
                'actual_changed_paths': paths, 'scope_violation_paths': violations,
                'transport_status': status, 'scope_action': 'failed_preserved'}
        Path(evidence).mkdir(parents=True, exist_ok=True)
        Path(evidence, 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        shutil.copyfile(state['patch_path'], Path(evidence, 'patch.diff'))
    Path(str(out) + '.status').write_text('\n'.join(rows) + '\n')
    reported = metrics['reported_changed_paths']
    scope_metrics = {'scope_policy_version': 1, 'scope_enforcement': 'posthoc',
                     'actual_changed_paths': paths, 'actual_changed_count': len(paths),
                     'attempt_changed_paths': paths, 'attempt_changed_count': len(paths),
                     'reported_changed_paths': reported, 'reported_changed_count': len(reported),
                     'scope_violation_paths': violations, 'scope_violation_count': len(violations),
                     'pathspec_report_mismatch': set(paths) != set(reported),
                     'scope_action': state['scope_action'], 'evidence_bundle': evidence}
    row = {'schema_version': 3, 'event': 'run_finished', 'run_key': state['run_key'],
           'attempt': state['attempt'], 'session_id': state.get('session_id'),
           'invocation_state': 'timeout' if transport_rc == 143 else 'failed' if transport_rc else 'ok',
           'runner_rc': rc, 'error_stage': error_stage,
           'duration_ms': int((time.monotonic() - started) * 1000),
           'head_end': git_value(state['cdir'], 'rev-parse', 'HEAD'),
           'upstream_end': git_value(state['cdir'], 'rev-parse', '@{upstream}'),
           **metrics, **scope_metrics, 'run_status': state['run_status'],
           'model': state['model'], 'reasoning_effort': state['effort'],
           'transport_status': status, 'token_usage': None, 'finished_at': utc(), **cloud_keys(state)}
    append_manifest(state, row)
    state['metrics'] = metrics
    state['actual_changed_paths'] = paths
    state['scope_violation_paths'] = violations
    if state['run_status'] == 'NEEDS_SCOPE':
        state['pending_scope_expansion'] = metrics['scope_expansion']
    else:
        state.pop('pending_scope_expansion', None)
    Path(state['state_file']).write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f'codex-run exit: {status} -> {out}')


def inspect_patch(state, patch):
    headers, modes, new_files, sections = patch_details(patch)
    parsed = patch_paths_git(state['patch_path'])
    if headers != parsed:
        raise ValueError('patch parse disagreement')
    base = state['apply_worktree'] if Path(state['apply_worktree']).exists() else None
    # A detached temporary worktree exposes symlinks at the remote base, which
    # can differ from the launch repo's current checkout. It is always removed.
    if base:
        violations, kinds = check_scope(headers, state['write_scope'], state['job'], modes, base)
    else:
        with tempfile.TemporaryDirectory(prefix='sol-base-') as temp:
            base = Path(temp) / 'base'
            proc = git(state['cdir'], 'worktree', 'add', '--detach', base, state['base_sha'], check=False)
            if proc.returncode:
                raise ValueError('cannot inspect apply base')
            try:
                violations, kinds = check_scope(headers, state['write_scope'], state['job'], modes, base)
            finally:
                git(state['cdir'], 'worktree', 'remove', '--force', base)
    report = report_path(state['job'])
    report_sections = [s for s in sections if report in (s['a'], s['b'])]
    if report_sections and (report not in new_files or len(report_sections) != 1 or
                            not report_sections[0]['new']):
        violations = sorted(set(violations) | {report})
        kinds[report] = 'report_not_new'
    raw_report = (extract_report(state['patch_path'], state['job'])
                  if report in headers and report not in violations else b'')
    return sorted(headers - {report}), violations, kinds, raw_report


def run(state, existing=False, saved_patch=False, approved_event=None):
    started = time.monotonic()
    state['started_at'] = utc()
    state['evidence_bundle'] = None
    prompt = build_prompt(state['original_prompt'], state['genre'], state['write_scope'], state['job'])
    Path(state['out']).parent.mkdir(parents=True, exist_ok=True)
    if not saved_patch:
        Path(state['out']).write_bytes(b'')
        Path(state['out'] + '.patch').write_bytes(b'')
        Path(state['out'] + '.submit.txt').write_bytes(b'')
        append_manifest(state, started_row(state, prompt))
    metrics, paths, violations = parse_report(b'', state['genre']), [], []
    transport_rc, error_stage = 0, None
    try:
        if saved_patch:
            patch = Path(state['patch_path']).read_bytes()
        else:
            transport = Transport(state, started + state['timeout'])
            state['session_id'] = state['cloud_task_id'] = submit(transport, prompt)
            state['cloud_task_url'] = 'https://chatgpt.com/codex/tasks/' + state['session_id']
            poll(transport)
            error_stage = 'report_capture'
            patch = fetch_patch(transport)
        try:
            paths, violations, kinds, report = inspect_patch(state, patch)
        except ValueError as exc:
            log(state, str(exc))
            state['run_status'], rc, state['scope_action'] = 'ACCEPTANCE_FAILED', 65, 'acceptance_failed'
            error_stage = 'report_capture'
        else:
            Path(state['out']).write_bytes(report)
            metrics = parse_report(report, state['genre'])
            expansion = metrics['scope_expansion']
            if expansion is not None and metrics['scope_expansion_valid']:
                try:
                    requested = normalize_scope(expansion['requested_paths'])
                    metrics['scope_expansion_valid'] = bool(requested) and all(
                        not allowed(p, state['write_scope']) for p in requested)
                except Refusal:
                    metrics['scope_expansion_valid'] = False
            state['run_status'], rc, state['scope_action'] = decide(metrics, violations)
            error_stage = ('report_capture' if metrics['report_parse'] == 'missing' else
                           'report_parse' if metrics['report_parse'] != 'valid' else None)
            if violations:
                state['evidence_bundle'] = state['out'] + '.evidence'
            else:
                try:
                    apply_patch(state, paths, existing)
                except Refusal as exc:
                    log(state, str(exc))
                    state['run_status'], rc, state['scope_action'] = 'APPLY_FAILED', 74, 'apply_failed_preserved'
                    error_stage = 'apply'
    except TimeoutError:
        state['run_status'], rc, state['scope_action'] = 'FAILED', 143, 'failed_preserved'
        transport_rc, error_stage = 143, 'execution'
    except Refusal as exc:
        log(state, str(exc))
        state['run_status'], rc, state['scope_action'] = 'FAILED', exc.rc, 'failed_preserved'
        transport_rc = exc.rc
        error_stage = error_stage or 'execution'
    if approved_event is not None and state['run_status'] in {'OK', 'NEEDS_SCOPE', 'ACCEPTANCE_FAILED'}:
        append_manifest(state, approved_event)
    write_outputs(state, metrics, rc, transport_rc, error_stage, started, paths, violations)
    return rc


def within(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def validate_artifacts(state, existing=False):
    if state['sandbox'] == 'danger-full-access':
        raise Refusal('danger-full-access is refused')
    if not existing and Path(state['apply_worktree']).exists():
        raise Refusal('apply worktree must not exist')
    artifacts = [state['out'] + suffix for suffix in ('', '.status', '.log', '.patch', '.state.json',
                 '.submit.txt', '.evidence')] + [state['manifest'], state['state_file']]
    if state.get('record_dir'):
        artifacts.append(state['record_dir'])
    for path in artifacts:
        if within(path, state['cdir']) or within(path, state['apply_worktree']):
            raise Refusal('runner artifacts must be outside repo and apply worktree: ' + path)
    if within(state['apply_worktree'], state['cdir']):
        raise Refusal('apply worktree must be outside repo')


def load_state(args):
    if '/' in args.run_key or '..' in args.run_key or not args.run_key:
        raise Refusal('invalid run key')
    if args.state_file:
        candidates = [Path(args.state_file)]
    else:
        root = Path(os.environ.get('SOL_CLOUD_STATE_DIR', os.getcwd()))
        candidates = sorted(root.glob('*.state.json'))
    found = []
    for path in candidates:
        try:
            state = json.loads(path.read_text())
            if state.get('run_key') == args.run_key:
                found.append(state)
        except (OSError, ValueError):
            pass
    if len(found) != 1:
        raise Refusal('no unique pending run; use --state-file <out>.state.json', 66)
    return found[0]


def approval(state, args, pending):
    additions = normalize_scope(args.approve_scope_add)
    if not additions or not args.approval_note.strip():
        raise Refusal('approval requires nonempty additions and a nonblank note')
    if pending is not None:
        valid = set(additions).issubset(pending)
    else:
        valid = set(additions).issubset(state['scope_violation_paths'])
    if not valid:
        raise Refusal('approval includes an unrequested path')
    old = state['write_scope']
    new = old + [x for x in additions if x not in old]
    return new, {'schema_version': 3, 'event': 'scope_expansion_approved',
                 'run_key': state['run_key'], 'session_id': state['session_id'],
                 'old_scope': old, 'approved_additions': additions, 'new_scope': new,
                 'approval_note': args.approval_note, 'approved_at': utc()}


def approve(args):
    state = load_state(args)
    if state['run_status'] != 'SCOPE_VIOLATION':
        raise Refusal('run is not a SCOPE_VIOLATION', 65)
    validate_artifacts(state)
    new, row = approval(state, args, None)
    trial = dict(state, write_scope=new)
    _, violations, _, _ = inspect_patch(trial, Path(state['patch_path']).read_bytes())
    if violations:
        raise Refusal('approved additions do not make saved patch scope-clean')
    state['write_scope'] = new
    return run(state, saved_patch=True, approved_event=row)


def resume(args):
    state = load_state(args)
    if state['run_status'] != 'NEEDS_SCOPE' or not state.get('session_id'):
        raise Refusal('run is not resumable from NEEDS_SCOPE', 65)
    target = state['apply_worktree']
    validate_artifacts(state, existing=True)
    new, row = approval(state, args, state['pending_scope_expansion']['requested_paths'])
    if git_value(target, 'status', '--porcelain'):
        raise Refusal('partial worktree is dirty; commit and push first')
    branch = git_value(target, 'branch', '--show-current')
    head = git_value(target, 'rev-parse', 'HEAD')
    if not branch or remote_sha(target, branch) != head:
        raise Refusal('partial branch is unpushed; commit and push first')
    state['cdir'], state['cloud_branch'], state['base_sha'] = target, branch, head
    state['write_scope'] = new
    state['attempt'] += 1
    encoded = compact(new)
    state['original_prompt'] = re.sub(r'(?m)^WRITE_SCOPE:.*$', lambda _: 'WRITE_SCOPE: ' + encoded,
                                     state['original_prompt'], count=1)
    state['original_prompt'] += ('\n\nSCOPE EXPANSION APPROVED BY LEAD: ' + args.approval_note +
                                 '\nAMENDED WRITE_SCOPE: ' + encoded)
    append_manifest(state, row)
    return run(state, existing=True)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('out')
    result.add_argument('--env', required=True)
    result.add_argument('--branch', required=True)
    result.add_argument('-C', dest='repo', required=True)
    result.add_argument('-m', '--model')
    result.add_argument('--effort')
    result.add_argument('-s', dest='sandbox', default='read-only')
    result.add_argument('--genre', choices=sorted(VERDICTS), required=True)
    result.add_argument('--write-scope', required=True)
    result.add_argument('--manifest')
    result.add_argument('--timeout', type=float, default=9000)
    result.add_argument('--poll', type=float, default=60)
    result.add_argument('--retries', type=int, default=2)
    result.add_argument('--apply-worktree')
    result.add_argument('--cx-bin', default='codex')
    result.add_argument('--record-dir')
    result.add_argument('--role')
    result.add_argument('--parent')
    result.add_argument('prompt')
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv and argv[0] in {'approve', 'resume'}:
            p = argparse.ArgumentParser()
            p.add_argument('run_key')
            p.add_argument('--approve-scope-add', required=True)
            p.add_argument('--approval-note', required=True)
            p.add_argument('--state-file')
            args = p.parse_args(argv[1:])
            return approve(args) if argv[0] == 'approve' else resume(args)
        args = parser().parse_args(argv)
        if not (args.timeout > 0 and args.poll >= 0 and args.retries >= 0):
            raise Refusal('timeout must be positive; poll and retries nonnegative')
        scope = normalize_scope(args.write_scope)
        prompt_scope = prompt_value(args.prompt, 'WRITE_SCOPE')
        if prompt_scope is None:
            raise Refusal('--write-scope requires a WRITE_SCOPE field in the prompt')
        normalize_scope(prompt_scope)
        job = Path(args.out).name.removesuffix('.md')
        normalize_scope([job])
        repo = git_value(args.repo, 'rev-parse', '--show-toplevel')
        if not repo:
            raise Refusal('runner requires a Git worktree')
        out = str(Path(args.out).resolve())
        state = {'run_key': dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                 f'-{os.getpid()}-{Path(args.out).name}', 'job': job, 'out': out,
                 'cdir': repo, 'genre': args.genre, 'write_scope': scope,
                 'original_prompt': args.prompt, 'sandbox': args.sandbox,
                 'model': args.model, 'effort': args.effort, 'timeout': args.timeout,
                 'poll': args.poll, 'retries': args.retries, 'attempt': 1,
                 'manifest': str(Path(args.manifest or out + '.manifest.jsonl').resolve()),
                 'state_file': out + '.state.json', 'patch_path': out + '.patch',
                 'cloud_env': args.env, 'cloud_branch': args.branch, 'session_id': None,
                 'cloud_task_id': None, 'cloud_task_url': None, 'apply_branch': None,
                 'apply_worktree': str(Path(args.apply_worktree or
                   Path(repo).parent / f'{Path(repo).name}-wt-cloud-{job}').resolve()),
                 'cx_bin': str(Path(args.cx_bin).resolve()) if '/' in args.cx_bin else args.cx_bin,
                 'record_dir': str(Path(args.record_dir).resolve()) if args.record_dir else None,
                 'role': args.role, 'parent': args.parent}
        validate_artifacts(state)
        state['base_sha'] = remote_sha(repo, args.branch)
        return run(state)
    except Refusal as exc:
        print('sol_cloud_run: ' + str(exc), file=sys.stderr)
        return exc.rc
    except SystemExit as exc:
        return 64 if exc.code else 0


if __name__ == '__main__':
    sys.exit(main())
