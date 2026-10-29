#!/usr/bin/env python3
"""Produce the restricted record and both deterministic disclosure views."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from joulewise import analysis_engine as engine
from joulewise import paper_reported_energy as energy
from joulewise import paper_reported_energy_issuer as issuer
from joulewise.analysis_engine import inputs
from joulewise.authentication_io import read_authentication_input
from joulewise.b5_analysis.archive import open_attempt_record, open_archive
from joulewise.b5_analysis.bracket import evaluate_window_bracket
from joulewise.b5_analysis.context import build_context
from joulewise.b5_analysis.disclosures import (
    canonical_json_bytes, produce_disclosures, render_disclosures, engine_contrast_observations,
)
from joulewise.b5_analysis.kept_units import _strict_json, load_kept_units
from joulewise.b5_analysis.windows import (
    AnalysisRefusal, SealPins, load_window_index, select_analysed_attempts, sealed_pack_table,
)
from joulewise.whole_window import canonical_sha256, NEG8_HARVEST_ALLOWANCE_RECORD

ROOT=Path(__file__).resolve().parents[1]
ROLES=("projection_alpha","projection_beta","extraction_alpha","extraction_beta","floor_artifact",
       "closeout","claim_verdicts","sensitivity","step_results","finalized_manifest")


class _Parser(argparse.ArgumentParser):
    def error(self,message):
        raise AnalysisRefusal("disclosure_input_invalid")


def _contained(custody,relative):
    if not isinstance(relative,str) or not relative or "\x00" in relative or "\\" in relative:
        raise AnalysisRefusal("step_output_path_invalid")
    path=PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or str(path)!=relative:
        raise AnalysisRefusal("step_output_path_invalid")
    target=custody/relative
    if not target.resolve().is_relative_to(custody.resolve()):
        raise AnalysisRefusal("step_output_path_invalid")
    return target


def load_step_outputs(custody,step_outputs):
    """Authenticate every declared role before any output is created."""
    document=_strict_json(read_authentication_input(step_outputs,grammar="json",label="disclosure step outputs"),
                          "disclosure_input_invalid")
    for role in ROLES:
        if role not in document:
            raise AnalysisRefusal("disclosure_input_missing:"+role)
    values,paths={},{}
    for role,reference in sorted(document.items()):
        if (not isinstance(reference,dict) or set(reference)!={"path","sha256"}
                or not isinstance(reference["sha256"],str)
                or not re.fullmatch(r"[0-9a-f]{64}",reference["sha256"])):
            raise AnalysisRefusal("disclosure_input_invalid")
        path=_contained(custody,reference["path"])
        raw=read_authentication_input(path,grammar="json",label="disclosure step output")
        if hashlib.sha256(raw).hexdigest()!=reference["sha256"]:
            raise AnalysisRefusal("step_output_digest_mismatch")
        values[role]=_strict_json(raw,"disclosure_input_invalid"); paths[role]=path
    return values,paths


def _planned_floor(spec):
    planned={}
    for cell in spec["cells"]:
        strata=planned.setdefault(cell["condition_family_id"],{})
        if cell["kind"]=="absolute":
            strata["repeat"]={r["bundle_id"]:(r["bundle_id"],) for r in cell["members"]}
        else:
            strata["quad"]={r["block_id"]:tuple(r["members"][p] for p in ("A1","B1","B2","A2")) for r in cell["blocks"]}
    return planned


def _floor_setup(window,archive,pins):
    """Same bindings and inputs as issue_pack, retained for labelled views."""
    prefix=f"sources/repo/configs/campaigns/{window.pack_id}/"
    local=ROOT/"configs/campaigns"/window.pack_id
    raw=read_authentication_input(local/"extraction_spec.json",grammar="json",label="reported-energy extraction spec")
    if raw!=archive.source_bytes(prefix+"extraction_spec.json"):
        raise AnalysisRefusal("extraction_spec_differs_from_archive")
    spec=_strict_json(raw,"extraction_spec_invalid"); energy._validate_registered_spec(spec)
    kept=load_kept_units(archive,sealed_catalog_sha256=pins.sealed["catalog_sha256"],planned_units=_planned_floor(spec))
    bracket=evaluate_window_bracket(archive,repo_root=ROOT)
    allowance=_strict_json(archive.output_bytes(NEG8_HARVEST_ALLOWANCE_RECORD),"neg8_allowance_record_invalid")
    row=inputs.archived_verdict_row(archive)
    if (canonical_sha256(row)!=allowance["verdict"]["row_sha256"] or
            row["evaluation_basis"]["sha256"]!=allowance["verdict"]["evaluation_basis_sha256"]):
        raise AnalysisRefusal("whole_window_verdict_provenance_invalid")
    parents=[]
    for name in ("selection.json","prefill_prompt_pin.json"):
        raw=archive.source_bytes(prefix+"prefill_pin/"+name)
        if raw!=read_authentication_input(local/"prefill_pin"/name,grammar="json",label="reported-energy sealed parent"):
            raise AnalysisRefusal("reported_energy_parent_differs_from_archive")
        parents.append(hashlib.sha256(raw).hexdigest())
    return {"spec":spec,"kept":kept,"bracket":bracket,"row":row,
            "selection_sha256":parents[0],"prompt_pin_sha256":parents[1]}


def _normalized_for_one_unit(setup,archive,view,context,cid,strict_validator):
    """Expose issuer rows when its kernel refused a one-unit interval."""
    spec=setup["spec"]
    index=next(i for i,c in enumerate(spec["reported_energy_cells"]) if c["cell_id"]==cid)
    cell=spec["reported_energy_cells"][index]; kept=view.for_reported_cell(spec,index)
    ids={run for units in kept.cell.kept.values() for unit in units for run in unit.run_ids}
    session=issuer.AuthenticatedConsumptionSession(view.window.claim_runs_root,ids,mode="issuing",
        evaluation_basis_sha256=setup["row"]["evaluation_basis"]["sha256"],
        consumption_semantics_id=issuer.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,archive_context=context)
    allowance=issuer.whole_window_drift_allowances(view.window.claim_runs_root,ids,consumption_session=session,
        evaluation_basis_sha256=setup["row"]["evaluation_basis"]["sha256"],
        consumption_semantics_id=issuer.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        neg8_harvest_archive=context.neg8_harvest_archive)
    if session.refusal_reasons:
        raise AnalysisRefusal(sorted(session.refusal_reasons)[0])
    if not session.ready:
        raise AnalysisRefusal("whole_window_verdict_provenance_invalid")
    model,_=energy._cell_identity(cid)
    binding={"model":model,"cell_id":cid,"extraction_spec_sha256":energy._digest(spec),
        "selection_sha256":setup["selection_sha256"],"prompt_pin_sha256":setup["prompt_pin_sha256"],
        "whole_window_basis_sha256":setup["row"]["evaluation_basis"]["sha256"],"attribution_floor_j":0.}
    return issuer.normalized_rows(cell,kept,session=session,runs_root=view.window.claim_runs_root,context=context,
        binding=binding,kept_units=view,strict_validator=strict_validator,
        allowances=allowance.allowances if allowance.status=="allowances" else {})


def _evidence_roots(artifact,extraction,windows):
    owners={r["cell_id"]:pack for pack,report in extraction.items() for r in report["cells"]}
    roots={}
    for cell in artifact["cells"]:
        for form in ("absolute","comparative"):
            provenance=cell["provenance"][form]
            pack=owners.get(provenance["calibration_cell_id"])
            if pack is None:
                raise AnalysisRefusal("disclosure_input_missing:floor_evidence_root")
            root_id=provenance["evidence_root_id"]; root=windows[pack].claim_runs_root
            if root_id in roots and roots[root_id]!=root:
                raise AnalysisRefusal("disclosure_input_invalid")
            roots[root_id]=root
    return roots


def build_disclosure_inputs(window_index,values,paths):
    """Index-owned archive/ledger locations; no free scientific path arguments."""
    from joulewise.cli import validate_bundle
    pins=SealPins.load(); table=sealed_pack_table(seal_pins=pins)
    index=load_window_index(window_index,seal_pins=pins,pack_table=table)
    records=tuple(open_attempt_record(e,seal_pins=pins,pack_table=table) for e in index.entries)
    windows=select_analysed_attempts(index,records,seal_pins=pins)
    archives={p:open_archive(w,seal_pins=pins,pack_table=table) for p,w in windows.items()}
    extraction={p:values["extraction_"+p] for p in ("alpha","beta")}
    setups={p:_floor_setup(windows[p],archives[p],pins) for p in ("alpha","beta")}
    evidence_roots=_evidence_roots(values["floor_artifact"],extraction,windows)
    # The finalized manifest is a step output, authenticated by the same
    # custody-relative digest table, never a free argument.
    manifest_path=paths["finalized_manifest"]
    if (values["claim_verdicts"]["inputs"]["analysis_manifest"]["file_sha256"] !=
            hashlib.sha256(read_authentication_input(manifest_path,grammar="json",label="finalized analysis manifest")).hexdigest()):
        raise AnalysisRefusal("step_output_digest_mismatch")
    built=inputs.block5_claim_gate_inputs(window_index,manifest_path,windows["gamma"].claim_runs_root,evidence_roots)
    archives.update(built["archives"])
    kept={p:s["kept"] for p,s in setups.items()}; kept["gamma"]=built["kept_units"]
    brackets={p:s["bracket"] for p,s in setups.items()}; brackets.update(built["brackets"])
    gamma_row=inputs.archived_verdict_row(archives["gamma"])

    def cell_estimates(pack,view,minimum):
        setup=setups[pack]
        context=build_context(archives[pack],view,brackets[pack],setup["row"])
        result=issuer.project_pack(setup["spec"],view,context=context,runs_root=windows[pack].claim_runs_root,
            evaluation_basis_sha256=setup["row"]["evaluation_basis"]["sha256"],
            selection_sha256=setup["selection_sha256"],prompt_pin_sha256=setup["prompt_pin_sha256"],
            strict_validator=validate_bundle,minimum=minimum)
        if minimum is None:
            for row in result["refused_cells"]:
                if row["code"]=="paper_reported_energy_kept_units_below_minimum":
                    result.setdefault("normalized_rows",{})[row["cell_id"]]=_normalized_for_one_unit(
                        setup,archives[pack],view,context,row["cell_id"],validate_bundle)
        return result

    def contrast_observations(view):
        # Fresh context and consumption session for every labelled view; an
        # earlier context/session is never modified after cached admission.
        context=build_context(archives["gamma"],view,brackets["gamma"],gamma_row)
        contexts={**built["archive_contexts"],str(windows["gamma"].claim_runs_root.resolve()):context}
        loaded=engine.load_analysis_inputs(manifest_path,windows["gamma"].claim_runs_root,paths["floor_artifact"],
            mode="read_replay",strict_validator=validate_bundle,evidence_roots=evidence_roots,
            neg8_harvest_archive=windows["gamma"].archive_root,kept_units=view,
            archive_contexts=contexts,gamma_archive=archives["gamma"])
        sentinel_entries=engine._sentinel_entries_by_block(loaded.manifest)
        prepared={row["contrast_id"]:engine._prepare_contrast(loaded,row,sentinel_entries,None,None,evidence_class="current")
                  for row in loaded.manifest["contrasts"]}
        return engine_contrast_observations(prepared)

    return {"index":index,"windows":windows,"archives":archives,"kept_units":kept,"brackets":brackets,
        "projections":{p:values["projection_"+p] for p in ("alpha","beta")},"extraction_reports":extraction,
        "floor_artifact":values["floor_artifact"],"closeout":values["closeout"],"claim_verdicts":values["claim_verdicts"],
        "contrast_observations":contrast_observations,"sensitivity":values["sensitivity"],"records":records,
        "cell_estimates":cell_estimates,"step_results":values["step_results"]}


def write_disclosures(custody,record):
    payloads=(("json",canonical_json_bytes(record)),
              ("unreleased.txt",render_disclosures(record,released=False).encode("utf-8")),
              ("released.txt",render_disclosures(record,released=True).encode("utf-8")))
    directory=_contained(custody,"disclosures")
    directory.mkdir(parents=True,exist_ok=True)
    files=[]; created=[]
    try:
        for suffix,raw in payloads:
            digest=hashlib.sha256(raw).hexdigest(); name=digest+"."+suffix
            target=_contained(custody,"disclosures/"+name)
            if target.exists():
                if target.read_bytes()!=raw:raise AnalysisRefusal("disclosure_output_exists")
            else:
                with target.open("xb") as out:
                    created.append(target); out.write(raw)
            files.append((name,digest))
    except Exception:
        for target in created:target.unlink(missing_ok=True)
        raise
    return files


def main(argv=None):
    parser=_Parser(description=__doc__)
    parser.add_argument("--window-index",type=Path,required=True)
    parser.add_argument("--custody",type=Path,required=True)
    parser.add_argument("--step-outputs",type=Path,required=True)
    try:
        args=parser.parse_args(argv)
        values,paths=load_step_outputs(args.custody,args.step_outputs)
        record=produce_disclosures(**build_disclosure_inputs(args.window_index,values,paths))
        files=write_disclosures(args.custody,record)
    except (AnalysisRefusal,energy.PaperReportedEnergyRefusal) as exc:
        print(exc.code); return 2
    except Exception:
        print("disclosure_input_invalid"); return 2
    for name,digest in files:print(name+" "+digest)
    return 0


if __name__=="__main__":raise SystemExit(main())
