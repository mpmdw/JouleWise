"""Unit tests for the pure T0.5 idle-admission core (audit P1.1/P1.2).

``CLEAN_IDLE_RECORDS_JSON`` is primary evidence copied verbatim (fields
trimmed to the evaluator's inputs) from the first 40 records of
``runs_recal5_20260719/p2015-df-rq-short-abs-r01/rich_telemetry_idle.jsonl``
- a clean-provenance quiet-mac idle window (300 samples, busy p95 0.211,
combined-power p95 0.143 W over the full window).
"""

from __future__ import annotations

import copy
import json
import math
import unittest

from joulewise.idle_admission import (
    ADAPTER_CONTINUITY_SCHEMA,
    CPU_ADMISSION_SCHEMA,
    EXTENSION_SCHEMA_VERSION,
    NEG8_BRACKET_SCHEMA,
    AdapterWattagePolicy,
    CpuAdmissionCriteria,
    IdleAdmissionExtension,
    IdleAdmissionPolicyError,
    Neg8BracketPolicy,
    evaluate_adapter_wattage_continuity,
    evaluate_cpu_idle_admission,
    evaluate_neg8_bracket,
    extract_adapter_observation,
)

CLEAN_IDLE_RECORDS_JSON = r"""[{"processor_combined_power_w":0.17891200000000002,"clusters":[{"cpus":[{"idle_ratio":0.827434,"down_ratio":0.0},{"idle_ratio":0.888924,"down_ratio":0.0},{"idle_ratio":0.924896,"down_ratio":0.0},{"idle_ratio":0.954602,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999625,"down_ratio":0.0},{"idle_ratio":0.996772,"down_ratio":0.0},{"idle_ratio":0.999802,"down_ratio":0.0},{"idle_ratio":0.95668,"down_ratio":0.0},{"idle_ratio":0.950103,"down_ratio":0.0},{"idle_ratio":0.999929,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0950899,"clusters":[{"cpus":[{"idle_ratio":0.938488,"down_ratio":0.0},{"idle_ratio":0.981255,"down_ratio":0.0},{"idle_ratio":0.985831,"down_ratio":0.0},{"idle_ratio":0.999111,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999444,"down_ratio":0.0},{"idle_ratio":0.968656,"down_ratio":0.0},{"idle_ratio":0.999084,"down_ratio":0.0},{"idle_ratio":0.929683,"down_ratio":0.0},{"idle_ratio":0.996987,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.081191,"clusters":[{"cpus":[{"idle_ratio":0.884461,"down_ratio":0.0},{"idle_ratio":0.986211,"down_ratio":0.0},{"idle_ratio":0.942326,"down_ratio":0.0},{"idle_ratio":0.996315,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999496,"down_ratio":0.0},{"idle_ratio":0.952028,"down_ratio":0.0},{"idle_ratio":0.999474,"down_ratio":0.0},{"idle_ratio":0.997426,"down_ratio":0.0},{"idle_ratio":0.997599,"down_ratio":0.0},{"idle_ratio":0.999949,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.170867,"clusters":[{"cpus":[{"idle_ratio":0.983999,"down_ratio":0.0},{"idle_ratio":0.997892,"down_ratio":0.0},{"idle_ratio":0.899549,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.963803,"down_ratio":0.0},{"idle_ratio":0.990963,"down_ratio":0.0},{"idle_ratio":0.997263,"down_ratio":0.0},{"idle_ratio":0.942427,"down_ratio":0.0},{"idle_ratio":0.991241,"down_ratio":0.0},{"idle_ratio":0.999963,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.07759869999999999,"clusters":[{"cpus":[{"idle_ratio":0.987977,"down_ratio":0.0},{"idle_ratio":0.961208,"down_ratio":0.0},{"idle_ratio":0.988453,"down_ratio":0.0},{"idle_ratio":0.998919,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999401,"down_ratio":0.0},{"idle_ratio":0.960788,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.937059,"down_ratio":0.0},{"idle_ratio":0.998738,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.06605849999999999,"clusters":[{"cpus":[{"idle_ratio":0.970721,"down_ratio":0.0},{"idle_ratio":0.890316,"down_ratio":0.0},{"idle_ratio":0.98611,"down_ratio":0.0},{"idle_ratio":0.982265,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.999342,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.970704,"down_ratio":0.0},{"idle_ratio":0.955443,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.10563,"clusters":[{"cpus":[{"idle_ratio":0.968974,"down_ratio":0.0},{"idle_ratio":0.893141,"down_ratio":0.0},{"idle_ratio":0.996806,"down_ratio":0.0},{"idle_ratio":0.99865,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998186,"down_ratio":0.0},{"idle_ratio":0.998925,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.996564,"down_ratio":0.0},{"idle_ratio":0.942999,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.06822790000000001,"clusters":[{"cpus":[{"idle_ratio":0.984169,"down_ratio":0.0},{"idle_ratio":0.956054,"down_ratio":0.0},{"idle_ratio":0.99748,"down_ratio":0.0},{"idle_ratio":0.999626,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998479,"down_ratio":0.0},{"idle_ratio":0.9988,"down_ratio":0.0},{"idle_ratio":0.999752,"down_ratio":0.0},{"idle_ratio":0.957863,"down_ratio":0.0},{"idle_ratio":0.932087,"down_ratio":0.0},{"idle_ratio":0.999981,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.179323,"clusters":[{"cpus":[{"idle_ratio":0.788789,"down_ratio":0.0},{"idle_ratio":0.839726,"down_ratio":0.0},{"idle_ratio":0.854379,"down_ratio":0.0},{"idle_ratio":0.834797,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.997589,"down_ratio":0.0},{"idle_ratio":0.949237,"down_ratio":0.0},{"idle_ratio":0.999276,"down_ratio":0.0},{"idle_ratio":0.99762,"down_ratio":0.0},{"idle_ratio":0.996548,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.105295,"clusters":[{"cpus":[{"idle_ratio":0.812441,"down_ratio":0.0},{"idle_ratio":0.805111,"down_ratio":0.0},{"idle_ratio":0.938964,"down_ratio":0.0},{"idle_ratio":0.93401,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.997091,"down_ratio":0.0},{"idle_ratio":0.996039,"down_ratio":0.0},{"idle_ratio":0.999895,"down_ratio":0.0},{"idle_ratio":0.972159,"down_ratio":0.0},{"idle_ratio":0.992441,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.11651099999999999,"clusters":[{"cpus":[{"idle_ratio":0.738614,"down_ratio":0.0},{"idle_ratio":0.814071,"down_ratio":0.0},{"idle_ratio":0.915861,"down_ratio":0.0},{"idle_ratio":0.959195,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.999628,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.970481,"down_ratio":0.0},{"idle_ratio":0.956045,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.120813,"clusters":[{"cpus":[{"idle_ratio":0.816731,"down_ratio":0.0},{"idle_ratio":0.867483,"down_ratio":0.0},{"idle_ratio":0.934853,"down_ratio":0.0},{"idle_ratio":0.905286,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.962733,"down_ratio":0.0},{"idle_ratio":0.992955,"down_ratio":0.0},{"idle_ratio":0.999471,"down_ratio":0.0},{"idle_ratio":0.944901,"down_ratio":0.0},{"idle_ratio":0.993838,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0927338,"clusters":[{"cpus":[{"idle_ratio":0.675641,"down_ratio":0.0},{"idle_ratio":0.8523,"down_ratio":0.0},{"idle_ratio":0.903378,"down_ratio":0.0},{"idle_ratio":0.978687,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998202,"down_ratio":0.0},{"idle_ratio":0.999192,"down_ratio":0.0},{"idle_ratio":0.999685,"down_ratio":0.0},{"idle_ratio":0.998992,"down_ratio":0.0},{"idle_ratio":0.99906,"down_ratio":0.0},{"idle_ratio":0.99972,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0984871,"clusters":[{"cpus":[{"idle_ratio":0.803317,"down_ratio":0.0},{"idle_ratio":0.791967,"down_ratio":0.0},{"idle_ratio":0.929396,"down_ratio":0.0},{"idle_ratio":0.959654,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999487,"down_ratio":0.0},{"idle_ratio":0.956528,"down_ratio":0.0},{"idle_ratio":0.999976,"down_ratio":0.0},{"idle_ratio":0.998835,"down_ratio":0.0},{"idle_ratio":0.961952,"down_ratio":0.0},{"idle_ratio":0.999418,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0892892,"clusters":[{"cpus":[{"idle_ratio":0.7589,"down_ratio":0.0},{"idle_ratio":0.875535,"down_ratio":0.0},{"idle_ratio":0.942464,"down_ratio":0.0},{"idle_ratio":0.974584,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999958,"down_ratio":0.0},{"idle_ratio":0.954019,"down_ratio":0.0},{"idle_ratio":0.999979,"down_ratio":0.0},{"idle_ratio":0.99966,"down_ratio":0.0},{"idle_ratio":0.998861,"down_ratio":0.0},{"idle_ratio":0.999979,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0725002,"clusters":[{"cpus":[{"idle_ratio":0.779485,"down_ratio":0.0},{"idle_ratio":0.933463,"down_ratio":0.0},{"idle_ratio":0.945127,"down_ratio":0.0},{"idle_ratio":0.984241,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998176,"down_ratio":0.0},{"idle_ratio":0.999963,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.955292,"down_ratio":0.0},{"idle_ratio":0.999413,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0711036,"clusters":[{"cpus":[{"idle_ratio":0.770156,"down_ratio":0.0},{"idle_ratio":0.9136,"down_ratio":0.0},{"idle_ratio":0.972624,"down_ratio":0.0},{"idle_ratio":0.992731,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999792,"down_ratio":0.0},{"idle_ratio":0.99801,"down_ratio":0.0},{"idle_ratio":0.99997,"down_ratio":0.0},{"idle_ratio":0.945007,"down_ratio":0.0},{"idle_ratio":0.997754,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0829026,"clusters":[{"cpus":[{"idle_ratio":0.865185,"down_ratio":0.0},{"idle_ratio":0.906614,"down_ratio":0.0},{"idle_ratio":0.949217,"down_ratio":0.0},{"idle_ratio":0.991636,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999888,"down_ratio":0.0},{"idle_ratio":0.998716,"down_ratio":0.0},{"idle_ratio":0.999627,"down_ratio":0.0},{"idle_ratio":0.968035,"down_ratio":0.0},{"idle_ratio":0.959826,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.13000299999999998,"clusters":[{"cpus":[{"idle_ratio":0.880157,"down_ratio":0.0},{"idle_ratio":0.812184,"down_ratio":0.0},{"idle_ratio":0.955759,"down_ratio":0.0},{"idle_ratio":0.979633,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999866,"down_ratio":0.0},{"idle_ratio":0.945972,"down_ratio":0.0},{"idle_ratio":0.998308,"down_ratio":0.0},{"idle_ratio":0.996186,"down_ratio":0.0},{"idle_ratio":0.996939,"down_ratio":0.0},{"idle_ratio":0.999958,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.129179,"clusters":[{"cpus":[{"idle_ratio":0.912782,"down_ratio":0.0},{"idle_ratio":0.917702,"down_ratio":0.0},{"idle_ratio":0.975834,"down_ratio":0.0},{"idle_ratio":0.98048,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.992996,"down_ratio":0.0},{"idle_ratio":0.918188,"down_ratio":0.0},{"idle_ratio":0.983747,"down_ratio":0.0},{"idle_ratio":0.956784,"down_ratio":0.0},{"idle_ratio":0.993366,"down_ratio":0.0},{"idle_ratio":0.99997,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.09953530000000001,"clusters":[{"cpus":[{"idle_ratio":0.895941,"down_ratio":0.0},{"idle_ratio":0.829383,"down_ratio":0.0},{"idle_ratio":0.965803,"down_ratio":0.0},{"idle_ratio":0.989715,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998153,"down_ratio":0.0},{"idle_ratio":0.95715,"down_ratio":0.0},{"idle_ratio":0.999585,"down_ratio":0.0},{"idle_ratio":0.999171,"down_ratio":0.0},{"idle_ratio":0.971837,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.108669,"clusters":[{"cpus":[{"idle_ratio":0.919069,"down_ratio":0.0},{"idle_ratio":0.858853,"down_ratio":0.0},{"idle_ratio":0.976398,"down_ratio":0.0},{"idle_ratio":0.997122,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999905,"down_ratio":0.0},{"idle_ratio":0.965471,"down_ratio":0.0},{"idle_ratio":0.999953,"down_ratio":0.0},{"idle_ratio":0.998782,"down_ratio":0.0},{"idle_ratio":0.967895,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.07497880000000001,"clusters":[{"cpus":[{"idle_ratio":0.898321,"down_ratio":0.0},{"idle_ratio":0.842332,"down_ratio":0.0},{"idle_ratio":0.964496,"down_ratio":0.0},{"idle_ratio":0.991828,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999533,"down_ratio":0.0},{"idle_ratio":0.998521,"down_ratio":0.0},{"idle_ratio":0.999875,"down_ratio":0.0},{"idle_ratio":0.973602,"down_ratio":0.0},{"idle_ratio":0.958433,"down_ratio":0.0},{"idle_ratio":0.999972,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0827499,"clusters":[{"cpus":[{"idle_ratio":0.924147,"down_ratio":0.0},{"idle_ratio":0.843101,"down_ratio":0.0},{"idle_ratio":0.967865,"down_ratio":0.0},{"idle_ratio":0.993443,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998717,"down_ratio":0.0},{"idle_ratio":0.998627,"down_ratio":0.0},{"idle_ratio":0.999325,"down_ratio":0.0},{"idle_ratio":0.966866,"down_ratio":0.0},{"idle_ratio":0.959294,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.113068,"clusters":[{"cpus":[{"idle_ratio":0.874661,"down_ratio":0.0},{"idle_ratio":0.835619,"down_ratio":0.0},{"idle_ratio":0.970557,"down_ratio":0.0},{"idle_ratio":0.987891,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.944332,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.997754,"down_ratio":0.0},{"idle_ratio":0.998957,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.06846970000000001,"clusters":[{"cpus":[{"idle_ratio":0.954887,"down_ratio":0.0},{"idle_ratio":0.916614,"down_ratio":0.0},{"idle_ratio":0.979464,"down_ratio":0.0},{"idle_ratio":0.991121,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999952,"down_ratio":0.0},{"idle_ratio":0.934336,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.958886,"down_ratio":0.0},{"idle_ratio":0.999047,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.108284,"clusters":[{"cpus":[{"idle_ratio":0.93017,"down_ratio":0.0},{"idle_ratio":0.937155,"down_ratio":0.0},{"idle_ratio":0.985431,"down_ratio":0.0},{"idle_ratio":0.989188,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999861,"down_ratio":0.0},{"idle_ratio":0.964202,"down_ratio":0.0},{"idle_ratio":0.999944,"down_ratio":0.0},{"idle_ratio":0.964696,"down_ratio":0.0},{"idle_ratio":0.994692,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0926476,"clusters":[{"cpus":[{"idle_ratio":0.911754,"down_ratio":0.0},{"idle_ratio":0.900026,"down_ratio":0.0},{"idle_ratio":0.981316,"down_ratio":0.0},{"idle_ratio":0.986868,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998786,"down_ratio":0.0},{"idle_ratio":0.998877,"down_ratio":0.0},{"idle_ratio":0.999968,"down_ratio":0.0},{"idle_ratio":0.958086,"down_ratio":0.0},{"idle_ratio":0.929872,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.06628400000000001,"clusters":[{"cpus":[{"idle_ratio":0.973596,"down_ratio":0.0},{"idle_ratio":0.89919,"down_ratio":0.0},{"idle_ratio":0.993112,"down_ratio":0.0},{"idle_ratio":0.995422,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999665,"down_ratio":0.0},{"idle_ratio":0.999164,"down_ratio":0.0},{"idle_ratio":0.999838,"down_ratio":0.0},{"idle_ratio":0.971085,"down_ratio":0.0},{"idle_ratio":0.956025,"down_ratio":0.0},{"idle_ratio":0.999959,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0745006,"clusters":[{"cpus":[{"idle_ratio":0.973698,"down_ratio":0.0},{"idle_ratio":0.911413,"down_ratio":0.0},{"idle_ratio":0.995934,"down_ratio":0.0},{"idle_ratio":0.995654,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998903,"down_ratio":0.0},{"idle_ratio":0.999029,"down_ratio":0.0},{"idle_ratio":0.999756,"down_ratio":0.0},{"idle_ratio":0.963779,"down_ratio":0.0},{"idle_ratio":0.961676,"down_ratio":0.0},{"idle_ratio":0.999891,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0744308,"clusters":[{"cpus":[{"idle_ratio":0.974387,"down_ratio":0.0},{"idle_ratio":0.895085,"down_ratio":0.0},{"idle_ratio":0.991305,"down_ratio":0.0},{"idle_ratio":0.995201,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999544,"down_ratio":0.0},{"idle_ratio":0.969372,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.957123,"down_ratio":0.0},{"idle_ratio":0.999927,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0833484,"clusters":[{"cpus":[{"idle_ratio":0.968019,"down_ratio":0.0},{"idle_ratio":0.909165,"down_ratio":0.0},{"idle_ratio":0.976918,"down_ratio":0.0},{"idle_ratio":0.990118,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999977,"down_ratio":0.0},{"idle_ratio":0.965407,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.962623,"down_ratio":0.0},{"idle_ratio":0.999165,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0665046,"clusters":[{"cpus":[{"idle_ratio":0.928985,"down_ratio":0.0},{"idle_ratio":0.927078,"down_ratio":0.0},{"idle_ratio":0.975499,"down_ratio":0.0},{"idle_ratio":0.990859,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999117,"down_ratio":0.0},{"idle_ratio":0.956313,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.999661,"down_ratio":0.0},{"idle_ratio":0.972799,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0969828,"clusters":[{"cpus":[{"idle_ratio":0.745325,"down_ratio":0.0},{"idle_ratio":0.952488,"down_ratio":0.0},{"idle_ratio":0.97237,"down_ratio":0.0},{"idle_ratio":0.978054,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999962,"down_ratio":0.0},{"idle_ratio":0.998829,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.939624,"down_ratio":0.0},{"idle_ratio":0.99606,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0764842,"clusters":[{"cpus":[{"idle_ratio":0.978361,"down_ratio":0.0},{"idle_ratio":0.94144,"down_ratio":0.0},{"idle_ratio":0.983954,"down_ratio":0.0},{"idle_ratio":0.997152,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999253,"down_ratio":0.0},{"idle_ratio":0.998577,"down_ratio":0.0},{"idle_ratio":0.999942,"down_ratio":0.0},{"idle_ratio":0.931289,"down_ratio":0.0},{"idle_ratio":0.956872,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.06626130000000001,"clusters":[{"cpus":[{"idle_ratio":0.96976,"down_ratio":0.0},{"idle_ratio":0.913685,"down_ratio":0.0},{"idle_ratio":0.990255,"down_ratio":0.0},{"idle_ratio":0.986936,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999811,"down_ratio":0.0},{"idle_ratio":0.998296,"down_ratio":0.0},{"idle_ratio":0.99992,"down_ratio":0.0},{"idle_ratio":0.96021,"down_ratio":0.0},{"idle_ratio":0.962161,"down_ratio":0.0},{"idle_ratio":0.999975,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.09760980000000001,"clusters":[{"cpus":[{"idle_ratio":0.93528,"down_ratio":0.0},{"idle_ratio":0.906105,"down_ratio":0.0},{"idle_ratio":0.994548,"down_ratio":0.0},{"idle_ratio":0.99858,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.98375,"down_ratio":0.0},{"idle_ratio":0.993273,"down_ratio":0.0},{"idle_ratio":0.998312,"down_ratio":0.0},{"idle_ratio":0.933172,"down_ratio":0.0},{"idle_ratio":0.994671,"down_ratio":0.0},{"idle_ratio":0.999936,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0950802,"clusters":[{"cpus":[{"idle_ratio":0.859932,"down_ratio":0.0},{"idle_ratio":0.98681,"down_ratio":0.0},{"idle_ratio":0.990705,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999987,"down_ratio":0.0},{"idle_ratio":0.945675,"down_ratio":0.0},{"idle_ratio":0.99924,"down_ratio":0.0},{"idle_ratio":0.999084,"down_ratio":0.0},{"idle_ratio":0.997474,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.0685772,"clusters":[{"cpus":[{"idle_ratio":0.960136,"down_ratio":0.0},{"idle_ratio":0.931797,"down_ratio":0.0},{"idle_ratio":0.980292,"down_ratio":0.0},{"idle_ratio":0.997082,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.999581,"down_ratio":0.0},{"idle_ratio":0.934954,"down_ratio":0.0},{"idle_ratio":0.999949,"down_ratio":0.0},{"idle_ratio":0.999011,"down_ratio":0.0},{"idle_ratio":0.958633,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]},{"processor_combined_power_w":0.12183100000000001,"clusters":[{"cpus":[{"idle_ratio":0.964822,"down_ratio":0.0},{"idle_ratio":0.777431,"down_ratio":0.0},{"idle_ratio":0.990285,"down_ratio":0.0},{"idle_ratio":0.997453,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.998945,"down_ratio":0.0},{"idle_ratio":0.99646,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0},{"idle_ratio":0.945261,"down_ratio":0.0},{"idle_ratio":0.999148,"down_ratio":0.0},{"idle_ratio":1.0,"down_ratio":0.0}]},{"cpus":[{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0},{"idle_ratio":0.0,"down_ratio":1.0}]}]}]"""

