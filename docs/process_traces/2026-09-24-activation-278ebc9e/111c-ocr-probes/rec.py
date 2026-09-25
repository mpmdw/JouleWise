import sys; sys.path.insert(0,'/Users/edr/code/wt-278ebc9e-ocr')
from joulewise import scored_packer as sp, scored_registration as sr
from tests.test_scored_registration import fixture
g,p=fixture(); reg=sr.Registration.from_mapping(g)
for field in ('sha256','item'):
    r=sp.pack(reg,p); v=0
    for _ in range(1200): v=[v]
    if field=='sha256': r['sha256']=v
    else: r['blocks'][0]['items'][0]=v
    try: sp._seal(reg,r); print(field,'ACCEPTED')
    except sp.PackingRefusal as e: print(field,'REFUSED',e.code)
    except RecursionError: print(field,'RecursionError')
