# Exhibit C — the clause under ruling (seat S3 branch HEAD 93799321), joulewise/calibration_bracketing.py
```python
    "inherited_ceiling_s": "0.010164834757777545",
    "registration_session_ids": (),
}
_D102_GENERATION_DERIVATIONS: dict[str, dict[str, Any]] = {
    PREDECESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    SUCCESSOR_ACCEPTANCE_ID: _D102_N19_DERIVATION,
    ANCHOR_V3_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r4 is a science-neutral estimator-pin reissue of r3: same corpus, same
    # member table, therefore the same D-102 derivation.
    ANCHOR_V3_R4_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r5 is the science-neutral production-capture flip reissue of r4.
    ANCHOR_V3_R5_ACCEPTANCE_ID: _D102_N17_DERIVATION,
    # r6 is the science-neutral capture-presentation reissue of r5.
    ANCHOR_V3_R6_ACCEPTANCE_ID: _D102_N17_DERIVATION,
}


def _registered_generation_row_is_complete(generation: Any) -> bool:
    """Whether a registered generation row carries every fence it must.

    The validator reads its epoch catalog, prior-set size, cutoff sequence,
    prefix mode and screen rule from this row instead of from literals, so a
    row that omits or malforms one of them must refuse rather than let the
    corresponding check evaporate.

    Two of the row's numbers are restatements rather than independent facts,
    and both are checked here rather than trusted.  ``inherited_ceiling_s`` is
    the same quantity as the row's own ``maximum_budgetable_drift_s`` and its
    99 % two-draw prediction: three copies a hand edit can silently
    desynchronise, after which the issuer would derive a successor's floor from
    a ceiling the predecessor never had.  And the operative screen must sit
    strictly BELOW that ceiling, because D-102 cl.3 spends the allowance
    ``max(observed_drift_s, bracket_screen_s)`` against it, and
    ``screen + excess == maximum`` at the bottom of ``_valid_acceptance_bound``
    would otherwise demand a zero or negative budgetable excess.  That is the
    shape of D-125's ``successor_screen_exceeds_budget_ceiling`` refusal.
    """

    if not isinstance(generation, Mapping):
        return False
    if not _GENERATION_ROW_REQUIRED_KEYS.issubset(set(generation)):
        return False
    catalog_ids = generation["epoch_catalog_ids"]
    session_ids = generation["registration_session_ids"]
    counts = (generation["prior_observation_count"], generation["cutoff_sequence"])
    operatives = generation["operatives"]
    if not isinstance(operatives, Mapping):
        return False
    ceiling = _decimal(generation["inherited_ceiling_s"])
    drift = _decimal(operatives.get("maximum_budgetable_drift_s"))
    prediction = _decimal(generation["prediction_99_two_draw_s"])
    screen = _decimal(operatives.get("bracket_screen_s"))
    if (
        ceiling is None
        or drift is None
        or prediction is None
        or screen is None
        or ceiling != drift
        or drift != prediction
        or not screen < drift
    ):
        return False
    if not all(
        isinstance(count, int) and not isinstance(count, bool) and count > 0
        for count in counts
    ):
        return False
    # The cutoff sequence is TWO ledger rows per observation (a reservation and
    # a finalization).  That relation is exact for a prefix built only from the
    # genesis import, and it is deliberately NOT imposed on a live prefix, whose
    # sessions add open and abort control rows the observation count does not
    # predict.
    if (
        generation["prior_prefix_mode"] == PRIOR_PREFIX_MODE_IMPORT_ONLY
        and generation["cutoff_sequence"]
        != 2 * generation["prior_observation_count"]
    ):
        return False
    return (
        isinstance(catalog_ids, tuple)
        and bool(catalog_ids)
```

