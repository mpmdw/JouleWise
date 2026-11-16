#!/bin/zsh
# F2 extension (Sol 6.1, 2026-11-15): queue b requires a PASS hand-read and a committed source.
# Test with JW_REPO/WT_ROOT/OUT_ROOT/CUSTODY/NO_FETCH/PGREP_PATTERN only; never contact the MBP here.
# stage_mbp_span.sh: stage one campaign span's bytes on the MBP BETWEEN spans, ahead of its item (RL-173 D: items issued ahead).
# Items builder, items-1115, 2026-11-15 PST. The lead runs it over SSH in a close interval; it never runs while a span,
# F0 or any measurement is armed (it refuses on a live fence or a live runner process). It writes only:
#   - one fresh DETACHED worktree at the item's pin, at the exact path the item's Start-and-check reuses
#     (`test -e <wt> || git worktree add --detach <wt> <pin>`), checked clean at the pin;
#   - the kit, copied OUTSIDE the checkout to the exact KIT path the item writes, sha256 asserted (the item re-writes it
#     from git and re-asserts the sha, so staging only proves the bytes are reachable on the host);
#   - the queue file from its commit on audit/2026-11-10-fable, copied outside the checkout, sha256 asserted;
#   - a staging record <out-root>/staged/<span>.staged.txt (refs, shas, paths, `date`).
# It opens no energy, power, meter, transcript, slot or custody file, runs no test and no Python, and starts nothing.
#
# Usage:  stage_mbp_span.sh [--dry-run] <span>
#   span: dev-02-s03 | dev-03-s01 | dev-03-s02 | dev-04-s01 | dev-04-s02 | dev-05-s01 | dev-05-s02
# Env overrides (defaults are the MBP paths the items use; the Air dry-run test points them at a local clone + scratch):
#   JW_REPO      canonical clone            (default /Users/edr/code/JouleWise)
#   JW_WT_ROOT   worktree root              (default /Users/edr/code/jw-wt)
#   JW_OUT_ROOT  campaign-out root          (default /Users/edr/campaign-out)
#   JW_CUSTODY   watchdog fence root        (default /Users/edr/night-custody/magistrate)
#   JW_NO_FETCH  1 = do not `git fetch` (Air test against a local clone that already holds the objects)
#   JW_PGREP_PATTERN  override the live-runner pattern (Air test only; never set on the MBP)
set -u
set -o pipefail

DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi
SPAN="${1:-}"
REPO="${JW_REPO:-/Users/edr/code/JouleWise}"
WT_ROOT="${JW_WT_ROOT:-/Users/edr/code/jw-wt}"
OUT_ROOT="${JW_OUT_ROOT:-/Users/edr/campaign-out}"
CUSTODY="${JW_CUSTODY:-/Users/edr/night-custody/magistrate}"
QDIR=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign
QCOMMIT=b7a0d98822865a01e67fc3cc1833c9b186be2181     # campaign queues committed Sun 11-15 00:22 PST (validate-queue ok, re-run 11-15 15:05)
V11=2d347f721552fe03bdd19f113e7bad7a7c24908e         # kit v1.1 pin (dev-03, dev-04, dev-05)
V1=b4b6aeb192da60d895a7529311b06599efff5be4          # v1 pin (dev-02)

die() { echo "STAGE STOP: $*" >&2; exit 1; }
run() { if [ "$DRY" = 1 ]; then echo "DRY: $*"; else "$@"; fi; }

