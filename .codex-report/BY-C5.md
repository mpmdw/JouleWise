## PROGRESS

- Slice 3 encoding step implemented and new focused tests green. Five paths changed: plan_inputs.py, driver_lane.py, test_plan_inputs.py, test_b6_plan_render.py, this report. No commit/push attempted (director owns Git writes).
- Done: BYTES native q/headroom encoding from registered sizing_b5.json pack disk_derivation; count is real planner stages including optional spares. DriverLane records terms/flag in metadata, passes only native fields to the closed writer. Missing/malformed P records disk.budget_missing and returns LaneMissing, never Refused.
- Done: real DriverLane → plan_inputs.build → plan.write_window_plan → disk.measure/judge synthetic BYTES pack: exact P requirement, REFUSE at P-1, PASS at P (1 test, exit 0). Plan-input module 6 tests green (includes alpha/beta/gamma unchanged inputs and spares); session-wrapper module 6 tests green. Sealed inventory diffs empty; git diff --check passes.
- Done: existing alpha/beta/gamma production regression finished (1 test, 6 failing subtests, 131.197 s, exit 1). All six passed budget assertions, then failed unchanged check_readers courier-path equality: actual /private/tmp/... versus expected /tmp/.... This is the local-route environmental category; no fix attempted.
- Next: replay CLI/tests inside bytes_gates; final per-pack q/headroom evidence; remaining targeted checks and finish report. BY-SLOTS must supply real draft launch authority and sizing/P (draft trees currently intentionally arm_attachments={}).
- Open: BY-H2 native raw_allocated_bytes producer, director-run real 9+1 replay and CI. No prohibited session trees accessed. Current head f73c62198, local branch by-c5, intended director destination lane/2026-10-22-bytes-c5-gates.

## SUMMARY

Stopped-session gates fix is already present and reproduced before/after.
C5 now replaces the 150 GiB reserve with H-DISK-RULING exact rational P.
Rates derive from one raw bundle's allocated byte receipts, without altering retained_bytes.
All twelve pass packs print both bases, per-model counts and allowances, WAIT, fixed, c and P.
Missing raw receipts flag disk.raw_bytes_missing; no available rates makes disk unavailable.
All 14 bytes_gates tests pass; H rates agree with disk_h at the required 1e-6 relative bar.
Pack encoding and synthetic end-to-end hazard verification are implemented in slice 3; replay and final reporting remain.
Only authorized source/test/report files changed; no hardware operation or Git write ran.
Slice 3 implements exact native encoding and proves P boundaries through the real planner/hazard; replay remains pending.

## GATES FIX

Baseline 8386706f2 preserves the author of 66b330b15, as directed. Evidence directory: `/tmp/jwtmp-byc5-evidence.zze_7sty` (temporary, not an enduring source). Both invocations use `/opt/homebrew/bin/python3.13 -B`, identical data-branch MEASUREMENTS and native export, and the repository kit plan. The old script was extracted with `git show bda481d5a:scripts/bytes_gates.py`.

- Before: exit 1, stderr `bytes_gates: [<class 'decimal.ConversionSyntax'>]`, no output JSON.
- After (8386706f2): exit 2, empty stderr, output JSON written. Exit 2 reflects failing computed lines on the stopped session; it is not a program fault.
- Sole production caller: scripts/bytes_h_session.py desk maps 1 to unavailable, 2 to fail, 0 to pass, other codes to program_fault, and its CLI returns gates_exit unchanged. Tests invoke bytes_gates directly; scripts/bytes_mac_kit.py only documents its command. Census: `rg -n 'bytes_gates|gates_exit' --glob '!*.json' --glob '!*.csv' --glob '!*.md' --glob '!*.html' .`.

## P PER SUB-PACK

Slice 2 real-H command (extracted data files only in TMPDIR):

`/opt/homebrew/bin/python3.13 -B scripts/bytes_gates.py --runs /tmp/jwtmp-byc5-disk-03yxkpvg/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/jwtmp-byc5-disk-03yxkpvg/MEASUREMENTS.raw.json --disk-evidence /tmp/jwtmp-byc5-disk-03yxkpvg/disk_h.json --out /tmp/jwtmp-byc5-disk-03yxkpvg/C5.json`

