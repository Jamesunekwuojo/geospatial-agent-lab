# GeoScout v3 Experimental Results

## Experimental comparison

GeoScout v3 evaluated GPT-OSS 20B and GPT-OSS 120B on the 20-task
GeoScout evidence benchmark using the semantic-v2 evaluation framework.

| Metric | GPT-OSS 20B | GPT-OSS 120B |
|---|---:|---:|
| Tasks | 20 | 20 |
| Grounded correctness | 90% | 95% |
| Answer correctness | 95% | 100% |
| Evidence support | 90% | 95% |
| Mean latency | 8.25 s | 9.76 s |
| Mean tool calls | 1.20 | 1.25 |
| Mean LLM calls | 2.20 | 2.25 |
| Mean total tokens | 2,013.55 | 2,030.90 |

GPT-OSS 120B achieved a 5-percentage-point higher grounded-correctness
rate than GPT-OSS 20B (95% vs. 90%). Answer correctness increased from
95% to 100%, while evidence support increased from 90% to 95%.

The higher performance was accompanied by higher mean latency. Mean
latency increased from 8.25 seconds to 9.76 seconds, approximately an
18.2% increase. Mean tool calls increased from 1.20 to 1.25, while mean
LLM calls increased from 2.20 to 2.25.

## Task-level failure distribution

GPT-OSS 20B produced two grounded failures:

- GE-010
- GE-019

GPT-OSS 120B produced one grounded failure:

- GE-010

Therefore, the difference in aggregate grounded correctness is
concentrated in GE-019.

Both models failed GE-010 under the semantic-v2 grounded evaluation.
GE-010 requires an evaluation caveat because the benchmark's
`answer_correct` field can remain true when the expected value is null;
the recorded final response did not constitute a substantive successful
answer.

## GE-019 case study

GE-019 provides the clearest qualitative difference between the two
models.

GPT-OSS 20B used `summarize_hotspots` and obtained evidence for the
degraded/hotspot count of 9. However, it did not acquire evidence for
the total study-cell count of 100. The resulting evaluation therefore
classified the task as unsupported and incorrect.

GPT-OSS 120B used `get_region` followed by `summarize_hotspots`. This
produced evidence for both required concepts:

- study-cell count = 100
- degraded-cell count = 9

The task was therefore classified as grounded-correct.

The result illustrates an important distinction for geospatial agents:
obtaining one correct spatial statistic is not necessarily sufficient
to support the conclusion requested by a task. The agent must also
acquire the contextual evidence required to ground the interpretation.

## Interpretation

The experiment provides evidence that, within this benchmark and
evaluation setting, GPT-OSS 120B achieved higher evidence-grounded task
performance than GPT-OSS 20B. However, the observed difference is
modest: one additional grounded-correct task out of twenty.

The results therefore should not be interpreted as evidence that the
120B model is generally superior for geospatial analysis. The
experiment compares two models on a small synthetic benchmark under a
specific agent architecture, toolset, and evaluation methodology.

The more significant observation is methodological: GE-019 exposes a
failure mode in which a model can obtain a correct numerical result
while failing to acquire all evidence required for a grounded spatial
interpretation.

## Evaluation limitations

The current semantic-v2 benchmark explicitly evaluates required
evidence concepts such as study-cell count and degraded-cell count.
It does not independently score all higher-order natural-language
spatial reasoning claims. In particular, GE-019 does not independently
evaluate the qualitative claim that degradation is "widespread" or
"contiguous".

The current `claim_groundedness` metric should also not be treated as
an independent metric from semantic evidence support because both are
derived from the same underlying semantic evidence mechanism.

Finally, GE-010 demonstrates a limitation in the current answer
correctness handling when benchmark requirements have null expected
values. This motivates a future evaluation design that separates
evidence acquisition, evidence correctness, answer correctness, and
higher-order spatial reasoning correctness more explicitly.