# The per-span table. Every value is copied from the item text (worktree path, KIT path, kit source, queue file and sha).
case "$SPAN" in
  f2-inst-p[1234]) PIN=$V11; WT=cadence-$SPAN; REFS=(align/2026-11-14-f2-inst audit/2026-11-10-fable)
              KSRC=1f683fc634ed6b8722a3976af400920ee1f7dd7d:docs/process/cadence/kits/f2-inst-01.v1.1.json
              KSHA=651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b
              KIT=kits/f2-inst-01.v1.1-1f683fc63.json
              QDIR=docs/process/cadence/queues
              if [ "$SPAN" = f2-inst-p1 ]; then
                QCOMMIT=1f683fc634ed6b8722a3976af400920ee1f7dd7d
                QFILE=f2-inst-01.v1.1.queue-a.json
                QSHA=ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892
              else
                [ "${JW_F2_HAND_READ:-}" = PASS ] || die "piece-1 hand-read must PASS before queue b is staged"
                QCOMMIT="${JW_F2_QUEUE_COMMIT:-}"; QFILE="${JW_F2_QUEUE_FILE:-}"; QSHA="${JW_F2_QUEUE_SHA:-}"
                [ -n "$QCOMMIT" ] && [ -n "$QFILE" ] && [ -n "$QSHA" ] || die "queue b must first be committed by the lead; supply JW_F2_QUEUE_COMMIT/FILE/SHA"
                QDIR="${JW_F2_QUEUE_DIR:-docs/process/cadence/queues}"
              fi;;
  dev-02-s03) PIN=$V1;  WT=cadence-dev-02-s03; REFS=(align/2026-11-14-campaign-runner audit/2026-11-10-fable)
              KSRC=589748f15af6415dc536520469cd19c7800d9adf:docs/process/cadence/kits/cl-dev-02.json
              KSHA=d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8; KIT=kits/cl-dev-02-589748f15-s03.json
              QFILE=QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json; QSHA=ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e;;
  dev-03-s01) PIN=$V11; WT=cadence-dev03-s01;  REFS=(align/2026-11-14-kit-v1-1 audit/2026-11-10-fable)
              KSRC=9cbb365a6957c3737617d8604ba6d06071ab018c:docs/process/cadence/kits/cl-dev-03.v1.1.json
              KSHA=0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b; KIT=kits/cl-dev-03.v1.1-9cbb365a6-s01.json
              QFILE=QUEUE-cl-dev-03-2d347f721.json; QSHA=403e53f91df6f34589a538b506cf57739e5f9d16770adc1e30c5a2a5ea527da2;;
  dev-03-s02) PIN=$V11; WT=cadence-dev03-rest; REFS=(align/2026-11-14-kit-v1-1 audit/2026-11-10-fable)
              KSRC=9cbb365a6957c3737617d8604ba6d06071ab018c:docs/process/cadence/kits/cl-dev-03.v1.1.json
              KSHA=0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b; KIT=kits/cl-dev-03.v1.1-9cbb365a6-s02.json
              QFILE=QUEUE-cl-dev-03-2d347f721-append-both.json; QSHA=366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb;;
  dev-04-s0[12]) PIN=$V11; WT=cadence-$SPAN; REFS=(align/2026-11-14-kit-v1-1 align/2026-11-14-dev04-05-kits audit/2026-11-10-fable)
              KSRC=fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-04.v1.1.json
              KSHA=1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228; KIT=kits/cl-dev-04.v1.1-fecaf73f3-${SPAN#dev-04-}.json
              QFILE=QUEUE-cl-dev-04-2d347f721.json; QSHA=691319634b268f2d2b9c7c6308fea737d3b0f777bb859a6a14fa1322f1870d72;;
  dev-05-s0[12]) PIN=$V11; WT=cadence-$SPAN; REFS=(align/2026-11-14-kit-v1-1 align/2026-11-14-dev04-05-kits audit/2026-11-10-fable)
              KSRC=fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-05.v1.1.json
              KSHA=2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a; KIT=kits/cl-dev-05.v1.1-fecaf73f3-${SPAN#dev-05-}.json
              QFILE=QUEUE-cl-dev-05-2d347f721.json; QSHA=391f438281af05fece9866ec532e7fdb4b0f478b297e403bd99da6153e2fafbb;;
  *) die "usage: $0 [--dry-run] dev-02-s03|dev-03-s01|dev-03-s02|dev-04-s01|dev-04-s02|dev-05-s01|dev-05-s02|f2-inst-p1|f2-inst-p2|f2-inst-p3|f2-inst-p4";;
esac
WTP="$WT_ROOT/$WT"
KITP="$OUT_ROOT/$KIT"
QP="$OUT_ROOT/queues/$QFILE"
REC="$OUT_ROOT/staged/$SPAN.staged.txt"
echo "stage $SPAN at $(date '+%Y-%m-%d %H:%M:%S %Z'): pin $PIN, worktree $WTP, kit $KITP, queue $QP"

