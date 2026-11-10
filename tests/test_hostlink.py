"""Non-root, offline checks; all sshd inputs and keys are synthetic."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / 'scripts/hostlink/hostlink_setup.sh'
SSHD = '/usr/sbin/sshd'


@unittest.skipUnless(Path(SSHD).is_file(), 'native OpenSSH sshd required')
class SSHConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='hostlink-test-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.drop = self.base / 'dropins'
        self.drop.mkdir()
        self.work = self.base / 'work'
        self.work.mkdir()
        self.key = self.base / 'hostkey'
        subprocess.run(['/usr/bin/ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(self.key)], check=True)
        self.config = self.base / 'sshd_config'
        self.config.write_text(f'Include {self.drop}/*\nUsePAM yes\n')
        (self.drop / '100-macos.conf').write_text('KbdInteractiveAuthentication yes\n')
        (self.drop / '050-jw-offload.conf').write_text('''Match User jw-offload
 AuthenticationMethods publickey
 PubkeyAuthentication yes
 PasswordAuthentication no
 KbdInteractiveAuthentication no
 AuthorizedKeysFile /tmp/synthetic-offload-keys
 ForceCommand /usr/bin/true
 PermitTTY no
 AllowTcpForwarding no
''')
        self.target = self.drop / '010-jw-hostlink.conf'

    def install(self, key_only=0, fail_post=False):
        source = SETUP.read_text()
        function = source[source.index('install_sshd() {'):source.index('\ninstall_sshd\n')]
        function = function.replace('/etc/ssh/sshd_config.d', str(self.drop))
        function = function.replace('/etc/ssh/sshd_config', str(self.config))
        function = function.replace('/usr/sbin/chown', '/usr/bin/true')
        # -t without -f means post-install validation; force it to use our fixture.
        wrapper = self.base / 'sshd-wrapper'
        wrapper.write_text(f'''#!/bin/bash
if [[ $# == 1 && $1 == -t ]]; then
  {'exit 1' if fail_post else f'exec {SSHD} -h "{self.key}" -f "{self.config}" "$@"'}
fi
exec {SSHD} -h "{self.key}" "$@"
''')
        wrapper.chmod(0o700)
        function = function.replace(SSHD, str(wrapper))
        script = '''set -u
FAILS=0
ok() { echo "OK $*"; }
warn() { echo "WARN $*"; }
fail() { echo "FAIL $*"; FAILS=$((FAILS+1)); }
'''
        script += function + '\nD=$DROP; C=$TARGET; WORK=$STAGE; U=edr; KEY_ONLY=$MODE\ninstall_sshd\nexit "$FAILS"\n'
        env = dict(os.environ, DROP=str(self.drop), TARGET=str(self.target), STAGE=str(self.work), MODE=str(key_only))
        return subprocess.run(['/bin/bash', '-c', script], env=env, capture_output=True, text=True)

    def effective(self, user):
        r = subprocess.run([SSHD, '-T', '-h', str(self.key), '-f', str(self.config), '-C', f'user={user},host=synthetic,addr=127.0.0.1'], check=True, capture_output=True, text=True)
        return dict(line.split(' ', 1) for line in r.stdout.splitlines())

    def test_preserves_auth_and_offload_confinement(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        owner = self.effective('edr')
        self.assertEqual(owner['kbdinteractiveauthentication'], 'yes')
        self.assertEqual(owner['clientaliveinterval'], '30')
        offload = self.effective('jw-offload')
        for name, value in [('authenticationmethods', 'publickey'), ('forcecommand', '/usr/bin/true'), ('authorizedkeysfile', '/tmp/synthetic-offload-keys'), ('permittty', 'no'), ('allowtcpforwarding', 'no')]:
            self.assertEqual(offload[name], value)

    def test_opt_in_key_only_beats_later_apple_default(self):
        r = self.install(key_only=1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for user in ['edr', 'jw-offload']:
            effective = self.effective(user)
            self.assertEqual(effective['passwordauthentication'], 'no')
            self.assertEqual(effective['kbdinteractiveauthentication'], 'no')
            self.assertEqual(effective['pubkeyauthentication'], 'yes')

    def test_shadowed_global_keeps_previous_bytes(self):
        previous = b'# previous\nClientAliveInterval 30\n'
        self.target.write_bytes(previous)
        (self.drop / '000-local.conf').write_text('PubkeyAuthentication no\n')
        r = self.install()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('shadowed', r.stdout)
        self.assertEqual(self.target.read_bytes(), previous)

    def test_invalid_candidate_keeps_previous_bytes(self):
        previous = b'# previous\n'
        self.target.write_bytes(previous)
        (self.drop / '200-invalid.conf').write_text('InvalidDirective yes\n')
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(self.target.read_bytes(), previous)

    def test_post_install_failure_restores_previous_bytes(self):
        previous = b'# previous\n'
        self.target.write_bytes(previous)
        self.assertNotEqual(self.install(fail_post=True).returncode, 0)
        self.assertEqual(self.target.read_bytes(), previous)


if __name__ == '__main__':
    unittest.main()
