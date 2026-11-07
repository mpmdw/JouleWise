#!/bin/zsh
# Quiet the measurement MacBook Pro's scheduled macOS background work (Ed, 2026-11-07; RUN_STATE 200).
# Run on the MBP:  sudo zsh mbp_quiet_os.zsh        (add --force to run while a measurement process is live)
# Idempotent. Touches no repo, custody or measurement data. Writes a log to /Users/Shared/JouleWise/.
# Undo:  sudo softwareupdate --schedule on; sudo mdutil -a -i on; sudo tmutil enable;
#        sudo launchctl enable gui/<uid>/com.apple.photoanalysisd (and .mediaanalysisd)
set -u
[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo zsh $0"; exit 2; }
U=${SUDO_UID:-501}; FORCE=${1:-}
if pgrep -fl 'align_r0_checks|r0_runner|run_night|align_r1_rehearsal|run_b5_analysis' >/dev/null && [[ $FORCE != --force ]]; then
  echo "A measurement/analysis process is running:"; pgrep -fl 'align_r0_checks|r0_runner|run_night|align_r1_rehearsal|run_b5_analysis'
  echo "Not changing anything mid-run. Re-run when it is done (or with --force)."; exit 3
fi
mkdir -p /Users/Shared/JouleWise; LOG=/Users/Shared/JouleWise/os-quiet-$(date -u +%Y%m%dT%H%M%SZ).log
exec > >(tee -a $LOG) 2>&1
echo "== mbp_quiet_os $(date) host=$(sysctl -n hw.model) user-uid=$U"

echo "\n== 1. Software Update: background scan and auto-download off"
softwareupdate --schedule off
defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool false
defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload -bool false
defaults write /Library/Preferences/com.apple.commerce AutoUpdate -bool false 2>/dev/null
echo "readback: $(softwareupdate --schedule 2>&1 | tail -1); AutomaticCheckEnabled=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled 2>&1); AutomaticDownload=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload 2>&1)"
echo "(Security responses / XProtect data updates are left ON on purpose.)"

echo "\n== 2. Spotlight indexing off (all volumes)"
mdutil -a -i off
mdutil -s / /System/Volumes/Data 2>&1 | sed 's/^/readback: /'

echo "\n== 3. Photos analysis agents disabled (photoanalysisd, mediaanalysisd)"
for svc in com.apple.photoanalysisd com.apple.mediaanalysisd; do
  launchctl disable gui/$U/$svc && echo "disabled gui/$U/$svc" || echo "could not disable $svc (SIP?); turn off iCloud Photos instead"
done
launchctl print-disabled gui/$U 2>/dev/null | grep -E 'photoanalysisd|mediaanalysisd' | sed 's/^/readback: /'
echo "Running copies are left alone (the magistrate holds them); they will not be relaunched."
pgrep -lx Photos >/dev/null && { echo "Photos is open: quitting it"; pkill -x Photos; } || echo "Photos not running"

echo "\n== 4. Time Machine automatic backups off"
tmutil disable 2>&1 | sed 's/^/tmutil: /'
echo "readback: AutoBackup=$(defaults read /Library/Preferences/com.apple.TimeMachine AutoBackup 2>&1)"
tmutil destinationinfo 2>&1 | head -5 | sed 's/^/readback: /'

echo "\n== Not changeable here: midnight /tmp cleaner (SIP; the magistrate prunes /private/tmp), XProtect (~05:40), daily maintenance (~12:53)."
echo "== Optional by hand: System Settings > [your name] > iCloud > Photos > off (stops iCloud Photos sync on this Mac)."
echo "== Done. Log: $LOG"