Exit 2 from stopped completeness gates; empty stderr; no ConversionSyntax. Rates use exact fractions of raw allocated bytes over measured decimal seconds. Agreement bar is 1e-6 relative per director ruling 1: stream 1805538.5168827055 vs disk_h 1805538.5168827053 B/s (relative difference 2.220446049250313e-16), wall 1285759.0452694688 vs 1285759.0452694688 B/s (relative difference 0). Optional --disk-evidence discloses BY-0 c_implied_alloc alongside c=2, hashes the additional source, and changes no P or refusal. With no evidence file, measured_c=null explicitly leaves the measurement unavailable.

```json
{
  "bytes-s1-p1": {
    "T_stream_max_s": 96.39069404196925,
    "disk_derivation": {
      "B_bytes": 21883930645,
      "allowances_by_model": {
        "qwen3-1p7b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 10891394915588033884894765753299
          },
          "stream_allowance_s": {
            "denominator": 8163178181648254000000000000000,
            "numerator": 783145273507629421873856021669061
          }
        },
        "qwen3-4b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 20407945454120635000000000000,
            "numerator": 2830923851452033592289994193241
          },
          "stream_allowance_s": {
            "denominator": 408158909082412700000000000000,
            "numerator": 40649626600132261505455935703143
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 71034160574,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 21883930645,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 1306108509063720640000000000000,
        "numerator": 15830616605462560281372141940369533
      },
      "wall_basis_bytes": 21697490999,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 55102232650623631667288407384551
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-1p7b": {
        "T_stream_max_s": 92.84918262495194,
        "bytes_per_member": 324861952,
        "est_minutes": 111.18417640400074,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 129.12722992897034,
        "request_mean_s": 2.9647043704986573,
        "runs_measured": 5
      },
      "qwen3-4b": {
        "T_stream_max_s": 96.39069404196925,
        "bytes_per_member": 328941568,
        "est_minutes": 115.5972910083914,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 134.25253896713258,
        "request_mean_s": 5.9694184303283695,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 42023792640,
    "required_free_bytes": 71034160574
  },
  "bytes-s1-p2": {
    "T_stream_max_s": 96.39069404196925,
    "disk_derivation": {
      "B_bytes": 21883930645,
      "allowances_by_model": {
        "qwen3-1p7b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 10891394915588033884894765753299
          },
          "stream_allowance_s": {
            "denominator": 8163178181648254000000000000000,
            "numerator": 783145273507629421873856021669061
          }
        },
        "qwen3-4b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 20407945454120635000000000000,
            "numerator": 2830923851452033592289994193241
          },
          "stream_allowance_s": {
            "denominator": 408158909082412700000000000000,
            "numerator": 40649626600132261505455935703143
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 71034160574,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 21883930645,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 1306108509063720640000000000000,
        "numerator": 15830616605462560281372141940369533
      },
      "wall_basis_bytes": 21697490999,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 55102232650623631667288407384551
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-1p7b": {
        "T_stream_max_s": 92.84918262495194,
        "bytes_per_member": 324861952,
        "est_minutes": 111.18417640400074,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 129.12722992897034,
        "request_mean_s": 2.9647043704986573,
        "runs_measured": 5
      },
      "qwen3-4b": {
        "T_stream_max_s": 96.39069404196925,
        "bytes_per_member": 328941568,
        "est_minutes": 115.5972910083914,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 134.25253896713258,
        "request_mean_s": 5.9694184303283695,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 42023792640,
    "required_free_bytes": 71034160574
  },
  "bytes-s2-p1": {
    "T_stream_max_s": 102.24723962508142,
    "disk_derivation": {
      "B_bytes": 22967763886,
      "allowances_by_model": {
        "qwen3-30b-a3b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 2400934759308310000000000000,
            "numerator": 349955922340690594900650014553
          },
          "stream_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 8200756288643801927698276077861
          }
        },
        "qwen3-8b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 5101986363530158750000000000,
            "numerator": 745597533139678689481931054499
          },
          "stream_allowance_s": {
            "denominator": 816317818164825400000000000000,
            "numerator": 86264603879409717683237745499413
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 73201827056,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 22841465166,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3304657500529636404465196911351201
      },
      "wall_basis_bytes": 22967763886,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 58328175787467973675844917065597
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-30b-a3b": {
        "T_stream_max_s": 97.23176879191305,
        "bytes_per_member": 329908224,
        "est_minutes": 121.46516441284938,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 141.0673777580261,
        "request_mean_s": 6.771204948425293,
        "runs_measured": 5
      },
      "qwen3-8b": {
        "T_stream_max_s": 102.24723962508142,
        "bytes_per_member": 334405632,
        "est_minutes": 121.78223016387842,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 141.43561201095582,
        "request_mean_s": 9.802446508407593,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 42549309440,
    "required_free_bytes": 73201827056
  },
  "bytes-s2-p2": {
    "T_stream_max_s": 102.24723962508142,
    "disk_derivation": {
      "B_bytes": 22967763886,
      "allowances_by_model": {
        "qwen3-30b-a3b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 2400934759308310000000000000,
            "numerator": 349955922340690594900650014553
          },
          "stream_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 8200756288643801927698276077861
          }
        },
        "qwen3-8b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 5101986363530158750000000000,
            "numerator": 745597533139678689481931054499
          },
          "stream_allowance_s": {
            "denominator": 816317818164825400000000000000,
            "numerator": 86264603879409717683237745499413
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 73201827056,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 22841465166,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3304657500529636404465196911351201
      },
      "wall_basis_bytes": 22967763886,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 58328175787467973675844917065597
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-30b-a3b": {
        "T_stream_max_s": 97.23176879191305,
        "bytes_per_member": 329908224,
        "est_minutes": 121.46516441284938,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 141.0673777580261,
        "request_mean_s": 6.771204948425293,
        "runs_measured": 5
      },
      "qwen3-8b": {
        "T_stream_max_s": 102.24723962508142,
        "bytes_per_member": 334405632,
        "est_minutes": 121.78223016387842,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 141.43561201095582,
        "request_mean_s": 9.802446508407593,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 42549309440,
    "required_free_bytes": 73201827056
  },
  "bytes-s3-p1": {
    "T_stream_max_s": 112.22990612499416,
    "disk_derivation": {
      "B_bytes": 24709054674,
      "allowances_by_model": {
        "qwen3-14b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 6474217913479255592038768844679
          },
          "stream_allowance_s": {
            "denominator": 408158909082412700000000000000,
            "numerator": 47330398691245516925420598873141
          }
        },
        "qwen3-next-80b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 6545344197423385472008594783023
          },
          "stream_allowance_s": {
            "denominator": 163263563632965080000000000000,
            "numerator": 16914145208797081356146249228721
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 76684408632,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 24053464961,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 10448868072509765120000000000,
        "numerator": 139200288283987826528273116525641
      },
      "wall_basis_bytes": 24709054674,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 62750300451441859415368376842833
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-14b": {
        "T_stream_max_s": 112.22990612499416,
        "bytes_per_member": 345513984,
        "est_minutes": 132.1833598265691,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 153.5152901172638,
        "request_mean_s": 17.414829206466674,
        "runs_measured": 5
      },
      "qwen3-next-80b": {
        "T_stream_max_s": 100.21633237495553,
        "bytes_per_member": 333053952,
        "est_minutes": 133.63553695581578,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 155.20182156562805,
        "request_mean_s": 9.04508671760559,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 43262013440,
    "required_free_bytes": 76684408632
  },
  "bytes-s3-p2": {
    "T_stream_max_s": 112.22990612499416,
    "disk_derivation": {
      "B_bytes": 24709054674,
      "allowances_by_model": {
        "qwen3-14b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 6474217913479255592038768844679
          },
          "stream_allowance_s": {
            "denominator": 408158909082412700000000000000,
            "numerator": 47330398691245516925420598873141
          }
        },
        "qwen3-next-80b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 6545344197423385472008594783023
          },
          "stream_allowance_s": {
            "denominator": 163263563632965080000000000000,
            "numerator": 16914145208797081356146249228721
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 76684408632,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 24053464961,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 10448868072509765120000000000,
        "numerator": 139200288283987826528273116525641
      },
      "wall_basis_bytes": 24709054674,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 62750300451441859415368376842833
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-14b": {
        "T_stream_max_s": 112.22990612499416,
        "bytes_per_member": 345513984,
        "est_minutes": 132.1833598265691,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 153.5152901172638,
        "request_mean_s": 17.414829206466674,
        "runs_measured": 5
      },
      "qwen3-next-80b": {
        "T_stream_max_s": 100.21633237495553,
        "bytes_per_member": 333053952,
        "est_minutes": 133.63553695581578,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 155.20182156562805,
        "request_mean_s": 9.04508671760559,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 43262013440,
    "required_free_bytes": 76684408632
  },
  "bytes-s4-p1": {
    "T_stream_max_s": 142.9448628750397,
    "disk_derivation": {
      "B_bytes": 27547300445,
      "allowances_by_model": {
        "qwen3-32b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 16263008657228787896484291177243
          },
          "stream_allowance_s": {
            "denominator": 163263563632965080000000000000,
            "numerator": 24115037219132903847314523041463
          }
        },
        "qwen3-8b-8bit": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 12501684878568190919754877589643
          },
          "stream_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 9024890800101023766671030234691
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 82360900174,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 27547300445,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3985488337822868723554195491770433
      },
      "wall_basis_bytes": 26855538139,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 68201439079425252791657259865797
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-32b": {
        "T_stream_max_s": 142.9448628750397,
        "bytes_per_member": 377110528,
        "est_minutes": 166.01998526535766,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 192.81251616477968,
        "request_mean_s": 39.618006801605226,
        "runs_measured": 5
      },
      "qwen3-8b-8bit": {
        "T_stream_max_s": 107.0052588749677,
        "bytes_per_member": 340156416,
        "est_minutes": 127.62272855394922,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 148.21865797042847,
        "request_mean_s": 14.76427903175354,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 45196963840,
    "required_free_bytes": 82360900174
  },
  "bytes-s4-p2": {
    "T_stream_max_s": 142.9448628750397,
    "disk_derivation": {
      "B_bytes": 27547300445,
      "allowances_by_model": {
        "qwen3-32b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 16263008657228787896484291177243
          },
          "stream_allowance_s": {
            "denominator": 163263563632965080000000000000,
            "numerator": 24115037219132903847314523041463
          }
        },
        "qwen3-8b-8bit": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 12501684878568190919754877589643
          },
          "stream_allowance_s": {
            "denominator": 81631781816482540000000000000,
            "numerator": 9024890800101023766671030234691
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 82360900174,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 27547300445,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3985488337822868723554195491770433
      },
      "wall_basis_bytes": 26855538139,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 68201439079425252791657259865797
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen3-32b": {
        "T_stream_max_s": 142.9448628750397,
        "bytes_per_member": 377110528,
        "est_minutes": 166.01998526535766,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 192.81251616477968,
        "request_mean_s": 39.618006801605226,
        "runs_measured": 5
      },
      "qwen3-8b-8bit": {
        "T_stream_max_s": 107.0052588749677,
        "bytes_per_member": 340156416,
        "est_minutes": 127.62272855394922,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 148.21865797042847,
        "request_mean_s": 14.76427903175354,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 45196963840,
    "required_free_bytes": 82360900174
  },
  "bytes-s5-p1": {
    "T_stream_max_s": 201.49829895899165,
    "disk_derivation": {
      "B_bytes": 22901363715,
      "allowances_by_model": {
        "llama-70b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 130610850906372064000000000000,
            "numerator": 35551270022896312928786107333377
          },
          "stream_allowance_s": {
            "denominator": 261221701812744128000000000000,
            "numerator": 54020413412194470005471826214809
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 73069026714,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 22901363715,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3313323502885796113375260121643283
      },
      "wall_basis_bytes": 21700998244,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 2612217018127441280000000000,
        "numerator": 44088911629161349056129245198997
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "llama-70b": {
        "T_stream_max_s": 201.49829895899165,
        "bytes_per_member": 439197696,
        "est_minutes": 226.8269301273516,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 263.43256844580173,
        "request_mean_s": 82.55686520040035,
        "runs_measured": 16
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 31293501440,
    "required_free_bytes": 73069026714
  },
  "bytes-s5-p2": {
    "T_stream_max_s": 201.49829895899165,
    "disk_derivation": {
      "B_bytes": 22901363715,
      "allowances_by_model": {
        "llama-70b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 130610850906372064000000000000,
            "numerator": 35551270022896312928786107333377
          },
          "stream_allowance_s": {
            "denominator": 261221701812744128000000000000,
            "numerator": 54020413412194470005471826214809
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 73069026714,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 22901363715,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 261221701812744128000000000000,
        "numerator": 3313323502885796113375260121643283
      },
      "wall_basis_bytes": 21700998244,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 2612217018127441280000000000,
        "numerator": 44088911629161349056129245198997
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "llama-70b": {
        "T_stream_max_s": 201.49829895899165,
        "bytes_per_member": 439197696,
        "est_minutes": 226.8269301273516,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 263.43256844580173,
        "request_mean_s": 82.55686520040035,
        "runs_measured": 16
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 31293501440,
    "required_free_bytes": 73069026714
  },
  "bytes-s6-p1": {
    "T_stream_max_s": 111.03078095801175,
    "disk_derivation": {
      "B_bytes": 16382541368,
      "allowances_by_model": {
        "qwen35-122b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 7733127455975572891344203626737
          },
          "stream_allowance_s": {
            "denominator": 816317818164825400000000000000,
            "numerator": 93614757959574015959440446217137
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 60031382020,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 14585071383,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 10448868072509765120000000000,
        "numerator": 84405558385170274738108638015081
      },
      "wall_basis_bytes": 16382541368,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 41604561831733586724555736838973
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen35-122b": {
        "T_stream_max_s": 111.03078095801175,
        "bytes_per_member": 343875584,
        "est_minutes": 157.8863706409618,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 183.3662877559662,
        "request_mean_s": 15.692169046401977,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 26527395840,
    "required_free_bytes": 60031382020
  },
  "bytes-s6-p2": {
    "T_stream_max_s": 111.03078095801175,
    "disk_derivation": {
      "B_bytes": 16382541368,
      "allowances_by_model": {
        "qwen35-122b": {
          "count": 50,
          "member_allowance_s": {
            "denominator": 40815890908241270000000000000,
            "numerator": 7733127455975572891344203626737
          },
          "stream_allowance_s": {
            "denominator": 816317818164825400000000000000,
            "numerator": 93614757959574015959440446217137
          }
        },
        "reference": {
          "count": 25,
          "member_allowance_s": {
            "denominator": 3265271272659301600000000000,
            "numerator": 426882080313251806367156893281
          },
          "stream_allowance_s": {
            "denominator": 6530542545318603200000000000000,
            "numerator": 612302832276072613101668810902833
          }
        }
      },
      "bytes_source": "raw_allocated_bytes: POSIX st_blocks*512, one raw bundle tree, inode-deduplicated",
      "extra_wait_raw_bytes": 12999877322,
      "fixed_retained_bytes": 1266544640,
      "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(r_s*sum(count*own stream allowance)), ceil(r_w*sum(count*own member allowance))); WAIT=ceil(r_s*7200); c=2; no reserve",
      "measured_c": 0.8020750916018277,
      "peak_copies": 2,
      "required_free_bytes": 60031382020,
      "session_wait_budget_s": 7200,
      "stream_basis_bytes": 14585071383,
      "stream_rate_bytes_per_s": {
        "denominator": 890824130839901,
        "numerator": 1608417280000000000000
      },
      "stream_seconds": {
        "denominator": 10448868072509765120000000000,
        "numerator": 84405558385170274738108638015081
      },
      "wall_basis_bytes": 16382541368,
      "wall_rate_bytes_per_s": {
        "denominator": 12509476685523987,
        "numerator": 16084172800000000000000
      },
      "wall_seconds": {
        "denominator": 3265271272659301600000000000,
        "numerator": 41604561831733586724555736838973
      }
    },
    "est_minutes": null,
    "measured_margin": 0.03325233382759357,
    "measured_margin_complete": false,
    "modules": {
      "qwen35-122b": {
        "T_stream_max_s": 111.03078095801175,
        "bytes_per_member": 343875584,
        "est_minutes": 157.8863706409618,
        "measured_margin": 0.03325233382759357,
        "measured_margin_complete": false,
        "member_wall_mean_s": 183.3662877559662,
        "request_mean_s": 15.692169046401977,
        "runs_measured": 5
      }
    },
    "non_claim": true,
    "programmed_span_s": null,
    "projected_footprint_bytes": 26527395840,
    "required_free_bytes": 60031382020
  }
}
```

