# Exhibit E — bench reproduction through production arithmetic (magistrate, 2026-09-13 10:25 PDT, venv Python; read-only)

```
$ python3 - <<PY
import math
from joulewise.detection_floor import abba_delta
for scale in (20.0, 200.0, 2000.0, 20000.0):
    a1,b1,b2,a2 = scale+0.1, scale+0.3, scale+0.0, scale+0.2
    d = abba_delta(a1,b1,b2,a2)
    z = math.fsum([0.5*b1, 0.5*b2, -0.5*a1, -0.5*a2])   # the zero-shift contrast: coefficient-weighted fsum of the same four energies
    print(scale, repr(d), repr(z), math.isclose(z, d, rel_tol=1e-9, abs_tol=1e-12))
PY
20.0 -1.7763568394002505e-15 0.0 admit |z-d|=1.776e-15
200.0 1.4210854715202004e-14 1.4210854715202004e-14 admit |z-d|=0.000e+00
2000.0 1.1368683772161603e-13 0.0 admit |z-d|=1.137e-13
20000.0 1.8189894035458565e-12 0.0 REFUSE |z-d|=1.819e-12
```

Reading: the two arithmetic paths agree to within the band at member energies of 20 J, 200 J and 2,000 J and diverge past it near 20,000 J, where the sequential (B1+B2−A1−A2)/2 rounds to 1.82e-12 J and the compensated fsum gives exactly 0. G2-a member energies are tens of joules (D-117 probes); a 20,000 J member is roughly a 30-minute continuous run at ~10 W.
