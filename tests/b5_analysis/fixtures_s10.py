"""S10 synthetic production-dispatch collection, at the governing harvest pins.

The producer runs only from a git-archive export. Normal tests restore cached
archives and never run a collection program from the analysis checkout.
"""
from __future__ import annotations
import atexit
import base64
import copy
import contextlib
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from types import SimpleNamespace
from unittest import mock
import zlib
import time
from concurrent.futures import ProcessPoolExecutor

from tests.b5_analysis import fixtures as s0

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'tests/fixtures/b5_analysis/s10'
PACK_IDS={'alpha':'d117_floor_qwen3-1p7b_v5','beta':'d117_floor_qwen3-8b_v5',
          'gamma':'d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'}
SYNTHETIC_BOOT='aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'
SEAMS=(
    ('producer','Runtime / mock-runtime duration constants','Model launch executes pinned prompts with synthetic model identities and .004331/.017331 per-token durations'),
    ('producer','Registry.resolve_telemetry / fake_powermetrics_process.py','The real PowermetricsTelemetryAdapter consumes synthetic primary XML'),
    ('producer','FixtureClock / TimedTelemetry collection clock','Synthetic paired clocks advance through the persisted idle interval'),
    ('producer','BatteryClock / battery_probe / environment guards','Synthetic hardware observations supply battery, adapter, display and environment readings during collection'),
    ('producer','self_consistent_calibration / clone_member','Generate primary pulse/telemetry/lifecycle bytes; real evidence derivation and reduction follow'),
    ('producer','harvest_checkout runner','git archive has no .git; only head/status observations are supplied; file digests are real'),
    ('producer','calibration_ledger._committed_pin_bytes','git archive has no commit for the new synthetic head pin; supply only its Git blob observation, with all ledger parsing and digest checks real'),
    ('producer','historical calibration custody visibility','The immutable synthetic cutoff prefix has historical locators. During production only, these are absent observations; current and previously built synthetic windows retain real calibration primary files'),
    ('producer','Seams.group_alive / Seams.boot_session_uuid / window_lineage.current_boot_session_id','Synthetic collection has no real chain process or boot observation; collection and harvest observe the window\'s synthetic boot'),
    ('producer','write_monitor_journals / write_cooldown','Synthetic hardware publishes complete monitor observations and hash-bound raw cooldown records; all joins are real'),
    ('producer','whole_window.REGISTERED_NEG8_REFERENCE_CORPUS_DIR','The pinned export resolves the exact sealed synthetic measurement corpus; corpus identity and bound arithmetic are still validated from its bytes'),
    ('consumer','windows.sealed_pack_table (partial builds only)','Pinned S0 peers satisfy the full-block selection fence until every S10 window exists; only the built sealed S10 target is opened'),
    ('consumer','mint_floor_artifact_generalized._actual_v2_git_state','The task forbids commits and intentionally leaves an uncommitted fixture; supply the actual base HEAD as the synthetic clean checkout observation'),
)


CONDITIONAL_SEAMS=(
    ('consumer','mint_floor_artifact_generalized._common_minted_artifact_launch_lineage (aggregate only)',
     'CONDITIONAL on open question Q-LINEAGE (stage S10 director, 2026-10-14): an aggregate floor joins two '
     'producers collected in two windows, so its two component lineages differ and the unchanged rule refuses '
     '(launch_lineage_conflict, generalized mint near line 3086). The fixture proceeds on the one option '
     'buildable without a production change: the aggregate omits its lineage carrier when, and only when, every '
     'component carries one and they differ. Each producer still requires one lineage across its own cells, '
     'and each component lineage is authenticated at mint. No number depends on the carrier. Every result from '
     'C5 on, and the joined run from step 5 on, is conditional on the ruling.'),
)


CONDITIONAL_SEAMS+=(
    ('consumer','analysis_manifest_v3._authenticate_floor_dependencies (exact_stack_only lookup only)',
     'CONDITIONAL on open question Q-EXACTSTACK (stage S10 director, 2026-10-14): the sealed GAMMA manifest '
     'declares exact_stack_only transport, and the finalizer then requires a floor cell keyed on the consumer '
     'family itself (sw-*), while every block-5 floor is measured on its floor-pack family (df-*) and names the '
     'consumers in its same-stack transport group. The fixture proceeds on the recommended reading: the consumer '
     'is served by its transport group\'s single source cell, whose group admits the consumer and whose stack '
     'identity equals the consumer\'s (both still checked). The finalizer sees, for that lookup only, the source '
     'cell also under each admitted consumer key; the bound floor_cell_id is the real source cell. Results from '
     'C8 on, and the joined run from step 8 on, are conditional on the ruling.'),
)