## PACK ENCODING

Slice 3: plan_inputs.build reads disk_derivation from the selected sizing_b5.json pack row (the same source as its time allowances), for bytes-s* only. It uses plan.read_plan_tree and b5_chain.stage_plan to obtain the native member-plus-spares count, then divmod(c*B,3*n); headroom=remainder+c*WAIT+fixed. Integer fields are checked for reconstruction of P, c=2 and WAIT duration=7200. P values remain future BY-SLOTS registration inputs; no generated registration is changed.

DriverLane removes the diagnostic disk_budget property before the closed-schema smoke/planner interface and retains it at session metadata disk_budget and notes. A missing or malformed P records disk.budget_missing in staging/disk-budget.json and returns LaneMissing, not Refused; no disk comparison runs for the absent record. The writer requires positive bytes_per_member, so a zero-budget plan would not parse. Existing alpha/beta/gamma inputs remain unchanged.

The production-shaped synthetic test supplies the omitted launch declaration in its TMPDIR checkout only. Real draft BYTES trees currently have arm_attachments={}, as scripts/bytes_plan_trees.py intentionally generates; their launch authority remains a BY-SLOTS prerequisite.

## REPLAY PROGRAM

Pending. Director owns real replay; the worker must not access night-b6, night-bytes or night-custody trees.

