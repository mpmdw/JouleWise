## D-173: paper supply custody — one custody-read seam for every claim-bearing paper input (magistrate, PROVISIONAL, 2026-09-04)

Origin: three paper-supplier lanes (D-123 reported means, D-165 outcome
renderer, gamma claim renderer) each failed three consecutive rounds with one
class — a caller-supplied document (a projection, a normalized stop object, a
dict plus bytes) entered the source chain and the supplier sealed it with its
own hash, so a fabricated number or reason could be rendered into the paper.
A three-seat design consult (Sol, Opus, blind Fable; traces
`docs/process_traces/2026-09-04-paper-i/11-*.md`, `12-*.md`) and the
adjudication packet (`14-*.md`) converged; the magistrate ruled (`15-*.md`).

Rule: a paper supplier or renderer obtains every claim-bearing input ONLY
through `joulewise/paper_custody.py`'s `open_paper_input(ref)`, where `ref` is one of
five closed typed refs each carrying only a role name and a runs root. In: that
ref — nothing else; a
git-tracked supply map (read through the repository's authentication session
and anchored on a clean tree, addendum 16) names every path and expected
digest, so no caller ever names a digest. Out: frozen verified objects carrying the digests actually verified, after a
fresh validator replay from disk; governed files are authorized through
clean Git blobs, generated files through receipts reached from a registered
custody inventory. No supplier accepts a dict, bytes, sequence, or
pre-validated object from a caller. Refusals use the closed `paper_custody_*`
namespace; nested validator codes are never renderable. Each family carries
an auto-census test: raw byte mutation, full caller resealing, and
replay-to-reopen replacement each yield the exact refusal code and zero
rendered output. Normative home: `docs/contracts/paper_supply_custody.md`.

Status: PROVISIONAL. Adopted by the magistrate to unblock the seam's
construction; it is placed before the next cold gate (the paper-supply
packet) BEFORE any supplier lands on main; Ed notified by email the same day
and may veto.