CLEAN_IDLE_RECORDS = json.loads(CLEAN_IDLE_RECORDS_JSON)


def production_extension_mapping() -> dict:
    return {
        "schema_version": EXTENSION_SCHEMA_VERSION,
        "policy_version": "idle-admission-core-v1",
        "claim_bearing": True,
        "cpu_criteria": {
            "cpu_busy_ratio_p95_max": 0.5,
            "processor_combined_power_w_p95_max": 1.0,
            "min_samples": 30,
            "on_missing_telemetry": "fail",
        },
        "adapter_wattage": {"require_known_wattage": True},
        "neg8_bracket": {
            "require_bracket": True,
            "max_abs_delta_j": 0.05,
            "max_rel_delta": 0.25,
        },
    }


def exploratory_extension_mapping() -> dict:
    mapping = production_extension_mapping()
    mapping["claim_bearing"] = False
    mapping["cpu_criteria"]["on_missing_telemetry"] = "flag"
    mapping["adapter_wattage"]["require_known_wattage"] = False
    mapping["neg8_bracket"]["require_bracket"] = False
    return mapping


def production_criteria(**overrides) -> CpuAdmissionCriteria:
    values = {
        "cpu_busy_ratio_p95_max": 0.5,
        "processor_combined_power_w_p95_max": 1.0,
        "min_samples": 30,
        "on_missing_telemetry": "fail",
    }
    values.update(overrides)
    return CpuAdmissionCriteria(**values)


