"""R04 prospective sensitivity analysis, not empirical power or approval.

The independent unit is a paired 18-decision episode. This script checks the
published design's stated normal-approximation assumptions *without* looking
at protected seeds, outcomes or any new model response.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

Z975=1.959963984540054
Z80=0.8416212335729143
CALLS_PER_EPISODE=4*18+5
CAP=2500


def sensitivity(delta=0.10, sigmas=(0.15,0.20,0.25)):
    if delta<=0 or any(s<=0 for s in sigmas):
        raise ValueError("POSITIVE_EFFECT_AND_SD_REQUIRED")
    rows=[]
    for sigma in sigmas:
        raw=((Z975+Z80)*sigma/delta)**2
        episodes=math.ceil(raw)
        rows.append({
          "assumed_paired_episode_sd":sigma,
          "target_absolute_risk_difference":delta,
          "normal_approx_n_raw":round(raw,6),
          "normal_approx_n_rounded":episodes,
          "estimated_calls":episodes*CALLS_PER_EPISODE,
          "fits_existing_2500_call_cap":episodes*CALLS_PER_EPISODE<=CAP
        })
    assert [x["normal_approx_n_rounded"] for x in rows]==[18,32,50]
    return {
      "schema":"WAMBU-R04-DEVELOPMENT-SENSITIVITY-ONLY-V1",
      "prospective_only":True,
      "exploratory_episode_counts":{"original_dev":8,"temporal_dev":4},
      "unit":"INDEPENDENT_PAIRED_EPISODE_NOT_DECISION_TURN",
      "alpha_two_sided":0.05,
      "nominal_power_target":0.80,
      "effect_delta_is_hypothesised_not_observed":True,
      "episode_variance_is_assumed_not_empirically_estimated":True,
      "existing_call_cap":CAP,
      "calls_per_episode":CALLS_PER_EPISODE,
      "rows":rows,
      "equivalence_or_superiority_established":False,
      "confirmatory_sample_frozen":False,
      "confirmatory_holdout_touched":False,
      "author_protocol_authorisation":False,
      "external_submission_authorised":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    r=sensitivity()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"nominal_n":[x["normal_approx_n_rounded"] for x in r["rows"]],
      "n32_calls":32*r["calls_per_episode"],
      "not_confirmatory":not r["confirmatory_sample_frozen"]}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
