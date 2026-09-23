# Lead note (magistrate f2d6899b): ruling 16 Q2 condition "a field in pilot_protocol_v3.json" against the registration-immutability convention

Ruling 16 Q2(a) admits the corecaptured t0 refusal on conditions. The first condition is: "record it where the precedent recorded the 0.5-busy-core rule (a field in `pilot_protocol_v3.json`, e.g. `t0_corecaptured_spawns_max: 2`, and this ruling's id appended to the `ruling` string)".

Primary evidence, read this session: `joulewise/night_gate.py:55-75`. The registration table is keyed by the sha256 of the registration's bytes. `QPE01_PILOT_REGISTRATION_SHA256` pins v3 as `69321c69…3616`. v1 and v2 stay byte-identical "as ruled history", because "re-pointing the constant above would carry the v2 entry away with it". The precedent did not edit v2 in place. It created v3 as a new file with its own digest and ruling string. The evidence-night sealed check (`joulewise/evidence_night.py` ~250-257) refuses any registration whose digest is not in `RULED_REGISTRATIONS` or whose bound chain digest differs.

Consequence. Editing v3's bytes would change its digest. That would either orphan the v3 history entry used by the 2026-09-23 07:00 pilot's records, or force a re-pin that the convention forbids. The literal condition therefore conflicts with the convention. The faithful reading of "where the precedent recorded" is a new registration version (v4) carrying the field and the ruling id. v4 is registration machinery that the evidence sealing and every future plan consume, so it is a claim-bearing change.

Proposal, for the cold final pass (reinterpreting a verdict is a mandatory cold-instance trigger, so the magistrate does not decide it alone):
- Land A271 now with the threshold as the named code constant plus the policy and README texts, which cite ruling 16.
- Register the v4 recording as a follow-up lane, and land it with the next registration change (block two, or the next pilot re-run), whichever comes first.
- The next arm notice names the new refusal in plain words, as Q2 requires, so Ed's veto covers it meanwhile.