def synthetic_records(
    count: int, *, busy: float, power_w: float
) -> list[dict]:
    return [
        {
            "processor_combined_power_w": power_w,
            "clusters": [
                {
                    "cpus": [
                        {"idle_ratio": 1.0 - busy, "down_ratio": 0.0},
                        {"idle_ratio": 0.99, "down_ratio": 0.0},
                    ]
                },
                # A parked cluster must never read as busy.
                {"cpus": [{"idle_ratio": 0.0, "down_ratio": 1.0}]},
            ],
        }
        for _ in range(count)
    ]


def observation(
    watts, description="140W USB-C Power Adapter", power_source="AC Power", source="obs"
) -> dict:
    return {
        "source": source,
        "adapter_watts": watts,
        "adapter_description": description,
        "power_source": power_source,
    }


class ExtensionParsingTests(unittest.TestCase):
    def test_production_extension_parses_and_hash_binds(self) -> None:
        extension = IdleAdmissionExtension.from_mapping(
            production_extension_mapping(), profile="production"
        )
        self.assertTrue(extension.claim_bearing)
        self.assertEqual(extension.cpu_criteria.min_samples, 30)
        first = extension.sha256()
        self.assertEqual(first, extension.sha256())
        loosened = production_extension_mapping()
        loosened["cpu_criteria"]["cpu_busy_ratio_p95_max"] = 0.6
        other = IdleAdmissionExtension.from_mapping(loosened, profile="production")
        self.assertNotEqual(first, other.sha256())

    def test_exploratory_extension_parses(self) -> None:
        extension = IdleAdmissionExtension.from_mapping(
            exploratory_extension_mapping(), profile="exploratory"
        )
        self.assertFalse(extension.claim_bearing)
        self.assertEqual(extension.cpu_criteria.on_missing_telemetry, "flag")

    def test_production_rejects_every_loosened_fail_closed_field(self) -> None:
        for mutate in (
            lambda m: m.update(claim_bearing=False),
            lambda m: m["cpu_criteria"].update(on_missing_telemetry="flag"),
            lambda m: m["adapter_wattage"].update(require_known_wattage=False),
            lambda m: m["neg8_bracket"].update(require_bracket=False),
        ):
            mapping = production_extension_mapping()
            mutate(mapping)
            with self.assertRaises(IdleAdmissionPolicyError):
                IdleAdmissionExtension.from_mapping(mapping, profile="production")

    def test_exploratory_must_be_non_claim_bearing(self) -> None:
        mapping = exploratory_extension_mapping()
        mapping["claim_bearing"] = True
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(mapping, profile="exploratory")

    def test_unknown_missing_keys_and_bad_versions_fail_closed(self) -> None:
        unknown = production_extension_mapping()
        unknown["surprise"] = True
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(unknown, profile="production")
        missing = production_extension_mapping()
        del missing["neg8_bracket"]
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(missing, profile="production")
        wrong_version = production_extension_mapping()
        wrong_version["schema_version"] = "joulewise.idle_admission_extension.v0"
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(wrong_version, profile="production")
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(
                production_extension_mapping(), profile="mystery"
            )
        with self.assertRaises(IdleAdmissionPolicyError):
            IdleAdmissionExtension.from_mapping(None, profile="production")