@contextlib.contextmanager
def conditional_exact_stack_seam():
    """Apply Q-EXACTSTACK's fixture-only option; see CONDITIONAL_SEAMS."""
    from joulewise import analysis_manifest_v3 as v3
    from scripts import finalize_analysis_manifest as finalize
    original=v3._authenticate_floor_dependencies
    def authenticate(prospective,floor,*,bundle_paths):
        cells=[c for c in floor.get('cells',[]) if isinstance(c,dict)]
        by_id={c.get('cell_id'):c for c in cells}
        aliases=[]
        for group in floor.get('transport_groups',[]):
            sources=group.get('source_cell_ids') if isinstance(group,dict) else None
            if not isinstance(sources,list) or len(sources)!=1 or sources[0] not in by_id:continue
            source=by_id[sources[0]];key=source.get('key')
            if not isinstance(key,dict):continue
            for row in group.get('allowed_consumer_condition_families') or []:
                if row.get('condition_family_id')==key.get('condition_family_id'):continue
                alias=copy.deepcopy(source)
                alias['key']={**alias['key'],'condition_family_id':row.get('condition_family_id'),
                              'condition_family_sha256':row.get('condition_family_sha256')}
                aliases.append(alias)
        view={**floor,'cells':[*floor.get('cells',[]),*aliases]}
        return original(prospective,view,bundle_paths=bundle_paths)
    # The same reading at the close-out's recheck of each finalized arm against
    # its floor cell (dominance_closeout._contrast_floor_binding_error): an arm is
    # compared with its bound cell's key when that cell's single-source transport
    # group admits the arm's family; eligibility, stack identity and the
    # common-mode replay are still checked. Extension recorded in PROVENANCE.md.
    from joulewise import dominance_closeout as closeout
    original_recheck=closeout._contrast_floor_binding_error
    def recheck(finalized_manifest,floor_artifact,replay_sidecar):
        try:
            cells={c['cell_id']:c for c in floor_artifact['cells']}
            admitted={}
            for group in floor_artifact.get('transport_groups',[]):
                sources=group.get('source_cell_ids')
                if isinstance(sources,list) and len(sources)==1:
                    admitted[sources[0]]={(r.get('condition_family_id'),r.get('condition_family_sha256'))
                                          for r in group.get('allowed_consumer_condition_families') or []}
            view=copy.deepcopy(finalized_manifest)
            for arm in view['arms']:
                cell=cells.get(arm.get('floor_cell_id'))
                family=(arm.get('condition_family_id'),arm.get('condition_family_sha256'))
                if cell is not None and family in admitted.get(cell['cell_id'],()):
                    arm['condition_family_id']=cell['key']['condition_family_id']
                    arm['condition_family_sha256']=cell['key']['condition_family_sha256']
        except (KeyError,TypeError,AttributeError):
            view=finalized_manifest
        return original_recheck(view,floor_artifact,replay_sidecar)
    # The same reading at the claim gate's floor resolution
    # (analysis_engine.resolve_floor, reached from the engine): the request of a
    # consumer family is resolved against its transport group's single source
    # cell, seen under the consumer's key, so the exact branch applies (stack
    # identity, binding, eligibility and values still checked) and the resolution
    # names the real source cell. Without it the v3 claim-verdict validator
    # refuses the transported resolution (v3 permits only exact or refused).
    from joulewise import analysis_engine as engine
    original_resolve=engine.resolve_floor
    def resolve(artifact,artifact_sha256,request,*,evidence_binding=None):
        view=artifact
        try:
            cells={c['cell_id']:c for c in artifact['cells']}
            family=(request.condition_family_id,request.condition_family_sha256)
            for group in artifact.get('transport_groups',[]):
                sources=group.get('source_cell_ids')
                if not (isinstance(sources,list) and len(sources)==1 and sources[0] in cells):continue
                admitted={(r.get('condition_family_id'),r.get('condition_family_sha256'))
                          for r in group.get('allowed_consumer_condition_families') or []}
                source=cells[sources[0]]
                if family not in admitted or (source['key']['condition_family_id'],source['key']['condition_family_sha256'])==family:
                    continue
                alias=copy.deepcopy(source)
                alias['key']={**alias['key'],'condition_family_id':family[0],'condition_family_sha256':family[1]}
                view={**artifact,'cells':[alias if c.get('cell_id')==alias['cell_id'] else c for c in artifact['cells']]}
                break
        except (KeyError,TypeError,AttributeError):
            view=artifact
        return original_resolve(view,artifact_sha256,request,evidence_binding=evidence_binding)
    with mock.patch.object(v3,'_authenticate_floor_dependencies',authenticate), \
         mock.patch.object(finalize,'_authenticate_floor_dependencies',authenticate), \
         mock.patch.object(closeout,'_contrast_floor_binding_error',recheck), \
         mock.patch.object(engine,'resolve_floor',resolve):
        yield


CONDITIONAL_SEAMS+=(
    ('consumer','analysis_engine.inputs._frozen_consumer_identity_set (hazard lineage over an unprojected sealed pack only)',
     'CONDITIONAL on open question Q-CONSUMERID (stage S10 resumed director, 2026-10-15): the claim gate authenticates '
     'a contrast arm\'s declared consumer identities only from the pack\'s U8 freeze receipt and identity-projection '
     'receipt, arm-time artifacts of the ARM route. The block-5 sealed packs are unprojected (state "unprojected", '
     'freeze_receipt null; the hazard route pins identities through identity_pins.json), so on a block-5 window every '
     'arm refuses consumer_identity_set_unauthenticated and every contrast floor is refused. The fixture proceeds on '
     'the recommended reading: on a hazard lineage whose pack projection is unprojected with no freeze receipt, the '
     'declared set is the scientific identities of the config files that the sealed pack\'s one identity unit for '
     'that family inventories, read under the committed pack tree the lineage digest authenticates (pack digest, one '
     'unit per family and each file\'s sha256 still checked); only the two arm-time receipts and the unit\'s null '
     'config-set pin are not required. Results from C9 on, and the joined run from step 9 on, are conditional on the '
     'ruling.'),
)


@contextlib.contextmanager
def conditional_consumer_identity_seam():
    """Apply Q-CONSUMERID's fixture-only option; see CONDITIONAL_SEAMS."""
    from joulewise.analysis_engine import inputs
    from joulewise import window_lineage
    original=inputs._frozen_consumer_identity_set
    def declared(evidence,condition_family_id):
        result=original(evidence,condition_family_id)
        if result is None or result:
            return result
        rows=[row.launch_lineage for row in evidence if isinstance(row.launch_lineage,dict)]
        if not rows or len(rows)!=len(evidence) or not all(window_lineage.is_hazard_lineage(r.get('launch_lineage')) for r in rows):
            return result
        roots={r.get('pack_root') for r in rows};digests={r.get('pack_sha256') for r in rows}
        if len(roots)!=1 or len(digests)!=1:
            return result
        try:
            pack_root=Path(next(iter(roots))).resolve(strict=True)
            if inputs.committed_pack_tree_sha256(pack_root)!=next(iter(digests)):
                return result
            tree,_raw=inputs._load_json_object(pack_root/'plan_tree.json','consumer identity plan tree')
            attachments=tree['arm_attachments'];projection=attachments['identity_pin_projection']
            if projection.get('state')!='unprojected' or attachments['arm_readiness'].get('freeze_receipt') is not None:
                return result
            units=[u for u in projection['identity_units']
                   if any(isinstance(b,dict) and b.get('family')==condition_family_id for b in u['consumer_bindings'])]
            if len(units)!=1:
                return result
            identities=set()
            for row in units[0]['config_inventory']:
                path=inputs._lexical_child_path(pack_root,row['path'],label='sealed identity config',require_directory=False)
                raw=inputs._read_analysis_input(path,label='sealed identity config')
                if hashlib.sha256(raw).hexdigest()!=row['sha256']:
                    return result
                identities.add(inputs.scientific_config_identity_sha256(inputs.parse_json_bytes(raw,require_canonical=False)))
            return frozenset(identities) or result
        except (inputs.AnalysisInputError,KeyError,OSError,TypeError,ValueError,AttributeError):
            return result
    with mock.patch.object(inputs,'_frozen_consumer_identity_set',declared):
        yield


@contextlib.contextmanager
def conditional_seams():
    """Every conditional seam of CONDITIONAL_SEAMS, as one context."""
    with conditional_aggregate_lineage_seam(),conditional_exact_stack_seam(),conditional_consumer_identity_seam():
        yield


