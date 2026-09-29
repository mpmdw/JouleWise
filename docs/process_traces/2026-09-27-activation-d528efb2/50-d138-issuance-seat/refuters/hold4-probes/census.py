import safety
import ast, json, re
from tests.test_claim_hold_census import CALIBRATION_READERS
terms=['load_calibration_acceptance_bound','_acceptance_bound_from_authenticated_bytes','_authenticate_acceptance_bytes','_registered_operatives_unchecked','inspect_acceptance_without_claim_authority','_authenticate_pack_launch_go','run_campaign','run_axi_spec_campaign','run_authenticated_campaign_child']
rows=[]
for directory in ['joulewise','scripts']:
 for path in sorted((safety.ROOT/directory).rglob('*.py')):
  src=path.read_text(); tree=ast.parse(src)
  def walk(node, ctx='module'):
   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)): ctx=node.name
   if isinstance(node,ast.Call):
    name=ast.unparse(node.func).split('.')[-1]
    if name in terms: rows.append([str(path.relative_to(safety.ROOT)),ctx,node.lineno,ast.unparse(node)])
   for child in ast.iter_child_nodes(node): walk(child,ctx)
  walk(tree)
for row in rows: print(json.dumps(row))
print('C5_REFERENCES')
for f in CALIBRATION_READERS:
 print('\n'+f)
 for n,line in enumerate((safety.ROOT/f).read_text().splitlines(),1):
  if re.search(r'configs/calibration|_CALIBRATION_CONFIG_DIR|calibration_acceptance_|\b[A-Za-z_]\w*_ACCEPTANCE_BOUND_PATH\b',line): print(str(n)+': '+line.strip())
(safety.SCRATCH/'calls.json').write_text(json.dumps(rows,indent=2)+'\n')
