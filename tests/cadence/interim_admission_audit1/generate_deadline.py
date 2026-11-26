"""Freeze actual pinned file serializers with a fake clock, tokenizer, token stream and sensor reader."""
import gzip
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

pin, src, out, *profiles=sys.argv[1:]
profile=profiles[0] if profiles else "journals"
root=Path(src).resolve()
sys.path.insert(0,str(root))
from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple import r1_runtime as rt
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.thermal_gates import ThermalSession
from joulewise.align.interfaces import ChatMessage
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig

class Tokenizer:
    eos_token_ids={0}
    def apply_chat_template(self,messages,**kwargs): return "invented prompt"
    def encode(self,text,**kwargs): return list(range(256))

class Sensors:
    def read(self,keys):
        return {"values":{k:40. if k.startswith("T") else 1200. for k in keys},"errors":{},"raw":{}}
    def close(self): pass

clock=FakeClock(1794719800.)
runtime=MlxRuntimeAdapter(clock)
runtime._model=object()
runtime._tokenizer=Tokenizer()
def stream(model,tokenizer,prompt,*,max_tokens,sampler=None,**kwargs):
    clock.sleep(settings["step"]["deadman_s"] + 1 if profile == "deadline" else .4)
    if profile=="endpoint-error": raise RuntimeError("synthetic stream exception")
    for i in range(0 if profile=="empty-stream" else 3):
        clock.sleep(.02)
        yield SimpleNamespace(token=i+1,text="x",finish_reason=None)
runtime._mlx_lm=SimpleNamespace(stream_generate=stream,make_sampler=lambda temp:object())
settings=json.loads((root/"configs/align/v4/r1_runtime.json").read_bytes())
template=json.loads((root/settings["templates"]["d_spam"]).read_bytes())
policy=rt.gate_policy(settings["sensors"],{"delta_fast_c":1.,"delta_slow_c":1.},
                       turn_cap_s=300,chunk_tokens=256,heavy=False,per_turn=False,g0_cap_s=1200)
spec=rt.step_spec(json.loads(template["workload_profile"]["prompt_text"]),
                  {"prefill_chars":526,"seed":121,"decode_tokens":4096},policy,deadman_s=settings["step"]["deadman_s"])
config=rt.member_config(template,spec,run_id="cadence-generated-L001",kind="cadence-leg")
config["hardware_target"]["notes"]="Conditionless calibration campaign leg (RL-149 section 2; non-claim; no v4 member)."
config["run_metadata"]["tags"]+=["cadence-campaign","cadence-leg=L001"]
config=BenchmarkConfig.from_mapping(config)
endpoint=MlxEndpoint(runtime,config,clock,episode_domain="synthetic.monotonic",
                     prepare_metadata={"mlx_version":"synthetic","mlx_lm_version":"synthetic"})
with tempfile.TemporaryDirectory() as tmp:
    directory=Path(tmp)
    context=SimpleNamespace(outputs_dir=directory)
    gate=ThermalSession(policy,clock,context=context,reader=Sensors(),status_reader=lambda:{
        "os_level":0,"pm_state":"Nominal","pm_observed_ns":round(clock.now()*1e9)})
    gate.start()
    for _ in range(61):
        clock.sleep(1.)
        gate.sample()
    gate.context=None  # The synthetic sidecar still writes its own journal.
    gate.capture_reference("first")
    gate.wait("G0")
    if profile=="hold":
        gate.wait("G1",turn=0)
        interval=gate.wait("H",turn=0,token_count=256,defer_resume=True)
        clock.sleep(.01)
        gate.resume_hold(interval)
        gate.persist_interval(interval)

    gate.close()
    from joulewise.align.apple.budget import EpisodeDeadman
    endpoint.deadman = EpisodeDeadman(clock,clock.stamp(),settings["step"]["deadman_s"])
    endpoint.chat([ChatMessage("user","invented prompt")],tools=(),max_tokens=4096,temperature=0.,seed=121)
    # Run the exact bundle serializer for every phase and token. No controller, device, or native ML is launched.
    writer=SimpleNamespace(_path=directory)
    events=[*gate.events,*endpoint.events]
    if profile=="controller":
        from joulewise.controller import _Execution
        execution=object.__new__(_Execution)
        execution._events=[]
        execution._clock=clock
        execution._config=config
        execution._battery_monotonic_ns=lambda:round(clock.now()*1e9)
        for name in ("validate","prepare","idle_baseline","warmup","measured_run","idle_drift_sentinel","cleanup","reduce"):
            execution._begin_stage(name)
            clock.sleep(.01)
            execution._complete_stage(name)
        events+=execution._events
    for e in events:
        RunBundleWriter._append_event_record(writer,e)
    def rows(name): return [json.loads(line) for line in (directory/name).read_bytes().splitlines()]
    docs={"config.json":config.to_dict(),"outputs/align_thermal.jsonl":rows("align_thermal.jsonl"),
          "events.jsonl":rows("events.jsonl"),"outputs/align_turns.jsonl":endpoint.turn_provenance}
    assert len(docs["outputs/align_turns.jsonl"])==1
    Path(out,pin+"-"+profile+".json.gz").write_bytes(gzip.compress(json.dumps(docs,sort_keys=True,separators=(",",":")).encode(),mtime=0))