# 1. Between spans only: no live fence, no live runner (the lead runs this in a close interval, never while armed).
test -d "$REPO/.git" -o -f "$REPO/.git" || die "no git clone at $REPO"
test ! -e "$CUSTODY/desk_fence.json" || die "a fence is live ($CUSTODY/desk_fence.json): a span or F0 is armed; stage in a close interval"
PAT="${JW_PGREP_PATTERN:-cadence_legs_runner|launch_cadence_span|align_r1_rehearsal|run_align_r1|launch_align_r0|km003c_monitor|hazard_monitor}"
if pgrep -fl "$PAT" >/dev/null 2>&1; then pgrep -fl "$PAT" >&2; die "a runner or monitor process is live; stage in a close interval"; fi
case "$WTP" in "$REPO"|"$REPO"/*) die "worktree path inside the canonical clone";; esac
case "$KITP" in "$WTP"/*|"$REPO"/*) die "kit path inside a checkout";; esac

# 2. Objects: fetch the refs the item fetches (skipped on the Air test), then assert every object is present.
if [ "${JW_NO_FETCH:-0}" != 1 ]; then
  for r in "${REFS[@]}"; do run git -C "$REPO" fetch -q origin "$r" || die "fetch $r"; done
fi
git -C "$REPO" cat-file -e "$PIN^{commit}" || die "pin $PIN not in $REPO"
git -C "$REPO" cat-file -e "$KSRC" || die "kit object $KSRC not in $REPO"
git -C "$REPO" cat-file -e "$QCOMMIT:$QDIR/$QFILE" || die "queue $QFILE not at $QCOMMIT in $REPO"
test "$(git -C "$REPO" show "$KSRC" | shasum -a 256 | cut -c1-64)" = "$KSHA" || die "kit sha at $KSRC"
test "$(git -C "$REPO" show "$QCOMMIT:$QDIR/$QFILE" | shasum -a 256 | cut -c1-64)" = "$QSHA" || die "queue sha at $QCOMMIT"

# 3. The fresh detached worktree at the pin (reused only if it is already exactly that: HEAD = pin, detached, clean).
if [ -e "$WTP" ]; then
  test "$(git -C "$WTP" rev-parse HEAD 2>/dev/null)" = "$PIN" || die "$WTP exists and is not at $PIN; the lead removes it (git -C $REPO worktree remove $WTP)"
  git -C "$WTP" symbolic-ref -q HEAD >/dev/null && die "$WTP is on a branch, not detached"
  test -z "$(git -C "$WTP" status --porcelain)" || die "$WTP is dirty"
  echo "worktree $WTP exists at $PIN, detached and clean: reused"
else
  run mkdir -p "$WT_ROOT"
  run git -C "$REPO" worktree add --quiet --detach "$WTP" "$PIN" || die "worktree add"
  if [ "$DRY" = 0 ]; then
    test "$(git -C "$WTP" rev-parse HEAD)" = "$PIN" || die "new worktree HEAD"
    test -z "$(git -C "$WTP" status --porcelain)" || die "new worktree dirty"
  fi
fi

# 4. Kit and queue, outside every checkout, sha asserted after the copy (temp file + rename; nothing overwritten silently).
copy_asserted() {   # $1 git object, $2 dest, $3 sha
  if [ -e "$2" ]; then
    test "$(shasum -a 256 "$2" | cut -c1-64)" = "$3" || die "$2 exists with another sha; the lead inspects it"
    echo "$2 exists with sha $3: kept"; return 0
  fi
  [ "$DRY" = 1 ] && { echo "DRY: git show $1 > $2 (sha $3)"; return 0; }
  mkdir -p "$(dirname "$2")"
  tmp="$2.staging.$$"
  git -C "$REPO" show "$1" > "$tmp" || { rm -f "$tmp"; die "git show $1"; }
  test "$(shasum -a 256 "$tmp" | cut -c1-64)" = "$3" || { rm -f "$tmp"; die "sha of $1"; }
  mv -n "$tmp" "$2"; test ! -e "$tmp" || { rm -f "$tmp"; die "$2 appeared during the copy"; }
  echo "$2 written, sha $3"
}
copy_asserted "$KSRC" "$KITP" "$KSHA"
copy_asserted "$QCOMMIT:$QDIR/$QFILE" "$QP" "$QSHA"

# 5. The staging record (the lead quotes its path in the item's READY line).
if [ "$DRY" = 0 ]; then
  mkdir -p "$(dirname "$REC")"
  {
    echo "span $SPAN staged $(date '+%Y-%m-%d %H:%M:%S %Z') (epoch $(date +%s)) by stage_mbp_span.sh on $(hostname -s)"
    echo "worktree $WTP HEAD $(git -C "$WTP" rev-parse HEAD) detached clean"
    echo "kit $KITP sha256 $(shasum -a 256 "$KITP" | cut -c1-64) from $KSRC"
    echo "queue $QP sha256 $(shasum -a 256 "$QP" | cut -c1-64) from $QCOMMIT:$QDIR/$QFILE"
  } > "$REC.tmp" && mv "$REC.tmp" "$REC"
  cat "$REC"
fi
echo "STAGED $SPAN (dry-run $DRY)"