@contextlib.contextmanager
def conditional_aggregate_lineage_seam():
    """Apply Q-LINEAGE's fixture-only option; see CONDITIONAL_SEAMS."""
    from scripts import mint_floor_artifact_generalized as mint
    original=mint._common_minted_artifact_launch_lineage
    original_variants=mint._artifact_sha256_containment_variants
    # Producer lineages the same mint run authenticated, by producer plan id:
    # the post-bind check rebuilds each component from the aggregate, which
    # under this option carries none, so the rebuild takes its producer's.
    producer_lineages={}
    def plan_id(artifact):
        return ((artifact.get('provenance') or {}).get('calibration_plan') or {}).get('plan_id')
    def aggregate(artifacts,*,label):
        if label=='aggregate components':
            lineages=[(a.get('provenance') or {}).get('launch_lineage') for a in artifacts]
            if (len(lineages)>1 and all(isinstance(l,dict) for l in lineages)
                    and len({mint._canonical_json_sha256(l) for l in lineages})==len(lineages)):
                for artifact,lineage in zip(artifacts,lineages):
                    producer_lineages[plan_id(artifact)]=copy.deepcopy(lineage)
                return None
        return original(artifacts,label=label)
    def variants(artifact):
        provenance=artifact.get('provenance')
        if (isinstance(provenance,dict) and 'launch_lineage' not in provenance
                and plan_id(artifact) in producer_lineages):
            artifact=copy.deepcopy(dict(artifact))
            artifact['provenance']['launch_lineage']=copy.deepcopy(producer_lineages[plan_id(artifact)])
        return original_variants(artifact)
    with mock.patch.object(mint,'_common_minted_artifact_launch_lineage',aggregate), \
         mock.patch.object(mint,'_artifact_sha256_containment_variants',variants):
        yield


def commit_checkout(root):
    """Make a synthetic measurement checkout a Git clone with its files committed.

    The measurement clone is a Git checkout with the sealed packs committed at
    HEAD: lineage publication records the committed pack-tree digest (D-134,
    window_lineage.committed_pack_sha256), and the claim gate recomputes it at
    the lineage's pack root (inputs._frozen_consumer_identity_set). One
    synthetic commit of the checkout's own bytes, at build and at restore.
    """
    git=lambda *a:subprocess.run(['git','-C',str(root),*a],check=True,capture_output=True,text=True).stdout
    if not (Path(root)/'.git').exists():git('init','-q')
    git('add','--all')
    if git('status','--porcelain'):
        git('-c','user.name=S10 synthetic measurement clone','-c','user.email=s10@example.invalid',
            '-c','commit.gpgsign=false','commit','-q','-m','S10 synthetic measurement clone')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):s0.put(path,value)


def ordered_members(roster, tree, measurement, pack_root):
    """Use the sealed launch order, including bound and endpoint references."""
    remaining={m['run_id']:m for m in roster['members'] if not m.get('spare_slot')}
    ordered=[]
    for stage in tree['stage_graph']:
        if stage.get('kind')!='campaign_collection':continue
        relative=stage.get('input',{}).get('path')
        base=Path(measurement)
        if not relative:
            reference=stage.get('input_ref',{})
            if reference.get('kind')=='pack_manifest':
                relative=reference['path'];base=Path(pack_root)
            elif reference.get('kind')=='external_input':
                external=tree['external_inputs']
                manifests=external['manifests'] if isinstance(external,dict) else external
                item=next(m for m in manifests
                          if m.get('input_id',m.get('external_input_id'))==reference['input_id'])
                relative=item.get('manifest_path') or item['manifest']['path']
        if not relative:continue
        payload=json.loads((base/relative).read_bytes())
        for item in payload.get('executed_order',[]):
            run_id=item.get('run_id')
            if run_id in remaining:ordered.append(remaining.pop(run_id))
    if remaining:raise ValueError('sealed collection order omits '+','.join(sorted(remaining)))
    return ordered


def member_config_path(member,measurement,pack_root):
    """Pinned rosters carry measurement-relative or pack-relative configs."""
    path=Path(measurement)/member['config_path']
    return path if path.is_file() else Path(pack_root)/member['config_path']


@dataclass
class ChainWindow:
    root: Path
    archive: Path
    claim: Path
    bound: Path
    custody: Path
    measurement: Path
    entry_data: dict
    writer_row: dict
    aborted: str
    truncated: str
    retired: str | None = None
    restorable: str | None = None

    @property
    def entry(self):
        from joulewise.b5_analysis.windows import IndexEntry
        return IndexEntry.from_mapping(self.entry_data)


@dataclass
class ChainFixture:
    index: Path
    root: Path
    windows: dict[str,ChainWindow]
    repo_root: Path

    @property
    def program_index(self):
        """During construction, S0 packs satisfy the full-block selection fence.

        Only built S10 packs are consumed. The temporary peers are real pinned
        S0 attempt records; their explicit pack identities use the permitted
        pack-table seam. Once all windows exist, this is the ordinary index.
        """
        if len(self.windows)==3:return self.index
        target=self.root/'partial-program-index.json'
        if target.exists():return target
        entries=json.loads(self.index.read_bytes())['attempts']
        for pack in PACK_IDS:
            if pack not in self.windows:
                shape='pin2' if pack=='alpha' else 'pin4'
                name='STD' if pack=='alpha' else pack.upper()+'_STD'
                directory=s0.FIXTURES/shape/name
                peer=json.loads((directory/'INDEX_ENTRY.json').read_bytes())
                archive=self.root/('partial-peer-'+pack)/'archive';archive.mkdir(parents=True)
                # These peers only pass through the attempt reader. Extract
                # its original four records without relocating or opening any
                # member, ledger or source from the unrelated mock pack.
                with tarfile.open(directory/'archive.tar.xz') as blob:
                    for relative in ('harvest.json','derived/exclusions.json','derived/window_flags.json','derived/neg8-screen.json'):
                        destination=archive/relative;destination.parent.mkdir(parents=True,exist_ok=True)
                        destination.write_bytes(blob.extractfile('archive/'+relative).read())
                peer['archive_root']=str(archive);entries.append(peer)
                for attempt in range(1,peer['attempt']):
                    entries.append({**peer,'attempt':attempt,'entry_kind':'no_archive',
                        'archive_root':None,'harvest_record_sha256':None,'verdict':'NO_COLLECTION',
                        'claim_usable':False,'record_citation':'synthetic-s10-progress.md:1'})
        put(target,{'schema':'joulewise.b5_window_index.v1','attempts':entries})
        return target

    @contextlib.contextmanager
    def seams(self):
        """Partial packs need S0 ids; the no-commit task needs Git metadata."""
        from scripts import mint_floor_artifact_generalized as mint
        head=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(mint,'_actual_v2_git_state',return_value=(head,None)))
            stack.enter_context(conditional_seams())
            if len(self.windows)==3:
                yield
                return
            from joulewise.b5_analysis import windows
            table={p:{**dict(row),**s0.PACK_TABLE[p]} for p,row in windows.sealed_pack_table().items()}
            stack.enter_context(mock.patch.object(windows,'sealed_pack_table',return_value=table))
            yield

    def restricted_floats(self):
        result=set()
        def visit(value):
            if type(value) is float:result.add(value)
            elif isinstance(value,dict):
                for child in value.values():visit(child)
            elif isinstance(value,list):
                for child in value:visit(child)
        for window in self.windows.values():
            paths=list(window.claim.glob('*/summary_metrics.json'))+[
                p for p in (window.archive/'withheld').rglob('*') if p.is_file()]
            for path in paths:
                raw=path.read_bytes()
                try:visit(json.loads(raw))
                except (UnicodeDecodeError,json.JSONDecodeError):
                    # Withheld records may be JSONL. Truncated removed-member
                    # summaries have no complete float value to enumerate.
                    for line in raw.splitlines():
                        try:visit(json.loads(line))
                        except (UnicodeDecodeError,json.JSONDecodeError):pass
        return frozenset(result)


