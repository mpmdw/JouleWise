import os, sys, tempfile
from pathlib import Path
ROOT = Path('/Users/edr/code/JouleWise-wt-d138-hold4-d528efb2')
SCRATCH = Path('/tmp/d138-hold4-d528efb2').resolve()
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
os.environ['TMPDIR'] = str(SCRATCH)
os.environ['JOULEWISE_CUSTODY_PARENT'] = str(SCRATCH / 'custody')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
tempfile.tempdir = str(SCRATCH)
def audit(event, args):
    if event == 'open':
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)) and (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)):
            p = Path(os.fsdecode(path)).resolve()
            if not p.is_relative_to(SCRATCH) and str(p) != '/dev/null':
                raise RuntimeError('SAFETY: outside scratch write: '+str(p))
    if event == 'subprocess.Popen':
        executable, argv, cwd, env = args
        words = list(map(str, argv)) if not isinstance(argv, str) else [argv]
        name = Path(str(executable)).name
        if name in ('sudo','systemsetup','powermetrics','ioreg','pmset'):
            raise RuntimeError('SAFETY: hardware/system command blocked '+name)
        if name == 'git':
            allowed = {'rev-parse','show','ls-files','diff','status','log','cat-file','ls-tree','rev-list','merge-base','check-attr'}
            if not any(w in allowed for w in words[1:]) or any(w in words for w in ('init','add','commit','checkout','reset','clean','config','worktree','clone')):
                raise RuntimeError('SAFETY: git write blocked '+repr(words))
sys.addaudithook(audit)