## END-TO-END

`tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard` passes (1 test, 16.637 s, exit 0). A synthetic bytes-s1-p1 registration sizing row uses B=1000001, WAIT=7200, fixed=19, hence P=2014421 bytes. Only the temporary tree is decorated with the existing fourteen launch bindings; no draft authority is asserted for committed trees. DriverLane.prepare_session/build/launch feeds the real plan.write_window_plan. driver.disk_targets groups its real target copies on one synthetic device; disk.measure stubs statvfs with f_frsize=1 to express both exact byte boundaries. disk.judge reports required_bytes exactly P, REFUSE at P-1 and PASS at P. This is synthetic evidence, not live hardware validation.

## SEALED INVENTORY

Checked the sealed inventory programmatically (all keys of its files mapping):

```python
paths = sorted(json.loads(Path("configs/campaigns/v5_claim_25g83/sealed_inventory.json").read_text())["files"])
subprocess.run(["git", "diff", "--name-only", "bda481d5a", "HEAD", "--", *paths], check=True)
subprocess.run(["git", "diff", "--name-only", "HEAD", "--", *paths], check=True)
```

Both commands exited 0 with empty stdout. No block-five changes.

## TESTS RUN

Slice 3 exact commands (each fresh module TMPDIR, synthetic-only):

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_plan_inputs` — exit 0, 6 tests, 0.012 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_session_wrapper` — exit 0, 6 tests, 0.431 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard` — exit 0, 1 test, 16.637 s. Earlier attempts failed first on extra disk_budget key (fixed by keeping disclosure in DriverLane metadata), then on the intentionally absent draft launch declaration (synthetic fixture now supplies it in TMPDIR only).
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_each_production_pack_uses_b6_screen_and_no_spares` — exit 1, 1 test, 6 failing subtests, 131.197 s. All alpha/beta/gamma budget assertions passed for both registration states; each failed the unchanged check_readers line 142 courier path assertion because actual resolves /private/tmp while expected retains /tmp. Environmental path-alias failure per local route; not chased.
- `git diff --check` — exit 0. Repeated sealed-inventory byte-path diff commands from bda481d5a and HEAD to working tree: both exit 0, stdout empty.