REAL_PROGRAMS_VARIABLE='JW_B5_S10_REAL_PROGRAMS'


@lru_cache(maxsize=1)
def chain_fixture() -> ChainFixture:
    # With all three windows committed, every class that restores them runs the
    # real programs for hours (one joined driver run is several hours) and
    # restores about 8 GB. They run on request, never in the ordinary suite.
    if os.environ.get(REAL_PROGRAMS_VARIABLE)!='1':
        import unittest
        raise unittest.SkipTest('S10 real-program chain: set '+REAL_PROGRAMS_VARIABLE+'=1 to run '
            '(restores about 8 GB; one joined driver run takes hours)')
    cached=os.environ.get('JW_B5_S10_CHAIN_CACHE')
    if cached:
        root=Path(cached).resolve()
        if not root.is_relative_to(ROOT/'.scratch-s10f/tmp'):
            raise ValueError('S10 persistent cache must be under worktree scratch TMPDIR')
        root.mkdir(parents=True,exist_ok=True)
        # A stable custody path lets sequential milestone commands retain
        # real earlier outputs. Restore immutable archive bytes afresh at the
        # same locators; earlier row/source hashes therefore stay identical.
        for path in root.iterdir():
            if path.name=='chain-custody':continue
            if path.is_dir():shutil.rmtree(path)
            else:path.unlink()
    else:
        temporary=tempfile.TemporaryDirectory(prefix='s10-chain-');atexit.register(temporary.cleanup)
        root=Path(temporary.name).resolve()
    windows={};known_digests={}
    relocations={Path(json.loads((FIXTURES/p/'INDEX_ENTRY.json').read_bytes())['archive_root']).parent:root/p
        for p in PACK_IDS if (FIXTURES/p/'archive.tar.xz').is_file()}
    for pack in PACK_IDS:
        directory=FIXTURES/pack
        if not (directory/'archive.tar.xz').is_file():continue
        descriptor=json.loads((directory/'INDEX_ENTRY.json').read_bytes())
        old=Path(descriptor['archive_root']).parent;target=root/pack;target.mkdir()
        with tarfile.open(directory/'archive.tar.xz') as blob:blob.extractall(target,filter='data')
        archive=target/'archive'
        for before,after in relocations.items():
            known_digests.update(s0._relocate_archive(archive,before,after,
                include_sidecars=True,known_digests=known_digests))
        for field in ('archive_root','claim_runs_root','bound_runs_root','custody_root','measurement_root'):
            descriptor[field]=str(target/Path(descriptor[field]).relative_to(old))
        from joulewise.b5.harvest import clone_tree
        for label,field in [('night-custody','custody_root'),('repo','measurement_root'),
                            ('claim-runs','claim_runs_root'),('bound-runs','bound_runs_root')]:
            source=archive/'sources'/label
            if source.exists():clone_tree(source,Path(descriptor[field]))
        hardware=target/'synthetic-hardware'
        if hardware.exists():clone_tree(hardware,Path(descriptor['measurement_root'])/'synthetic-hardware')
        for name,relative in [('calibration_observation_ledger.jsonl','runs/calibration_observation_ledger.jsonl'),
                              ('calibration_ledger_head.json','configs/calibration/calibration_ledger_head.json')]:
            ledger_target=Path(descriptor['measurement_root'])/relative;ledger_target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(archive/'sources/ledger'/name,ledger_target)
        # The restored measurement checkout is again a Git clone with the
        # archived sealed pack committed (see commit_checkout).
        commit_checkout(Path(descriptor['measurement_root']))
        descriptor['harvest_record_sha256']=sha(archive/'harvest.json')
        structure=json.loads((directory/'STRUCTURE.json').read_bytes())
        claim=Path(descriptor['claim_runs_root'])
        windows[pack]=ChainWindow(target,archive,claim,Path(descriptor['bound_runs_root']),
            Path(descriptor['custody_root']),Path(descriptor['measurement_root']),descriptor,
            json.loads((claim/'whole-window-verdict.json').read_bytes()),structure['aborted'],structure['truncated'],
            structure.get('retired'),structure.get('restorable'))
    index=root/'window-index.json'
    entries=[w.entry_data for w in windows.values()]
    if 'beta' in windows:
        for shape in ('pin2','pin3'):
            directory=FIXTURES/('beta_history_'+shape)
            data=json.loads((directory/'INDEX_ENTRY.json').read_bytes())
            target=root/('beta-history-'+shape);target.mkdir()
            with tarfile.open(directory/'archive.tar.xz') as blob:blob.extractall(target,filter='data')
            old=Path(data['archive_root']).parent
            if (target/'archive/sources/ledger/calibration_observation_ledger.jsonl').exists():
                s0._relocate_archive(target/'archive',old,target,include_sidecars=True)
            for field in ('archive_root','claim_runs_root','bound_runs_root','custody_root','measurement_root'):
                data[field]=str(target/Path(data[field]).relative_to(old))
            data['harvest_record_sha256']=sha(target/'archive/harvest.json')
            entries.append(data)
    put(index,{'schema':'joulewise.b5_window_index.v1','attempts':entries})
    return ChainFixture(index,root,AvailableWindows(windows),ROOT)


class AvailableWindows(dict):
    def __missing__(self,key):
        raise FileNotFoundError('window not built: '+str(key))


def restore_prior_custody(destination,pack):
    """Restore prior synthetic capture locators; never rebuild their archives."""
    from joulewise.b5.harvest import clone_tree
    scratch=Path(os.environ['TMPDIR']).resolve()
    for prior in PACK_IDS:
        if prior==pack:break
        directory=Path(destination)/prior
        descriptor=json.loads((directory/'INDEX_ENTRY.json').read_bytes())
        root=Path(descriptor['archive_root']).parent.resolve()
        if not root.is_relative_to(scratch):
            raise ValueError('prior synthetic custody must be under scratch TMPDIR: '+str(root))
        if Path(descriptor['claim_runs_root']).exists():continue
        root.mkdir(parents=True,exist_ok=True)
        with tarfile.open(directory/'archive.tar.xz') as blob:
            blob.extractall(root,filter='data')
        for label,field in [('night-custody','custody_root'),('repo','measurement_root'),
                            ('claim-runs','claim_runs_root'),('bound-runs','bound_runs_root')]:
            source=root/'archive/sources'/label
            if source.exists():clone_tree(source,Path(descriptor[field]))
        hardware=root/'synthetic-hardware'
        if hardware.exists():clone_tree(hardware,Path(descriptor['measurement_root'])/'synthetic-hardware')
        print('RESTORED_PRIOR_CUSTODY',prior,root,flush=True)


