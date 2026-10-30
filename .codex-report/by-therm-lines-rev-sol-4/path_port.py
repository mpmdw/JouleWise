"""Replace the historical /tmp/jw checkout location only; no semantic port."""
import sys
from pathlib import Path
name=sys.argv[1];sys.argv=sys.argv[1:]
exec(compile(Path(name).read_text().replace('/tmp/jw',str(Path.cwd())),name,'exec'),{'__name__':'__main__','__file__':name})
