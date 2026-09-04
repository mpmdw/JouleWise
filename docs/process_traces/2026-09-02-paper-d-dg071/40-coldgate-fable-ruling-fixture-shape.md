# Cold Fable seat — ruling on the fixture-shape packet (file 38), verbatim

Seat: fresh Fable instance, packet-only (no loop context), read-only on `/Users/edr/code/JouleWise-wt-paper-d2` at `73417fee`; ran its own mutant × fixture bench (17 mutants × 3 fixtures) in its scratch directory. Scratchpad paths redacted to `<scratchpad>`.

---

## Ruling

**Charter digest (§9, recorded before the merits).** Expected value: none was supplied to this seat independently of the packet (hygiene NIT — the charter requires one). Observed: `shasum -a 256 docs/process/coldgate_charter.md` → `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, equal to the registry entry at `docs/process/coldgate_charter_registry.md:16` in the same checkout (`73417fee`). Not a mismatch; proceeding. Checkout confirmed clean and code-identical to `e6687638` for both files at issue.

**Packet hygiene (§6).** Neutrally assembled; the diagnosis is labelled as offered; no cherry-picking found. One MATERIAL defect that bears on Q2: the packet reports `--first-parent` and `--follow` as "indistinguishable from the reference on this fixture" without checking them against the repository's real history, and the candidate cure's own P3 ("reachable from HEAD") has no corresponding H-clause, so the packet's fixture list does not test its own property. Q2's "close the class" is unanswerable in the strict sense (a wrong implementation may always special-case the fixture); I answer it in the sense that matters — every *natural* alternative reading of the reference command.

---

**Q1 — Diagnosis: AFFIRM in substance, REJECT the proposed remedy (i).** The structural problem is fixture-by-enumeration, yes — but the magistrate's cure (i), "restate the assertions as P1/P2′/P3 checked with git", adds no discriminating power. The test already knows the correct sha by construction; `git_commit == <known sha>` is a complete specification of the output for that history, and P1/P2′/P3 follow from it automatically. **What decides the test's power is the history it builds, full stop.** Executed proof: F1 (the packet's shape with all three P-assertions) is passed by three wrong implementations (table below). The right framing is not "state the property" but "enumerate the *axes* of the reference command, and build one history pair on which every other choice on each axis returns a different commit": starting ref (HEAD vs HEAD^ vs `--all`), pathspec (exact vs directory vs glob vs none), change filter (any vs `A` vs `M`), traversal (default vs `--first-parent`), depth (`-1` vs `HEAD~k`). That is finite and closed by construction; the mutant list is derived from it, not the reverse. The alternatives Q1 offers — "the test should not exist; `script_sha256` + `git show` suffice" — I reject: an add-commit producer would record a commit at which `git show` hashes to *different* bytes, so the reader's own check would raise a false alarm about a dirty producer. The test earns its place, at should-fix weight, not more.

**Q2 — Cure shape: REJECT the packet's H1–H3 shape as closing anything; a different shape (F2 below) kills every wrong implementation named in the packet plus all of mine.** Named wrong implementations that pass H1–H3 (executed, F1 column): `git log -1 --format=%H HEAD^ -- <path>` (start from the parent, a *plausible* "skip the commit that contains the artifact" reasoning); `git log --all -1 --format=%H -- <path>` (the P3 failure mode the packet's own fixture list forgot); `git log --first-parent -1 --format=%H -- <path>`. The last is not academic: **on the real repository, for `docs/paper/round7/fill-checklist.md`, the reference returns the branch commit `7fc87a7f` and `--first-parent` returns the PR merge commit `31de700a`** — JouleWise lands PRs as merge commits (≥40 in history), so after #276 merges a first-parent producer would record the merge commit and a reader following the Method prose would get a different sha. **`--first-parent` counts as WRONG.** **`--follow` counts as equivalent for `-1`**: identical on linear history, on renames (rename-only and rename-then-modify probed), and on merge history with distinct timestamps; it diverges only when a merge's two parents share a commit timestamp (probed: `add` returned instead of `modify`), which is a synthetic-fixture artifact — hence a rule for the fixture: **every commit gets a distinct pinned timestamp**, so neither the reference nor a variant depends on tie-breaking. Do not engineer a kill for `--follow`.

The simpler shape (F2): shared prefix root → add (earlier bytes) → **L** (modify to the on-disk bytes); **repository A stops at L, so L is HEAD** (this alone kills every `HEAD~k`, k ≥ 1, and every "start from HEAD^" lookup — no need for H3's differing-depth trick); repository B merges L in with `--no-ff` (kills `--first-parent`), then changes `scripts/other.py` (kills directory/glob/unscoped), then an empty commit (kills HEAD in B), and carries a later producer change on a branch HEAD does not reach (kills `--all`/`--branches`). The add commit ≠ L in both (kills `--diff-filter=A`). The test asserts these shape facts with git directly, so a future "simplification" of the fixture fails loudly instead of silently shedding kills. Residual survivor: `--diff-filter=M` (refuses on any repo where the script was only ever added) — NIT, implausible; it is killed by F0 only because F0's producer commit is an add, a shape F1/F2 rightly give up. Code is in Executed evidence; runtime 0.53 s.

**Q3 — Merge gating: #276 merges now; the F2 cure lands as its own small follow-up PR, tracked as a kernel row that carries the code below. Should-fix, not blocker.** In reader terms: the reader's path is JSON/MD → Method prose → `git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py` → `git show 6b6deb2f:… | shasum`. I ran that path at `73417fee`: reference = recorded = `6b6deb2f`, zero later changes to the path on the HEAD line, hash `d657d75f…` = `producer.script_sha256`. Test power never enters that path, so the reader loses **nothing** under either route; the test's comment at `tests/…:697-704` makes no false claim. What differs is process risk: in-PR means a fourth round on the same test inside a 38-file trace plus a fresh pass; a separate PR is reviewable against the mutant table as its acceptance evidence. One binding condition on the follow-up: **it must touch only the test file** — any edit to the script moves the reference's answer away from `6b6deb2f` and voids byte-identical replay.

**Q4 — Severity: AFFIRM both as graded.** G1-SF1 should-fix — two plausible wrong implementations pass, artifact verified correct, no reader harm today; not a blocker. G1-N1 nit — agreed, with the note that `HEAD~2` is the fixed-depth family, killed wholesale by "L is HEAD in repository A", not one k at a time.

**Q5 — Process: REJECT file 36's "SF1 ≠ M1"; the trigger should have fired at SF1.** File 36 compared the defects at the producer level (M1: the producer lacked the property). But M1 had two parts, and the test half — *the fixture was shaped so that a wrong implementation coincided with the reference* (identical HEADs) — is exactly SF1's signature (HEAD^ coincided). File 36 line 13 records Sol 253 saying so in as many words: "the same fixture-construction class as M1, narrower." The delta-3 ruling file 36 leaned on (file 32 Q1: a residual the cure *enumerated in advance* is not a recurrence) does not transfer: nobody enumerated "HEAD^ still passes" when M1 was cured. For Ed, the usable rule: **a survivor the cure's own record named in advance is a residual; a survivor it did not name is a recurrence, and two unnamed survivors in a row fire the trigger.** The statement "if the next pass finds a *third* survivor… the trigger fires" reinterpreted a two-round trigger as a three-round one; it was transparent and written for Ed, and the miss cost one bench fix plus one fresh pass, which produced survivors three and four — as the trigger predicts.

## Executed evidence

All scratch under `<scratchpad>/coldgate-fixture-fable/` (`bench.py`, `make_fixtures.py`, `test_F{0,1,2}.py`, `table2.txt`, `probe/`). Nothing written under the checkout (`git status --short | wc -l` → 0).

Real repository (checkout `73417fee`, `P=scripts/issue_dg071_dg075_statistics.py`):
```
ref/firstpar/follow/all/dirpath : 6b6deb2f…   addonly: 3fca7d6b…   recorded: 6b6deb2f…
git rev-list 6b6deb2f..HEAD -- $P | wc -l     → 0
git show 6b6deb2f:$P | shasum -a 256          → d657d75fc4bf…537f46d9 (= producer.script_sha256)
git log --merges -40 | wc -l                  → 40 (PRs land as merge commits)
```
On main (`31de700a`), `docs/paper/round7/fill-checklist.md`: `ref 7fc87a7f` / `follow 7fc87a7f` / `1stpar 31de700a`.

Mutant × fixture (`python bench.py`; each cell = focused provenance test / full 27-test module; host repo has the script modified after add with L at HEAD~5, as on the real checkout; `TMPDIR` exported to scratch):
```
mutant       F0 (committed)      F1 (packet H1-H3)   F2 (this seat)      note
base         SURVIVES/SURVIVES   SURVIVES/SURVIVES   SURVIVES/SURVIVES   reference
head         killed/killed       killed/killed       killed/killed       rev-parse HEAD
headparent   killed/killed       killed/killed       killed/killed       rev-parse HEAD^
head2        SURVIVES/SURVIVES   killed/killed       killed/killed       rev-parse HEAD~2
unscoped     killed/killed       killed/killed       killed/killed       log -1 (no pathspec)
dirpath      SURVIVES/SURVIVES   killed/killed       killed/killed       -- scripts/
addonly      SURVIVES/SURVIVES   killed/killed       killed/killed       --diff-filter=A
firstparent  SURVIVES/SURVIVES   SURVIVES/SURVIVES   killed/killed       WRONG on merge histories (main verified)
follow       SURVIVES/SURVIVES   SURVIVES/SURVIVES   SURVIVES/SURVIVES   equivalent for -1
allrefs      SURVIVES/SURVIVES   SURVIVES/SURVIVES   killed/killed       --all (P3 failure mode)
skiphead     SURVIVES/SURVIVES   SURVIVES/SURVIVES   killed/killed       log -1 HEAD^ -- path
glob         SURVIVES/SURVIVES   killed/killed       killed/killed       -- 'scripts/*.py'
modonly      killed/killed       SURVIVES/SURVIVES   SURVIVES/SURVIVES   --diff-filter=M (nit residual)
parent       killed/killed       killed/killed       killed/killed       --format=%P
revlist      SURVIVES/SURVIVES   SURVIVES/SURVIVES   SURVIVES/SURVIVES   equivalent
reverse      SURVIVES/SURVIVES   SURVIVES/SURVIVES   SURVIVES/SURVIVES   equivalent
cwdignored   killed/killed       killed/killed       killed/killed       cwd=None call-site mutant
```
`--follow` probes (`probe/`): rename-only → both `rename`; rename+modify → both `modify-after-rename`; merge with L dated equal to its sibling parent → `ref=modify follow=add`; L dated +1 s → both `modify`. A first F2 draft with tied timestamps "killed" `--follow` — that kill was the artifact, removed by `stamp()`.

F2 test, as executed (replaces `tests/test_issue_dg071_dg075_statistics.py:653-778`; imports already present):
```python
    def test_producer_commit_is_the_scripts_last_commit_not_head(self) -> None:
        """Same producer commit L in two repositories; every other natural
        answer differs from L in at least one of them.

        Shared prefix (identical hashes): root -> add producer (earlier bytes)
        -> L: modify producer to the bytes on disk.  Repository A stops at L,
        so L IS HEAD there and every HEAD~k (k >= 1), and every "start from
        HEAD^" lookup, records an older commit.  Repository B merges L in as
        a side branch (--no-ff), then changes another file under scripts/,
        then adds an empty commit, and carries a LATER change to the producer
        on a branch that HEAD does not reach.  In B, HEAD / HEAD^ / HEAD~k,
        an unscoped or directory- or glob-scoped log, --first-parent (returns
        the merge), and --all / --branches (return the unreachable branch)
        all record something other than L; the add-commit (--diff-filter=A)
        differs from L in both.  The fixture asserts each of those shape
        facts with git directly, so a simplification of the fixture fails
        here before it silently weakens the mutants this test kills.
        """

        checkouts = [self.root / "checkout-a", self.root / "checkout-b"]
        fixture_raw = self.bundle.read_bytes()
        script_raw = SCRIPT_PATH.read_bytes()
        path = ISSUER.SCRIPT_REPOSITORY_PATH

        def environment(date: str) -> dict[str, str]:
            return {
                **os.environ,
                "GIT_AUTHOR_NAME": "Fixture Author",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": date,
                "GIT_COMMITTER_NAME": "Fixture Committer",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_DATE": date,
            }

        def git(checkout: Path, *arguments: str, date: str = "2000-01-01T00:00:00+00:00") -> str:
            completed = subprocess.run(
                ["git", "-c", "commit.gpgSign=false", *arguments],
                cwd=checkout, env=environment(date), check=True,
                capture_output=True, text=True,
            )
            return completed.stdout.strip()

        def commit(checkout: Path, message: str, *, date: str = "2000-01-01T00:00:00+00:00") -> str:
            git(checkout, "add", "-A", date=date)
            git(checkout, "commit", "--quiet", "--allow-empty", "-m", message, date=date)
            return git(checkout, "rev-parse", "HEAD", date=date)

        def stamp(second: int) -> str:
            return f"2000-01-01T00:00:{second:02d}+00:00"

        def sha256_at(checkout: Path, commit_id: str) -> str:
            blob = subprocess.run(
                ["git", "show", f"{commit_id}:{path}"], cwd=checkout,
                check=True, capture_output=True,
            ).stdout
            return hashlib.sha256(blob).hexdigest()

        outputs, producer_commits = [], []
        for index, checkout in enumerate(checkouts):
            fixture = checkout / ISSUER.PINNED_BUNDLE_REPOSITORY_PATH
            fixture.parent.mkdir(parents=True)
            fixture.write_bytes(fixture_raw)
            script = checkout / path
            script.parent.mkdir(parents=True)
            git(checkout, "init", "--quiet")
            git(checkout, "checkout", "--quiet", "-b", "trunk")
            commit(checkout, "root", date=stamp(0))
            script.write_bytes(script_raw + b"# earlier revision\n")
            base = commit(checkout, "add producer", date=stamp(1))
            script.write_bytes(script_raw)
            producer = commit(checkout, "modify producer", date=stamp(2))
            producer_commits.append(producer)
            if index == 1:
                git(checkout, "checkout", "--quiet", "-B", "trunk", base)
                git(checkout, "merge", "--quiet", "--no-ff", "-m", "merge producer", producer, date=stamp(3))
                (checkout / "scripts" / "other.py").write_text("x = 1\n")
                commit(checkout, "other script", date=stamp(4))
                commit(checkout, "later", date=stamp(5))
                git(checkout, "checkout", "--quiet", "-b", "unreachable", producer)
                script.write_bytes(script_raw + b"# unreachable later revision\n")
                commit(checkout, "unreachable producer change", date=stamp(6))
                git(checkout, "checkout", "--quiet", "trunk")
            head = git(checkout, "rev-parse", "HEAD")
            out = checkout / "issued.json"
            exit_code, stderr, _ = self._run_main(
                out, pinned_path=fixture,
                pinned_sha256=hashlib.sha256(fixture_raw).hexdigest(),
                repository_root=checkout,
            )
            self.assertEqual(exit_code, 0, stderr)
            outputs.append(out.read_bytes())
            payload = json.loads(outputs[-1])
            recorded = payload["producer"]["git_commit"]
            self.assertEqual(recorded, producer)
            # The recorded commit contains the recorded bytes (the reader's check).
            self.assertEqual(sha256_at(checkout, recorded), payload["producer"]["script_sha256"])
            # Nothing HEAD reaches changed the producer after it.
            self.assertEqual(git(checkout, "rev-list", f"{recorded}..HEAD", "--", path), "")
            self.assertNotEqual(base, recorded)  # the add commit is a different commit
            if index == 0:
                self.assertEqual(head, recorded)  # A: the last change IS HEAD
            else:
                for depth in ("HEAD", "HEAD^", "HEAD~2", "HEAD~3"):
                    self.assertNotEqual(git(checkout, "rev-parse", depth), recorded)
                # fixture-shape facts a wrong lookup would return instead of L
                self.assertNotEqual(git(checkout, "log", "-1", "--format=%H", "--", "scripts/"), recorded)
                self.assertNotEqual(git(checkout, "log", "--first-parent", "-1", "--format=%H", "--", path), recorded)
                self.assertNotEqual(git(checkout, "log", "--all", "-1", "--format=%H", "--", path), recorded)
        self.assertEqual(producer_commits[0], producer_commits[1])
        self.assertEqual(outputs[0], outputs[1])
        payload = json.loads(outputs[0])
        self.assertFalse(payload["input_bundle"]["path"].startswith("/"))
```
Replay: `python make_fixtures.py && python bench.py` in the scratch directory (about 3 minutes; 17 mutants × 3 fixtures × 2 runs).

## What this seat did NOT check

- The F2 test was run against scratch copies of the checkout's two files, never inside the checkout itself (read-only constraint); it was not run under CI's git version or a `git init` with a different `init.defaultBranch`/hook template — `checkout -b trunk` on the unborn branch worked on git 2.50.1 (Apple Git-155) only.
- Mutants outside the single argv line and the `cwd` call site (e.g. a producer that reads the path from a different constant); PR #276's other files; the Sol/Opus seats' outputs (sealed from me by design).
- Whether `--follow` diverges from the reference on the real repository under any *future* merge shape — only the current history and three synthetic shapes were probed.
- Files 31–37 beyond the sections cited in Q5 and the G1 findings; `MAGISTRATE-NOTES.md` and all loop narrative, per charter §4.
