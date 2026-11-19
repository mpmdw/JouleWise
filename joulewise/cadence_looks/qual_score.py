"""Blind qualification intake and source-bound publication for lm-qual-01."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import statistics
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence_looks import interim_release as release
from joulewise.cadence_looks import manifest, manifest_dispatch, qualification_manifest, schema_check


LOOK = "lm-qual-01"
INTERIM = "lm-interim-01"
DOC = "docs/process/cadence/looks/"
LEDGER = DOC + "LOOKS.json"
MAN = ("docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
       "looks/lm-qual-01.manifest.json")
REGISTRATION = "59557d6e8e00fcba6a2bdb2bfa4189bd6d7aee98"
REGISTRATION_SHA = "d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab"
STAGE = DOC + LOOK + ".stage1.json"
STAGE_SCHEMA = DOC + LOOK + ".stage1.schema.json"
OUTPUT_SCHEMA = DOC + LOOK + ".output.schema.json"
CONFIG = "configs/align/v4/r1_runtime.json"
KITS = DOC + "qualification-kit-commitments.json"
INTERIM_MAN = DOC + INTERIM + ".json"
INTERIM_SCHEMA = DOC + INTERIM + ".output.schema.json"
SLOTS = re.compile(rb'("path": "([^"]+)",\n\s*"sha256": )"PENDING:CODE"')
MAIN = "refs/remotes/origin/main"
RULES = ("ran_to_cap", "g0_released", "sidecar_coverage", "km003c_clean",
         "not_a_contaminated_attempt", "block_power_mode")
ROSTER_FIELDS = ("leg_key", "leg_type", "pair", "P", "N", "order")
SHORT_CAPS = {3724: "1.10", 3151: "1.30"}
PAIR_DESIGN = (((3151, False), (3724, True)),
               ((3151, True), (3724, True)),
               ((3724, False), (3151, True)))


class Refusal(ValueError):
    """A prerequisite failed while scoring inputs were still closed."""


def require(condition, notice):
    if not condition:
        raise Refusal(notice)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def public_bytes(record, schema, bindings):
    """The validator and writer both require this closed, source-bound encoding."""
    require(not schema_check.errors(record, schema), "invalid public schema")
    require(type(record["included_legs"]) is int, "included legs requires an integer token")
    require(bindings.keys() == record.keys() - {"qualified_qualification"}, "incomplete public bindings")
    require(all(type(record[key]) is type(value) and record[key] == value for key, value in bindings.items()),
            "public report differs from its sources")
    return release.dump(record)


def validate_public(candidate, schema, bindings):
    record = qualification_manifest._decode(candidate)
    require(public_bytes(record, schema, bindings) == candidate, "noncanonical public report")
    return record


def publish_public(destination, reservation, record, schema, bindings):
    """Expose complete bytes once, using the reservation for the staging name."""
    payload = public_bytes(record, schema, bindings)
    pending = reservation / ".publication"
    release.write_private(pending, payload)
    try:
        os.link(pending, destination)
    finally:
        pending.unlink()


def decision(legs, scores, dates):
    """RL-181 §1.1 and RL-188 §3. The private prints retain one- and two-day estimates."""
    from joulewise.cadence_looks.fit_interim import SD_FLOOR_J, t_quantile

    series = []
    for leg in legs:
        if leg["leg_type"] != "A" or leg["N"] != 4096 or not all(leg["rules"].values()):
            continue
        key = leg["leg_key"]
        rail = scores[key]["gpu_rail"]
        series.append((key, dates[leg["span_id"]], rail["residual"], rail["prefixes"]["3724"]["residual"]))
    days = {row[1] for row in series}
    report = {"estimate": None, "ci90": None, "n_legs": len(series), "n_days": len(days),
              "sd_long": None, "sd_short": None, "differences": {}}
    if len(series) < 3:
        return "not_evaluable", report
    sd_long = statistics.stdev(row[2] for row in series)
    sd_short = statistics.stdev(row[3] for row in series)
    report.update(sd_long=sd_long, sd_short=sd_short)
    if min(sd_long, sd_short) <= SD_FLOOR_J:
        return "not_evaluable", report
    by_day = defaultdict(list)
    for key, day, long, short in series:
        difference = long / sd_long - short / sd_short
        report["differences"][key] = difference
        by_day[day].append(difference)
    means = [statistics.mean(values) for values in by_day.values()]
    mean = statistics.mean(means)
    report["estimate"] = mean
    if len(days) == 1:
        return "not_evaluable", report
    half_width = t_quantile(0.95, len(days) - 1) * statistics.stdev(means) / math.sqrt(len(days))
    lower, upper = mean - half_width, mean + half_width
    report["ci90"] = [lower, upper]
    if len(days) < 3:
        return "not_evaluable", report
    return ("yes" if lower >= -0.10 and upper <= 0.10 else "no"), report


def read_regular(path):
    require(path.is_absolute() and path.resolve() == path and "RESTRICTED" not in path.parts,
            "noncanonical or restricted metadata path")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "input must be a regular file")
        return stream.read()


def fixture_host_token(raw):
    """Convert the generated ioreg projection to the same token as the hardware probe."""
    probe = qualification_manifest._decode(raw)
    require(type(probe) is dict and probe.keys() == {"IOPlatformUUID"}, "invalid generated host probe")
    values = probe["IOPlatformUUID"]
    require(type(values) is list and len(values) == 1, "generated host probe needs exactly one UUID")
    uuid = values[0]
    require(type(uuid) is str and re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", uuid),
            "invalid IOPlatformUUID")
    return "hw1:" + digest(("joulewise.execution_host.v1:" + uuid.upper()).encode("ascii"))


def git(repo, *args):
    status, value, _ = manifest._git(repo, *args)
    require(status == 0, "required Git evidence unavailable")
    return value


def blob(repo, commit, name):
    return git(repo, "show", f"{commit}:{name}")


def row_at(repo, commit, look):
    ledger = qualification_manifest._decode(blob(repo, commit, LEDGER))
    require(ledger["schema"] == "joulewise.cadence_look_ledger.v1", "unexpected ledger schema")
    rows = [row for row in ledger["looks"] if row["look_id"] == look]
    require(len(rows) == 1, "expected one ledger row for the look")
    return rows[0]


def named_commit(repo, ref):
    value = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip().decode("ascii")
    require(re.fullmatch("[0-9a-f]{40}", value), "expected an exact Git commit")
    return value


def manifest_pins(document):
    inclusion = [rule["code"] for rule in document["inclusion"]["rules"] if "code" in rule]
    pins = document["pins"]
    return (*inclusion, pins["scorer"], *pins["code"], *pins["schemas"].values())


def filled_manifest(registration, pins):
    """Fill only the registered byte slots, including each inclusion-code occurrence."""
    paths = {pin["path"]: pin["sha256"] for pin in pins}
    require(len(pins) == 32 and len(paths) == 30 and all(re.fullmatch("[0-9a-f]{64}", x) for x in paths.values()),
            "unexpected final pin inventory")
    require(all(pin["sha256"] == paths[pin["path"]] for pin in pins), "inconsistent repeated pin")
    candidate, count = SLOTS.subn(lambda m: m[1] + b'"' + paths[m[2].decode()].encode() + b'"', registration)
    require(count == len(pins) and b"PENDING:CODE" not in candidate, "unfilled or unknown pin slot")
    return candidate


def validate_final_command(registration, final):
    """Invoke the sanctioned validator over the exact authenticated public bytes."""
    with ExitStack() as streams:
        readers, writers = [], []
        for payload in (registration, final):
            rd, wr = os.pipe()
            readers.append(streams.enter_context(os.fdopen(rd, "rb")))
            writers.append((streams.enter_context(os.fdopen(wr, "wb")), payload))
        reg, candidate = (reader.fileno() for reader in readers)
        command = [sys.executable, "-B", "-E", "-s", "-m", "joulewise.cadence_looks.manifest_dispatch",
                   "validate", f"/dev/fd/{candidate}", "--final", "--registration", f"/dev/fd/{reg}"]
        with subprocess.Popen(command, cwd=ROOT, pass_fds=(reg, candidate),
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as validator:
            for reader in readers:
                reader.close()

            def deliver(stream, payload):
                with stream:
                    stream.write(payload)

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(deliver, writer, payload) for writer, payload in writers]
                for delivery in futures:
                    try:
                        delivery.result()
                    except BrokenPipeError:
                        # On refusal the dispatcher can exit before reading the registration pipe.
                        pass
            require(validator.wait() == 0, "sanctioned final validation refused")


def authenticated_registration(repo, main, commit, expected):
    require(re.fullmatch("[0-9a-f]{40}", commit), "invalid registration commit")
    git(repo, "merge-base", "--is-ancestor", REGISTRATION, commit)
    git(repo, "merge-base", "--is-ancestor", commit, main)
    raw = blob(repo, commit, MAN)
    historical = row_at(repo, commit, LOOK)
    require(historical == {"look_id": LOOK, "status": "registered", "manifest_path": MAN,
                           "sha256": digest(raw)} and digest(raw) == expected,
            "registration differs from the historical mainline row")
    anchor = blob(repo, REGISTRATION, MAN)
    require(digest(anchor) == REGISTRATION_SHA, "published registration differs from its authenticated bytes")
    midpoint = b"c = P + (first_stamp + last_stamp) / 2."
    require(anchor.count(midpoint) == 1, "RL-188 correction no longer identifies one sentence")
    corrected = anchor.replace(midpoint, b"c = P + (first_stamp + 1 + last_stamp) / 2.", 1)
    require(raw == (anchor if commit == REGISTRATION else corrected), "registration science differs")
    return raw


def mainline_final(repo):
    require(repo == ROOT, "campaign invocation requires its executing checkout")
    _, main = manifest.shared_ref(repo, "origin/main")
    row = row_at(repo, main, LOOK)
    require(row["status"] in ("committed", "stage1_committed") and row["manifest_path"] == MAN,
            "final manifest must be committed on main")
    registration = authenticated_registration(repo, main, row["registration_commit"], row["registration_sha256"])
    final = blob(repo, main, MAN)
    require(digest(final) == row["sha256"] and read_regular(repo / MAN) == final,
            "final manifest differs from main")
    validate_final_command(registration, final)
    doc = qualification_manifest._decode(final)
    pins = manifest_pins(doc)
    require(filled_manifest(registration, pins) == final, "final pin inventory differs")
    for rel, sha in {pin["path"]: pin["sha256"] for pin in pins}.items():
        path_raw = blob(repo, main, rel)
        require(digest(path_raw) == sha and read_regular(repo / rel) == path_raw, "executing source changed")
    return doc


class FixtureSources:
    """A file projection of synthetic Git evidence under the explicit --inputs interface."""

    def __init__(self, repo, inputs):
        require(repo != ROOT and repo.parent == inputs.parent and not git(repo, "remote").strip()
                and git(repo, "symbolic-ref", "HEAD").strip() == b"refs/heads/fixture",
                "file projections require a disposable fixture repository")
        require(Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel").strip())).resolve() == repo,
                "fixture repository must be a worktree root")
        require(git(repo, "rev-parse", "--is-shallow-repository").strip() == b"false", "incomplete fixture history")
        self.repo = repo
        self.inputs = inputs
        self.main = named_commit(repo, MAIN)
        self.row = row_at(repo, self.main, LOOK)
        self.registration = self.row["registration_commit"]
        require(re.fullmatch("[0-9a-f]{40}", self.registration), "invalid registration commit")
        git(repo, "merge-base", "--is-ancestor", self.registration, self.main)

    def bound(self, rel, *, git_name=None, commit=None):
        raw = blob(self.repo, commit or self.main, git_name or rel)
        require(read_regular(self.inputs / rel) == raw, "fixture projection differs from its committed source")
        return raw

    def final(self):
        require(self.row["status"] in ("committed", "stage1_committed") and self.row["manifest_path"] == MAN,
                "final manifest must be committed")
        self.bound(LEDGER)
        registered = self.bound("registration.json", git_name=MAN, commit=self.registration)
        historical = row_at(self.repo, self.registration, LOOK)
        require(historical == {"look_id": LOOK, "status": "registered", "manifest_path": MAN,
                               "sha256": digest(registered)}, "registration is absent from its named history")
        require(digest(registered) == self.row["registration_sha256"], "registration hash disagrees with the ledger")
        anchor = blob(ROOT, REGISTRATION, MAN)
        require(digest(anchor) == REGISTRATION_SHA, "published registration differs from its authenticated bytes")
        registration_doc, _ = qualification_manifest._parse(registered)
        fixture_blocks = registration_doc["reads"]["blocks"]
        authorized_blocks = json.loads(anchor)["reads"]["blocks"]
        for fixture, authorized in zip(fixture_blocks, authorized_blocks, strict=True):
            before = f'"kit_sha256": "{authorized["kit_sha256"]}"'.encode()
            after = f'"kit_sha256": "{fixture["kit_sha256"]}"'.encode()
            anchor = anchor.replace(before, after, 1)
        require(registered == anchor, "fixture changed registration outside the three generated kit bindings")
        final = self.bound(MAN)
        require(digest(final) == self.row["sha256"], "final manifest hash disagrees with the ledger")
        doc, _ = qualification_manifest._parse(final)
        pins = manifest_pins(doc)
        require(filled_manifest(registered, pins) == final, "final differs outside registered pin slots")
        self.verify_pins(pins)
        return doc

    def verify_pins(self, pins):
        for path, sha in {pin["path"]: pin["sha256"] for pin in pins}.items():
            committed = self.bound(path)
            require(digest(committed) == sha and read_regular(ROOT / path) == committed,
                    "executing source differs from the committed pin")

    def blind(self, doc):
        """Authenticate all source bytes, then derive the public roster from those bytes."""
        commitments = json.loads(self.bound(KITS, commit=self.registration))[LOOK]["kit_sha256_by_block"]
        interim = self.interim()
        config_pin, = (item["sha256"] for item in interim["fit"]["dependencies"] if item["path"] == CONFIG)
        config_paths = ("dev/" + CONFIG, CONFIG)
        raw = {name: self.bound(name, commit=self.registration) for name in config_paths}
        config_dev, config_qual = (digest(raw[name]) for name in config_paths)
        require(config_dev == config_pin, "development configuration differs from its pin")
        require(all("d_n_chunk_status" in json.loads(raw[name]) for name in config_paths),
                "missing phase configuration label")
        dates, roster, pairs = {}, [], []
        registration_time = int(git(self.repo, "show", "-s", "--format=%ct", self.registration))
        for index, block in enumerate(doc["reads"]["blocks"]):
            block_id, kit_sha = block["block_id"], block["kit_sha256"]
            kit_name = "kits/" + block_id + ".json"
            raw[kit_name] = self.bound(kit_name, commit=self.registration)
            kit = json.loads(raw[kit_name])
            require(digest(raw[kit_name]) == kit_sha == commitments[block_id]
                    and kit["block_id"] == block_id and kit["config_sha256"] == config_qual
                    and set(kit["spans"]) == set(block["spans"]), "issued kit differs from independent commitments")
            for pos, span in enumerate(block["spans"]):
                evidence = {}
                for name in ("receipt", "hand", "desk", "q1", "roster"):
                    rel = f"spans/{span}/{name}.json"
                    raw[rel] = self.bound(rel, git_name="evidence/" + rel)
                    evidence[name] = json.loads(raw[rel])
                identity = {"span_id": span, "block_id": block_id, "kit_sha256": kit_sha}
                receipt = evidence["receipt"]
                t0 = receipt["t0_epoch_s"]
                require(type(t0) is int and t0 > registration_time and receipt == {
                    **identity, "t0_epoch_s": t0, "registration_at_issue": self.registration},
                    "span receipt lacks strict registration precedence or identity")
                require(all(evidence[kind] == identity for kind in ("hand", "desk", "q1")),
                        "span hand, desk or Q1 evidence differs from the registered span")
                require(evidence["roster"]["span_id"] == span, "blind roster is for a different span")
                dates[span] = datetime.fromtimestamp(t0, ZoneInfo("America/Los_Angeles")).date().isoformat()
                rows, pair = span_roster(kit["spans"][span], evidence["roster"]["legs"], span,
                                         PAIR_DESIGN[index][pos])
                roster.extend(rows)
                pairs.append(pair)
        return roster, dates, pairs, {"development_sha256": config_dev, "qualification_sha256": config_qual}, raw

    def interim(self):
        row = row_at(self.repo, self.main, INTERIM)
        raw = self.bound(INTERIM_MAN)
        doc = qualification_manifest._decode(raw)
        require(row["manifest_path"] == INTERIM_MAN and row["sha256"] == digest(raw)
                and doc["look_id"] == INTERIM and doc["status"] == "committed", "interim manifest is unauthenticated")
        return doc

    def public_freeze_sha(self):
        """Bind the generated public report without opening the coefficient file."""
        row = row_at(self.repo, self.main, INTERIM)
        interim = self.interim()
        public_root = row["public_root"]
        require(row["status"] in ("run", "frozen") and manifest._relative_directory(public_root),
                "interim public result is unavailable")
        schema_pin = interim["outputs"]["schema"]
        require(schema_pin["path"] == INTERIM_SCHEMA, "unexpected interim public schema")
        schema_raw = self.bound(INTERIM_SCHEMA)
        require(digest(schema_raw) == schema_pin["sha256"], "interim public schema changed")
        raw = self.bound(f"{public_root}/{INTERIM}/PUBLIC.json")
        require(digest(raw) == row["output_sha256"], "interim public result differs from the ledger")
        report = release.read_public(raw, json.loads(schema_raw), look_id=INTERIM)
        fields = {"manifest_sha256": "sha256", "stage1_sha256": "stage1_sha256",
                  "coefficients_sha256": "coefficients_sha256"}
        require(all(report[key] == row[value] for key, value in fields.items()),
                "interim public result differs from its commitments")
        commit = report["commit"]
        git(self.repo, "merge-base", "--is-ancestor", commit, self.main)
        execution = row_at(self.repo, commit, INTERIM)
        bound_keys = ("sha256", "stage1_sha256", "public_root", "custody_root", "execution_host")
        require(execution["status"] == "stage1_committed"
                and all(execution[key] == row[key] for key in bound_keys), "interim execution row changed")
        require(report["twin_agrees"] == "yes", "named freeze-2 intake awaits the shared reader")
        return report["coefficients_sha256"]

    def execution_destinations(self, execution):
        require(not manifest.look_spent(self.repo, LOOK, execution), "look ID is spent in ledger history")
        custody = Path(self.row["custody_root"])
        require(self.repo.parent in custody.parents and manifest._relative_directory(self.row["public_root"]),
                "generated destinations must stay in the fixture world")
        local_host = fixture_host_token(read_regular(self.inputs / "local-host.json"))
        require(local_host == self.row["execution_host"], "generated host differs from its committed token")
        return release.destinations(self.repo, self.row)


def edges(lo, hi):
    return {"edge_lo": lo, "edge_hi": hi, "gaps": hi - lo}


def terminal_edges(turn):
    """The last full block's closing stamp and the last produced token, per RL-188 A1."""
    if turn["decode_tokens"] % 256 == 0:
        return None
    lo = turn["segments"][-1]["edge_hi"]
    hi = turn["decode_tokens"] - 1
    return {**edges(lo, hi), "context_tokens": turn["prefill_tokens"] + (lo + 1 + hi) / 2}


