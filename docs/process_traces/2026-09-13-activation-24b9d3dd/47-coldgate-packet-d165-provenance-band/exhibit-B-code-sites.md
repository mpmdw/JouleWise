# Exhibit B — code sites at main 1421242633769e5a2ffa25eaf51d8da9a49273fe

## joulewise/dominance_closeout.py lines 940–975 (the D-165 replay consumer's zero-point guard)
```python
                    "bundle_residual_half_widths_j"
                ],
                member_envelope_integral_sum_j=block[
                    "member_envelope_integral_sum_j"
                ],
            )
            delta = _finite_number(
                block["delta_j"], _COMMON_MODE_INPUT_INVALID
            )
            zero_point = _finite_number(
                block["zero_point_contrast_j"],
                _COMMON_MODE_INPUT_INVALID,
            )
            onset = _finite_values(
                block["onset_sweep_j"], _COMMON_MODE_INPUT_INVALID
            )
            offset = _finite_values(
                block["offset_sweep_j"], _COMMON_MODE_INPUT_INVALID
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(_COMMON_MODE_INPUT_INVALID) from exc
        if zero_point not in onset or zero_point not in offset:
            raise ValueError(_COMMON_MODE_ZERO_POINT_MEMBERSHIP)
        if not math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError(_COMMON_MODE_ZERO_POINT_DIVERGENCE)
        deltas.append(delta)
        splits.append((split["shared_width_j"], split["local_width_j"]))

    point_floor = comparative_false_effect_floor(
        deltas, admissible_half_widths_j=[0.0] * len(deltas)
    ).unguarded_floor_j
    common_mode_floor = 0.0
    for shared_sign in (-1.0, 1.0):
        for local_mask in range(1 << len(blocks)):
            corner = [
                delta
```

## joulewise/dominance_closeout.py lines 895–905 (the other isclose site, for context)
```python
    if (
        not math.isfinite(bound)
        or bound <= 0.0
        or not math.isclose(
            bound,
            authenticated_bound,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    ):
        raise ValueError(_COMMON_MODE_OPERATIVE_BOUND_INVALID)
```

## joulewise/floor_extraction.py lines 570–600 (the upstream duplicate predicate)
```python
                "by exact equality",
            )
        try:
            residual_count = len(raw_residuals)
        except TypeError:
            residual_count = -1
        if residual_count != 4:
            _common_mode_refuse(
                "common_mode_precondition_failed",
                f"block {index} must have exactly four bundle residuals",
            )
        residuals: list[float] = []
        for raw in raw_residuals:
            residual = _common_mode_finite(raw)
            if residual is None or residual < 0.0:
                _common_mode_refuse(
                    "common_mode_precondition_failed",
                    f"block {index} residuals must be finite and nonnegative",
                )
            residuals.append(residual)
        if not math.isclose(
            zero_point,
            deltas[index],
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            _common_mode_refuse(
                "common_mode_zero_point_divergence_out_of_domain",
                f"block {index} zero point diverges from its block delta "
                "outside the registered provenance band",
            )
```

## joulewise/floor_extraction.py lines 2505–2545 (member envelope integral sum and the zero-shift contrast: weighted fsum of re-integrated member energies)
```python
            ):
                onset_delta = support_edge_s - window.start_s
                if -shared_edge_bound_s <= onset_delta <= shared_edge_bound_s:
                    onset_candidates.add(onset_delta)
                offset_delta = support_edge_s - window.end_s
                if -shared_edge_bound_s <= offset_delta <= shared_edge_bound_s:
                    offset_candidates.add(offset_delta)

    coefficients = {"A1": -0.5, "B1": 0.5, "B2": 0.5, "A2": -0.5}

    member_envelope_integral_sum = math.fsum(
        abs(coefficients[position])
        * _integrate(
            by_position[position][0],
            by_position[position][1].start_s - bound,
            by_position[position][1].end_s + bound,
        )
        for position in _ABBA_POSITIONS
    )
    if (
        not math.isfinite(member_envelope_integral_sum)
        or member_envelope_integral_sum < 0.0
    ):
        raise CommonModeEstimatorRefusal(
            "common_mode_precondition_failed",
            "the coefficient-weighted member envelope integral sum must be "
            "finite and nonnegative",
        )

    def contrast(onset_s: float, offset_s: float) -> float:
        return math.fsum(
            coefficients[position]
            * _integrate(
                by_position[position][0],
                by_position[position][1].start_s + onset_s,
                by_position[position][1].end_s + offset_s,
            )
            for position in _ABBA_POSITIONS
        )

    return _common_mode_block_input_from_contrast(
```

## joulewise/detection_floor.py lines 1444–1455 (the stored ABBA delta)
```python
        deltas,
        admissible_half_widths_j=block_widths,
    )


def abba_delta(a1_j: float, b1_j: float, b2_j: float, a2_j: float) -> float:
    """Exact ABBA block delta ``(B1 + B2 - A1 - A2) / 2``; sign is B - A."""
    members = _clean_values([a1_j, b1_j, b2_j, a2_j], "ABBA members")
    a1, b1, b2, a2 = members
    return (b1 + b2 - a1 - a2) / 2.0


```