## The two registered rows (r6/n17 and n19) at the same HEAD
```python
)
ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
# The identity-epoch generation vocabulary.  A registered generation names the
# epoch ids its prior-observation-set catalog may carry; the TARGET epoch is
# the catalog entry whose six-field vector equals the artifact's own
# ``identity_epoch``, and is resolved from the artifact rather than registered,
# so a catalog can never disagree with the identity it claims to bind.
D079_EPOCH_CATALOG_ID = "d079_epoch"
# Ledger session kinds (ruling 46 §R-a A7), stamped on the session's open
# receipt by the ledger writer.  A `bracket`
# session reserves the endpoints of one claim window; a `derivation` session
# reserves a night of derivation-only captures that build a future acceptance
# and license no measurement.  A row with no kind at all predates the field
# and is read as `bracket`.
BRACKET_SESSION_KIND = "bracket"
DERIVATION_SESSION_KIND = "derivation"
# Prior-set prefix modes (ruling 46 §R-b V6).  ``import_only`` is the genesis
# fence every issued generation to date was derived under: every ledger row at
# or below the cutoff is a historical import.  ``import_plus_live`` is reserved
# for a generation whose corpus was captured live on this machine, whose prefix
# therefore holds finalized live rows as well.
PRIOR_PREFIX_MODE_IMPORT_ONLY = "import_only"
PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE = "import_plus_live"
_PRIOR_PREFIX_MODES = frozenset(
    {PRIOR_PREFIX_MODE_IMPORT_ONLY, PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE}
)
# Registered bracket-screen derivation rules (ruling 46 §R-b V7).  Only the
# rule every issued generation was actually derived under is implemented here:
# the quantized corpus range IS the operative screen.  The D-125 envelope rule
# a successor may be derived under is Ed's open item and its
# ``successor_screen_exceeds_budget_ceiling`` refusal is not implemented in
# this module, so an unimplemented rule name refuses here rather than silently
# degrading to the rule below.
SCREEN_RULE_RANGE_EQUALS_SCREEN = "range_equals_screen"
_REGISTERED_SCREEN_RULES = frozenset({SCREEN_RULE_RANGE_EQUALS_SCREEN})
# Mechanism-named, outcome-independent corpus exclusions (ruling 46 §R-a A6).
# Today's only registered class is `affine_clock_fit_empty`: the anchor-v3
# replay found NO feasible affine wall-versus-monotonic clock fit for that
# capture, so no bound can be derived from it at all.  The exclusion turns on
# that replay outcome, never on the value the capture produced.  It is the
# class recorded at r6 `derivation_notes.excluded_predecessor_members`.
REGISTERED_CORPUS_EXCLUSION_REASONS = frozenset({"affine_clock_fit_empty"})
# Terminal dispositions a LIVE row may carry inside an `import_plus_live`
# cutoff prefix.  `abandoned` is deliberately absent: it maps to the
# `unresolved` classification, which is not an observation.
_LIVE_PREFIX_ADMITTED_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid"}
)
# The keys every registered generation row must carry, so that a future row
# that forgets one refuses instead of falling back to a literal.
_GENERATION_ROW_REQUIRED_KEYS = frozenset(
    {
        "corpus_n",
        "corpus_doubling_trigger",
        "prediction_95_two_draw_s",
        "prediction_99_two_draw_s",
        "operatives",
        "epoch_catalog_ids",
        "prior_prefix_mode",
        "prior_observation_count",
        "cutoff_sequence",
        "screen_rule",
        "inherited_ceiling_s",
        "registration_session_ids",
    }
)
# The D-102 derivation is corpus-indexed, not global: corpus size, the two
# two-draw prediction pins, the ratified operative comparators, the
# corpus-doubling trigger vocabulary, the epoch catalog the prior set may name,
# the prior-set size and cutoff sequence, the prefix mode, the screen rule, the
# ceiling a successor inherits, and the ledger sessions of the registration are
# all functions of the member table a generation was derived from.  Retaining
# them per generation is what keeps the predecessor generations authenticating
# byte-identically after the live default moves.
_D102_N19_DERIVATION: dict[str, Any] = {
    "corpus_n": 19,
    "corpus_doubling_trigger": "corpus_doubles_from_19_to_38",
    "prediction_95_two_draw_s": "0.008826584887500717",
    "prediction_99_two_draw_s": "0.012093166090593858",
    "operatives": {
        "bracket_screen_s": "0.010818",
        "preflight_level_screen_s": "0.033558756679900",
        "max_budgetable_excess_s": "0.001275166090593858",
        "maximum_budgetable_drift_s": "0.012093166090593858",
    },
    "epoch_catalog_ids": (D079_EPOCH_CATALOG_ID,),
    "prior_prefix_mode": PRIOR_PREFIX_MODE_IMPORT_ONLY,
    "prior_observation_count": 38,
    "cutoff_sequence": 76,
    "screen_rule": SCREEN_RULE_RANGE_EQUALS_SCREEN,
    # The ceiling in force for this generation (its 99 % two-draw prediction),
    # which a D-125 successor lineage inherits as a lower bound.  The row states
    # it explicitly because the issuer that derives the successor reads it from
    # here rather than recomputing it from the predecessor's bytes.
    "inherited_ceiling_s": "0.012093166090593858",
    # Import-only generations have no live capture registration.
    "registration_session_ids": (),
}
_D102_N17_DERIVATION: dict[str, Any] = {
    "corpus_n": 17,
    "corpus_doubling_trigger": "corpus_doubles_from_17_to_34",
    "prediction_95_two_draw_s": "0.007377644019421586",
    "prediction_99_two_draw_s": "0.010164834757777545",
    "operatives": {
        "bracket_screen_s": "0.009724",
        "preflight_level_screen_s": "0.032898493715362",
        "max_budgetable_excess_s": "0.000440834757777545",
        "maximum_budgetable_drift_s": "0.010164834757777545",
    },
    "epoch_catalog_ids": (D079_EPOCH_CATALOG_ID,),
    "prior_prefix_mode": PRIOR_PREFIX_MODE_IMPORT_ONLY,
    "prior_observation_count": 38,
    "cutoff_sequence": 76,
    "screen_rule": SCREEN_RULE_RANGE_EQUALS_SCREEN,
    "inherited_ceiling_s": "0.010164834757777545",
```