def span_roster(kit, rows, span, design):
    from joulewise.cadence_looks import fit_interim

    require(len(kit) == len(rows) == 6, "wrong span roster length")
    out = []
    for index, (expected, raw) in enumerate(zip(kit, rows, strict=True)):
        leg = {key: raw[key] for key in ROSTER_FIELDS}
        require(leg == expected and raw["span_id"] == span and raw["order"] == index
                and re.fullmatch(re.escape(span) + "/" + re.escape(leg["leg_type"]) + r"[0-9]{3}", leg["leg_key"]),
                "blind leg disagrees with the issued kit")
        rules = raw["rules"]
        require(rules.keys() == set(RULES) and all(type(value) is bool for value in rules.values()),
                "missing blind inclusion rule")
        turn = raw["turn"]
        require((turn["prefill_tokens"], turn["decode_tokens"]) == (leg["P"], leg["N"]), "turn cap or cell differs")
        fit_interim._validate_turn(turn, "blind turn")
        out.append({**leg, "span_id": span, "maintenance_job": raw["maintenance_job"], "rules": rules,
                    "segments": [edges(seg["edge_lo"], seg["edge_hi"]) for seg in turn["segments"][1:]],
                    "prefixes": [edges(seg["edge_lo"], seg["edge_hi"]) for seg in turn["prefix_tails"]],
                    "terminal": terminal_edges(turn)})
    require(len({leg["leg_key"] for leg in out}) == 6, "duplicate leg identity")
    a_legs = [leg for leg in out if leg["leg_type"] == "A"]
    require(len(a_legs) == 4 and all(leg["pair"] is None and leg["N"] == 4096 for leg in a_legs),
            "unexpected A roster")
    cap, full_first = design
    l_legs = [leg for leg in out if leg["leg_type"] == "L"]
    require(len(l_legs) == 2 and [leg["N"] for leg in l_legs] == ([4096, cap] if full_first else [cap, 4096]),
            "unexpected L order or cap")
    full, short = l_legs if full_first else l_legs[::-1]
    require(full["pair"] == short["pair"] and isinstance(full["pair"], str) and full["pair"]
            and full["P"] == short["P"], "L pair identity or cell disagrees")
    return out, {"span_id": span, "pair_id": full["pair"], "ratio": SHORT_CAPS[cap], "full": full["leg_key"],
                 "short": short["leg_key"], "full_first": full_first,
                 "included": [leg["leg_key"] for leg in l_legs if all(leg["rules"].values())]}


