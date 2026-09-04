# Cold-gate consult brief template

Status: tracked source template. Copy this file into the cold gate's custody
directory, replace every angle-bracketed field, and list the completed brief
in the sealed packet's exhibit manifest. This template does not itself confer
authority or make a charter candidate operative.

## Question and authority

- Atomic question: `<one proposition that can receive one verdict>`
- Controlling authority: `<repository-relative path at immutable revision and exact lines>`
- Proposed disposition: `<the proponent's argument, clearly labelled as argument>`

## Listed packet inputs

List every input by repository-relative custody path, SHA-256 digest, and the
proposition it supports. Include contrary evidence. The packet remains subject
to the manifest grammar enforced by `scripts/validate_gate_packet.py`.

| Custody path | SHA-256 | Proposition addressed |
| --- | --- | --- |
| `<path>` | `<64 hexadecimal characters>` | `<proposition>` |

## Executed evidence

`Executed:` Complete this section whenever a dispositive premise (a fact on
which the requested decision depends) says that an evidence-production path
(the code or command expected to make evidence) does or does not yield a named
artifact. The listed packet inputs above must include either an execution
record or a code-path proof.

- Evidence form: `<execution record, code-path proof, or artifact-pair exhibit>`

Execution record:

- Exact command and arguments: `<argv>`
- Working-tree revision: `<full Git object identifier>`
- Exit code: `<integer>`
- Produced-or-absent artifact path: `<path and whether it was produced or absent>`
- Custody input containing the record: `<path from the table above>`

Code-path proof, when execution is not the evidence:

- Refusal site: `<repository-relative file:line>`
- Why that site proves absence: `<bounded explanation>`
- Custody input containing the proof: `<path from the table above>`

For a premise that compares a named field or set across two artifacts, packs,
or units, add an artifact-pair exhibit: both repository-relative artifact
paths at one named revision, the field as a full JSON Pointer, and both
observed values. A JSON Pointer is the slash-delimited address of a value in a
JSON document, such as `/identity_units/0/model_runtime_config/config_set_sha256`.

## Packet-hygiene declaration

- Omitted evidence: `<none, or list and explain>`
- Narrative excerpts: `<none, or give source, revision or digest, exact line range, proposition, and why primary evidence is unavailable>`
- Known authority conflict: `<none, or identify it>`

## Charter pin

Charter under validation: `<operative charter path>`

Version and SHA-256: `<version>` `<digest independently obtained from the charter registry>`
