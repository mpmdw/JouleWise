"""S9 synthetic disclosures. All arithmetic seams are explicitly named.

Pinned/synthetic-pack fixtures are module cached, never rebuilt per test.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import tempfile
from contextlib import redirect_stdout
from types import SimpleNamespace as NS
import unittest
from unittest import mock

from joulewise.b5_analysis import disclosures as d
from joulewise.b5_analysis.kept_units import KeptUnits, ReportedCellKept, Unit, DroppedUnit, CellKeptUnits
from joulewise.b5_analysis.windows import AnalysisRefusal
from joulewise import paper_reported_energy as energy
from tests.b5_analysis.test_reported_cell import case, R, B
from functools import lru_cache
from tests.b5_analysis.test_sensitivity import PassHarness, pass_fixture


@lru_cache(maxsize=1)
def sensitivity():
    pass_fixture()
    return PassHarness().call()


class FakeArchive:
    """Byte adapter only: no archive authentication is claimed for this seam."""
    def __init__(self):
        self.outputs = {"derived/flags.jsonl": b"", "derived/roster.json": b'{"members":[]}'}
        self.outputs.update({"derived/window_flags.json":b'{"hazards":{}}',
            "derived/neg8-screen.json":d.canonical_json_bytes({"rescreen":{"decision":"passed","survivors":{
                "reference_counts":{"start":3,"midpoint":1,"end":3},"reference_losses":[],"midpoint_lost":False}},
                "harvest_reference_losses":{},"bound_formula":"registered-count-adjusted-bound"}),
            "derived/neg8-bound.json":b'{"members_committed":18,"members_collected":18,"dropped_bundle_ids":[]}',
            "derived/neg8-corpus-physics.json":b'{"members_bound":18,"members_collected":18,"members_kept":12,"beyond_cap":[],"dropped":[]}',
            "derived/neg8-allowance.json":b'{"source":"survivor_rescreen"}'})
        self.sources = {"sources/claim-runs/whole-window-verdict.json":b'{"excluded_bundles":[]}'}
        self.withheld = {"withheld/meter.json": b'{"members":{}}',
            "withheld/battery-assist.json":b'{"members":{},"captures":{}}',
            "withheld/neg8-rescreen-bracket.json":b'{"allowance_j":0.05}'}
        self.record = {"outputs": self.outputs}

    def output_bytes(self, name): return self.outputs[name]
    def source_bytes(self, name): return self.sources[name]
    def source_names(self): return tuple(sorted(n.removeprefix("sources/") for n in self.sources))
    def withheld_bytes(self, name): return self.withheld[name]


class Harness:
    def __init__(self, remove_r=(), remove_b=()):
        self.records=[]; self.windows={}; self.archives={}; self.kept={}; self.brackets={}
        for i,p in enumerate(d.PACK_ORDER):
            entry=NS(pack=p,plan_id=p+"-synthetic-plan",attempt=1,seal="second",cause_key=None,
                verdict="COLLECTED",g10_requested=False,g10_redraw_cycles=None,t0_epoch_s=1000+i)
            rec=NS(entry=entry,kind="harvested",record_shape="pin2" if p=="alpha" else "pin4",
                verdict="COLLECTED",claim_usable=True,flags_by_family={},g10_codes={},
                yield_counts={"planned":50,"succeeded":50},calibration_bracket=None,reference_source=None)
            self.records.append(rec)
            win=NS(pack=p,pack_id=p+"-synthetic-pack",plan_id=entry.plan_id,attempt=1,
                harvest_pin="a"*40,record=rec)
            self.windows[p]=win; self.archives[p]=FakeArchive()
            win.claim_runs_root=Path("/synthetic-claim"); win.custody_root=Path("/synthetic-custody")
            self.archives[p].window=win
            self.archives[p].sources[f"sources/repo/configs/campaigns/{win.pack_id}/extraction_spec.json"]=d.canonical_json_bytes({
                "cells":[{"cell_id":"floor-a","kind":"absolute","condition_family_id":"synthetic"}]})
            self.kept[p]=KeptUnits(win,"1"*64,"2"*64,d.SealPins.load().sealed["catalog_sha256"],{},{},{})
            self.brackets[p]=NS(b_fiducial_s=.035 if p=="alpha" else .045,
                sources_sha256sums_sha256="3"*64,ledger_copy_sha256="4"*64,terminal_sequence=500)
        self.index=NS(entries=tuple(r.entry for r in self.records))
        c,rows,binding,k=case(remove_r,remove_b)
        dropped=tuple(replace(u,codes=("member.admission_aborted",),families=("MEMBER_VALIDITY",)) for u in k.cell.dropped)
        k=replace(k,cell=replace(k.cell,dropped=dropped))
        self.cell=c; self.rows=case()[1]; self.binding=binding; self.base_kept=k
        # Fabricated full roster, including the existing one-member meter seam.
        self.archives["alpha"].outputs["derived/roster.json"]=d.canonical_json_bytes({"members":
            [{"run_id":r["member"]["bundle_id"],"kind":"science"} for r in self.rows]+
            [{"run_id":"alpha-one","kind":"science"}]})
        self.archives["beta"].outputs["derived/roster.json"]=d.canonical_json_bytes({"members":
            [{"run_id":run,"kind":"science"} for run in ("beta-inside","beta-outside")]})
        self.kept["alpha"]=replace(self.kept["alpha"],cells={"synthetic":k.cell})
        self.projections={"alpha":{"cells":[energy._project_cell(c,rows,binding,kept=k,
            exclusions_sha256="1"*64)],"refused_cells":[]},"beta":{"cells":[],"refused_cells":[]}}
        self.extraction={"alpha":{"cells":[]},"beta":{"cells":[]}}
        self.floor={"cells":[]}; self.closeout={}; self.verdicts={"contrasts":[]}
        self.sens=deepcopy(sensitivity()); self.steps={"no_analysed_window_harvested_twice":True,
            "windows":{p:{"stored_verdict":{"status":"failed","conditions":[]},"member_reasons":[],
                "adapter_continuity":"passed","tripwires":{"excluded_reference_in_screen":"passed",
                "kept_member_outside_verdict_membership":"passed"},"deciding_references":7,"deciding_spares":0,
                "writer_excluded_count":0,"reference_parity":"passed","ledger_prefix_test":"passed"} for p in d.PACK_ORDER}}
        for r in self.steps["windows"].values():r.update(writer_excluded_by_family={},writer_excluded_all_removed=True)
        self.calls=[]; self.observations={}

    def flag(self,pack,code,run=None,**kwargs):
        catalog=d._catalog(); entry=catalog.codes[code]
        row={"code":code,"family":entry["family"],"blinding":entry["blinding"],
            "scope":{"level":"member" if run else "window","run_id":run},**kwargs}
        self.archives[pack].outputs["derived/flags.jsonl"]+=d.canonical_json_bytes(row)+b"\n"

    def estimate(self,pack,view,minimum):
        self.calls.append((pack,view,minimum))
        cell=view.cell("synthetic")
        rr=tuple(sorted(u.positions[0] for u in cell.kept["repeat"]))
        qq=tuple(sorted(u.positions for u in cell.kept["quad"]))
        kept=ReportedCellKept(cell,rr,tuple(n for n in range(1,11) if n not in rr),qq,
            tuple(tuple(range(n,n+4)) for n in range(11,51,4) if tuple(range(n,n+4)) not in qq))
        rows=[r for r in self.rows if r["member"]["ordinal"] in energy._kept_ordinals(kept)]
        try:
            value=energy._project_cell(self.cell,rows,self.binding,kept=kept,
                exclusions_sha256="1"*64,minimum=minimum)
            return {"cells":[value],"refused_cells":[]}
        except energy.PaperReportedEnergyRefusal as exc:
            return {"cells":[],"refused_cells":[{"cell_id":self.cell["cell_id"],"code":exc.code}],
                    "normalized_rows":{self.cell["cell_id"]:rows}}

    def observe(self,view):
        return {cid:[deepcopy(r) for r in rows if r["block_id"] in
            {u.unit_id for u in view.for_contrast(cid).kept["quad"]}]
            for cid,rows in self.observations.items()}

    def add_contrast(self,ds=(3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7),*,cid="decode",removed=(4,),sides=None):
        units=[]; dropped=[]; rows=[]
        for n,delta in enumerate(ds,1):
            bid=f"{cid}-b{n:02d}"
            u=Unit(cid,"quad",bid,tuple(bid+"-"+p for p in ("A1","B1","B2","A2")),
                tuple(range(4*n-3,4*n+1)),("science",)*4)
            if n in removed:
                dropped.append(DroppedUnit(**u.__dict__,codes=("member.admission_aborted",),families=("MEMBER_VALIDITY",)))
            else:units.append(u)
            a,b=sides[n-1] if sides is not None else (10.,10.+delta)
            rows.append({"block_id":bid,"a_mean_j":a,"b_mean_j":b,"d_j":delta})
        cell=CellKeptUnits(cid,True,{"quad":len(ds)},{"quad":5},{"quad":tuple(units)},tuple(dropped),0,len(units))
        self.kept["gamma"]=replace(self.kept["gamma"],cells={**self.kept["gamma"].cells,cid:cell})
        self.observations[cid]=rows
        val=d._paired_values([r for i,r in enumerate(rows,1) if i not in removed])
        self.verdicts["contrasts"].append({"contrast_id":cid,"estimator":{"n":val["n"],"estimate":val["mean_j"],
            "s_d":val["s_d"],"SE_total":val["se"],"t_critical_95":val["t_star"],
            "metrology_aware_CI95":{"lower":val["lower_j"],"upper":val["upper_j"]}},
            "deterministic_bounds":{"decision_interval":{"lower":val["lower_j"]-.05,"upper":val["upper_j"]+.05}},
            "floor":{"active_floor_j":1.2},"loo":{"rows":[]}})

    def produce(self):
        # Fabricated exclusions have no writer. Supply matching fabricated
        # flags here, while preserving every deliberately supplied flag byte.
        for pack,view in self.kept.items():
            if not isinstance(self.archives[pack],FakeArchive):continue
            present={json.loads(r)["code"] for r in self.archives[pack].outputs["derived/flags.jsonl"].splitlines() if r.strip()}
            for cell in view.cells.values():
                for unit in cell.dropped:
                    for code in unit.codes:
                        if code not in present:
                            self.flag(pack,code,unit.run_ids[0]);present.add(code)
        with mock.patch.object(d,"rebuilt_roster",side_effect=lambda archive,row:json.loads(archive.output_bytes("derived/roster.json"))):
            return d.produce_disclosures(self.index,self.windows,self.archives,self.kept,self.brackets,
                self.projections,self.extraction,self.floor,self.closeout,self.verdicts,self.observe,
                self.sens,records=self.records,cell_estimates=self.estimate,step_results=self.steps)

    def text(self): return d.render_disclosures(self.produce(),released=True)


class PartATests(unittest.TestCase):
    def test_A1_A3_A4_canonical_and_pure_renderer(self):
        from joulewise.b5_analysis.steps import classify_step4_exit
        self.assertIs(d.classify_step4_exit,classify_step4_exit)
        h=Harness(); record=h.produce()
        record["cells"].append(d._item("sentinel",True,"sentinel 123.45678 J",mean_j=123.45678))
        raw=d.canonical_json_bytes(record)
        from joulewise.whole_window import canonical_sha256
        self.assertEqual(hashlib.sha256(raw).hexdigest(),canonical_sha256(record))
        self.assertIn("sentinel: withheld until the release event",d.render_disclosures(record,released=False))
        self.assertIn("123.45678",d.render_disclosures(record,released=True))
        self.assertEqual(raw,d.canonical_json_bytes(record))
        self.assertEqual(record["schema_version"],"joulewise.b5_disclosures.v1")

    def test_A2_adapter_matches_real_engine(self):
        from tests.b5_analysis import fixtures_s5 as s5
        loaded=s5.arithmetic_inputs([3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7])
        with s5.arithmetic_seams(loaded): prepared,*_=s5.prepared_pair(loaded)
        rows=d.engine_contrast_observations(prepared)
        for cid,p in prepared.items():
            self.assertEqual([r["d_j"] for r in rows[cid]],list(p["estimate"].paired_values))
            self.assertEqual([r["block_id"] for r in rows[cid]],list(p["estimate"].block_ids))
        fallback=d.engine_contrast_observations({cid:{**p,"estimate":None} for cid,p in prepared.items()})
        self.assertEqual(fallback,rows)
        rows["decode"][0]["a_mean_j"]=-1
        self.assertNotEqual(prepared["decode"]["observations"][0].value_a,-1)

    def test_R9_sensitivity_shape_and_label(self):
        for edit in (lambda s:s.update(label="primary"),lambda s:s.pop("b_max"),
                     lambda s:s["windows"]["alpha"].pop("widened")):
            h=Harness(); edit(h.sens)
            with self.assertRaises(AnalysisRefusal) as cm:h.produce()
            self.assertEqual(cm.exception.code,"sensitivity_record_invalid")

    def test_R10_flag_blinding(self):
        # A flag that loosens its code's catalog blinding refuses. (S10: a flag may
        # tighten it, as the sealed catalog sets for diagnostic.s1_structural; see
        # FlagBlindingTests.)
        catalog=d._catalog()
        code=next(c for c,entry in sorted(catalog.codes.items()) if entry["blinding"]=="RESTRICTED")
        h=Harness(); h.flag("alpha",code)
        a=h.archives["alpha"]; row=json.loads(a.outputs["derived/flags.jsonl"])
        row["blinding"]="STRUCTURE"; a.outputs["derived/flags.jsonl"]=d.canonical_json_bytes(row)
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"flag_blinding_differs_from_catalog")


def items(record,name,line): return [r for r in record[name] if r["line"]==line]


class PartBTests(unittest.TestCase):
    def test_T1_B1_assist_example_whole_quad(self):
        h=Harness(); h.flag("alpha","battery.assist",h.rows[2]["member"]["bundle_id"])
        h.flag("alpha","battery.assist",h.rows[34]["member"]["bundle_id"])
        rec=h.produce(); row=items(rec,"cells","battery_assist_cell")[0]; text=d.render_disclosures(rec,released=True)
        self.assertEqual((row["n_r"],row["n_b"]),(9,9))
        self.assertEqual(len(h.calls[0][1].kept_run_ids("synthetic")),45)
        self.assertIn("10.16222 J; h = 0.12333 J",text)
        self.assertIn("10.16000 J; h = 0.10833 J",text)
        self.assertEqual(row["assist_members"],{"repeat":1,"quad":1})

    def test_R1_R3_no_assist_never_recomputes(self):
        h=Harness(); h.flag("alpha","battery.assist_outside_request",h.rows[0]["member"]["bundle_id"])
        rec=h.produce(); row=items(rec,"cells","battery_assist_cell")[0]
        self.assertEqual(row["without"],row["primary"])
        self.assertEqual(h.calls,[])
        self.assertIn("no assisted member; without equals with",d.render_disclosures(rec,released=True))
        for key in ("mean_j","h_j","B_j","lower_j","upper_j"):
            self.assertEqual(row["without"][key].hex(),row["primary"][key].hex())

    def test_T2_B2_below_minimum_exact_table(self):
        for remaining,mean,half in [(4,"10.17000","0.15262"),(3,"10.16667","0.21273"),(2,"10.18000","0.63953")]:
            with self.subTest(remaining=remaining):
                h=Harness()
                for r in h.rows[remaining:10]:h.flag("alpha","battery.assist",r["member"]["bundle_id"])
                with mock.patch.object(energy,"estimate_reported_cell",wraps=energy.estimate_reported_cell) as kernel:
                    try:rec=h.produce()
                    except energy.PaperReportedEnergyRefusal as exc:self.fail("registered below-minimum line refused: "+exc.code)
                self.assertIn(mean+" J; h = "+half+" J",d.render_disclosures(rec,released=True))
                self.assertIn("below the registered minimum of 5 units",d.render_disclosures(rec,released=True))
                self.assertIsNone(h.calls[0][2]); self.assertIsNone(kernel.call_args.kwargs["minimum"])

    def test_T3_B3_one_and_none(self):
        for remaining,words in [(1,"no interval (one unit); below the registered minimum of 5 units"),
                                (0,"not computable (no unit left in a stratum)")]:
            h=Harness()
            for r in h.rows[remaining:10]:h.flag("alpha","battery.assist",r["member"]["bundle_id"])
            text=h.text(); self.assertIn(words,text)
            if remaining:self.assertIn("10.16000 J; no interval",text)
        h=Harness(); cell,rows,binding,k=case(tuple(range(3,11)))
        v=energy.estimate_reported_cell(rows,k,minimum=None)
        self.assertEqual(d._one_unit_mean(rows,2).hex(),v.mean_j.hex())

    def test_R12_only_exact_kernel_refusal_caught(self):
        h=Harness(); h.flag("alpha","battery.assist",h.rows[0]["member"]["bundle_id"])
        def refuse(*args):raise energy.PaperReportedEnergyRefusal("paper_reported_energy_request_invalid")
        h.estimate=refuse
        with self.assertRaises(energy.PaperReportedEnergyRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"paper_reported_energy_request_invalid")

    def test_T4_B4_contrast_example_and_small_n(self):
        h=Harness(); h.add_contrast(); cell=h.kept["gamma"].cell("decode")
        h.flag("gamma","battery.assist",next(u for u in cell.kept["quad"] if u.unit_id=="decode-b03").run_ids[1])
        rec=h.produce(); row=items(rec,"contrasts","battery_assist_contrast")[0]
        self.assertEqual((row["n"],row["assist_quads"]),(8,1))
        self.assertEqual(row["t_star"],2.365)
        text=d.render_disclosures(rec,released=True)
        self.assertIn("2.96250 J; s_d = 0.16850 J; se = 0.059574 J; t* = 2.365",text)
        self.assertIn("[2.82161, 3.10339]",text)
        for remain,words in [(1,"no interval (one quad); below the registered minimum of 5 quads"),
                             (0,"not computable (no quad left)")]:
            hh=Harness(); hh.add_contrast()
            for u in hh.kept["gamma"].cell("decode").kept["quad"][remain:]:hh.flag("gamma","battery.assist",u.run_ids[1])
            self.assertIn(words,hh.text())

    def test_T5_B5_load_correlated_example(self):
        h=Harness((6,),(5,9)); cell=h.kept["alpha"].cell("synthetic")
        changed=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero",),families=("PHYSICS_IN_SPAN",))
            if u.stratum=="repeat" else u for u in cell.dropped))
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":changed})
        text=h.text()
        self.assertIn("10.14000 J; h = 0.11557 J",text)
        self.assertIn("restored repeat 1, quad 0; code families: PHYSICS_IN_SPAN",text)
        self.assertEqual(h.calls[0][2],5)
        changed=replace(cell,dropped=tuple(replace(u,codes=("clock.step_overlap",)) for u in cell.dropped))
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":changed})
        self.assertNotIn("load-correlated",h.text())

    def test_R7_mixed_codes_stay_removed(self):
        h=Harness((6,)); cell=h.kept["alpha"].cell("synthetic")
        mixed=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero","member.admission_aborted"),
            families=("PHYSICS_IN_SPAN","MEMBER_VALIDITY")) for u in cell.dropped))
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":mixed})
        self.assertIn("no unit restored",h.text()); self.assertEqual(h.calls,[])
        h.add_contrast(); cell=h.kept["gamma"].cell("decode")
        mixed=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero","member.admission_aborted")) for u in cell.dropped))
        h.kept["gamma"]=replace(h.kept["gamma"],cells={"decode":mixed})
        self.assertIn("no unit restored; restored quads 0",h.text())

    def test_B5_contrast_restoration_calls_view(self):
        h=Harness(); h.add_contrast(); cell=h.kept["gamma"].cell("decode")
        cell=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero",),families=("PHYSICS_IN_SPAN",)) for u in cell.dropped))
        h.kept["gamma"]=replace(h.kept["gamma"],cells={"decode":cell})
        rec=h.produce(); row=items(rec,"contrasts","load_correlated_contrast")[0]
        self.assertEqual(row["values"]["n"],10); self.assertEqual(row["restored_count"],1)
        self.assertNotIn("outcome",row["values"])

    def test_load_correlated_cell_refusal_is_the_line_not_the_record(self):
        # Early cold passes F1 (S10): plan 8.1's line never gates anything, so a
        # typed refusal on the restored view is that line's text.
        h=Harness((6,),(5,9)); cell=h.kept["alpha"].cell("synthetic")
        changed=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero",),families=("PHYSICS_IN_SPAN",))
            if u.stratum=="repeat" else u for u in cell.dropped))
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":changed})
        primary=h.estimate
        def estimate(pack,view,minimum):
            if view.sensitivity_label=="load-correlated":raise AnalysisRefusal("member_code_on_kept_unit")
            return primary(pack,view,minimum)
        h.estimate=estimate
        rec=h.produce(); row=items(rec,"cells","load_correlated_cell")[0]
        self.assertEqual(row["values"],{"status":"refused","code":"member_code_on_kept_unit"})
        self.assertIn("not computable: member_code_on_kept_unit",d.render_disclosures(rec,released=True))
        self.assertTrue(items(rec,"cells","reported_cell"))

    def test_load_correlated_contrast_refusal_is_the_line_and_defects_propagate(self):
        from joulewise.analysis_engine.inputs import AnalysisInputError
        h=Harness(); h.add_contrast(); cell=h.kept["gamma"].cell("decode")
        cell=replace(cell,dropped=tuple(replace(u,codes=("thermal.os_level_nonzero",),families=("PHYSICS_IN_SPAN",)) for u in cell.dropped))
        h.kept["gamma"]=replace(h.kept["gamma"],cells={"decode":cell})
        observe=h.observe
        def refusing(view):
            if view.sensitivity_label=="load-correlated":raise AnalysisInputError("member_code_on_kept_unit")
            return observe(view)
        h.observe=refusing
        rec=h.produce(); row=items(rec,"contrasts","load_correlated_contrast")[0]
        self.assertEqual(row["values"],{"status":"refused","code":"member_code_on_kept_unit"})
        self.assertIn("not computable: member_code_on_kept_unit",row["text"])
        self.assertTrue(items(rec,"contrasts","primary_contrast"))
        def broken(view):
            if view.sensitivity_label=="load-correlated":raise RuntimeError("defect")
            return observe(view)
        h.observe=broken
        with self.assertRaises(RuntimeError):h.produce()

    def test_T6_B6_magnitude_ratio_and_token(self):
        h=Harness(); h.add_contrast((10,12,8),removed=(),sides=((10,20),(10,22),(10,18)))
        text=h.text(); self.assertIn("1.9933 [1.5534, 2.5578]",text)
        self.assertIn("Recorded timing bounds are not propagated into it",text); self.assertIn(d.GROSS_SENTENCE,text)
        token=Harness();token.add_contrast((2.1,2.1,2.1),removed=())
        self.assertIn("0.004102 J per output token",token.text())

    def test_T7_B7_exact_cross_window_boundary(self):
        h=Harness(); primary=h.projections["alpha"]["cells"][0]
        primary["interval"]["h_j"]=0.; mean=primary["mean_j"]
        exact=energy.T975[2]/math.sqrt(3); rounded=d._ci_t_critical(2)/math.sqrt(3)
        delta=(exact+rounded)/2
        h.add_contrast((3,3,3),removed=(),sides=[(mean+delta+x,mean+delta+x+3) for x in (-1,0,1)])
        text=h.text()
        self.assertIn("estimates differ by",text); self.assertNotIn("estimates agree within",text)
        row=items(h.produce(),"cells","cross_window")[0]
        self.assertAlmostEqual(row["h_G_j"],exact,places=13)
        self.assertLess(exact,delta); self.assertGreater(rounded,delta)
        # The plan's simple agree case, using the same actual side-mean estimator.
        primary["mean_j"]=10.16; primary["interval"]["h_j"]=.108
        span=.2*math.sqrt(3)/energy.T975[2]
        h.observations["decode"]=[{**r,"a_mean_j":10.3+x} for r,x in zip(h.observations["decode"],(-span,0,span))]
        self.assertIn("estimates agree within their within-window intervals (difference 0.14000 J)",h.text())

    def test_T8_T20_B8_meter_all_members(self):
        h=Harness((6,)); rhos=[.78,.80,.81,.79,.82,.80,.77,.81,.80,.83]
        members={h.rows[i]["member"]["bundle_id"]:{"rho":rho,"rail_delta_J":rho*600,
            "machine":{"delta_J":600,"battery_available":True}} for i,rho in enumerate(rhos)}
        h.archives["alpha"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":members})
        text=h.text(); self.assertIn("median 0.8000; range 0.7700 to 0.8300; IQR 0.7925 to 0.8100",text)
        self.assertIn("plausible spread 0.0750; consistent",text)
        self.assertIn("removed by the exclusion function",text)
        removed=h.rows[5]["member"]["bundle_id"]
        members[removed]={"rho":640/600,"rail_delta_J":640,"machine":{"delta_J":600}}
        h.flag("alpha","meter.battery_activity",removed)
        h.archives["alpha"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":members})
        text=h.text(); self.assertIn("range 0.7700 to 1.0667",text)
        self.assertIn("outside the hard band; meter flags: meter.battery_activity",text)
        self.assertIn("no clean window; no central band",text); self.assertIn(d.MACHINE_BOUNDARY,text)
        # Force the removed row to determine the median, so M7 changes printed bytes.
        members={run:{**row,"rho":.1 if run==removed else .9} for run,row in list(members.items())[:2]+[(removed,members[removed])]}
        members[removed]["rho"]=.1; members[next(iter(members))]["rho"]=.5
        h.archives["alpha"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":members})
        self.assertIn("median 0.5000; range 0.1000 to 0.9000",h.text())

    def test_B8_per_model_first_clean_window_not_computable(self):
        h=Harness(); h.add_contrast(); units=h.kept["gamma"].cell("decode").kept["quad"]
        h.archives["alpha"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":{
            "alpha-one":{"rho":.8,"rail_delta_J":480,"machine":{"delta_J":600}}}})
        h.archives["gamma"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":{
            units[0].run_ids[1]:{"rho":.9,"rail_delta_J":540,"machine":{"delta_J":600}},
            units[0].run_ids[0]:{"rho":.8,"rail_delta_J":480,"machine":{"delta_J":600}},
            units[1].run_ids[0]:{"rho":None,"rail_delta_J":None,"machine":None}}})
        text=h.text()
        self.assertIn("first clean window for qwen3-8b: gamma",text)
        self.assertIn("first clean window for qwen3-1p7b: alpha",text)
        self.assertIn("1 of 1 member windows inside",text); self.assertIn("not computable",text)

    def test_T9_B9_contrast_interval_each_n(self):
        h=Harness(); h.add_contrast(); h.add_contrast(cid="prefill",removed=(3,4))
        text=h.text(); self.assertIn("rounded t* (2.306 for 2.306004)",text)
        self.assertIn("rounded t* (2.365 for 2.364624)",text)

    def test_T10_B10_copy_verdict_and_loo(self):
        h=Harness(); h.add_contrast(); h.add_contrast(cid="prefill",removed=(3,4))
        row=h.verdicts["contrasts"][0]; row["floor"]["active_floor_j"]=2.99
        row["deterministic_bounds"]["decision_interval"]={"lower":2.8,"upper":3.2}
        row["loo"]["rows"]=[{"omitted_block_id":"decode-b03","estimate":2.0,"influence_triggers":["estimate_magnitude"]}]
        text=h.text(); self.assertIn(d.DECISION_SENTENCE,text)
        self.assertIn("Leaving out quad 3 moves the estimate by 1.00000 J",text)
        self.assertIn("leave-one-out rows 1",text)
        self.assertEqual(items(h.produce(),"contrasts","loo_counts")[0]["exclusive_block_numbers"],["3"])
        copied=items(h.produce(),"contrasts","decision_floor")[0]
        self.assertEqual(copied["decision_interval"],row["deterministic_bounds"]["decision_interval"])

    def test_T11_B11_floor_composition_and_attribution(self):
        h=Harness(); h.extraction["alpha"]["cells"]=[{"cell_id":"floor-a","kind":"absolute","floor":{
            "guarded_floor_j":.5,"whole_window_drift_allowance_j":.2,"drift_widened_guarded_floor_j":.7,
            "whole_window_drift_allowance_provenance":{"source":"survivor_rescreen"}}}]
        h.floor["cells"]=[{"floor_abs_j":.7,"provenance":{"absolute":{"calibration_cell_id":"floor-a"}}}]
        text=h.text(); self.assertIn("guarded operative floor 0.50000 J; allowance added 0.20000 J from survivor_rescreen",text)
        self.assertIn("minted floor 0.70000 J",text)
        self.assertIn("up to 0.01000 J",text)
        # The issuer's allowance provenance carries numeric derivation
        # provenance, not the harvest's source word. Bind that word separately.
        del h.extraction["alpha"]["cells"][0]["floor"]["whole_window_drift_allowance_provenance"]["source"]
        self.assertIn("from survivor_rescreen",h.text())
        h.extraction["alpha"]["cells"][0]["floor"]["drift_widened_guarded_floor_j"]=.71
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"floor_report_composition_inconsistent")

    def test_T12_real_project_pack_labelled_view(self):
        from tests.b5_analysis import fixtures_s8 as s8
        fixture=s8.synthetic_pack()
        # S8's arithmetic dropped-code word is deliberately "synthetic";
        # S9 needs catalog-bound codes, so only that structural seam changes.
        fixture=NS(**{**vars(fixture),"kept":replace(fixture.kept,cells={cid:replace(c,
            dropped=tuple(replace(u,codes=("member.admission_aborted",),families=("MEMBER_VALIDITY",)) for u in c.dropped))
            for cid,c in fixture.kept.cells.items()})})
        with s8.pack_seams(fixture): primary=s8.project(fixture)
        h=Harness(); h.projections["alpha"]=primary; h.kept["alpha"]=fixture.kept
        for key,value in primary["window"].items():setattr(h.windows["alpha"],key,value)
        run=primary["cells"][0]["members"][0]["bundle_id"]; h.flag("alpha","battery.assist",run)
        calls=[]
        def estimate(pack,view,minimum):
            calls.append((view.sensitivity_label,minimum))
            f=NS(**{**vars(fixture),"kept":view})
            with s8.pack_seams(f):return s8.project(f,minimum=minimum)
        h.estimate=estimate
        rec=h.produce(); row=items(rec,"cells","battery_assist_cell")[0]
        self.assertEqual((row["n_r"],row["n_b"]),(8,8))
        self.assertEqual(calls,[("battery-assist",None)])
        self.assertNotEqual(row["primary"]["mean_j"],row["without"]["mean_j"])


class PartCTests(unittest.TestCase):
    def test_T13_restricted_codes_values_and_canonical_bytes(self):
        h=Harness((6,)); catalog=d._catalog()
        restricted=next(c for c,v in catalog.codes.items() if v["blinding"]=="RESTRICTED")
        cell=h.kept["alpha"].cell("synthetic"); u=cell.dropped[0]
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":replace(cell,dropped=(replace(
            u,codes=(restricted,),families=(catalog.codes[restricted]["family"],)),))})
        h.flag("alpha",restricted,u.run_ids[0]); record=h.produce()
        a=h.archives["alpha"]
        screen=json.loads(a.outputs["derived/neg8-screen.json"])
        screen["rescreen"]["survivors"]["reference_losses"]=[{"bundle_id":"reference","slot":"start","reason":restricted}]
        a.outputs["derived/neg8-screen.json"]=d.canonical_json_bytes(screen)
        record=h.produce()
        # Every restricted renderable leaf gets a unique sentinel; redaction
        # must be exhaustive even when a leaf's rendering contains other text.
        markers=[]
        for section in ("cells","floors","contrasts","block_lines","fixed_sentences"):
            for n,row in enumerate(record[section]):
                if row["restricted"]:
                    marker=f"{123.45678+n:.5f}"; markers.append(marker); row["text"]+=" "+marker
        for rows in record["window_lines"].values():
            for n,row in enumerate(rows):
                if row["restricted"]:
                    marker=f"{234.56789+n:.5f}"; markers.append(marker); row["text"]+=" "+marker
        raw=d.canonical_json_bytes(record)
        before=d.render_disclosures(record,released=False); after=d.render_disclosures(record,released=True)
        self.assertIn("removed (restricted code)",before); self.assertNotIn(restricted,before)
        self.assertIn(catalog.codes[restricted]["family"],before); self.assertIn(restricted,after)
        flag_count=next(r for r in record["window_lines"]["alpha"] if r["line"]=="flag_count" and r["code"]==restricted)
        self.assertTrue(flag_count["restricted"]);self.assertEqual(flag_count["count"],1)
        for marker in markers:self.assertNotIn(marker,before)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),hashlib.sha256(d.canonical_json_bytes(record)).hexdigest())

    def test_T14_eleven_attempt_history_all_pin_shapes(self):
        h=Harness(); records=[]
        for pack,seal,number,shape,kind in [("alpha","first",n,"pin1","harvested") for n in (1,2,3)]+[
            ("alpha","second",1,"pin2","harvested")]+[("beta","second",n,"pin3" if n<6 else "pin4","no_archive" if n==2 else "harvested") for n in range(1,7)]+[
            ("gamma","second",1,"pin4","harvested")]:
            rec=deepcopy(h.records[1 if pack=="beta" else 0 if pack=="alpha" else 2])
            rec.entry.attempt=number;rec.entry.seal=seal; rec.entry.plan_id=f"{pack}-{seal}-a{number}";rec.entry.cause_key="clock" if number==2 else None
            rec.record_shape=shape;rec.kind=kind
            if pack=="beta" and number==1:rec.reference_source="claim_campaign_manifests_authenticated"
            if pack=="beta" and number<6:
                rec.claim_usable=False;rec.verdict="NO_COLLECTION" if kind=="no_archive" else "NULL"
                rec.entry.verdict=rec.verdict
            if shape=="pin4":rec.calibration_bracket={"observed_triggers":["freshness"],"recorded_only_triggers":["corpus_doubles_from_24_to_48"],
                "corpus_doubling":{"count":48},"other_session_systematic_sequences":[400,401]}
            records.append(rec)
        h.records=records;h.index.entries=tuple(r.entry for r in records)
        text=h.text()
        self.assertEqual(len(items(h.produce(),"block_lines","attempt_history")),11)
        self.assertIn("beta-second-a1 attempt 1",text);self.assertIn("catalog-path screen",text)
        self.assertIn("corpus doubling count: 48; other-session systematic sequences: 400, 401",text)
        self.assertIn("not recorded by this harvest's program",text)
        self.assertIn("beta-second-a2 attempt 2: NO_COLLECTION; cause key clock; not harvested",text)
        self.assertIn("Superseded first-seal attempts:",text)
        self.assertIn("attempts of this pack: 3",text);self.assertIn("attempts of this pack: 6",text)
        history=items(h.produce(),"block_lines","attempt_history")
        self.assertTrue(history[-1]["superseded"])

    def test_T15_monitor_arm_hazards_and_arm_unmeasured(self):
        h=Harness(); a=h.archives["alpha"]; run=h.rows[0]["member"]["bundle_id"]
        a.sources["sources/night-custody/hazards/monitor/monitor.jsonl"]=b'\n'.join(d.canonical_json_bytes(r) for r in [
            {"kind":"session_start"},{"kind":"cost","values":{"cpu_self_s":.12,"cpu_children_s":.23}}])
        a.sources["sources/night-custody/hazards/meter/stream-001.jsonl"]=d.canonical_json_bytes({"k":"t","utime_s":.2,"stime_s":.1})
        a.sources[f"sources/claim-runs/{run}/events.jsonl"]=b'\n'.join(d.canonical_json_bytes(r) for r in [
            {"event_type":"phase_start","phase":"decode","metadata":{"monotonic_ns":1_000_000_000}},
            {"event_type":"phase_end","phase":"decode","metadata":{"monotonic_ns":2_000_000_000}}])
        a.sources[f"sources/claim-runs/{run}/metadata.json"]=d.canonical_json_bytes({"uncertainty_evidence":{"clock_anchor":{
            "status":"bounded","effective_clock_anchor_bound_s":.04,"clock_stamps":{
                "sampling_started":{"monotonic_before_s":1.},"sampling_stopped":{"monotonic_after_s":2.}}}}})
        a.sources["sources/night-custody/hazards/monitor/contention.jsonl"]=d.canonical_json_bytes({"module":"contention","kind":"interval",
            "started":{"monotonic_ns":1_000_000_000},"finished":{"monotonic_ns":2_000_000_000},"values":{"host_busy_cpu_s_per_s":2.}})
        a.outputs["derived/window_flags.json"]=d.canonical_json_bytes({"hazards":{"battery":{"arm":[{"phase":"instant","verdict":"passed",
            "measurement":{"values":{"instant_amperage_ma":-12,"hostname":"must-not-copy","wall_ns":444}}}]}}})
        h.flag("beta","contention.arm_unmeasured");h.flag("alpha","thermal.os_level_nonzero",run)
        text=h.text();self.assertIn("hazard CPU 0.350000 s; probes inside target phases 1; meter reader CPU 0.300000 s",text)
        self.assertIn("instant_amperage_ma -12",text);self.assertNotIn("must-not-copy",text)
        self.assertIn("host's total busy CPU during requests: 2.000000 s",text)
        self.assertIn("members with anchor status bounded: 1",text)
        self.assertIn("At this window's arm the contention check returned no reading and did not refuse; the monitor measured it during the window.",text)

    def test_T16_temperature_two_readings_none_plateau_and_disagreement(self):
        h=Harness();a=h.archives["alpha"]
        for stage,values in [("warm",[3000,3350]),("empty",[]),("plateau",[3000,3350,3360,3370]),("disagree",[3000,3400])]:
            a.sources[f"sources/claim-runs/campaign_manifests/{stage}.json"]=d.canonical_json_bytes({"stage_id":stage,"members":[{}],
                "battery_temperature_readings":[{"temperature_centi_c":v} for v in values]})
        h.flag("alpha","thermal.stage_battery_rise",observed={"config_dir":"warm"})
        h.flag("alpha","thermal.battery_temperature_unmeasured",observed={"config_dir":"empty"})
        text=h.text();self.assertIn("Stage warm warmed by 3.50 K without levelling off; the window's NEG-8 screen passed",text)
        self.assertIn("battery temperature not recorded for this stage",text)
        self.assertIn("stage plateau:",text);self.assertIn("plateau yes; harvest flag no; producer flag no",text)
        rows=h.produce()["window_lines"]["alpha"]
        empty=next(r for r in rows if r["line"]=="battery_temperature" and r["stage_id"]=="empty")
        self.assertTrue(empty["temperature_unmeasured"])
        disagree=next(r for r in rows if r["line"]=="battery_temperature" and r["stage_id"]=="disagree")
        self.assertTrue(disagree["differs_from_harvest_flag"])

    def test_T17_reference_writer_loss_midpoint_counts_and_spare(self):
        h=Harness();a=h.archives["alpha"]
        a.outputs["derived/roster.json"]=d.canonical_json_bytes({"members":[{"run_id":"midpoint","neg8_slot":"midpoint"},
            {"run_id":"spare","spare_slot":"start"}]})
        a.sources["sources/claim-runs/whole-window-verdict.json"]=d.canonical_json_bytes({"excluded_bundles":[{"bundle_id":"midpoint"}]})
        physics=json.loads(a.outputs["derived/neg8-corpus-physics.json"]);physics.update(beyond_cap=["corpus17","corpus18"],
            dropped=[{"bundle_id":"corpus13","reasons":["thermal.os_level_nonzero"]}]);a.outputs["derived/neg8-corpus-physics.json"]=d.canonical_json_bytes(physics)
        h.flag("alpha","member.retried","spare",observed={"status":"succeeded"})
        h.flag("alpha","neg8.corpus_member_dropped","corpus13",observed={"source":"harvest_physics","reason":"thermal.os_level_nonzero"})
        text=h.text();self.assertIn("lost reference midpoint; slot midpoint; reason writer_excluded",text)
        self.assertIn(d.MIDPOINT_SENTENCE,text);self.assertIn("spare spare; slot start; succeeded yes",text)
        self.assertIn("realised references (start, midpoint, end): 3, 1, 3 against planned (3, 1, 3)",text)
        self.assertIn("corpus collected 18; in-window bound 18; deciding clean corpus 12",text)
        self.assertIn("corpus member corpus13 dropped for physics: thermal.os_level_nonzero",text)

    def test_T18_g10_with_and_without_cycles(self):
        h=Harness();h.records[0].g10_codes={"g10.discharged":1};h.records[0].entry.g10_requested=True
        text=h.text();self.assertIn("G10: g10.discharged 1; redraw cycles: not recorded in the block's records",text)
        h.records[0].entry.g10_redraw_cycles=2;self.assertIn("redraw cycles: 2",h.text())

    def test_T19_erratum_pin2_pin4_and_strict_bound_mark(self):
        h=Harness();h.records[1].calibration_bracket={"observed_triggers":[],"recorded_only_triggers":["doubling"],
            "corpus_doubling":{"count":48},"other_session_systematic_sequences":[410]}
        text=h.text();self.assertIn("sealed rule: the bracket read fresh, so no trigger was observed",text)
        self.assertIn("recorded-only triggers: doubling; corpus doubling count: 48",text)
        self.assertIn("alpha: operative bound below 36.46 ms: yes (0.035000 s)",text)
        self.assertIn("beta: operative bound below 36.46 ms: no (0.045000 s)",text)
        h.brackets["alpha"].b_fiducial_s=d.SCREEN_BOUND_S
        self.assertIn("alpha: operative bound below 36.46 ms: no",h.text())
        self.assertFalse(next(r for r in h.produce()["window_lines"]["alpha"] if r["line"]=="below_screen_bound")["below"])

    def test_T21_all_fixed_sentences_match_sealed_plan(self):
        plan=Path("configs/campaigns/v5_claim_25g83/analysis_plan_block5.md").read_text()
        # Markdown wraps sentences across lines; joining whitespace leaves
        # every word, apostrophe and punctuation byte unchanged.
        plan=" ".join(plan.split())
        constants=[d.ATTRIBUTION_SENTENCE,d.GROSS_SENTENCE,d.AGREE_SENTENCE,d.DIFFER_SENTENCE,
            d.DECISION_SENTENCE,d.LOO_SENTENCE,d.MACHINE_BOUNDARY,d.CONDITIONALITY,d.ARM_SENTENCE,
            d.MONITOR_SENTENCE,d.MIDPOINT_SENTENCE,d.TEMPERATURE_SENTENCE,*d.FIXED_SENTENCES.values()]
        for sentence in constants:
            with self.subTest(sentence=sentence):self.assertIn(sentence,plan)

    def test_T24_deterministic_no_path_time_host(self):
        h=Harness();r1=h.produce();r2=h.produce()
        self.assertEqual(d.canonical_json_bytes(r1),d.canonical_json_bytes(r2))
        for released in (False,True):self.assertEqual(d.render_disclosures(r1,released=released),d.render_disclosures(r2,released=released))
        raw=d.canonical_json_bytes(r1).decode()
        for forbidden in ("/synthetic-claim","/synthetic-custody","wall_ns","monotonic_ns","hostname","username","timestamp"):
            self.assertNotIn(forbidden,raw)


class PartDTests(unittest.TestCase):
    def test_T22_ruling_lines_and_required_keys(self):
        h=Harness();row=h.steps["windows"]["alpha"]
        row["stored_verdict"]["conditions"]=[{"condition":"whole_window_bundle_invalid","answered_by":"exclusions"},
            {"condition":"neg8_screen_failed","answered_by":"survivor screen"}]
        restricted=next(c for c,v in d._catalog().codes.items() if v["blinding"]=="RESTRICTED")
        row["member_reasons"]=[{"reason":"whole_window_bundle_invalid","count":2,"all_removed":True,
            "families":["MEMBER_VALIDITY"],"codes":[restricted]}]
        h.flag("alpha",restricted,"removed-member")
        text=h.text();self.assertIn("stored verdict status: failed",text)
        self.assertIn("stored condition whole_window_bundle_invalid; answered by exclusions",text)
        self.assertIn("2 members; every one removed: yes",text)
        self.assertIn("adapter-continuity decision: passed",text)
        self.assertIn("deciding screen used 7 references and 0 spares",text)
        self.assertIn("no analysed window was harvested twice",text)
        self.assertIn("terminal sequence 500; prefix test passed",text)
        self.assertIn("stored verdict's status and NEG-8 bracket decided nothing",text)
        self.assertIn("restricted code",d.render_disclosures(h.produce(),released=False))
        del row["ledger_prefix_test"]
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"disclosure_input_missing:windows.alpha.ledger_prefix_test")

    def test_D4_sensitivity_full_shape_values_and_equality_words(self):
        h=Harness(); harness=PassHarness(); harness.hold_D=True
        h.sens=harness.call()
        rec=h.produce();text=d.render_disclosures(rec,released=True)
        self.assertIn("B_max 0.040000 s attained at ledger sequence 456; T = 500",text)
        self.assertIn("b_op 0.038000 s; b_sens 0.040000 s; values differ from primary",text)
        self.assertIn("b_op 0.045000 s; b_sens 0.045000 s; sensitivity values equal primary values",text)
        self.assertIn("sensitivity outcome equals primary: yes",text)
        self.assertIn("Sensitivity values are never composed into a primary number.",text)
        self.assertEqual(rec["sensitivity"],h.sens)
        self.assertTrue(all(r["restricted"] for r in rec["block_lines"] if r["line"].startswith("sensitivity")))
        h.sens["contrasts"][0]["outcome_equals_primary"]=False
        self.assertIn("sensitivity outcome equals primary: no",h.text())
        del h.sens["reported_cells"][0]["sensitivity"]["h_j"]
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"sensitivity_record_invalid")

    def test_closeout_ratios_copy_operands_and_n(self):
        h=Harness();h.floor["cells"]=[{"cell_id":"minted","absolute":{"n":7},"comparative":{"n_blocks":9}}]
        h.closeout={"independent_ratios":[{"cell_id":"minted","component":"absolute","status":"complete",
            "point_unguarded_floor_j":.5,"corner_widened_unguarded_floor_j":1.2,"ratio":2.4}],
            "comparative_common_mode_ratios":[{"cell_id":"minted","component":"comparative","status":"complete",
            "point_unguarded_floor_j":.2,"common_mode_corner_widened_unguarded_floor_j":.5,"ratio":2.5}],
            "branch":"A","dominance_sentence_licensed":True}
        text=h.text();self.assertIn("R 2.4000; numerator 1.20000 J; denominator 0.50000 J; n = 7",text)
        self.assertIn("R_cm 2.5000; numerator 0.50000 J; denominator 0.20000 J; n = 9",text)
        self.assertIn("D-165 branch A; dominance sentence licensed: yes",text)

    def test_D_malformed_facts_and_reharvest_account(self):
        h=Harness();h.steps["windows"]["alpha"]["deciding_references"]=123.45678
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"disclosure_input_invalid")
        h=Harness();h.steps["no_analysed_window_harvested_twice"]=False
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"disclosure_input_missing:reharvests")
        h.steps["reharvests"]=[{"pack":"alpha","original_pin":"a"*40,"deciding_pin":"b"*40,
            "original_harvest_sha256":"c"*64,"deciding_harvest_sha256":"d"*64,
            "reason":"excluded_reference_in_screen","survivors_before":7,"survivors_after":6}]
        self.assertIn("survivors 7 to 6",h.text())


class PartETests(unittest.TestCase):
    def step_table(self,root):
        from scripts import produce_b5_disclosures as script
        table={}
        for role in script.ROLES:
            raw=d.canonical_json_bytes({"role":role})
            (root/(role+".json")).write_bytes(raw)
            table[role]={"path":role+".json","sha256":hashlib.sha256(raw).hexdigest()}
        path=root/"step-outputs.json";path.write_bytes(d.canonical_json_bytes(table))
        return table,path

    def kwargs(self,h):
        return {"index":h.index,"windows":h.windows,"archives":h.archives,"kept_units":h.kept,"brackets":h.brackets,
            "projections":h.projections,"extraction_reports":h.extraction,"floor_artifact":h.floor,
            "closeout":h.closeout,"claim_verdicts":h.verdicts,"contrast_observations":h.observe,
            "sensitivity":h.sens,"records":h.records,"cell_estimates":h.estimate,"step_results":h.steps}

    def test_T23_script_three_hash_files_stdout_and_digest_refusal(self):
        from scripts import produce_b5_disclosures as script
        h=Harness()
        with tempfile.TemporaryDirectory(prefix="s9-script-") as temporary:
            root=Path(temporary);table,path=self.step_table(root);out=io.StringIO()
            with mock.patch.object(script,"build_disclosure_inputs",return_value=self.kwargs(h)), \
                 mock.patch.object(d,"rebuilt_roster",side_effect=lambda archive,row:json.loads(archive.output_bytes("derived/roster.json"))),redirect_stdout(out):
                rc=script.main(["--window-index",str(root/"index.json"),"--custody",str(root),"--step-outputs",str(path)])
            self.assertEqual(rc,0);lines=out.getvalue().splitlines();self.assertEqual(len(lines),3)
            self.assertEqual(len(list((root/"disclosures").iterdir())),3)
            for line in lines:
                name,digest=line.split();self.assertEqual(name.split(".")[0],digest)
                self.assertEqual(hashlib.sha256((root/"disclosures"/name).read_bytes()).hexdigest(),digest)
                self.assertRegex(line,r"^[0-9a-f]{64}\.(json|unreleased\.txt|released\.txt) [0-9a-f]{64}$")
            for marker in ("10.16000","0.040000","0.10833"):self.assertNotIn(marker,out.getvalue())
            before={p.name:p.read_bytes() for p in (root/"disclosures").iterdir()}
            (root/"projection_alpha.json").write_bytes((root/"projection_alpha.json").read_bytes()+b" ")
            out=io.StringIO()
            with mock.patch.object(script,"build_disclosure_inputs",return_value=self.kwargs(h)) as builder,redirect_stdout(out):
                rc=script.main(["--window-index",str(root/"index.json"),"--custody",str(root),"--step-outputs",str(path)])
            self.assertEqual(rc,2);self.assertEqual(out.getvalue(),"step_output_digest_mismatch\n")
            builder.assert_not_called()
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/"disclosures").iterdir()})

    def test_E_missing_role_traversal_and_symlink_refuse_before_write(self):
        from scripts import produce_b5_disclosures as script
        out=io.StringIO()
        with redirect_stdout(out):rc=script.main(["--archive","not-a-free-argument"])
        self.assertEqual(rc,2);self.assertEqual(out.getvalue(),"disclosure_input_invalid\n")
        with tempfile.TemporaryDirectory(prefix="s9-script-") as temporary:
            root=Path(temporary);table,path=self.step_table(root)
            table.pop("sensitivity");path.write_bytes(d.canonical_json_bytes(table))
            with self.assertRaises(AnalysisRefusal) as cm:script.load_step_outputs(root,path)
            self.assertEqual(cm.exception.code,"disclosure_input_missing:sensitivity")
            table,path=self.step_table(root)
            for bad in ("../outside.json","/outside.json","x/../projection_alpha.json"):
                table["projection_alpha"]["path"]=bad;path.write_bytes(d.canonical_json_bytes(table))
                with self.assertRaises(AnalysisRefusal) as cm:script.load_step_outputs(root,path)
                self.assertEqual(cm.exception.code,"step_output_path_invalid")
            (root/"link.json").symlink_to("/etc/hostname")
            table["projection_alpha"]["path"]="link.json";path.write_bytes(d.canonical_json_bytes(table))
            with self.assertRaises(AnalysisRefusal) as cm:script.load_step_outputs(root,path)
            self.assertEqual(cm.exception.code,"step_output_path_invalid")
            self.assertFalse((root/"disclosures").exists())

    def test_E_repeat_write_is_identical_and_append_only(self):
        from scripts import produce_b5_disclosures as script
        h=Harness();record=h.produce()
        with tempfile.TemporaryDirectory(prefix="s9-repeat-") as temporary:
            root=Path(temporary)
            a=script.write_disclosures(root,record);b=script.write_disclosures(root,record)
            self.assertEqual(a,b);self.assertEqual(len(list((root/"disclosures").iterdir())),3)

    def test_E_production_callables_with_real_issuer_and_engine(self):
        from scripts import produce_b5_disclosures as script
        from tests.b5_analysis import fixtures_s5 as s5,fixtures_s8 as s8
        from joulewise import whole_window as ww
        from joulewise import cli
        fixture=s8.synthetic_pack();h=Harness();loaded=s5.arithmetic_inputs([3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7])
        sentinel_link={"block_id":loaded.manifest["contrasts"][0]["block_ids"][0],
            "start_entry_id":"sentinel-start","end_entry_id":"sentinel-end"}
        loaded=replace(loaded,manifest={**loaded.manifest,"sentinel_links":[sentinel_link]})
        h.windows["alpha"].claim_runs_root=fixture.root
        for w in h.windows.values():w.archive_root=fixture.root
        kept=replace(fixture.kept,window=NS(**{**vars(fixture.kept.window),"claim_runs_root":fixture.root}))
        setup={"spec":fixture.spec,"kept":kept,"bracket":h.brackets["alpha"],
            "row":{"evaluation_basis":{"sha256":"c"*64}},"selection_sha256":"a"*64,"prompt_pin_sha256":"b"*64}
        contexts=[]
        def context(*args,**kwargs):
            value=ww.ArchiveContext(fixture.root,window_bracket={"b_fiducial_s":.04})
            contexts.append(value);return value
        def load(*args,**kwargs):
            view=kwargs["kept_units"]
            return replace(loaded,kept_units=view,kept_quads=view.cells)
        built={"archives":h.archives,"kept_units":loaded.kept_units,"brackets":h.brackets,"archive_contexts":{}}
        with tempfile.TemporaryDirectory(prefix="s9-callables-") as temporary:
            root=Path(temporary);manifest=root/"manifest.json"
            manifest_raw=d.canonical_json_bytes(loaded.manifest);manifest.write_bytes(manifest_raw)
            values={"floor_artifact":h.floor,"extraction_alpha":h.extraction["alpha"],"extraction_beta":h.extraction["beta"],
                "projection_alpha":h.projections["alpha"],"projection_beta":h.projections["beta"],"closeout":h.closeout,
                "claim_verdicts":{**h.verdicts,"inputs":{"analysis_manifest":{"file_sha256":hashlib.sha256(manifest_raw).hexdigest()}}},
                "sensitivity":h.sens,"step_results":h.steps}
            with mock.patch.object(script,"load_window_index",return_value=h.index), \
                 mock.patch.object(script,"open_attempt_record",side_effect=h.records), \
                 mock.patch.object(script,"select_analysed_attempts",return_value=h.windows), \
                 mock.patch.object(script,"open_archive",side_effect=lambda window,**kw:h.archives[window.pack]), \
                 mock.patch.object(script,"_floor_setup",return_value=setup), \
                 mock.patch.object(script,"_evidence_roots",return_value={}), \
                 mock.patch.object(inputs_module:=script.inputs,"block5_claim_gate_inputs",return_value=built), \
                 mock.patch.object(inputs_module,"archived_verdict_row",return_value={}), \
                 mock.patch.object(script,"build_context",side_effect=context), \
                 mock.patch.object(cli,"validate_bundle",return_value=()):
                kwargs=script.build_disclosure_inputs(root/"index.json",values,{"finalized_manifest":manifest,"floor_artifact":root/"floor.json"})
                with s8.pack_seams(fixture):
                    cell=next(iter(kept.cells.values()))
                    remove=[u.unit_id for u in cell.kept["repeat"]][1:]
                    view=kept.without_units(cell.cell_id,remove,label="battery-assist")
                    result=kwargs["cell_estimates"]("alpha",view,None)
                    self.assertIn(fixture.spec["reported_energy_cells"][0]["cell_id"],result["normalized_rows"])
                    self.assertEqual(len(result["normalized_rows"][fixture.spec["reported_energy_cells"][0]["cell_id"]]),33)
                with s5.arithmetic_seams(loaded),mock.patch.object(script.engine,"load_analysis_inputs",side_effect=load), \
                     mock.patch.object(script.engine,"_prepare_contrast",wraps=script.engine._prepare_contrast) as prepare:
                    primary=kwargs["contrast_observations"](loaded.kept_units)
                    restored=loaded.kept_units.with_units_restored("decode",[loaded.kept_units.cell("decode").dropped[0].unit_id],label="load-correlated")
                    changed=kwargs["contrast_observations"](restored)
                self.assertEqual(prepare.call_count,4)
                for call in prepare.call_args_list:
                    self.assertEqual(call.args[2],{sentinel_link["block_id"]:("sentinel-start","sentinel-end")})
                self.assertEqual(len(primary["decode"]),9);self.assertEqual(len(changed["decode"]),10)
                self.assertEqual(len(contexts),3);self.assertEqual(len({id(c) for c in contexts}),3)


class ReviewFindingTests(unittest.TestCase):
    def test_G1_primary_contrast_copies_verdict_fields(self):
        h=Harness();h.add_contrast()
        est=h.verdicts["contrasts"][0]["estimator"]
        # These fields deliberately differ from the observation recomputation;
        # the primary line must copy the verdict's metrology values unchanged.
        est.update(SE_total=.123456,t_critical_95=7.891,
            metrology_aware_CI95={"lower":1.23456,"upper":4.56789})
        record=h.produce();row=items(record,"contrasts","primary_contrast")[0]
        self.assertEqual(row["estimator"],est)
        self.assertEqual(row["text"],
            "decode: 3.00000 J; s_d = 0.19365 J; se = 0.123456 J; "
            "t* = 7.891; interval [1.23456, 4.56789] J")
        self.assertIn(row["text"],d.render_disclosures(record,released=True))

    def test_G1_observations_differ_refuses_before_any_line(self):
        for change in ("one_ulp_delta","missing_block","estimate","s_d","n"):
            with self.subTest(change=change):
                h=Harness();h.add_contrast();h.add_contrast((1.,2.,4.),removed=(),cid="prefill")
                rows=h.observations["prefill"];est=h.verdicts["contrasts"][1]["estimator"]
                if change=="one_ulp_delta":
                    rows[-1]["d_j"]=math.nextafter(rows[-1]["d_j"],math.inf)
                    recomputed=d._paired_values(rows)
                    self.assertEqual(recomputed["mean_j"].hex(),est["estimate"].hex())
                    self.assertNotEqual(recomputed["s_d"].hex(),est["s_d"].hex())
                elif change=="missing_block":rows.pop()
                elif change=="n":est["n"]+=1
                else:est[change]=math.nextafter(est[change],math.inf)
                result={"cells":[],"floors":[],"contrasts":[],"fixed_sentences":[],
                    "window_lines":{p:[] for p in d.PACK_ORDER}}
                before=deepcopy(result)
                with self.assertRaises(AnalysisRefusal) as cm:
                    d._energy_lines(result,h.windows,h.archives,h.kept,h.projections,h.extraction,
                        h.floor,h.verdicts,h.observe,h.estimate,{p:[] for p in d.PACK_ORDER})
                self.assertEqual(cm.exception.code,"contrast_observations_differ_from_verdict")
                self.assertEqual(result,before)

    def test_G3_first_clean_window_uses_time_and_prints_pack_order(self):
        h=Harness();h.add_contrast();quad=h.kept["gamma"].cell("decode").kept["quad"][0]
        h.windows["gamma"].record.entry.t0_epoch_s=999
        h.archives["gamma"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":{
            quad.run_ids[1]:{"rho":.8,"rail_delta_J":480,"machine":{"delta_J":600}},
            quad.run_ids[2]:{"rho":.9,"rail_delta_J":540,"machine":{"delta_J":600}}}})
        h.archives["beta"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":{
            "beta-inside":{"rho":.85,"rail_delta_J":510,"machine":{"delta_J":600}},
            "beta-outside":{"rho":.95,"rail_delta_J":570,"machine":{"delta_J":600}}}})
        record=h.produce()
        gamma=next(r for r in record["window_lines"]["gamma"] if r["line"]=="machine_summary")
        beta=next(r for r in record["window_lines"]["beta"] if r["line"]=="machine_summary")
        for row in (gamma,beta):
            self.assertEqual(row["model"],"qwen3-8b")
            self.assertEqual(row["central_band"],{"pack":"gamma","plan_id":h.windows["gamma"].plan_id,
                "attempt":1,"lower":.8,"upper":.9})
        self.assertNotIn("member windows inside",gamma["text"])
        self.assertIn("1 of 2 member windows inside the first clean window's band",beta["text"])
        text=d.render_disclosures(record,released=True)
        self.assertLess(text.index(d.MACHINE_BOUNDARY),text.index(beta["text"]))
        self.assertLess(text.index(beta["text"]),text.index(gamma["text"]))
        self.assertNotIn("t0_epoch_s",d.canonical_json_bytes(record).decode("utf-8"))

    def test_G4_computed_p42_has_no_cross_window_line(self):
        h=Harness();h.add_contrast(cid="prefill-p2048")
        target=h.projections["alpha"]["cells"][0]
        target["phase"]="prefill"
        p42=deepcopy(target);p42["cell_id"]="reported-prefill-p42"
        cell=h.kept["alpha"].cell("synthetic");cid="synthetic-p42"
        excluded=replace(cell,cell_id=cid,target=False,
            kept={s:tuple(replace(u,cell_id=cid) for u in units) for s,units in cell.kept.items()},
            dropped=tuple(replace(u,cell_id=cid) for u in cell.dropped))
        h.kept["alpha"]=replace(h.kept["alpha"],cells={"synthetic":cell,cid:excluded})
        h.projections["alpha"]["cells"].append(p42)
        self.assertFalse(d._projection_cell(h.kept["alpha"],p42).target)
        record=h.produce()
        self.assertIn(p42["cell_id"],[r["cell_id"] for r in items(record,"cells","reported_cell")])
        checks=items(record,"cells","cross_window")
        self.assertEqual([r["cell_id"] for r in checks],[target["cell_id"]])


class CounterfactualTests(unittest.TestCase):
    def test_R8_removed_meter_member_controls_printed_median(self):
        h=Harness((6,));removed=h.rows[5]["member"]["bundle_id"]
        members={run:{"rho":rho,"rail_delta_J":600*rho,"machine":{"delta_J":600}}
            for run,rho in [(h.rows[0]["member"]["bundle_id"],.5),(h.rows[1]["member"]["bundle_id"],.9),(removed,.1)]}
        h.archives["alpha"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":members})
        self.assertIn("median 0.5000; range 0.1000 to 0.9000",h.text())

    def test_B8_dirty_other_model_prevents_central_band(self):
        h=Harness();h.add_contrast();cell=h.kept["gamma"].cell("decode")
        a,b=cell.kept["quad"][0].run_ids[:2]
        h.flag("gamma","meter.battery_activity",a)
        h.archives["gamma"].withheld["withheld/meter.json"]=d.canonical_json_bytes({"members":{
            a:{"rho":.8,"rail_delta_J":480,"machine":{"delta_J":600}},
            b:{"rho":.9,"rail_delta_J":540,"machine":{"delta_J":600}}}})
        rows=h.produce()["window_lines"]["gamma"]
        summary=next(r for r in rows if r["line"]=="machine_summary" and r["model"]=="qwen3-8b")
        self.assertNotIn("central_band",summary)

    def test_production_projection_window_mismatch_refuses(self):
        h=Harness();h.projections["alpha"].update(mode="production",window={"pack":"alpha","plan_id":"wrong-window",
            "attempt":1,"harvest_pin":"a"*40},exclusions_sha256="1"*64)
        with self.assertRaises(AnalysisRefusal) as cm:h.produce()
        self.assertEqual(cm.exception.code,"disclosure_input_invalid")


class PinnedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One archived real-writer/pinned-harvest fixture, cached by S3B.
        from tests.b5_analysis import fixtures_s3b as s3b
        from tests.b5_analysis.fixtures_s1 import s0_planned
        from joulewise.b5_analysis.kept_units import load_kept_units
        cls.archive=s3b.original_handle(s3b.cached("BETA_STD"))
        cls.kept=load_kept_units(cls.archive,sealed_catalog_sha256=d.SealPins.load().sealed["catalog_sha256"],
                                planned_units=s0_planned())

    def test_real_pinned_archive_disclosure_sources(self):
        h=Harness();h.archives["beta"]=self.archive;h.windows["beta"]=self.archive.window
        h.kept["beta"]=self.kept;h.records[1]=self.archive.window.record;h.index.entries=tuple(r.entry for r in h.records)
        real_roster=d.rebuilt_roster
        real_withheld=self.archive.withheld_bytes
        # S0 exported this fixture with meter_joins disabled and no meter
        # record/flag. Only that absent fixture capability uses a byte seam.
        with mock.patch.object(d,"rebuilt_roster",side_effect=lambda a,row:
                real_roster(a,row) if a is self.archive else json.loads(a.output_bytes("derived/roster.json"))), \
             mock.patch.object(self.archive,"withheld_bytes",side_effect=lambda name:
                b'{"members":{}}' if name=="withheld/meter.json" else real_withheld(name)):
            record=d.produce_disclosures(h.index,h.windows,h.archives,h.kept,h.brackets,h.projections,
                h.extraction,h.floor,h.closeout,h.verdicts,h.observe,h.sens,records=h.records,
                cell_estimates=h.estimate,step_results=h.steps)
        text=d.render_disclosures(record,released=True)
        self.assertIn("beta: realised references",text)
        self.assertIn("beta: NEG-8 allowance source survivor_rescreen",text)
        raw=d.canonical_json_bytes(record).decode()
        self.assertNotIn(str(self.archive.window.archive_root),raw)
        self.assertNotIn(str(self.archive.window.claim_runs_root),raw)


class FixRegressionTests(unittest.TestCase):
    """All counterfactual energies, shares, bounds and temperatures are made up."""

    @staticmethod
    def empty_record():
        return {name: [] for name in ('cells','floors','contrasts','block_lines','fixed_sentences')} | {
            'window_lines': {p: [] for p in d.PACK_ORDER}}

    def machine(self, h):
        record = self.empty_record()
        with mock.patch.object(d, 'rebuilt_roster', side_effect=lambda a, r: json.loads(a.output_bytes('derived/roster.json'))):
            d._machine_lines(record,h.windows,h.archives,h.kept,h.projections,
                {p:d._flags(h.archives[p],d._catalog()) for p in d.PACK_ORDER})
        return record

    def energy_lines(self, h):
        record = self.empty_record()
        with mock.patch.object(d, 'rebuilt_roster', side_effect=lambda a, r: json.loads(a.output_bytes('derived/roster.json'))):
            d._energy_lines(record,h.windows,h.archives,h.kept,h.projections,h.extraction,
                h.floor,h.verdicts,h.observe,h.estimate,
                {p:d._flags(h.archives[p],d._catalog()) for p in d.PACK_ORDER})
        return record

    def test_F1_floor_meter_models_and_gamma_band(self):
        h=Harness(); h.add_contrast((3.,3.,3.),removed=())
        shares=(.78,.80,.81,.79,.82,.80,.77,.81,.80,.83)
        science=[r['member']['bundle_id'] for r in h.rows[:10]]
        members={run:{'rho':rho,'rail_delta_J':rho*600.,'machine':{'delta_J':600.}}
                 for run,rho in zip(science,shares)}
        aux=[f'synthetic-aux-{i:02d}' for i in range(25)]
        roster=[{'run_id':run,'kind':'science'} for run in science]
        for i,run in enumerate(aux):
            config='configs/synthetic-aux.json' if i%2 else 'synthetic-aux.json'
            roster.append({'run_id':run,'kind':'auxiliary','config_path':config})
            path=('sources/repo/'+config if config.startswith('configs/') else
                  f'sources/repo/configs/campaigns/{h.windows["alpha"].pack_id}/'+config)
            h.archives['alpha'].sources[path]=d.canonical_json_bytes({'model':{'name':'Qwen2.5-1.5B-Instruct-4bit'}})
            members[run]={'rho':.40,'rail_delta_J':40.,'machine':{'delta_J':100.}}
        h.archives['alpha'].outputs['derived/roster.json']=d.canonical_json_bytes({'members':roster})
        h.archives['alpha'].withheld['withheld/meter.json']=d.canonical_json_bytes({'members':members})
        units=h.kept['gamma'].cell('decode').kept['quad']
        h.archives['gamma'].withheld['withheld/meter.json']=d.canonical_json_bytes({'members':{
            u.run_ids[0]:{'rho':rho,'rail_delta_J':rho*600.,'machine':{'delta_J':600.}}
            for u,rho in zip(units,(.40,.80,.84))}})
        record=self.machine(h)
        summaries={r['model']:r for r in record['window_lines']['alpha'] if r['line']=='machine_summary'}
        row=summaries['qwen3-1p7b']
        for key,value in {'median':.80,'minimum':.77,'maximum':.83,'q25':.7925,'q75':.81,'spread':.075}.items():
            self.assertAlmostEqual(row[key],value,places=13)
        self.assertIn('; consistent;',row['text'])
        self.assertEqual((row['central_band']['lower'],row['central_band']['upper']),(.77,.83))
        aux_rows=[r for r in record['window_lines']['alpha'] if r['line']=='machine_member' and r['run_id'] in aux]
        self.assertEqual(len(aux_rows),25)
        self.assertTrue(all(r['model']=='Qwen2.5-1.5B-Instruct-4bit' for r in aux_rows))
        self.assertEqual(summaries['Qwen2.5-1.5B-Instruct-4bit']['median'],.40)
        gamma=next(r for r in record['window_lines']['gamma'] if r['line']=='machine_summary')
        self.assertIn('1 of 3 member windows inside',gamma['text'])
        self.assertEqual(gamma['central_band'],row['central_band'])

    def test_F1_unplaced_and_unreadable_auxiliary_refuse(self):
        for member,config in ((None,None),({'run_id':'unplaced','kind':'auxiliary'},None),
                ({'run_id':'unplaced','kind':'auxiliary','config_path':'missing.json'},None),
                ({'run_id':'unplaced','kind':'auxiliary','config_path':'bad.json'},{})):
            h=Harness()
            h.archives['alpha'].outputs['derived/roster.json']=d.canonical_json_bytes({'members':[] if member is None else [member]})
            if config is not None:
                h.archives['alpha'].sources[f'sources/repo/configs/campaigns/{h.windows["alpha"].pack_id}/bad.json']=d.canonical_json_bytes(config)
            h.archives['alpha'].withheld['withheld/meter.json']=d.canonical_json_bytes({'members':{
                'unplaced':{'rho':.8,'rail_delta_J':80.,'machine':{'delta_J':100.}}}})
            with self.subTest(member=member), self.assertRaisesRegex(AnalysisRefusal,'^disclosure_input_missing:meter_member_model$'):
                self.machine(h)

    def test_F2_pass_wire_and_acceptance_member_bmax(self):
        for sequence in (456,None):
            from joulewise.b5_analysis.bracket import BMax
            h=Harness(); h.sens=PassHarness().call(BMax(.04,sequence,500))
            record=h.produce(); text=d.render_disclosures(record,released=True)
            self.assertEqual(record['sensitivity'],h.sens)
            phrase=('attained at ledger sequence 456' if sequence is not None else
                    'attained by a member of the acceptance (no ledger sequence)')
            self.assertIn(phrase,text)
            for line in ('sensitivity_reported','sensitivity_floor','sensitivity_contrast'):
                rows=items(record,'block_lines',line)
                self.assertTrue(rows)
                for row in rows:
                    if row['record'].get('status')!='refused':
                        self.assertTrue(row['text'].endswith('; not below primary: yes'))
            for name in ('reported_cells','floor_cells','contrasts'):
                row=next(r for r in h.sens[name] if r.get('status')!='refused')
                row['not_below_primary']=False
            record=h.produce()
            for line in ('sensitivity_reported','sensitivity_floor','sensitivity_contrast'):
                self.assertTrue(any(r['text'].endswith('; not below primary: no') for r in items(record,'block_lines',line)))

    def test_F2_monotonicity_required_bool_and_sequence_range(self):
        for name in ('reported_cells','floor_cells','contrasts'):
            for value in ('absent',0,1,'yes',None):
                record=deepcopy(sensitivity()); row=next(r for r in record[name] if r.get('status')!='refused')
                if value=='absent': row.pop('not_below_primary')
                else: row['not_below_primary']=value
                with self.subTest(name=name,value=value), self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_record_invalid$'):
                    d._validate_sensitivity(record)
        for seq in (0,501,True,'456',-1):
            record=deepcopy(sensitivity()); record['b_max']['attained_by_sequence']=seq
            with self.subTest(sequence=seq), self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_record_invalid$'):
                d._validate_sensitivity(record)
        for seq in (1,500,None):
            record=deepcopy(sensitivity()); record['b_max']['attained_by_sequence']=seq
            d._validate_sensitivity(record)
        record=deepcopy(sensitivity())
        next(r for r in record['reported_cells'] if r['status']=='refused')['not_below_primary']=True
        with self.assertRaisesRegex(AnalysisRefusal,'^sensitivity_record_invalid$'):
            d._validate_sensitivity(record)

    def test_F3_screen_bound_unreleased_identity(self):
        records=[]
        for bound in (.035,.045):
            h=Harness(); h.brackets['alpha'].b_fiducial_s=bound; record=self.empty_record()
            with mock.patch.object(d,'rebuilt_roster',side_effect=lambda a,r:json.loads(a.output_bytes('derived/roster.json'))):
                d._structure_lines(record,h.index,h.records,h.windows,h.archives,h.kept,h.brackets,
                    h.projections,h.extraction,d._catalog(),{p:[] for p in d.PACK_ORDER})
            records.append(record)
        self.assertEqual(*(d.render_disclosures(r,released=False) for r in records))
        self.assertNotEqual(*(d.render_disclosures(r,released=True) for r in records))
        for record,bound in zip(records,(.035,.045)):
            row=next(r for r in record['window_lines']['alpha'] if r['line']=='below_screen_bound')
            self.assertEqual(row['b_op_s'],bound); self.assertEqual(row['below'],bound<d.SCREEN_BOUND_S)
            self.assertEqual(sum(r['line']=='below_screen_bound' for rs in record['window_lines'].values() for r in rs),3)

    def test_F3_loo_unreleased_identity_and_sorted_trigger_rows(self):
        records=[]
        for count in (0,1,2):
            h=Harness(); h.add_contrast((3.,3.,3.),removed=())
            h.verdicts['contrasts'][0]['loo']['rows']=[
                {'omitted_block_id':f'decode-b{n:02d}','estimate':estimate,
                 'influence_triggers':['estimate_magnitude'] if i<count else []}
                for i,(n,estimate) in enumerate(((3,2.),(1,1.5)))]
            records.append(self.energy_lines(h))
        self.assertEqual(len({d.render_disclosures(r,released=False) for r in records}),1)
        self.assertEqual(len({d.render_disclosures(r,released=True) for r in records}),3)
        for count,record in enumerate(records):
            rows=items(record,'contrasts','loo_magnitude')
            self.assertEqual(len(rows),1)
            expected=sorted([{'block_number':str(n),'movement_j':abs(estimate-3.)}
                             for n,estimate in ((3,2.),(1,1.5))[:count]],key=lambda r:int(r['block_number']))
            self.assertEqual(rows[0]['rows'],expected)
            if not count:self.assertEqual(rows[0]['text'],'decode: no leave-one-out row raised the magnitude trigger')
            else:
                self.assertEqual(rows[0]['text'],'decode: '+' '.join(d.LOO_SENTENCE.replace('quad k','quad '+r['block_number']).replace('X',f"{r['movement_j']:.5f}") for r in expected))

    def test_F3_restricted_flag_presence_unreleased_identity(self):
        records=[]
        catalog=d._catalog()
        code=next(code for code,spec in catalog.codes.items() if spec['blinding']=='RESTRICTED')
        for present in (False,True):
            h=Harness()
            if present:h.flag('alpha',code,h.rows[0]['member']['bundle_id'])
            record=self.empty_record()
            with mock.patch.object(d,'rebuilt_roster',side_effect=lambda a,r:json.loads(a.output_bytes('derived/roster.json'))):
                d._structure_lines(record,h.index,h.records,h.windows,h.archives,h.kept,h.brackets,
                    h.projections,h.extraction,catalog,{p:d._flags(h.archives[p],catalog) for p in d.PACK_ORDER})
            records.append(record)
        self.assertEqual(*(d.render_disclosures(r,released=False) for r in records))
        self.assertNotEqual(*(d.render_disclosures(r,released=True) for r in records))
        for record,count in zip(records,(0,1)):
            row=next(r for r in record['window_lines']['alpha'] if r['line']=='flag_count' and r['code']==code)
            self.assertEqual(row['count'],count); self.assertTrue(row['restricted'])

    def test_M6_prefill_and_decode_token_denominators(self):
        h=Harness()
        for cid in ('prefill','decode'):h.add_contrast((2.1,2.3,1.9),cid=cid,removed=())
        record=self.energy_lines(h)
        for row in items(record,'contrasts','magnitude_per_token'):
            cid=row['contrast_id']; denom=2048 if cid=='prefill' else 512
            verdict=next(v for v in h.verdicts['contrasts'] if v['contrast_id']==cid)
            self.assertEqual(row['denominator'],denom)
            self.assertEqual(row['value_j'],verdict['estimator']['estimate']/denom)
            self.assertEqual(row['metrology'],{k:v/denom for k,v in verdict['estimator']['metrology_aware_CI95'].items()})
            self.assertEqual(row['decision'],{k:v/denom for k,v in verdict['deterministic_bounds']['decision_interval'].items()})
            self.assertIn('J per '+('prompt' if cid=='prefill' else 'output')+' token',row['text'])

    def test_M7_negative_decision_near_end(self):
        h=Harness(); h.add_contrast((-3.,-3.,-3.),removed=())
        verdict=h.verdicts['contrasts'][0]; verdict['floor']['active_floor_j']=1.2
        for upper,appended in ((-1.,True),(-1.3,False)):
            verdict['deterministic_bounds']['decision_interval']={'lower':-4.,'upper':upper}
            row=items(self.energy_lines(h),'contrasts','decision_floor')[0]
            self.assertIn(f'near end {-upper:.5f} J',row['text'])
            self.assertEqual(d.DECISION_SENTENCE in row['text'],appended)

    def test_M19_beta_cross_window_uses_b_side(self):
        h=Harness(); primary=h.projections['alpha']['cells'][0]
        beta=deepcopy(primary); beta['cell_id']='synthetic-beta'; beta['mean_j']=13.; beta['interval']['h_j']=.1
        h.projections['beta']['cells']=[beta]
        h.kept['beta']=replace(h.kept['beta'],cells=h.kept['alpha'].cells)
        h.add_contrast((3.,3.,3.),removed=(),sides=((10.,13.),(10.02,13.02),(9.98,12.98)))
        rows=items(self.energy_lines(h),'cells','cross_window')
        self.assertEqual({r['pack'] for r in rows},{'alpha','beta'})
        # Own exact df=2 quantile and arithmetic, independent of the producer.
        for row in rows:
            sides=[r['a_mean_j' if row['pack']=='alpha' else 'b_mean_j'] for r in h.observations['decode']]
            F=primary['mean_j'] if row['pack']=='alpha' else beta['mean_j']
            hF=primary['interval']['h_j'] if row['pack']=='alpha' else .1
            G=sum(sides)/len(sides); hG=4.302652729749464*statistics.stdev(sides)/math.sqrt(3)
            delta=G-F; agree=abs(delta)<=math.sqrt(hG*hG+hF*hF)
            self.assertEqual(row['G_j'],G); self.assertAlmostEqual(row['h_G_j'],hG,places=13)
            self.assertEqual(row['delta_j'],delta); self.assertEqual(row['agree'],agree)
            self.assertEqual(row['text'],(d.AGREE_SENTENCE if agree else d.DIFFER_SENTENCE).replace('Δ',f'{delta:.5f}'))
        self.assertTrue(next(r for r in rows if r['pack']=='beta')['agree'])

    def test_M27_negative_machine_minus_rail_outside_band(self):
        h=Harness(); science=[r['member']['bundle_id'] for r in h.rows[:3]]
        members={run:{'rho':rho,'rail_delta_J':rail,'machine':{'delta_J':600.}}
                 for run,rho,rail in zip(science,(.78,.82,.90),(468.,492.,700.))}
        h.flag('alpha','meter.drops_excess',science[2])
        h.archives['alpha'].withheld['withheld/meter.json']=d.canonical_json_bytes({'members':members})
        record=self.machine(h)
        bad=next(r for r in record['window_lines']['alpha'] if r['line']=='machine_member' and r['run_id']==science[2])
        self.assertFalse(bad['plausible']); self.assertIn('outside the hard band',bad['text'])
        self.assertIn('meter.drops_excess',bad['meter_flags'])
        summary=next(r for r in record['window_lines']['alpha'] if r['line']=='machine_summary')
        self.assertAlmostEqual(summary['spread'],(.82-.78)/.80)
        self.assertEqual((summary['central_band']['lower'],summary['central_band']['upper']),(.78,.82))
        self.assertEqual(summary['maximum'],.90)

    def test_M28_temperature_rise_strict_three_kelvin(self):
        for rise,flagged in ((3.2,True),(3.0,False)):
            h=Harness(); archive=h.archives['alpha']; record=self.empty_record()
            archive.sources['sources/claim-runs/campaign_manifests/synthetic.json']=d.canonical_json_bytes({
                'stage_id':'synthetic','members':[{}],'battery_temperature_readings':[
                    {'temperature_centi_c':3000},{'temperature_centi_c':3000+round(rise*100)}]})
            d._temperature_lines(record,'alpha',archive,[],'passed',{'members':[]})
            row=next(r for r in record['window_lines']['alpha'] if r['line']=='battery_temperature')
            self.assertEqual(row['producer_flag'],flagged); self.assertFalse(row['harvest_flag']); self.assertFalse(row['plateau'])
            self.assertEqual(bool([r for r in record['window_lines']['alpha'] if r['line']=='temperature_disagreement']),flagged)


if __name__ == "__main__": unittest.main()


class FlagBlindingTests(unittest.TestCase):
    """S10 joined run, step 11: the pinned harvest writes diagnostic.s1_structural's
    precheck_counts flag RESTRICTED over the code's STRUCTURE default, as the sealed
    catalog says; the producer refused every window flag_blinding_differs_from_catalog."""

    def test_a_flag_may_tighten_its_code_blinding_never_loosen_it(self):
        catalog=d._catalog()
        structure=next(code for code,entry in sorted(catalog.codes.items()) if entry['blinding']=='STRUCTURE')
        restricted=next(code for code,entry in sorted(catalog.codes.items()) if entry['blinding']=='RESTRICTED')
        def archive(rows):
            value=FakeArchive();value.outputs['derived/flags.jsonl']=b''.join(d.canonical_json_bytes(r)+b'\n' for r in rows)
            return value
        def row(code,word):
            return {'code':code,'family':catalog.codes[code]['family'],'blinding':word,'scope':{'level':'window','run_id':None}}
        rows=d._flags(archive([row(structure,'STRUCTURE'),row(structure,'RESTRICTED')]),catalog)
        self.assertEqual(len(rows),2)
        self.assertEqual(d._code(structure,catalog,rows)['blinding'],'RESTRICTED')
        self.assertEqual(d._code(structure,catalog,rows[:1])['blinding'],'STRUCTURE')
        with self.assertRaisesRegex(AnalysisRefusal,'^flag_blinding_differs_from_catalog$'):
            d._flags(archive([row(restricted,'STRUCTURE')]),catalog)
        with self.assertRaisesRegex(AnalysisRefusal,'^flag_blinding_differs_from_catalog$'):
            d._code(restricted,catalog,[row(restricted,'STRUCTURE')])