def build_export(pack,destination):
    """Collect one synthetic window; all production imports are the export's.

    The export directory is its own clean Git repository (one synthetic commit
    of the exported tree), as the measurement clone is: the controller records
    the state of the checkout holding its own source, and the claim gate admits
    only members whose recorded source state is clean.
    """
    started=time.monotonic()
    shape='pin2' if pack=='alpha' else 'pin4'
    pin=json.loads(s0.PINS_PATH.read_bytes())['pins'][shape]
    if os.environ.get('B5_S0_EXPORT_PIN')!=pin['head']:raise ValueError('requires exact pinned export')
    for relative,digest in pin['files'].items():
        if sha(ROOT/relative)!=digest:raise ValueError('pinned program byte mismatch: '+relative)
    restore_prior_custody(destination,pack)
    s0._load_export_support()
    from tests import test_harvest_b5_window as hb
    from tests.b5_analysis.support_s10.member import calibration,collect_job,clone_job,PHYSICS_CACHE
    from tests.b5_analysis.support_s10 import member as producer
    from joulewise import calibration_ledger as ledger, whole_window as ww, window_lineage as lineage
    from joulewise.b5 import harvest as h
    from joulewise.identity_pins import derive_model_runtime_config_from_metadata
    from scripts import run_campaign as rc
    from joulewise.schemas import BenchmarkConfig
    # Collection happens in the window's (synthetic) boot, as in production;
    # the host's real boot identity is not the window's. In a sandbox that
    # cannot read kern.bootsessionuuid the controller skipped this comparison.
    mock.patch.object(lineage,'current_boot_session_id',return_value=SYNTHETIC_BOOT).start()
    root=Path(tempfile.mkdtemp(prefix='s10-'+pack+'-')).resolve()
    (root/'builder.pid').write_text(str(os.getpid()))
    print('BUILD_ROOT',root,flush=True)
    w=object.__new__(hb.Window)
    w.root=root;w.measurement=root/'measurement';w.pack=w.measurement/'configs/campaigns'/PACK_IDS[pack]
    w.custody=root/'custody';w.claim=w.custody/'runs_claim';w.bound=w.custody/'runs_bound'
    w.archive=root/'archive';w.ledger=w.measurement/'runs/calibration_observation_ledger.jsonl'
    w.pin=w.measurement/'configs/calibration/calibration_ledger_head.json';w.plan_path=w.custody/'night_plan.json'
    for name in ('configs','joulewise','scripts'):shutil.copytree(ROOT/name,w.measurement/name)
    inventory=json.loads((w.measurement/'configs/campaigns/v5_claim_25g83/sealed_inventory.json').read_bytes())
    changed=[p for p,digest in inventory['files'].items() if sha(w.measurement/p)!=digest]
    if changed:
        # The measurement checkout is the sealed source inventory; the
        # writer/harvest imports remain the exact governing export above.
        repository=ROOT.parents[1]
        raw=subprocess.run(['git','-C',str(repository),'archive',inventory['head'],*changed],
                           check=True,capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(raw))as exported:
            exported.extractall(w.measurement,filter='data')
    for relative,digest in inventory['files'].items():
        if sha(w.measurement/relative)!=digest:raise ValueError('sealed measurement bytes differ: '+relative)
    # Keep the synthetic hardware executable in the archived measurement
    # tree. Calibration authentication must not depend on a scratch export
    # that will be absent when the fixture is restored on another checkout.
    hardware=w.measurement/'synthetic-hardware';hardware.mkdir()
    shutil.copyfile(producer.PROCESS,hardware/producer.PROCESS.name)
    shutil.copyfile(producer.PROCESS.with_name('paired_clock_native_records.json'),
                    hardware/'paired_clock_native_records.json')
    producer.PROCESS=hardware/producer.PROCESS.name
    for path in (w.claim,w.bound,w.custody/'hazards'):path.mkdir(parents=True,exist_ok=True)
    w.registration=w.measurement/hb.REGISTRATION_RELATIVE
    w.sealed_files=dict(inventory['files'])
    attempt=3 if pack=='beta' else 1
    attempt_id=f'v5-b5-{pack}-a{attempt}-s10-synthetic'
    session_id='s10-'+pack+'-bracket'
    tree=json.loads((w.pack/'plan_tree.json').read_bytes());plan=tree['plan'];identity=tree['window_identity']
    with mock.patch.multiple(hb,PACK_ID=PACK_IDS[pack],PLAN_ID=attempt_id,SESSION_ID=session_id,H_CLAIM=inventory['head']):
        hb.Window._build_night(w,{})
    night_plan=json.loads(w.plan_path.read_bytes());night_plan['t0_epoch_s']=1791649800 if shape=='pin2' else 1791738001
    night_plan['hazard_window']['attempt']=attempt
    put(w.plan_path,night_plan)
    # The archived, committed synthetic cutoff prefix is opaque historical
    # custody. No historical locator is opened by this producer.
    w.ledger.parent.mkdir(parents=True,exist_ok=True)
    previous={'beta':'alpha','gamma':'beta'}.get(pack)
    if previous is None:
        w.ledger.write_bytes(zlib.decompress(base64.b85decode(hb.PREFIX.read_bytes())))
    else:
        with tarfile.open(Path(destination)/previous/'archive.tar.xz') as blob:
            w.ledger.write_bytes(blob.extractfile('archive/sources/ledger/calibration_observation_ledger.jsonl').read())
    acceptance=json.loads((w.measurement/hb.ACCEPTANCE).read_bytes());cutoff=acceptance['ledger_cutoff']
    last_receipt=json.loads(w.ledger.read_bytes().splitlines()[-1])
    put(w.pin,{'sequence':last_receipt['sequence'],'head_digest':last_receipt['receipt_digest'],'ledger_schema':ledger.LEDGER_SCHEMA})
    epoch=acceptance['identity_epoch']
    base=1791649000. if shape=='pin2' else 1791739000.
    put(w.custody/'night/chain.started',{'epoch_s':base-1800.,'pgid':999999,'pid':999999,
        'monotonic_ns':round((base-1800.-producer.EPOCH_ORIGIN+100.)*1e9),'start_time':None})
    # Three different operative bounds (B1). GAMMA's is the smallest: the claim
    # gate transports a floor only to a consumer whose clock-anchor bound is no
    # harder than the floor window's (detection_floor.transport_refusal_reasons),
    # and with one seed per workload the synthetic envelopes have no spread.
    lag={'alpha':.021331,'beta':.022331,'gamma':.020331}[pack]
    pre=w.claim/'instrument_validation'/f'{session_id}-pre'
    evidence=calibration(pre,base-600.,lag)
    bindings=evidence['bindings']
    other=w.claim/'instrument_validation/other-systematic'
    other_evidence=calibration(other,base-1200.,.061331,os_build='25F84' if pack=='alpha' else '25G83')
    other_epoch={k:other_evidence['bindings'][k] for k in epoch}
    other_bindings=other_evidence['bindings']
    other_session_id='s10-other-'+pack+'-session'
    other_slots={s:{'attempt_id':'s10-other-'+pack+'-'+s,'custody_locator':str(other if s=='pre' else w.claim/'instrument_validation/other-post'),
        'identity_epoch':other_epoch,'t1_bindings':other_bindings} for s in ('pre','post')}
    ledger.append_bracket_session_receipt(w.ledger,session_id=other_session_id,window_id='s10-other-window',
        plan_id='s10-other-plan',plan_sha256=sha(w.pack/'calibration_plan.json'),evidence_root_id='s10-other-evidence',
        runs_root=w.claim,slots=other_slots,head_pin_path=w.pin,require_committed_pin=False)
    ledger.finalize_bracket_session_slot(w.ledger,session_id=other_session_id,slot='pre',disposition='systematic-invalid',
        custody_locator=str(other),artifact_sha256=ledger.artifact_hashes(other),identity_epoch=other_epoch,t1_bindings=other_bindings,
        capture_wall_time_s=str(other_evidence['capture_wall_time_s']),exact_bound_lexeme_s=str(other_evidence['b_fiducial_s']))
    ledger.abort_bracket_session(w.ledger,session_id=other_session_id,reason='synthetic_systematic_pre')
    put(w.pin,ledger.terminal_head_pin_for_session(w.ledger,session_id=other_session_id))
    post=w.claim/'instrument_validation'/f'{session_id}-post'
    slots={s:{'attempt_id':f'{session_id}-{s}','custody_locator':str(pre if s=='pre' else post),
        'identity_epoch':epoch,'t1_bindings':bindings} for s in ('pre','post')}
    ledger.append_bracket_session_receipt(w.ledger,session_id=session_id,window_id=identity['window_id'],plan_id=plan['plan_id'],
        plan_sha256=sha(w.pack/'calibration_plan.json'),evidence_root_id=identity['evidence_root_id'],runs_root=w.claim,
        slots=slots,head_pin_path=w.pin,require_committed_pin=False)
    ledger.claim_bracket_session_slot(w.ledger,session_id=session_id,slot='pre',attempt_id=pre.name)
    pre_final=ledger.finalize_bracket_session_slot(w.ledger,session_id=session_id,slot='pre',disposition='valid',
        custody_locator=str(pre),artifact_sha256=ledger.artifact_hashes(pre),identity_epoch=epoch,t1_bindings=bindings,
        capture_wall_time_s=str(evidence['capture_wall_time_s']),exact_bound_lexeme_s=str(evidence['b_fiducial_s']))
    put(w.pin,{'sequence':pre_final['sequence'],'head_digest':pre_final['receipt_digest'],
               'ledger_schema':ledger.LEDGER_SCHEMA})
    # Completion records are published only after every synthetic launch.
    for name in ('chain.exited','result.json'):(w.custody/'night'/name).unlink()
    # Production publishes the committed pack-tree digest of the measurement
    # clone's pack (the driver's pack_sha256), not the plan tree's file digest.
    commit_checkout(w.measurement)
    published=lineage.publish_window_lineage(pack_root=w.pack,pack_id=PACK_IDS[pack],plan_id=plan['plan_id'],
        window_id=identity['window_id'],bracket_session_id=session_id,pre_attempt_id=pre.name,post_attempt_id=post.name,
        claim_runs_root=w.claim,bound_runs_root=w.bound,custody_root=w.custody,
        pack_sha256=lineage.committed_pack_sha256(w.pack),
        arm_decision_path=w.custody/'hazards/arm.json',boot_session_id=SYNTHETIC_BOOT)
    roster=h.build_roster(w.pack,w.measurement)
    members=ordered_members(roster,tree,w.measurement,w.pack)
    science=[m for m in members if m['kind']=='science']
    aborted=next((m['run_id'] for m in science if m.get('block_id') is None),science[0]['run_id'])
    truncated=next(m['run_id'] for m in science if m.get('block_id') and m['run_id']!=aborted)
    if pack=='gamma':
        truncated=next(m['run_id'] for m in science if 'prefill' in m['run_id'])
    retired=None
    restorable=(next(m['run_id'] for m in science if 'prefill' in m['run_id'] and m.get('block_id') is None)
        if pack=='beta' else None)
    if pack in ('beta','gamma'):
        fault=next(m for m in science if m['run_id']==(truncated if pack=='beta' else aborted))
        retired=next(m['run_id'] for m in science if m.get('block_id')==fault['block_id']
            and m['run_id'] not in (aborted,truncated))
    jobs=[]
    for n,m in enumerate(members):
        source=member_config_path(m,w.measurement,w.pack);config=json.loads(source.read_bytes())
        runs=w.bound if m.get('stage_id') in ('neg8_bound','neg8_bound_corpus') else w.claim
        last=base+n*200.
        jobs.append((runs,config,last,w.measurement/hb.POLICY,pre,source,producer.PROCESS))
    # The first pack measures full-controller cost. Later packs collect one
    # real-dispatch seed per workload, then synthesize and reduce each member's
    # distinct primary bytes in a foreground process pool.
    seed_results={};clone_jobs={};templates={}
    if os.environ.get('S10_FULL_CONTROLLER_MEMBERS')=='1':
        seed_results[0]=collect_job(jobs[0])
        print('FIRST_MEMBER_COST_S',seed_results[0][1],flush=True)
    else:
        for n,job in enumerate(jobs):
            m=members[n]
            runs,config,member_base,*_=job
            key=json.dumps([config['model']['name'],config['workload_profile'],config['sampling']],sort_keys=True)
            if key not in templates:
                seed_results[n]=collect_job(job);templates[key]=(Path(seed_results[n][0]),member_base)
                from joulewise.cli import validate_bundle
                problems=validate_bundle(Path(seed_results[n][0]),strict=True,physics_cache=PHYSICS_CACHE)
                if problems:raise ValueError('seed strict validation refused: '+str(problems))
                print('SEED_MEMBER_COST_S',n,seed_results[n][1],flush=True)
            else:
                source,old_epoch=templates[key]
                increment=.73331 if m['kind']=='science' else .003331
                power=7.331+(zlib.crc32(config['run_id'].encode())%13)*increment
                clone_jobs[n]=(source,runs/config['run_id'],config,member_base-old_epoch,power)
    rows=[];bound_rows=[];pin_units={};costs=[]
    with ProcessPoolExecutor(max_workers=8) as pool:
      pending=(pool.map(collect_job,jobs[1:]) if os.environ.get('S10_FULL_CONTROLLER_MEMBERS')=='1'
          else pool.map(clone_job,clone_jobs.values()))
      for n,m in enumerate(members):
        result=seed_results[n] if n in seed_results else next(pending)
        source=member_config_path(m,w.measurement,w.pack);runs=jobs[n][0]
        bundle=Path(result[0]);costs.append(result[1])
        if n in (0,1):
            from joulewise.cli import validate_bundle
            problems=validate_bundle(bundle,strict=True,physics_cache=PHYSICS_CACHE)
            print('FIRST_MEMBER_STRICT',problems,flush=True)
            if problems:raise ValueError('first member is not strict-valid')
        raw_metadata=json.loads((bundle/'metadata.json').read_bytes())
        # A production member is collected from the measurement clone, a clean
        # checkout; the claim gate excludes a member whose recorded source state
        # is not clean. The export must therefore be a clean repository of its own.
        provenance=raw_metadata.get('source_provenance') or {}
        if provenance.get('claim_eligible') is not True:
            raise ValueError('producer source checkout is not clean: '+str(provenance.get('reason_codes')))
        _stack,triple=derive_model_runtime_config_from_metadata(json.loads((bundle/'config.json').read_bytes()),raw_metadata)
        if m['kind']=='science':
            rel=source.relative_to(w.pack).as_posix()
            unit=next(u for u in tree['arm_attachments']['identity_pin_projection']['identity_units']
                      if any(p['path']==rel for p in u['config_inventory']))
            pin_units[unit['identity_unit_id']]=triple
        elif m.get('neg8_slot'):pin_units['neg8_reference']=triple
        if runs==w.claim:
            rows.append({'config':str(source),'run_id':m['run_id'],'execution':'invoked','bundle_ids':[m['run_id']],
                         'role':rc.NEG8_REFERENCE_ROLE if m.get('neg8_slot') else m['role'],
                         **({'sentinel_position':m['neg8_slot'],'canonical_neg8_workload':True,
                              'scientific_config_sha256':ww._scientific_config_identity(bundle)[0]} if m.get('neg8_slot') else {})})
        else:
            bound_rows.append({'config':str(source),'run_id':m['run_id'],'execution':'invoked',
                'bundle_ids':[m['run_id']],'role':m['role']})
        print('COLLECTED',pack,n+1,len(members),m['run_id'],flush=True)
    print('MEMBER_COSTS',json.dumps({'min_s':min(costs),'max_s':max(costs),'mean_s':sum(costs)/len(costs)}),flush=True)
    own_pins=root/'synthetic-launch-identity-pins.json';put(own_pins,{'schema':'joulewise.b5_identity_pins.v1','units':pin_units})
    night_plan['hazard_window']['identity_pins_path']=str(own_pins);put(w.plan_path,night_plan)
    # Both faults predate the verdict writer and source inventory.
    for p in (w.claim/aborted).iterdir():
        if p.is_dir():shutil.rmtree(p)
        else:p.unlink()
    (w.claim/truncated/'summary_metrics.json').write_text('{"status":')
    if retired:
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V2
        producer.coarsen_member(w.claim/retired,anchor_method=CLOCK_METHOD_V2)
        from joulewise.cli import validate_bundle
        problems=validate_bundle(w.claim/retired,strict=True)
        if problems:raise ValueError('retired-method producer is not strict-valid: '+str(problems))
    # A genuinely unreadable endpoint reference leaves two start survivors
    # and forces the pinned writer/harvest's real survivor re-screen.
    (w.claim/'neg8-window-start-r1/summary_metrics.json').write_text('{"status":')
    post_evidence=calibration(post,last+800.,lag+.001)
    ledger.claim_bracket_session_slot(w.ledger,session_id=session_id,slot='post',attempt_id=post.name)
    ledger.finalize_bracket_session_slot(w.ledger,session_id=session_id,slot='post',disposition='valid',
        custody_locator=str(post),artifact_sha256=ledger.artifact_hashes(post),identity_epoch=epoch,t1_bindings=bindings,
        capture_wall_time_s=str(post_evidence['capture_wall_time_s']),exact_bound_lexeme_s=str(post_evidence['b_fiducial_s']))
    put(w.pin,ledger.terminal_head_pin_for_session(w.ledger,session_id=session_id))
    from joulewise.calibration_bracketing import build_calibration_bracket_binding
    snapshot=ledger.load_calibration_ledger_snapshot(w.ledger,w.pin,require_committed_pin=False,
        verify_custody=False,baseline_sequence=cutoff['sequence'],baseline_digest=cutoff['head_digest'])
    binding=build_calibration_bracket_binding(snapshot,session_id=session_id,window_id=identity['window_id'],
        plan_id=plan['plan_id'],plan_sha256=sha(w.pack/'calibration_plan.json'),
        evidence_root_id=identity['evidence_root_id'],runs_root=w.claim)
    binding_path=w.claim/'calibration_bracket_binding.json'
    binding_path.write_bytes(ledger.canonical_json_bytes(binding)+b'\n')
    put(w.custody/'night/chain.exited',{'epoch_s':last+400.,'exit_code':0,
        'monotonic_ns':round((last+400.-producer.EPOCH_ORIGIN+100.)*1e9)})
    put(w.custody/'night/result.json',{'schema':'joulewise.unattended_night_result.v1','verdict':'GO'})
    policy={'sha256':sha(w.measurement/hb.POLICY)}
    from tests.b5_analysis.support_s10.journals import write_monitor_journals,write_cooldown
    excursions=[(base+next(n for n,m in enumerate(members) if m['run_id']==run)*200.+90.,
        base+next(n for n,m in enumerate(members) if m['run_id']==run)*200.+100.)
        for run in (retired,restorable) if run is not None]
    write_monitor_journals(w.custody/'hazards/monitor',base-1800.,last+1800.,charge_intervals=excursions)
    for runs,provenance_rows in ((w.claim,rows),(w.bound,bound_rows)):
        for row in provenance_rows:
            row['preceding_campaign_cooldown']=write_cooldown(runs,row['run_id'],'s10-'+pack)
        token=rc.acquire_campaign_lock(runs)
        try:
            # A floor spec addresses complete science campaigns. NEG8 endpoint
            # launches are a separate reference campaign, as in production;
            # grouping them with science fabricates omitted-spec members.
            science_ids={member['run_id'] for member in science}
            groups=([('s10.json',[row for row in provenance_rows if row['run_id'] in science_ids]),
                     ('s10-neg8.json',[row for row in provenance_rows if row['run_id'] not in science_ids])]
                    if runs==w.claim else [('s10.json',provenance_rows)])
            for filename,campaign_rows in groups:
                if campaign_rows:
                    # run_campaign records the identity its own resolver finds
                    # for a stage's config directory: a contrast pack's science
                    # stages carry the pack's prospective manifest id, reference
                    # stages and floor packs none (run_campaign.py near 10241;
                    # the writer's hazard-window grouping comment near 7752).
                    identities={getattr(rc.resolve_prospective_analysis_manifest_v3(Path(row['config']).parent),
                                        'manifest_id',None) for row in campaign_rows}
                    if len(identities)!=1:raise ValueError('one campaign manifest spans two analysis identities')
                    rc.write_campaign_provenance(runs/'campaign_manifests'/filename,{
                        'schema_version':'joulewise.campaign_provenance.v2','session_id':'s10-'+pack,
                        'analysis_manifest_id':identities.pop(),'campaign_policy':policy,'members':campaign_rows})
        finally:rc.release_campaign_lock(token)
    # A physically invalid corpus member forces the real survivor re-screen.
    # The driver records the collected subset before the real mint.
    from joulewise.b5 import chain
    corpus=w.measurement/hb.CORPUS_RELATIVE
    collected=w.custody/'night/transcript'/chain.NEG8_COLLECTED_MANIFEST
    collected.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(corpus,collected)
    corpus_members=json.loads(corpus.read_bytes())['members']
    put(w.custody/'night/transcript'/chain.NEG8_COLLECTED_SUMMARY,{
        'schema':'joulewise.b5_neg8_corpus_collected.v1',
        'committed_manifest':{'path':str(corpus),'sha256':sha(corpus)},
        'collected_manifest':{'path':str(collected),'sha256':sha(collected)},
        'members_listed':len(corpus_members),'members_kept':len(corpus_members),
        'kept_bundle_ids':[m['bundle_id'] for m in corpus_members],'dropped':[],
        'identical_to_committed':True,'mint_rule':None})
    put(w.bound/'neg8-drift-bound.json',ww.mint_neg8_drift_bound_artifact(w.bound,collected))
    put(w.custody/'night/hazard_result.json',{'schema':'joulewise.b5_hazard_night.v1','neg8_corpus':chain.neg8_corpus_record(w.custody/'night')})
    writer_args=['--whole-window-verdict','--whole-window-verdict-output',str(w.claim/'whole-window-verdict.json'),
        '--runs-dir',str(w.claim),'--campaign-policy',str(w.measurement/hb.POLICY),
        '--log',str(w.claim/'campaign_log.jsonl'),
        '--neg8-drift-bound',str(w.bound/'neg8-drift-bound.json'),'--calibration-ledger',str(w.ledger),'--head-pin',str(w.pin),
        '--bracket-binding',str(binding_path)]
    # A git-archive export cannot contain a newly committed synthetic pin.
    # Supply only that Git observation, never a ledger-loader result.
    original_custody=ledger._custody_reasons
    def window_custody(observations,repo_root,*,mode='issuing'):
        return original_custody([o for o in observations if o.sequence>cutoff['sequence']],repo_root,mode=mode)
    with mock.patch.object(ledger,'_committed_pin_bytes',side_effect=lambda path,repo_root:Path(path).read_bytes()), \
         mock.patch.object(ledger,'_custody_reasons',side_effect=window_custody), \
         mock.patch.object(ww,'REGISTERED_NEG8_REFERENCE_CORPUS_DIR',new=corpus.parent):
        writer_exit=rc.main(writer_args)
    row=json.loads((w.claim/'whole-window-verdict.json').read_bytes())
    def checkout():
        def runner(argv,**kw):return SimpleNamespace(returncode=0,stdout=pin['head']+'\n' if 'rev-parse' in argv else '',stderr='')
        return h.harvest_checkout(runner=runner)
    seams=h.Seams(group_alive=lambda _:False,boot_session_uuid=lambda:SYNTHETIC_BOOT,
                  harvest_checkout=checkout,exclusions_compute=hb.EXCLUSIONS,workers=8)
    original_state=ledger._custody_state
    visible_roots={w.root}
    for prior in PACK_IDS:
        descriptor=Path(destination)/prior/'INDEX_ENTRY.json'
        if descriptor.is_file():
            visible_roots.add(Path(json.loads(descriptor.read_bytes())['archive_root']).parent)
    def visible_custody(path,*args,**kwargs):
        if not any(Path(path).is_relative_to(r) for r in visible_roots):return 'absent'
        return original_state(path,*args,**kwargs)
    with mock.patch.object(ledger,'_custody_state',side_effect=visible_custody), \
         mock.patch.object(ww,'REGISTERED_NEG8_REFERENCE_CORPUS_DIR',new=corpus.parent):
        record=w.harvest(seams=seams,prepare_desk=False,run_g3=False)
    entry={'pack':pack,'pack_id':PACK_IDS[pack],'attempt':attempt,'plan_id':attempt_id,
        't0_epoch_s':night_plan['t0_epoch_s'],'seal':'second','entry_kind':'harvested',
        'archive_root':str(w.archive),'harvest_record_sha256':sha(w.archive/'harvest.json'),
        'superseded_archive_roots':[],'claim_runs_root':str(w.claim),'bound_runs_root':str(w.bound),
        'custody_root':str(w.custody),'measurement_root':str(w.measurement),'harvest_pin':pin['head'],
        'verdict':record['verdict'],'claim_usable':record['claim_usable'],'cause_key':None}
    put(root/'INDEX_ENTRY.json',entry)
    put(root/'STRUCTURE.json',{'aborted':aborted,'truncated':truncated,'retired':retired,'restorable':restorable,
        'writer_exit':writer_exit,'member_count':len(members),
        'build_wall_s':time.monotonic()-started,'member_cost_s':costs})
    if not record['claim_usable']:raise ValueError('harvest not usable: '+str(record.get('exclude_window_reasons'))+'; '+str(root))
    destination=Path(destination)/pack;destination.mkdir(parents=True,exist_ok=True)
    pending=destination/'archive.pending.tar.xz'
    with tarfile.open(pending,'w:xz',preset=3) as blob:
        blob.add(w.archive,arcname='archive')
        blob.add(hardware,arcname='synthetic-hardware')
    total=sum(p.stat().st_size for p in Path(destination).parent.rglob('*') if p.is_file())
    if total>60_000_000:
        raise ValueError('S10 fixture bytes exceed 60 MB: '+str(total))
    for name in ('INDEX_ENTRY.json','STRUCTURE.json'):shutil.copyfile(root/name,destination/name)
    pending.replace(destination/'archive.tar.xz')
    return root


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pack',choices=PACK_IDS);parser.add_argument('destination',type=Path)
    args=parser.parse_args();print(build_export(args.pack,args.destination))