def blind_summary(roster, pairs):
    included = [leg for leg in roster if all(leg["rules"].values())]
    by_ratio = {}
    for ratio in SHORT_CAPS.values():
        selected = [pair for pair in pairs if pair["ratio"] == ratio]
        complete = [p["pair_id"] for p in selected if len(p["included"]) == 2]
        incomplete = [p["pair_id"] for p in selected if len(p["included"]) != 2]
        by_ratio[ratio] = {"complete": len(complete), "incomplete": len(incomplete),
                           "complete_ids": complete, "incomplete_ids": incomplete}
    counts = {"included_legs": len(included), "by_cell": dict(Counter(str(x["P"]) for x in included)),
              "by_job": dict(Counter(x["maintenance_job"] or "unmarked" for x in included)), "by_ratio": by_ratio}
    joint = {f"{pos}/{order}": [] for pos in (1, 2) for order in ("full_first", "short_first")}
    for pair in pairs:
        cell = "full_first" if pair["full_first"] else "short_first"
        joint[f"{pair['span_id'][-1]}/{cell}"].append(pair["pair_id"])
    singletons = [p["included"][0] for p in pairs if len(p["included"]) == 1]
    return counts, singletons, joint


def stage1(source, doc):
    import numpy

    roster, dates, pairs, config, files = source.blind(doc)
    counts, singletons, joint = blind_summary(roster, pairs)
    record = {"schema": "joulewise.cadence_looks.qual_stage1.v1", "look_id": LOOK,
              "registration_commit": source.registration, "registration_sha256": source.row["registration_sha256"],
              "manifest_sha256": source.row["sha256"], "input_sha256": digest(release.dump({k: digest(v) for k, v in files.items()})),
              "numpy_version": numpy.__version__, "configs": config, "dates": dates, "roster": roster, "pairs": pairs,
              "counts": counts, "singletons": singletons, "joint": joint}
    schema = json.loads(source.bound(STAGE_SCHEMA))
    require(not schema_check.errors(record, schema), "stage 1 failed its closed blind schema")
    return release.dump(record)


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in ("stage1", "stage2", "validate-public"):
        command = commands.add_parser(operation)
        command.add_argument("--repo", required=True, type=Path)
        command.add_argument("--inputs", type=Path, help="explicit generated Git projections")
        command.add_argument("--stage1", required=True, type=Path)
        if operation == "validate-public":
            command.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.inputs is None:
            mainline_final(args.repo.absolute())
            raise Refusal("campaign closure intake is pending admission")
        source = FixtureSources(args.repo.absolute(), args.inputs.absolute())
        doc = source.final()
        blind = stage1(source, doc)
        stage_path = args.stage1.absolute()
        require(stage_path.parent == source.repo.parent, "fixture stage-1 file must stay in the generated world")
        if args.operation == "stage1":
            release.write_private(stage_path, blind)
            return 0
        require(source.row["status"] == "stage1_committed" and source.row["stage1_path"] == STAGE,
                "stage 1 has no authoritative commitment")
        require(blind == blob(source.repo, source.main, STAGE) == read_regular(stage_path)
                and digest(blind) == source.row["stage1_sha256"], "stage-1 bytes or sources changed")
        execution = named_commit(source.repo, "HEAD")
        git(source.repo, "merge-base", "--is-ancestor", execution, source.main)
        require(row_at(source.repo, execution, LOOK) == source.row and blob(source.repo, execution, STAGE) == blind,
                "execution row or stage-1 bytes differ from main")
        for rel, sha in {pin["path"]: pin["sha256"] for pin in manifest_pins(doc)}.items():
            require(digest(blob(source.repo, execution, rel)) == sha, "execution revision pin changed")
        if args.operation == "validate-public":
            require(args.candidate.absolute().parent == source.repo.parent,
                    "fixture candidate must stay in the generated world")
            stage = json.loads(blind)
            schema = json.loads(source.bound(OUTPUT_SCHEMA))
            bindings = {
                "look_id": LOOK, "commit": execution, "manifest_sha256": source.row["sha256"],
                "stage1_sha256": digest(blind), "coefficients_sha256": source.public_freeze_sha(),
                "development_config_sha256": stage["configs"]["development_sha256"],
                "qualification_config_sha256": stage["configs"]["qualification_sha256"],
                "included_legs": stage["counts"]["included_legs"], "type_m_residual": "not_run",
                "stage2_error": "no",
            }
            validate_public(read_regular(args.candidate.absolute()), schema, bindings)
            return 0
        source.public_freeze_sha()
        source.execution_destinations(execution)
        raise Refusal("shared freeze-2 reader and native L predictor pending admission")
    except Exception:
        manifest_dispatch.exit_with_failure(2, lambda: "REFUSE qualification before read\n")


if __name__ == "__main__":
    sys.exit(cli())
