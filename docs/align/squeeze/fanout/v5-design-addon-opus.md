# Fanout report: v5-design-addon (Opus 5.5 seat)

- **Built:** a design document only, `docs/align/squeeze/v5-design/addon-opus.md`. No code, no tests, nothing run or measured. Other v5-design seats were not read.
- **Rulings assumed:** all six standing rulings in the brief. The document also requests five new lead rulings (its §1 and §15):
  - L-a: the runtime is authenticated, and R (the count audit) is a jaw;
  - L-b: oracle relocation is the runtime-external attacker model;
  - L-c: sabotage-only prompt freedom, including hint off;
  - L-d: the T-window slot split;
  - L-e: Ed's go for the cloud GPU and the API budget.
- **Open questions:** see §15. The main one is whether oracle relocation is acceptable. If the agent must have a real compute tool, ADD-ON cannot keep v4's calibration exchangeable.
