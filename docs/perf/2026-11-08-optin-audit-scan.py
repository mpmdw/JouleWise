"""Read-only AST audit of skip gates, including local imports and inherited setup.

Run with PYTHONNOUSERSITE=1 and GIT_CONFIG_GLOBAL=/dev/null. Reads Git objects
only; never imports tests or follows paths in their source. The output is
a conservative inventory, not a unittest execution or a proof about dynamic code.
"""
import ast, subprocess, tarfile, io, json, re, collections, argparse, os

os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True)
args = parser.parse_args()
refs=['05b6d04cba4868531cc03da187689a3dc187e0eb',
      '8fb75b316b876476cbc55cee46c85d69e2f068c3',
      '1313698017e8277e4791b368eb8fde0d94748b1e']
result={}
def module(p): return p[:-3].replace('/','.').removesuffix('.__init__')
for ref in refs:
 tar=tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','archive',ref,'tests','scripts/shard_tests.py','scripts/quick_suite.py','.github/workflows'])))
 sources={m.name:tar.extractfile(m).read().decode() for m in tar if m.isfile() and m.name.endswith('.py') and 'restricted' not in m.name.split('/')}
 trees={p:ast.parse(s) for p,s in sources.items() if p.startswith('tests/')}
 nodes={};classes={};imports={};assigns={};locations={};direct={};class_gate={}
 def decs(n,p):
  return [{'path':p,'line':d.lineno,'gate':ast.unparse(d)} for d in n.decorator_list if re.search(r'skip|live_hw|slow|expectedFailure',ast.unparse(d),re.I)]
 for p,t in trees.items():
  mod=module(p); imports[mod]={};assigns[mod]={}
  for n in t.body:
   if isinstance(n,ast.ImportFrom):
    base=mod.split('.') if p.endswith('/__init__.py') else mod.split('.')[:-1]
    target='.'.join(base[:len(base)-n.level+1]+([n.module] if n.module else [])) if n.level else n.module or ''
    for a in n.names:imports[mod][a.asname or a.name]=target+'.'+a.name
   elif isinstance(n,ast.Import):
    for a in n.names:imports[mod][a.asname or a.name.split('.')[0]]=a.name if a.asname else a.name.split('.')[0]
   elif isinstance(n,(ast.Assign,ast.AnnAssign)):
    for a in n.targets if isinstance(n,ast.Assign) else [n.target]:
     if isinstance(a,ast.Name) and n.value:assigns[mod][a.id]=ast.unparse(n.value)
   if isinstance(n,ast.FunctionDef):nodes[mod+'.'+n.name]=(n,p,None)
   elif isinstance(n,ast.ClassDef):
    cid=mod+'.'+n.name; classes[cid]=(n,p);class_gate[cid]=decs(n,p)
    for f in n.body:
     if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)):nodes[cid+'.'+f.name]=(f,p,cid)
 def resolve(mod,value,local=None):
  bits=value.split('.');lookup=dict(imports[mod]);lookup.update(local or {});return '.'.join([lookup.get(bits[0],mod+'.'+bits[0]),*bits[1:]])
 def bases(cid):
  c,p=classes[cid];return [resolve(module(p),ast.unparse(b)) for b in c.bases]
 def methods(cid,seen=()):
  if cid in seen:return {}
  out={}
  for b in bases(cid):
   if b in classes:out.update(methods(b,(*seen,cid)))
  out.update({k.rsplit('.',1)[1]:k for k in nodes if k.rsplit('.',1)[0]==cid})
  return out
 method_cache={cid:methods(cid) for cid in classes}
 for key,(n,p,cid) in nodes.items():
  mod=module(p);gs=decs(n,p);calls=[];local={}
  for v in ast.walk(n):
   if isinstance(v,ast.ImportFrom):
    base=mod.split('.') if p.endswith('/__init__.py') else mod.split('.')[:-1]
    target='.'.join(base[:len(base)-v.level+1]+([v.module] if v.module else [])) if v.level else v.module or ''
    for a in v.names:local[a.asname or a.name]=target+'.'+a.name
   elif isinstance(v,ast.Import):
    for a in v.names:local[a.asname or a.name.split('.')[0]]=a.name if a.asname else a.name.split('.')[0]
  for v in ast.walk(n):
   if not isinstance(v,ast.Call):continue
   text=ast.unparse(v.func)
   if re.search(r'(?:skipTest|SkipTest|require_live_hw)$',text):gs.append({'path':p,'line':v.lineno,'gate':ast.unparse(v)})
   if cid and text.startswith(('self.','cls.','case.')):
    target=method_cache[cid].get(text.split('.')[1]);calls.extend([target] if target else [])
   else:calls.append(resolve(mod,text,local))
  direct[key]=(gs,calls)
 def walk(key,seen=None):
  if seen is None:seen=set()
  if key in seen or key not in direct:return []
  seen.add(key);gs,calls=direct[key];out=list(gs)
  for k in calls:out+=walk(k,seen)
  return out
 def class_setup(cid,seen=()):
  if cid in seen:return []
  c,p=classes[cid];out=list(class_gate[cid])
  for b in bases(cid):
   if b in classes:out+=class_setup(b,(*seen,cid))
  for m in ['setUp','setUpClass']:
   if cid+'.'+m in nodes:out+=walk(cid+'.'+m)
  return out
 rows=[]
 for cid,(c,p) in classes.items():
  setup=class_setup(cid)+walk(module(p)+'.setUpModule')
  for method,key in method_cache[cid].items():
   if not method.startswith('test'):continue
   gs=setup+walk(key)
   # Expected failures are retained separately from skip gates.
   if gs:
    unique={json.dumps(g,sort_keys=True):g for g in gs}
    gs=list(unique.values());n,owner,_=nodes[key]
    rows.append({'id':cid+'.'+method,'path':p,'line':n.lineno,'defined_path':owner,'gates':gs})
 # G10 binds these module-level functions to unittest methods at import time.
 for p,t in trees.items():
  if 'test_g10_clock_step_control.py' not in p:continue
  for n in t.body:
   if isinstance(n,ast.FunctionDef) and n.name.startswith('test'):
    gs=walk(module(p)+'.'+n.name)
    if gs:rows.append({'id':module(p)+'.G10ControlTests.'+n.name,'path':p,'line':n.lineno,'gates':gs})
 # Expand names used by gate expressions without evaluating any code or path.
 for r in rows:
  for g in r['gates']:
   mod=module(g['path']);g['bindings']={k:v for k,v in assigns[mod].items() if re.search(r'\b'+re.escape(k)+r'\b',g['gate'])}
 result[ref]={'rows':rows,'sha':subprocess.check_output(['git','rev-parse',ref],text=True).strip()}
 print(ref,len(rows),'candidate methods',len({r['path'] for r in rows}),'modules',flush=True)
json.dump(result,open(args.output,'w'),indent=2)
