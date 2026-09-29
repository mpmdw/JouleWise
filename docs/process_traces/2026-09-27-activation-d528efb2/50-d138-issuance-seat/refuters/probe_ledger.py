import sys, ast, json
from pathlib import Path
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2")
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"tests"))
import joulewise.calibration_bracketing as b
from scripts import validate_powermetrics_fiducial as pf
from scripts import write_derivation_night_inputs as night
import test_claim_hold_routes as T
held = b.load_calibration_acceptance_bound(b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH, allow_claim_held=True)
ident = dict(held["identity_epoch"])
print("identity 25G83:", ident)
# E: ordinary capture preflight at 25G83 against every registered file + genesis-fixture path
paths = {k: v["path"] for k, v in b.ISSUED_ACCEPTANCE_REGISTRY.items()}
for k, p in paths.items():
    try:
        r = pf._derive_preflight_systematic_screen_s(ident, acceptance_path=p)
        print("E", k, "-> RETURNED", r)
    except pf._AcceptancePreflightError as e:
        print("E", k, "->", e.reason, e.context.get("stale_fields"))
# F: bracket evaluation at 25G83, 2 fresh endpoints, every registered artifact explicit + default
for k, p in paths.items():
    art = b.load_calibration_acceptance_bound(p, allow_claim_held=True)
    if art is None:
        print("F", k, "unloadable"); continue
    try:
        res, reasons = T.synthetic_bracket(art, ident, 2, explicit=True)
        a = res["acceptance"] or {}
        print("F explicit", k, "->", res["status"], reasons, (a.get("freshness") or {}).get("reason"), (a.get("freshness") or {}).get("stale_fields"))
    except Exception as e:
        print("F explicit", k, "-> EXC", type(e).__name__, str(e)[:120])
res, reasons = T.synthetic_bracket(b.load_calibration_acceptance_bound(), ident, 2)
print("F default ->", res["status"], reasons, res["acceptance"]["artifact"]["acceptance_id"], res["acceptance"]["freshness"].get("stale_fields"))
# G: derivation-kind rows never become candidates
from joulewise.calibration_ledger import LedgerObservation, CalibrationLedgerSnapshot, CalibrationBracketSession
obs = LedgerObservation(sequence=1, receipt_digest="d"*64, attempt_id="a", content_id="c"*64, artifact_sha256={}, identity_epoch=ident,
    t1_bindings={"anchor_method_version": b.ACTIVE_CAPTURE_ANCHOR_METHOD}, capture_wall_time_s="1", exact_bound_lexeme_s="0.02",
    disposition="valid", custody_locator="/tmp/x", bracket_session_id="deriv-1")
sess = CalibrationBracketSession(session_id="deriv-1", window_id="w", plan_id="p", plan_sha256="a"*64, evidence_root_id="r", runs_root="/tmp",
    capability_receipt_digest="b"*64, capability_sequence=1, slot_attempt_ids={}, state="finalized", finalized_slots={}, session_kind="derivation")
snap = CalibrationLedgerSnapshot(ledger_schema="x", ledger_path=Path("/tmp/l"), head_sequence=1, head_digest="c"*64, receipts=(), observations=(obs,),
    refusal_reasons=(), bracket_sessions=(sess,), baseline_sequence=0, baseline_digest="0"*64)
print("G derivation-kind row is derivation:", b._is_derivation_kind_observation(obs, snap))
obs2 = LedgerObservation(**{**obs.__dict__, "bracket_session_id": "missing-session"}) if hasattr(obs, "__dict__") else None
if obs2 is not None:
    print("G row naming unknown session kind:", b._observation_session_kind(obs2, snap))
# H: census weakness demo (same AST rule as HR-6) on synthetic sources
rule = lambda src: [1 for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and any(k.arg=="allow_claim_held" and isinstance(k.value, ast.Constant) and k.value.value is True for k in n.keywords)]
for src in ["f(p, allow_claim_held=True)", "flag=True\nf(p, allow_claim_held=flag)", "f(p, **{'allow_claim_held': True})", "f(p, allow_claim_held=1)", "import os\nf(p, allow_claim_held=bool(os.environ.get('X')))"]:
    print("H census catches", repr(src), "->", bool(rule(src)))
# I: hold table mutability
print("I hold table type:", type(b.CLAIM_HELD_ACCEPTANCE_IDS).__name__)