Final slice-2 C5 module run: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates` — exit 0, 14 tests, 4.082 s, no skips. Includes measured-c disclosure invariance. H was rerun with --disk-evidence; exit 2, empty stderr, every P unchanged and measured_c=0.8020750916018277 beside c=2.


Slice 2 additional checks:

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph` — exit 1; 6 tests, 5.917 s, one failure: test_a_complete_arm_and_monitor_run_load_no_retired_module expected GO, got NULL. Five static graph tests pass. The failing test imports unchanged hazards/arm and its Rig, not bytes_gates; no hazard implementation was edited. Cause not established; report to director rather than alter hardware paths.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist` — exit 0; 23 tests in 69.967 s; OK, one skip.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session` — still running at this checkpoint (one failure marker observed; details pending); tool session 71288. Do not rerun the whole module in the next short slice: select individual classes/tests.
- `git diff --check` — exit 0. Sealed paths diff from both bda481d5a and HEAD — empty, exit 0 (working-tree comparison includes this slice).


Slice 2: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates` — exit 0, 13 tests, 3.990 s initially and 8.400 s after adding the cross-basis counterexample, no skips. Tests derive the integer P boundary exactly; unprinted continuous values use the director's 1e-6 relative/absolute bar. No whole suite.


`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates`

Exit 0; 11 tests in 1.132 seconds; OK, no skips or environmental failures. This is baseline verification; no implementation is claimed. Whole suite excluded by the task.

## R6 DRAFT

For each BYTES pass session the sole disk refusal is measured session-volume free bytes, statvfs f_bavail multiplied by f_frsize with purgeable bytes excluded, below P. P = 2(B + WAIT) + fixed. B is the larger of ceil(r_s times the sum of model count times that model’s stream allowance) and ceil(r_w times the sum of model count times that model’s member-wall allowance). Rates are maxima over timed H members of one raw bundle tree’s inode-deduplicated POSIX st_blocks times 512 divided by stream seconds or member-wall seconds respectively. Each model uses its own measured allowances including the measured request max/min margin; the stream allowance includes mean request time plus maximum stream-minus-request time. Each full basis rounds up once in exact rational arithmetic. WAIT=ceil(r_s times 7200 seconds), fixed is the committed fixed-artifact allocation, and two copies count raw plus the partitioned rsync backups; the harvest APFS clone adds no copy. No reserve or further margin is added. All terms, P, free bytes and the measured whole-window implied copy count are disclosed; missing inputs are flags. The native three-target budget encodes P exactly with q=floor(2B/(3n)) and headroom=(2B-3nq)+2WAIT+fixed, where n is the writer’s actual members-plus-spares count; disk.budget_encoded_from_p names that encoding. BY-SLOTS fills the pack-specific values from the C5 output printed above, whose provisional stopped-session status remains disclosed.

## CI

Director creates draft PR and reads CI under the local route. No PR number supplied yet.

## DECISIONS I MADE

Slice 3: registered disk terms live in sizing_b5.json packs[label].disk_derivation, next to that pack’s own time allowances; BYTES draft registration files remain unchanged. The sealed writer cannot accept diagnostic input keys or zero bytes_per_member. DriverLane keeps disk_budget in session metadata, and an absent P yields a durable disk.budget_missing diagnostic plus LaneMissing before planning, never Refused. The draft pass tree’s deliberately absent launch declaration is supplied only by the synthetic E2E fixture; actual launch readiness belongs to BY-SLOTS. Flags here are preparation metadata, not harvested member flags, so no flag-catalog mutation is required for this step.

Director ruling 1: per-run raw_allocated_bytes is the only disk-rate byte source (allocated st_blocks*512, raw-only tree, inode-deduplicated). Missing raw byte receipts enter no rate, are counted in disk.raw_bytes_missing; no rate makes disk unavailable. Never halve retained_bytes. Rates compare at 1e-6 relative; derived integer bytes compare exactly. BY-H2 owns native producer support. Synthetic never-ran receipts carry raw_allocated_bytes=null.


Applied director precedence: H ruling and committed disk_terms win over the paraphrase; B is the maximum of two summed bases, each rounded once using exact rational arithmetic. c=2; measured c is disclosure. WAIT uses stream rate for registered 7200 seconds; fixed comes unchanged from disk.fixed_retained_bytes. Local route overrides cloud setup, commits and PR operations.

## OPEN ISSUES

BY-H2 must add raw_allocated_bytes to scripts/bytes_h_session.py measurements(): POSIX st_blocks*512 of that run's raw bundle tree only (one copy, runs-parent/<stage dir>/<run_id>, inode-deduplicated); null for members that never ran. retained_bytes keeps raw plus archive allocations and must not be halved.

The existing production reader regression has the /private/tmp versus /tmp courier-path environmental failure described in TESTS RUN.

The native producer lacks raw_allocated_bytes, so tests.test_bytes_h_session.test_fully_observed_native_export_extracts_and_clears_c5 currently expects pass where the new contract requires unavailable. BY-H2 producer support must restore that integration; its file and test are outside this write scope.

Remaining: finish planner and real hazard verification, replay program/tests, remaining targeted tests and R6 paragraph. Real 9+1 replay and CI remain director-owned. Local branch by-c5; HEAD f73c62198; intended destination lane/2026-10-22-bytes-c5-gates. Proposed slice commit: BY-C5: encode registered P exactly in native pass disk budget.

## NEEDS_RULING

none; director ruling 1 resolved the byte source.
