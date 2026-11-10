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

    def test_rerun_without_flag_keeps_prior_key_only_policy(self):
        self.target.write_text('PasswordAuthentication no\nKbdInteractiveAuthentication no\n')
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        owner = self.effective('edr')
        self.assertEqual(owner['passwordauthentication'], 'no')
        self.assertEqual(owner['kbdinteractiveauthentication'], 'no')

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


class FirewallTests(unittest.TestCase):
    def test_exact_macos15_readback_and_fail_closed(self):
        source = SETUP.read_text()
        function = source[source.index('firewall_state_ok() {'):source.index('\nFW_GLOBAL=')]
        good = ['Firewall is enabled. (State = 1)', 'Firewall has block all state set to disabled.', 'Firewall stealth mode is on', 'Automatically allow built-in signed software ENABLED.\nAutomatically allow downloaded signed software DISABLED.']
        for index, wrong in [(0, 'Firewall is disabled. (State = 0)'), (1, 'Firewall is blocking all non-essential incoming connections.'), (1, ''), (1, 'unknown'), (2, 'Firewall stealth mode is off'), (3, 'Automatically allow built-in signed software DISABLED.')]:
            values = good.copy()
            values[index] = wrong
            r = subprocess.run(['/bin/bash', '-c', function + '\nfirewall_state_ok "$@"', 'fixture', *values])
            self.assertNotEqual(r.returncode, 0, values)
        self.assertEqual(subprocess.run(['/bin/bash', '-c', function + '\nfirewall_state_ok "$@"', 'fixture', *good]).returncode, 0)


class ClientTests(unittest.TestCase):
    def test_fallback_order_bounded_final_connection_and_no_command_retry(self):
        with tempfile.TemporaryDirectory(prefix='hostlink-client-') as d:
            base = Path(d)
            log = base / 'calls'
            ssh = base / 'ssh'
            ssh.write_text('''#!/bin/bash
printf '%s\\n' "$*" >> "$CALL_LOG"
[[ $* == *mbp-wired* ]] && exit 255
[[ ${!#} == true ]] && exit 0
exit 17
''')
            ssh.chmod(0o700)
            wrapper = base / 'jwssh'
            wrapper.write_text((ROOT / 'scripts/hostlink/jwssh').read_text().replace('/usr/bin/ssh', str(ssh)))
            r = subprocess.run(['/bin/bash', str(wrapper), 'mbp', 'do-once'], env=dict(os.environ, CALL_LOG=str(log)))
            self.assertEqual(r.returncode, 17)
            calls = log.read_text().splitlines()
            self.assertEqual(len(calls), 3)
            self.assertIn('mbp-wired true', calls[0])
            self.assertIn('mbp true', calls[1])
            self.assertIn('ConnectTimeout=4', calls[2])
            self.assertIn('BatchMode=yes', calls[2])
            self.assertIn('mbp do-once', calls[2])

    def test_invalid_peer_never_invokes_ssh(self):
        r = subprocess.run(['/bin/bash', str(ROOT / 'scripts/hostlink/jwssh'), '-oProxyCommand=bad'], capture_output=True)
        self.assertEqual(r.returncode, 2)

    def test_shared_host_block_without_hostname_preserves_aliases(self):
        with tempfile.TemporaryDirectory(prefix='hostlink-config-') as d:
            config = Path(d) / 'config'
            config.write_text('''Host mbp mbp-lan mbp-ip mbp-wired
 User edr
 IdentityFile /tmp/synthetic-key
 IdentitiesOnly yes
Host mbp mbp-lan
 HostName synthetic-mbp.local
Host mbp-ip
 HostName 192.0.2.2
Host mbp-wired
 HostName 10.77.0.2
''')
            for alias, expected in [('mbp', 'synthetic-mbp.local'), ('mbp-ip', '192.0.2.2'), ('mbp-wired', '10.77.0.2')]:
                r = subprocess.run(['/usr/bin/ssh', '-G', '-F', str(config), alias], capture_output=True, text=True, check=True)
                self.assertIn('hostname ' + expected, r.stdout.splitlines())


class SudoersTests(unittest.TestCase):
    def test_candidate_validation_precedes_install_and_failed_full_check_rolls_back(self):
        with tempfile.TemporaryDirectory(prefix='hostlink-sudoers-') as d:
            base = Path(d)
            drop = base / 'sudoers.d'
            drop.mkdir()
            config = base / 'sudoers'
            config.write_text(f'@includedir {drop}\n')
            target = drop / 'jw-hostlink-edr'
            target.write_text('# previous rule\n')
            previous = target.read_bytes()
            work = base / 'work'
            work.mkdir()
            validator = base / 'visudo'
            validator.write_text('''#!/bin/bash
# Fixture: reject the complete policy only once the candidate was installed.
if [[ $2 == "$POLICY" ]] && /usr/bin/grep -q NOPASSWD "$RULE"; then exit 1; fi
if [[ $2 == *.new ]]; then echo checked > "$VALIDATED"; fi
exit 0
''')
            validator.chmod(0o700)
            source = SETUP.read_text()
            function = source[source.index('install_sudoers() {'):source.index('\n[[ $NOPASSWD != 1 ]]')]
            # Replace longer paths first, including the regex's literal directory.
            function = function.replace('/etc/sudoers.d', str(drop)).replace('/etc/sudoers', str(config))
            function = function.replace('/usr/sbin/chown', '/usr/bin/true').replace('/usr/bin/install -d -o root -g wheel -m 0755', '/bin/mkdir -p')
            function = function.replace('/usr/sbin/visudo', str(validator))
            prelude = 'FAILS=0; U=edr; WORK=$STAGE; ok() { :; }; fail() { FAILS=$((FAILS+1)); };\n'
            env = dict(os.environ, STAGE=str(work), POLICY=str(config), RULE=str(target), VALIDATED=str(base / 'validated'))
            r = subprocess.run(['/bin/bash', '-c', prelude + function + '\ninstall_sudoers\nexit "$FAILS"'], env=env, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0, r.stderr)
            self.assertTrue((base / 'validated').exists())
            self.assertEqual(target.read_bytes(), previous)


if __name__ == '__main__':
    unittest.main()
