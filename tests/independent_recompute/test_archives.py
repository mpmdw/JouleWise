"""S12-S14: selection, complete raw archives, independence, and CLI failures."""
import ast
import contextlib
import io
import itertools
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile
import unittest
from .support import (assert_values_agree, recompute as r, SCRIPT, full_pack, remove_member, dump, run_cli, bundle)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_S12_kept_unit_bookkeeping(self):
        alpha = full_pack(self.root,"ALPHA")
        gamma = full_pack(self.root,"GAMMA")
        beta = full_pack(self.root,"BETA")
        archives = {"ALPHA":alpha,"BETA":beta,"GAMMA":gamma}
        rc,original,_ = run_cli(archives,self.root/"before.json")
        self.assertEqual(rc,0)
        remove_member(alpha,"fixture-decode-b03-b2")
        remove_member(gamma,"fixture-decode-b03-b2")
        _,after,_ = run_cli(archives,self.root/"after.json")
        cid="df-ph-decode-qwen3-1p7b"
        self.assertEqual(after["reported_cells"][cid]["n_b"],9)
        self.assertEqual(after["floors"]["Qwen3-1.7B-4bit/decode/comparative"]["n"],9)
        contrast="ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"
        self.assertEqual(after["contrasts"][contrast]["n"],9)
        self.assertNotIn("fixture-decode-b03",after["contrasts"][contrast]["kept_quads"])
        path=alpha/"derived/exclusions.json"
        exclusions=json.loads(path.read_text())
        next(c for c in exclusions["cells"] if c["cell_id"]==cid)["kept_units"]["quad"].append("fixture-decode-b03")
        dump(path,exclusions)
        _,stale,_=run_cli(archives,self.root/"stale.json")
        self.assertEqual(stale["reported_cells"][cid]["n_b"],9)
        self.assertTrue(any(f["code"]=="kept_units_disagree" for f in stale["flags"]))
        remove_member(alpha,"neg8-window-start-r1")
        _,reference_removed,_ = run_cli(archives,self.root/"reference.json")
        self.assertEqual(after["reported_cells"],reference_removed["reported_cells"])
        self.assertEqual(after["floors"],reference_removed["floors"])
        path=alpha/"sources/claim-runs/fixture-decode-b04-a1/metadata.json"
        metadata=json.loads(path.read_text()); metadata["model"]["name"]="Qwen3-8B-4bit";dump(path,metadata)
        _,wrong,_=run_cli(archives,self.root/"wrong.json")
        self.assertEqual(wrong["reported_cells"][cid]["n_b"],8)
        self.assertTrue(any(f["code"]=="kept_unit_identity_mismatch" for f in wrong["flags"]))
        self.assertNotIn("fixture-decode-b04",wrong["reported_cells"][cid]["kept_units"]["quad"])
        kept=[i for i in range(1,11) if i not in (3,4)]
        expected=.2*statistics.fmean(10+.1*i for i in range(1,11))+.8*statistics.fmean(10+.1*i+.2+.025*i for i in kept)
        assert_values_agree(self, wrong["reported_cells"][cid]["mean_j"], expected)

    def test_S13_full_three_pack_closed_form(self):
        archives={p:full_pack(self.root,p) for p in ("ALPHA","BETA","GAMMA")}
        _,out,_=run_cli(archives,self.root/"all.json",("--member-detail",))
        # This rail-only fixture has no meter; each absent machine line is disclosed.
        self.assertEqual([(f["pack"], f["code"]) for f in out["flags"]],
                         [(p, "meter_absent") for p in ("ALPHA", "BETA", "GAMMA")])
        for pack,model_tag,model,extra in (("ALPHA","qwen3-1p7b",r.MODELS["ALPHA"],0.),
                                         ("BETA","qwen3-8b",r.MODELS["BETA"],2.)):
            for arm,phase in (("decode","decode"),("prefill-p2048","prefill")):
                cid=f"df-ph-{arm}-{model_tag}"
                repeats=[10+extra+.1*i for i in range(1,11)]
                means=[10+extra+.1*i+.2+.025*i for i in range(1,11)]
                expected=statistics.fmean(repeats+[v for mean in means for v in [mean]*4])
                cell=out["reported_cells"][cid]
                assert_values_agree(self, cell["mean_j"], expected)
                self.assertEqual((cell["n_r"],cell["n_b"],cell["n_bundles"]),(10,10,50))
                h=2.262157162798205*math.sqrt(.04*statistics.variance(repeats)/10+.64*statistics.variance(means)/10)
                kind=.2*statistics.fmean(2*v*.0453 for v in repeats)+.8*statistics.fmean(
                    2*v*.0453 for i in range(1,11) for v in [10+extra+.1*i+.2]*2+[10+extra+.1*i+.2+.05*i]*2)
                allowance=out["windows"][pack]["neg8"]["allowance_j"]
                assert_values_agree(self, cell["interval"]["kind_averages_j"][0], kind)
                assert_values_agree(self, cell["lower_j"], expected-h-kind-allowance/2)
                assert_values_agree(self, cell["per_token"]["j_per_token"], expected/(512 if phase=="decode" else 2048))
                for form in ("absolute","comparative"):
                    if form=="absolute":
                        values=repeats; widths=[2*v*.0453 for v in values]
                    else:
                        values=[.05*i for i in range(1,11)]
                        widths=[2*.045*(.05*i)+.0006*(2*(10+extra+.1*i+.2)+.05*i) for i in range(1,11)]
                    def direct_floor(v):
                        mean=statistics.fmean(v)
                        deviations=[x-mean for x in v] if form=="absolute" else v
                        pred=2.262*statistics.stdev(deviations)*math.sqrt(1.1)
                        if form=="comparative":pred+=abs(mean)
                        return max(max(abs(x) for x in deviations),pred)
                    point=direct_floor(values)
                    corner=max(direct_floor([v+s*w for v,s,w in zip(values,signs,widths)])
                               for signs in itertools.product((-1,1),repeat=10))
                    floor=out["floors"][f"{model}/{phase}/{form}"]
                    assert_values_agree(self, floor["point_unguarded_floor_j"], point)
                    assert_values_agree(self, floor["guarded_floor_j"], corner)
                    ratio=out["dominance"]["ratios"][f"{model}/{phase}/{form}"]
                    assert_values_agree(self, ratio["R"], corner/point)
        for arm,phase in (("decode","decode"),("prefill-p2048","prefill")):
            cid=f"ctr-d117-{arm}-qwen3-1p7b-vs-qwen3-8b"
            contrast=out["contrasts"][cid]
            d=[3+.02*i for i in range(1,11)]
            assert_values_agree(self, contrast["dbar_j"], 3.11)
            se=statistics.stdev(d)/math.sqrt(10)
            assert_values_agree(self, contrast["se_j"], se)
            assert_values_agree(self, contrast["metrology_interval_j"][0], 3.11-2.262*se)
            logs=[math.log((10+.1*i+3+.02*i)/(10+.1*i)) for i in range(1,11)]
            desc=out["descriptive"][cid]
            assert_values_agree(self, desc["ratio"], math.exp(statistics.fmean(logs)))
            assert_values_agree(self, desc["ratio_interval"][0], math.exp(statistics.fmean(logs)-
                2.262157162798205*statistics.stdev(logs)/math.sqrt(10)))
            terms=contrast["D_terms_j"]
            assert_values_agree(self, terms[2], out["windows"]["GAMMA"]["neg8"]["allowance_j"])
        self.assertEqual(len(out["dominance"]["ratios"]),8)
        self.assertEqual(len(out["dominance"]["common_mode"]),4)
        self.assertEqual(out["dominance"]["branch"],"B" if out["dominance"]["failed"] else "A")
        self.assertEqual(len(out["members"]["ALPHA"]),119)

    def test_S14_only_standard_library_imports(self):
        tree=ast.parse(SCRIPT.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names=[a.name.split('.')[0] for a in node.names]
            elif isinstance(node,ast.ImportFrom):names=[(node.module or '').split('.')[0]]
            else:continue
            for name in names:
                with self.subTest(module=name):self.assertIn(name,sys.stdlib_module_names)
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name)
                             and n.func.id in ("__import__","exec","eval") for n in ast.walk(tree)))

    def test_determinism_and_partial_pack_rules(self):
        alpha=full_pack(self.root,"ALPHA",5)
        _,first,line1=run_cli({"ALPHA":alpha},self.root/"one.json")
        _,second,line2=run_cli({"ALPHA":alpha},self.root/"two.json")
        self.assertEqual((self.root/"one.json").read_bytes(),(self.root/"two.json").read_bytes())
        self.assertEqual(line1,line2)
        self.assertEqual(first["mode"],"REGISTERED")
        for section in ("dominance","floor_gate","contrasts","descriptive"):
            self.assertEqual(first[section],r.missing_pack())
        self.assertNotIn("members",first)
        self.assertTrue((self.root/"one.json").read_bytes().endswith(b"\n"))

    def test_disclosure_selection_and_battery_scope(self):
        alpha=full_pack(self.root,"ALPHA")
        remove_member(alpha,"fixture-decode-r06",("thermal.os_level_nonzero",))
        remove_member(alpha,"fixture-decode-b05-a1",("thermal.os_level_nonzero","member.admission_aborted"))
        flags=[{"code":"battery.assist","scope":{"run_id":"fixture-decode-r03"}},
               {"code":"battery.assist","scope":{"run_id":"fixture-decode-b07-a1"}},
               {"code":"battery.assist_outside_request","scope":{"run_id":"fixture-decode-r04"}}]
        (alpha/"derived/flags.jsonl").write_text(''.join(json.dumps(f)+'\n' for f in flags))
        _,out,_=run_cli({"ALPHA":alpha},self.root/"disclosure.json")
        cid="df-ph-decode-qwen3-1p7b"
        sensitivity=out["disclosures"]["load_sensitivity"][cid]
        self.assertEqual((sensitivity["n_r"],sensitivity["n_b"]),(10,9))
        battery=out["disclosures"]["battery_assist"][cid]
        self.assertEqual((battery["n_r"],battery["n_b"]),(8,8))
        self.assertEqual(battery["assist_members_by_stratum"],{"repeat":1,"quad":1})

    def test_missing_plist_stops_comparison_and_primary_plist_stays_independent(self):
        root=self.root/"runs"; path=bundle(root,"fixture-r01")
        flags=[]; reader=r.Reader("ALPHA",flags)
        primary=r.Member(path,"fixture-r01",reader,.045)
        data=(path/"power_trace.csv").read_text().replace(",10.0,powermetrics",",20.0,powermetrics")
        (path/"power_trace.csv").write_text(data)
        again=r.Member(path,"fixture-r01",reader,.045)
        self.assertEqual(primary.energies,again.energies)
        self.assertTrue(any(f["code"]=="trace_csv_plist_mismatch" for f in flags))
        (path/"raw/powermetrics.plist").unlink()
        fallback=r.Member(path,"fixture-r01",reader,.045)
        self.assertEqual(fallback.energies,{})
        self.assertFalse(fallback.usable)
        self.assertEqual(fallback.comparison["status"], "not_compared")
        self.assertTrue(any(f["code"]=="trace_plist_missing" for f in flags))

    def test_missing_malformed_data_is_zero_exit(self):
        archive=self.root/"empty";archive.mkdir()
        for data in ("",'{"cells": null}',"not JSON"):
            (archive/"harvest.json").write_text(data)
            rc,out,_=run_cli({"ALPHA":archive},self.root/"empty.json")
            self.assertEqual(rc,0)
            self.assertTrue(out["flags"])
            self.assertTrue(all(f["code"] in r.FLAG_CODES for f in out["flags"]))

    def test_unreadable_root_and_usage_errors(self):
        for args in (("--alpha",str(self.root/"absent"),"--out",str(self.root/"x.json")),
                     ("--alpha-exclusions","x","--out",str(self.root/"x.json")),()):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                r.main(args)
            self.assertEqual(exc.exception.code,2)

    def test_nonfinite_numbers_sanitized(self):
        flags=[]
        self.assertEqual(r.sanitize({"x":[float('inf'),float('nan')]},flags),{"x":[None,None]})
        self.assertEqual([f["code"] for f in flags],["nonfinite_value"]*2)

    def test_malformed_member_structures_flag_and_continue(self):
        path=bundle(self.root/"members","fixture-r01")
        for metadata in ({"uncertainty_evidence":{"clock_anchor":[]}},
                         {"uncertainty_evidence":{"clock_anchor":{"status":"bounded",
                          "first_sample_end_point_epoch_s":float('nan')}}}):
            dump(path/"metadata.json",metadata)
            flags=[]
            member=r.Member(path,"fixture-r01",r.Reader("ALPHA",flags),.045)
            self.assertFalse(member.usable)
            self.assertTrue(flags)
        bundle(self.root/"members","fixture-r01")
        (path/"raw/powermetrics.plist").write_bytes(b'<plist><bad')
        flags=[]
        member=r.Member(path,"fixture-r01",r.Reader("ALPHA",flags),.045)
        self.assertFalse(member.usable)
        self.assertEqual(member.comparison["reason"], "trace_plist_unreadable")
        self.assertTrue(any(f["code"]=="trace_plist_unreadable" for f in flags))

    def test_not_estimable_contrast_keeps_holm_family(self):
        row=r.finish_contrast(r.contrast_stats([3.,3.1,2.9,3.2]),.001,1.)
        self.assertEqual(row["outcome"],"not_estimable")
        assert_values_agree(self, row["p"], 1.)
        assert_values_agree(self, r.holm([.001,row["p"]]), [.002,1.])

    def test_malformed_run_id_cannot_escape_runs_root(self):
        from unittest.mock import patch
        alpha=full_pack(self.root,"ALPHA",5)
        path=alpha/"derived/roster.json"
        roster=json.loads(path.read_text())
        row=next(m for m in roster["members"] if m["run_id"]=="fixture-decode-r01")
        row["run_id"]="../outside-r01"
        dump(path,roster)
        flags=[]
        w=r.Window("ALPHA",alpha,flags)
        with patch.object(w,"member",wraps=w.member) as load:
            selected=w.select("df-ph-decode-qwen3-1p7b","repeat")
        self.assertEqual(len(selected),4)
        self.assertFalse(any(call.args[0]=="../outside-r01" for call in load.call_args_list))
        self.assertTrue(any(f["code"]=="unit_shape_invalid" for f in flags))

    def test_d124_breakpoint_extremum_not_grid(self):
        # A narrow record spike puts the onset optimum at a non-grid breakpoint.
        members=[]
        from types import SimpleNamespace
        for p in r.POSITIONS:
            records=[(-1,.0037,1),(.0037,.0041,100 if p.startswith('b') else 1),(.0041,2,1)]
            members.append(SimpleNamespace(run_id="x-b01-"+p,records=records,edges={"decode":(0,.5)},
                energies={"decode":r.overlap(records,0,.5)[0]},
                residual={"decode":{"max_abs_delta_j":0.}}))
        split=r.common_width(members,"decode",.01)
        assert_values_agree(self, split["shared_j"], .0396)

    def test_token_mismatch_preserves_energy(self):
        alpha=full_pack(self.root,"ALPHA",5)
        path=alpha/"sources/claim-runs/fixture-prefill-p2048-r01/metadata.json"
        meta=json.loads(path.read_text());meta["workload_provenance"]["prompt"]["realized_token_count"]=2047;dump(path,meta)
        _,out,_=run_cli({"ALPHA":alpha},self.root/"tokens.json")
        cell=out["reported_cells"]["df-ph-prefill-p2048-qwen3-1p7b"]
        self.assertIsNotNone(cell["mean_j"]);self.assertIsNone(cell["per_token"]["j_per_token"])
        self.assertEqual(cell["n_r"],5)
        self.assertTrue(any(f["code"]=="kept_member_token_mismatch" for f in out["flags"]))