class CpuIdleAdmissionTests(unittest.TestCase):
    def test_clean_corpus_evidence_passes(self) -> None:
        result = evaluate_cpu_idle_admission(
            CLEAN_IDLE_RECORDS, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["schema_version"], CPU_ADMISSION_SCHEMA)
        self.assertEqual(result["decision"], "admitted")
        self.assertTrue(result["admitted"])
        self.assertEqual(result["conditions"], [])
        self.assertEqual(result["sample_count"], 40)
        self.assertLess(result["cpu_busy_ratio_p95"], 0.5)
        self.assertLess(result["processor_combined_power_w_p95"], 1.0)

    def test_gpu_idle_but_cpu_active_fails(self) -> None:
        result = evaluate_cpu_idle_admission(
            synthetic_records(40, busy=0.9, power_w=0.15),
            production_criteria(),
            gpu_admitted=True,
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn("cpu_busy_ratio_p95_exceeded", result["conditions"])

    def test_combined_power_active_fails(self) -> None:
        result = evaluate_cpu_idle_admission(
            synthetic_records(40, busy=0.05, power_w=5.0),
            production_criteria(),
            gpu_admitted=True,
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn(
            "processor_combined_power_w_p95_exceeded", result["conditions"]
        )

    def test_missing_telemetry_fails_closed_under_production(self) -> None:
        for records in (None, []):
            result = evaluate_cpu_idle_admission(
                records, production_criteria(), gpu_admitted=True
            )
            self.assertEqual(result["decision"], "failed")
            self.assertIn("cpu_baseline_telemetry_missing", result["conditions"])

    def test_missing_telemetry_is_flagged_under_exploratory(self) -> None:
        result = evaluate_cpu_idle_admission(
            None,
            production_criteria(on_missing_telemetry="flag"),
            gpu_admitted=True,
        )
        self.assertEqual(result["decision"], "flagged")
        self.assertFalse(result["admitted"])
        self.assertIn("cpu_baseline_telemetry_missing", result["conditions"])

    def test_malformed_record_fails_closed(self) -> None:
        records = copy.deepcopy(synthetic_records(40, busy=0.05, power_w=0.15))
        del records[7]["clusters"][0]["cpus"][0]["idle_ratio"]
        result = evaluate_cpu_idle_admission(
            records, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_malformed", result["conditions"])
        nonfinite = copy.deepcopy(synthetic_records(40, busy=0.05, power_w=0.15))
        nonfinite[3]["processor_combined_power_w"] = float("nan")
        result = evaluate_cpu_idle_admission(
            nonfinite, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_malformed", result["conditions"])

    def test_insufficient_samples_fail_closed_under_production(self) -> None:
        records = synthetic_records(10, busy=0.05, power_w=0.15)
        result = evaluate_cpu_idle_admission(
            records, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn(
            "cpu_baseline_sample_count_insufficient", result["conditions"]
        )
        flagged = evaluate_cpu_idle_admission(
            records,
            production_criteria(on_missing_telemetry="flag"),
            gpu_admitted=True,
        )
        self.assertEqual(flagged["decision"], "flagged")

    def test_gpu_admission_is_still_required(self) -> None:
        records = synthetic_records(40, busy=0.05, power_w=0.15)
        failed = evaluate_cpu_idle_admission(
            records,
            production_criteria(on_missing_telemetry="flag"),
            gpu_admitted=False,
        )
        self.assertEqual(failed["decision"], "failed")
        self.assertIn("gpu_idle_admission_not_passed", failed["conditions"])
        unknown = evaluate_cpu_idle_admission(
            records, production_criteria(), gpu_admitted=None
        )
        self.assertEqual(unknown["decision"], "failed")
        self.assertIn("gpu_idle_admission_unknown", unknown["conditions"])

    def test_exactly_on_threshold_passes(self) -> None:
        records = synthetic_records(40, busy=0.5, power_w=1.0)
        result = evaluate_cpu_idle_admission(
            records, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["decision"], "admitted")
        over = evaluate_cpu_idle_admission(
            synthetic_records(40, busy=0.5, power_w=math.nextafter(1.0, math.inf)),
            production_criteria(),
            gpu_admitted=True,
        )
        self.assertEqual(over["decision"], "failed")

    def test_parked_cluster_never_reads_busy(self) -> None:
        records = [
            {
                "processor_combined_power_w": 0.1,
                "clusters": [{"cpus": [{"idle_ratio": 0.0, "down_ratio": 1.0}]}],
            }
            for _ in range(40)
        ]
        result = evaluate_cpu_idle_admission(
            records, production_criteria(), gpu_admitted=True
        )
        self.assertEqual(result["decision"], "admitted")
        self.assertEqual(result["cpu_busy_ratio_p95"], 0.0)


class AdapterWattageContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.require_known = AdapterWattagePolicy(require_known_wattage=True)
        self.lenient = AdapterWattagePolicy(require_known_wattage=False)

    def test_stable_wattage_passes(self) -> None:
        result = evaluate_adapter_wattage_continuity(
            [observation(140.0), observation(140.0), observation(140.0)],
            self.require_known,
        )
        self.assertEqual(result["schema_version"], ADAPTER_CONTINUITY_SCHEMA)
        self.assertEqual(result["decision"], "stable")
        self.assertTrue(result["stable"])
        self.assertEqual(result["conditions"], [])
        self.assertEqual(result["distinct_adapter_watts"], [140.0])

    def test_140_70_140_precedent_is_flagged_with_transitions(self) -> None:
        result = evaluate_adapter_wattage_continuity(
            [observation(140.0), observation(70.0), observation(140.0)],
            self.require_known,
        )
        self.assertEqual(result["decision"], "flagged")
        self.assertIn("adapter_wattage_discontinuity", result["conditions"])
        self.assertEqual(
            [
                (row["from_watts"], row["to_watts"])
                for row in result["wattage_transitions"]
            ],
            [(140.0, 70.0), (70.0, 140.0)],
        )

    def test_description_change_is_flagged(self) -> None:
        result = evaluate_adapter_wattage_continuity(
            [
                observation(140.0, description="140W USB-C Power Adapter"),
                observation(140.0, description="96W USB-C Power Adapter"),
            ],
            self.require_known,
        )
        self.assertEqual(result["decision"], "flagged")
        self.assertIn("adapter_description_changed", result["conditions"])

    def test_power_source_change_is_flagged(self) -> None:
        result = evaluate_adapter_wattage_continuity(
            [
                observation(140.0, power_source="AC Power"),
                observation(140.0, power_source="Battery Power"),
            ],
            self.require_known,
        )
        self.assertEqual(result["decision"], "flagged")
        self.assertIn("adapter_power_source_changed", result["conditions"])

    def test_unknown_wattage_fails_closed_under_production(self) -> None:
        rows = [observation(140.0), observation(None)]
        failed = evaluate_adapter_wattage_continuity(rows, self.require_known)
        self.assertEqual(failed["decision"], "failed")
        self.assertIn("adapter_wattage_unknown", failed["conditions"])
        flagged = evaluate_adapter_wattage_continuity(rows, self.lenient)
        self.assertEqual(flagged["decision"], "flagged")

    def test_no_observations_fail_closed_under_production(self) -> None:
        result = evaluate_adapter_wattage_continuity([], self.require_known)
        self.assertEqual(result["decision"], "failed")
        self.assertIn("adapter_observations_missing", result["conditions"])

    def test_extract_adapter_observation_normalizes_fail_soft(self) -> None:
        row = extract_adapter_observation(
            {"adapter_watts": 140, "adapter_description": "140W USB-C Power Adapter"},
            source="bundle:environment",
            power_source="AC Power",
        )
        self.assertEqual(row["adapter_watts"], 140.0)
        self.assertEqual(row["power_source"], "AC Power")
        for bad in (None, {"adapter_watts": True}, {"adapter_watts": -5}, {}):
            row = extract_adapter_observation(bad, source="s")
            self.assertIsNone(row["adapter_watts"])
            self.assertIsNone(row["adapter_description"])


class Neg8BracketTests(unittest.TestCase):
    def setUp(self) -> None:
        # 8.0 and the 0.5 J / 0.0625 tolerances are exactly representable,
        # so the exactly-on-threshold case is exact in IEEE-754.
        self.policy = Neg8BracketPolicy(
            require_bracket=True, max_abs_delta_j=0.5, max_rel_delta=0.0625
        )

    def test_exactly_on_both_thresholds_passes(self) -> None:
        result = evaluate_neg8_bracket(8.0, 8.5, self.policy)
        self.assertEqual(result["schema_version"], NEG8_BRACKET_SCHEMA)
        self.assertEqual(result["decision"], "passed")
        self.assertTrue(result["passed"])
        self.assertEqual(result["conditions"], [])
        self.assertEqual(result["abs_delta_j"], 0.5)

    def test_one_ulp_over_fails(self) -> None:
        result = evaluate_neg8_bracket(
            8.0, math.nextafter(8.5, math.inf), self.policy
        )
        self.assertEqual(result["decision"], "failed")
        self.assertIn("neg8_bracket_abs_delta_exceeded", result["conditions"])
        self.assertIn("neg8_bracket_rel_delta_exceeded", result["conditions"])

    def test_absolute_only_satisfied_fails(self) -> None:
        policy = Neg8BracketPolicy(
            require_bracket=True, max_abs_delta_j=1.0, max_rel_delta=0.01
        )
        result = evaluate_neg8_bracket(8.0, 8.5, policy)
        self.assertEqual(result["decision"], "failed")
        self.assertEqual(
            result["conditions"], ["neg8_bracket_rel_delta_exceeded"]
        )

    def test_relative_only_satisfied_fails(self) -> None:
        policy = Neg8BracketPolicy(
            require_bracket=True, max_abs_delta_j=0.25, max_rel_delta=0.25
        )
        result = evaluate_neg8_bracket(8.0, 8.5, policy)
        self.assertEqual(result["decision"], "failed")
        self.assertEqual(
            result["conditions"], ["neg8_bracket_abs_delta_exceeded"]
        )

    def test_missing_bracket_fails_closed_when_required(self) -> None:
        for start, end in ((None, 8.5), (8.0, None), (None, None)):
            result = evaluate_neg8_bracket(start, end, self.policy)
            self.assertEqual(result["decision"], "failed")
            self.assertIn("neg8_bracket_missing", result["conditions"])
        lenient = Neg8BracketPolicy(
            require_bracket=False, max_abs_delta_j=0.5, max_rel_delta=0.0625
        )
        flagged = evaluate_neg8_bracket(None, None, lenient)
        self.assertEqual(flagged["decision"], "flagged")

    def test_invalid_reference_fails_closed(self) -> None:
        for start, end in ((0.0, 8.5), (-1.0, 8.5), (float("nan"), 8.5), (8.0, float("inf"))):
            result = evaluate_neg8_bracket(start, end, self.policy)
            self.assertEqual(result["decision"], "failed")
            self.assertIn("neg8_bracket_reference_invalid", result["conditions"])


if __name__ == "__main__":
    unittest.main()
