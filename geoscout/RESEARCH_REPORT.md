# GeoScout Research Report

## An Evidence-Grounded AI Agent for Environmental Geospatial Analysis

**Version:** 3
**Status:** Frozen research prototype
**Baseline:** `geoscout-v3-baseline`
**Author:** Abah James Unekwuojo

---

# Abstract

Large language model agents are increasingly being used to translate natural-language requests into executable workflows involving external tools and structured data. In environmental geospatial analysis, however, producing a plausible natural-language answer is not sufficient. A reliable system must select appropriate geospatial operations, execute them correctly, distinguish computed evidence from interpretation, and provide outputs that can be inspected and evaluated.

GeoScout is an independent research prototype investigating this problem through an evidence-grounded agent architecture. The system uses an LLM as a planning and tool-selection component while delegating geospatial computation to deterministic GIS tools. Agent trajectories, tool executions, observations, latency, token usage, and evidence relationships are recorded for evaluation.

A controlled v3 experiment evaluated GPT-OSS 20B and GPT-OSS 120B on a 20-task synthetic environmental geospatial benchmark. GPT-OSS 20B achieved 90% grounded correctness, 95% answer correctness, and 90% evidence support. GPT-OSS 120B achieved 95% grounded correctness, 100% answer correctness, and 95% evidence support.

The experiment also revealed failure modes that are not adequately represented by final-answer accuracy alone. In one task, both models failed to acquire the required evidence and produced no analytical answer. In another, the agent correctly identified nine degraded cells but made a stronger unsupported claim about their spatial distribution.

These observations motivate a broader research direction: evaluating geospatial agents not only according to whether their answers are correct, but also according to whether their computational workflow and claims are supported by observable evidence.

---

# 1. Introduction

## 1.1 Background

Environmental monitoring frequently requires analysis across spatial and temporal dimensions. Examples include vegetation-change detection, land-cover analysis, erosion assessment, environmental suitability analysis, and statistical summarization.

Traditional geospatial workflows often require users to understand data formats, coordinate reference systems, GIS operations, spatial analysis libraries, and domain-specific processing pipelines.

Recent advances in large language models have introduced another possibility: users can describe an analytical objective in natural language and allow an AI agent to determine which computational operations should be performed.

This creates a new class of system:

> **The geospatial AI agent.**

Rather than simply generating text, such an agent must interact with external computational tools.

The GeoNatureAgent Benchmark is an example of this emerging evaluation direction. It evaluates environmental geospatial agents through structured tool calling and includes capabilities such as tool selection, spatial reasoning, error handling, temporal analysis, and interpretation. The paper reports that environmental geospatial tool orchestration remains challenging and identifies tool selection as a particularly important capability.
GeoScout was developed as an independent exploration of this broader problem.

---

## 1.2 Problem Statement

A geospatial agent can fail in several different ways.

For example, an agent may:

1. misunderstand the user's question;
2. select the wrong GIS tool;
3. fail to execute a required tool;
4. execute a tool but fail to use its result;
5. calculate or report an incorrect value;
6. produce a correct numerical observation but attach an unsupported interpretation;
7. produce a plausible answer without sufficient computational evidence.

Therefore:

> **Final-answer correctness alone is insufficient for evaluating reliable geospatial agents.**

A research-oriented evaluation should also examine the computational evidence behind the answer.

---

# 2. Research Motivation

GeoScout was designed around three capabilities that the project is intended to demonstrate:

### Agentic AI

* planning;
* tool selection;
* multi-step execution;
* interaction with external tools;
* response synthesis.

### Geospatial engineering

* geospatial data handling;
* deterministic GIS computation;
* coordinate reference systems;
* vegetation-change analysis;
* spatial hotspot detection.

### Research capability

* controlled experiments;
* benchmark construction;
* measurable evaluation;
* execution telemetry;
* evidence tracing;
* failure analysis.

The central design principle is:

> **Make the agent's workflow explicit, make GIS computation deterministic, make produced evidence traceable, and evaluate the resulting behavior empirically.**

---

# 3. Research Questions

## 3.1 Primary Research Question

> **How reliably can an LLM agent plan and execute environmental geospatial analysis workflows using structured deterministic tools while producing answers grounded in observable evidence?**

## 3.2 Secondary Research Question

> **Where do geospatial agents fail when their natural-language interpretations go beyond the evidence produced by their computational workflow?**

The second question is particularly important because an answer can contain both supported and unsupported statements.

---

# 4. Research Positioning

GeoScout is related to recent work on agentic geospatial analysis but is not intended to reproduce any particular existing system.

The project was motivated in part by the **GeoNatureAgent Benchmark**, which evaluates environmental geospatial agents through structured tool calls. That benchmark uses 93 tasks across 18 capability categories and exposes agents to 16 tools. Its authors report that environmental geospatial tool orchestration remains a significant challenge.
GeoScout instead investigates a narrower architectural question using a controlled synthetic environment.

The distinction can be summarized as:

```text
GeoNatureAgent
    │
    ├── Broad environmental-agent benchmark
    ├── 93 tasks
    ├── 18 capability categories
    └── 16-tool environment
            │
            │ motivates broader problem
            ▼
GeoScout
    │
    ├── Independent research prototype
    ├── Controlled synthetic environment
    ├── Explicit evidence grounding
    ├── Execution telemetry
    └── Failure-oriented evaluation
```

GeoScout should therefore be understood as an **independent architectural and evaluation experiment**, not an official implementation, reproduction, or extension of the GeoNatureAgent Benchmark.

---

# 5. System Design

## 5.1 Design Principle

The system separates language-model reasoning from deterministic computation.

```text
Natural-language question
          │
          ▼
     LLM Planner
          │
          ▼
     Tool Selection
          │
          ▼
 Deterministic GIS Tool
          │
          ▼
      Tool Result
          │
          ▼
   Evidence Collection
          │
          ▼
       Evaluation
          │
          ▼
     Final Response
```

The LLM is responsible for deciding **what should be done**.

The GIS implementation is responsible for determining **what the computation actually produces**.

---

## 5.2 Agent Layer

The agent receives a natural-language environmental question and interacts with a structured tool interface.

The execution process records:

* tool calls;
* tool observations;
* execution status;
* execution errors;
* LLM calls;
* latency;
* token counts;
* final answer;
* overall status.

This produces an inspectable execution trajectory rather than only a final text response.

---

## 5.3 Tool Registry

The geospatial tools are defined through structured schemas and exposed through a tool registry.

The core operations include:

| Tool                     | Function                                       |
| ------------------------ | ---------------------------------------------- |
| `load_dataset`           | Load the environmental dataset                 |
| `get_region`             | Inspect region-level properties                |
| `calculate_ndvi_change`  | Calculate NDVI change                          |
| `detect_change_hotspots` | Detect cells exceeding a degradation threshold |
| `calculate_statistics`   | Compute descriptive statistics                 |
| `summarize_hotspots`     | Summarize hotspot results                      |
| `export_hotspots`        | Export hotspot outputs                         |

The tool layer is implemented under:

```text
src/geoscout/tools/
```

The important architectural property is that these operations are implemented as deterministic Python GIS functions rather than generated free-form analytical code.

---

# 6. Experimental Dataset

## 6.1 Dataset Design

The v3 prototype uses a synthetic environmental dataset.

The purpose of the synthetic dataset is not to represent a real geographic location. Instead, it provides a controlled environment in which:

* the ground truth is known;
* the spatial pattern is reproducible;
* the degradation threshold is controlled;
* external data availability does not affect the experiment;
* model behavior can be compared under identical conditions.

---

## 6.2 Dataset Characteristics

The dataset contains:

* 100 grid cells;
* a 10 × 10 spatial arrangement;
* CRS `EPSG:4326`;
* baseline NDVI;
* current NDVI;
* calculated NDVI change;
* predefined degraded cells.

NDVI change is calculated as:

```text
NDVI change = current NDVI − baseline NDVI
```

A cell is classified as degraded when:

```text
NDVI change ≤ −0.10
```

The resulting ground truth contains:

```text
Study cells:       100
Degraded cells:      9
Minimum change:  −0.25
Maximum change:   0.043707936990109886
Mean change:     −0.018650758199393255
```

The nine degraded cells form the predefined hotspot pattern used throughout the controlled experiment.

---

# 7. Benchmark Design

## 7.1 Benchmark Scope

The v3 benchmark contains:

> **20 environmental geospatial tasks**

The tasks are identified as `GE-001` through `GE-020`.

They include:

* simple single-tool tasks;
* medium-complexity analytical tasks;
* multi-tool tasks;
* reasoning-oriented tasks.

The benchmark therefore progresses from direct retrieval of geospatial properties toward questions requiring combinations of observations and interpretation.

---

## 7.2 Task Categories

The benchmark uses three broad categories:

### Single-tool

Tasks that can be answered using one appropriate GIS operation.

Examples include:

* number of degraded cells;
* study-region size;
* CRS;
* minimum NDVI change;
* maximum NDVI change.

### Multi-tool

Tasks requiring more than one geospatial observation.

Examples include combinations of:

* study-region properties;
* hotspot detection;
* statistical summaries.

### Reasoning

Tasks in which the agent must interpret one or more computational results.

These tasks are especially important because they create opportunities for the model to move beyond directly observed numerical evidence.

---

# 8. Evaluation Framework

GeoScout evaluates agent behavior using multiple related measurements.

## 8.1 Evidence Support

Evidence support asks:

> **Did the agent obtain the required evidence from an executed GIS tool?**

For example, if a task requires the number of degraded cells, acceptable evidence may include:

```text
calculate_statistics.degraded_cells
```

or:

```text
summarize_hotspots.hotspot_count
```

when the corresponding evidence rule permits it.

The evaluator checks tool observations against semantic evidence requirements.

---

## 8.2 Answer Correctness

Answer correctness asks:

> **Does the final answer contain the expected result?**

Numerical results can be compared using a specified tolerance.

The evaluator also supports qualitative answer requirements where defined.

---

## 8.3 Grounded Correctness

GeoScout defines grounded correctness as:

```text
Grounded Correctness
=
Evidence Support
AND
Answer Correctness
```

Therefore an answer is considered grounded only when both conditions are satisfied.

This prevents a numerically correct answer from automatically being treated as fully reliable if the required computational evidence was not acquired.

---

# 9. Evidence Representation

The evidence layer connects semantic requirements to concrete tool outputs.

For example:

```text
Concept:
degraded_cell_count

Expected value:
9

Supporting evidence:

Tool:
calculate_statistics

Field:
degraded_cells

Observed value:
9
```

This relationship is represented through an evidence trace.

Conceptually:

```text
Semantic requirement
        │
        ▼
Accepted tool / field
        │
        ▼
Observed value
        │
        ▼
Evidence trace
```

The v3 experiment generated:

> **68 evidence traces**

across the model-task evaluations.

---

# 10. Important Evaluation Caveat

The current evaluation implementation contains an important methodological limitation.

Some benchmark requirements have:

```text
expected_value = null
```

For these requirements, the evaluator treats the existence of an observed value as sufficient evidence support.

In the current implementation:

```text
if actual is None:
    return False

if expected is None:
    return True
```

Therefore, a requirement with a null expected value is effectively testing:

> **Was an appropriate value produced by an acceptable tool?**

rather than:

> **Was the produced value independently verified against ground truth?**

This distinction matters.

For example, the benchmark can establish that:

```text
calculate_statistics.mean_change
```

was produced and was non-null.

It does not necessarily establish, through the benchmark requirement itself, that the value was numerically correct when the expected value is null.

This is an intentional limitation of the current v3 evaluation design and should be addressed in a future benchmark version.

---

# 11. Claim Groundedness Caveat

The v3 evaluation also reports `claim_groundedness`.

However, this metric should **not be interpreted as an independent measurement from evidence support**.

The current semantic claim evaluation ultimately relies on the same semantic evidence requirements.

Therefore:

```text
claim_groundedness
```

and:

```text
evidence_support_rate
```

share the same underlying semantic evidence machinery.

For this reason, the main v3 comparison emphasizes:

* grounded correctness;
* answer correctness;
* evidence support.

A future evaluation framework should implement an independent claim-level evaluator capable of distinguishing:

```text
Evidence acquisition
        ↓
Evidence correctness
        ↓
Claim correctness
        ↓
Grounded claim
```

---

# 12. Experimental Setup

## 12.1 Models

The v3 experiment compares:

```text
openai/gpt-oss-20b
openai/gpt-oss-120b
```

The models were evaluated using the same benchmark and tool environment.

---

## 12.2 Evaluation Scale

Each model was evaluated against:

```text
20 benchmark tasks
```

giving:

```text
2 models × 20 tasks = 40 model-task evaluations
```

All 40 evaluations generated evidence traces, with:

```text
68 total evidence traces
```

across the experiment.

---

## 12.3 Frozen Baseline

The evaluated v3 state was explicitly frozen using the Git tag:

```text
geoscout-v3-baseline
```

The corresponding model comparison artifact is:

```text
evaluation/results/model_comparison_v3.json
```

This ensures that subsequent development can be distinguished from the evaluated experimental state.

---

# 13. Results

## 13.1 Aggregate Comparison

The v3 results were:

| Metric               | GPT-OSS 20B | GPT-OSS 120B |
| -------------------- | ----------: | -----------: |
| Tasks                |          20 |           20 |
| Grounded correctness |         90% |      **95%** |
| Answer correctness   |         95% |     **100%** |
| Evidence support     |         90% |      **95%** |
| Mean latency         |      8.25 s |       9.76 s |
| Mean tool calls      |        1.20 |         1.25 |
| Mean LLM calls       |        2.20 |         2.25 |
| Mean total tokens    |    2,013.55 |     2,030.90 |

The 120B model therefore achieved a five-percentage-point improvement in grounded correctness and evidence support, while achieving perfect answer correctness on this benchmark.

It also had slightly higher average latency and slightly higher tool/LLM-call counts.

---

## 13.2 GPT-OSS 20B

GPT-OSS 20B achieved:

```text
Grounded correctness: 90%
Answer correctness:   95%
Evidence support:     90%
```

This indicates that most benchmark tasks produced both the required evidence and a correct answer.

However, two failure cases are particularly informative for understanding the remaining errors.

---

## 13.3 GPT-OSS 120B

GPT-OSS 120B achieved:

```text
Grounded correctness: 95%
Answer correctness:   100%
Evidence support:     95%
```

The model therefore improved on the primary grounding metric relative to GPT-OSS 20B.

However, the larger model did not eliminate the important workflow failure observed on `GE-010`.

This demonstrates that increasing model scale did not guarantee complete workflow reliability within the current experimental setting.

---

# 14. Failure Analysis

Aggregate metrics conceal important differences between failure types.

GeoScout therefore records task-level evidence traces and execution information to examine individual failures.

---

## 14.1 GE-010 — Evidence Acquisition Failure

Both GPT-OSS 20B and GPT-OSS 120B failed on `GE-010`.

The required concept was:

```text
hotspot_mean_ndvi_change
```

but no supporting evidence was produced.

The evidence trace records:

```text
Concept:
hotspot_mean_ndvi_change

Expected:
None

Supported:
False
```

The trajectory also indicated:

```text
actual_tools = []
```

and the final response was:

```text
The agent returned no final answer.
```

This is important because it is not best described as a numerical reasoning error.

The agent did not reach the stage at which the required numerical result could be reasoned about.

The failure is more accurately classified as:

> **workflow completion / evidence acquisition failure**

This distinction matters for agent evaluation.

A system designed to improve numerical reasoning would not necessarily solve a failure in which the model never executes the required tool.

---

# 15. GE-019 — Unsupported Spatial Interpretation

`GE-019` is the most informative grounding failure in the v3 experiment.

The task required evidence concerning the study region and degraded cells.

For GPT-OSS 20B, the evidence trace showed:

```text
study_cell_count
Expected: 100
Supported: False

degraded_cell_count
Expected: 9
Supported: True

Evidence:
summarize_hotspots.hotspot_count = 9
```

Therefore the model had valid evidence for the number of degraded cells but did not obtain evidence for the study-cell count.

The final answer went beyond this evidence.

It described the degraded cells as forming a contiguous block and concluded that degradation was widespread within the study region.

The problem is not necessarily that the numerical observation was incorrect.

The problem is that the stronger spatial interpretation was not explicitly established by the evaluated evidence requirements.

This illustrates a central distinction:

```text
Observed fact
    ↓
9 degraded cells
    ↓
Spatial interpretation
    ↓
"The degradation is widespread"
```

The final step requires additional spatial reasoning.

The current benchmark does not independently score this higher-order spatial claim.

---

# 16. Why GE-019 Matters

GE-019 exposes a broader challenge in evidence-grounded AI.

Consider these statements:

### Direct computational statement

> Nine cells exceeded the degradation threshold.

This can be directly supported by:

```text
summarize_hotspots.hotspot_count = 9
```

### Spatial interpretation

> The degradation is widespread.

This requires additional reasoning about:

* the proportion of the study region affected;
* spatial distribution;
* clustering;
* connectivity;
* geographic extent;
* potentially domain-specific meaning of "widespread."

Therefore:

> **Evidence for a numerical fact does not automatically constitute evidence for every interpretation derived from that fact.**

This is one of the primary research insights emerging from the current prototype.

---

# 17. Evidence vs. Interpretation

GeoScout's architecture suggests a useful conceptual separation:

```text
                 ┌─────────────────────┐
                 │  Tool Observation   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Computed Evidence  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Supported Claim     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Interpretation      │
                 └─────────────────────┘
```

The current prototype provides relatively strong support for the first three layers.

The fourth layer remains an important research opportunity.

---

# 18. Discussion

## 18.1 What the Experiment Demonstrates

The v3 experiment demonstrates that a controlled architecture can make several aspects of agent behavior observable.

Instead of recording only:

```text
Question → Answer
```

GeoScout records:

```text
Question
   ↓
LLM calls
   ↓
Tool selection
   ↓
Tool execution
   ↓
Tool observations
   ↓
Evidence
   ↓
Evaluation
   ↓
Answer
```

This enables failure analysis at intermediate stages.

---

## 18.2 Model Scale

The GPT-OSS 120B model performed better than GPT-OSS 20B on the primary v3 metrics:

```text
Grounded correctness:
90% → 95%

Answer correctness:
95% → 100%

Evidence support:
90% → 95%
```

Within this controlled experiment, this is consistent with improved performance from the larger model.

However, the experiment is too small to establish a general relationship between parameter scale and geospatial-agent reliability.

The correct interpretation is therefore:

> **GPT-OSS 120B performed better than GPT-OSS 20B on this 20-task GeoScout benchmark.**

It should not be generalized beyond this experimental setting without further testing.

---

# 19. Agentic Reliability

The results suggest that agent reliability is multi-dimensional.

A model can fail because:

```text
Question understanding
        ↓
Tool selection
        ↓
Tool execution
        ↓
Evidence acquisition
        ↓
Numerical reasoning
        ↓
Interpretation
        ↓
Final response
```

A final-answer score collapses these stages into one number.

GeoScout instead attempts to preserve enough execution information to determine where the failure occurred.

This is especially useful for future research into:

* tool routing;
* workflow planning;
* recovery;
* evidence grounding;
* spatial reasoning.

---

# 20. Limitations

## 20.1 Synthetic Data

The current experiment uses synthetic vegetation data.

This provides excellent control and reproducibility but does not establish performance on real satellite imagery or operational environmental datasets.

---

## 20.2 Small Benchmark

The benchmark contains only 20 tasks.

This is appropriate for an early research prototype but insufficient for broad claims about environmental geospatial-agent performance.

---

## 20.3 Limited Model Coverage

Only two models were compared in v3.

A broader comparison would be required to understand how architecture and model choice interact.

---

## 20.4 Incomplete Ground-Truth Coverage

Several benchmark requirements have `expected_value = null`.

This means some evidence checks establish evidence acquisition rather than independently verifying numerical correctness.

---

## 20.5 Spatial Reasoning

The current benchmark does not independently evaluate all higher-order spatial interpretations.

In particular, claims such as:

```text
widespread
contiguous
clustered
concentrated
spatially significant
```

require richer spatial reasoning than the current evaluator provides.

---

## 20.6 Claim Evaluation

The current `claim_groundedness` implementation is not independent from semantic evidence support.

A stronger future evaluator should independently identify natural-language claims and evaluate whether each claim is supported by the computational evidence.

---

## 20.7 Real Geospatial APIs

The current implementation uses local deterministic GIS tools rather than a production-scale remote-sensing or geospatial API.

This simplifies the experiment but limits direct conclusions about deployment environments.

---

# 21. Research Implications

The current prototype suggests several directions for research.

## 21.1 Evidence Acquisition Should Be Evaluated Separately

An agent can fail before it produces an answer.

Therefore:

```text
Evidence acquisition
```

should be measured independently from:

```text
Answer correctness
```

---

## 21.2 Evidence Correctness Should Be Distinguished from Evidence Presence

A tool output existing is not necessarily equivalent to that output being correct.

Future evaluation should distinguish:

```text
Evidence presence
        ↓
Evidence correctness
        ↓
Claim correctness
        ↓
Grounded answer
```

---

## 21.3 Spatial Interpretation Requires Dedicated Metrics

A statement such as:

> "Vegetation degradation is widespread."

should be evaluated using explicit spatial properties.

Possible future metrics could include:

* affected-area proportion;
* hotspot density;
* connected-component size;
* spatial clustering;
* spatial coverage;
* distance-based concentration;
* region-relative extent.

This would allow qualitative spatial claims to be tested against deterministic spatial measurements.

---

# 22. Future Work

## 22.1 GeoScout v4 Benchmark

A future benchmark could expand the current 20 tasks into a more comprehensive evaluation suite.

Potential additions include:

* larger task counts;
* more environmental indicators;
* more complex multi-step workflows;
* tool-selection stress tests;
* tool failure cases;
* recovery tasks;
* explicit rejection tasks;
* spatial reasoning tasks.

---

## 22.2 Stronger Evidence Model

A future evidence framework could distinguish:

```text
Evidence Acquisition
        ↓
Evidence Correctness
        ↓
Claim Support
        ↓
Claim Correctness
        ↓
Grounded Answer
```

This would make the evaluation substantially more informative.

---

## 22.3 Explicit Spatial Reasoning Evaluation

Future tasks should contain independently verifiable spatial claims.

For example:

```text
Is degradation widespread?
```

could be evaluated using a predefined criterion such as:

```text
affected_cells / total_cells ≥ threshold
```

Similarly:

```text
Are hotspots spatially contiguous?
```

could be evaluated using connected-component analysis.

---

## 22.4 Tool Failure and Recovery

A major extension would intentionally introduce tool failures.

The experiment could measure:

```text
Initial tool failure
       ↓
Agent detects failure
       ↓
Agent diagnoses failure
       ↓
Agent selects alternative action
       ↓
Agent completes workflow
```

This would provide a stronger test of genuine agentic behavior.

---

## 22.5 Real Environmental Data

A future version could evaluate GeoScout using:

* satellite-derived vegetation indices;
* land-cover products;
* environmental monitoring datasets;
* remotely sensed temporal observations;
* real geospatial APIs.

This would test whether the architecture transfers beyond synthetic data.

---

## 22.6 Model Diversity

Future experiments should include a broader range of:

* open-weight models;
* frontier models;
* model sizes;
* tool-calling implementations.

This would allow the architecture to be evaluated independently of one model family.

---

# 23. Reproducibility

The v3 environment uses Python 3.12 and `uv` for dependency management.

The repository contains:

```text
pyproject.toml
uv.lock
.python-version
```

The main experiment artifacts are stored under:

```text
evaluation/
```

The synthetic dataset is:

```text
data/synthetic/vegetation_grid.geojson
```

The v3 model comparison is:

```text
evaluation/results/model_comparison_v3.json
```

The baseline is frozen at:

```text
geoscout-v3-baseline
```

The project test suite currently passes:

```text
74 tests passed
```

and Ruff reports:

```text
All checks passed!
```

These checks provide basic software-level validation of the implementation.

---

# 24. Research Artifact Organization

The project separates source code, data, evaluation definitions, results, and experiments.

```text
geoscout/
│
├── data/
│   └── synthetic/
│
├── evaluation/
│   ├── benchmarks/
│   ├── results/
│   └── experiments/
│
├── scripts/
│
├── src/
│   └── geoscout/
│       ├── agent/
│       ├── data/
│       ├── evaluation/
│       ├── tools/
│       └── utils/
│
└── tests/
```

This structure allows implementation and experimental artifacts to evolve while preserving the frozen v3 baseline.

---

# 25. Conclusion

GeoScout investigates a specific question within the broader field of agentic GeoAI:

> **Can an environmental geospatial agent be evaluated according to not only what it says, but also what it executes and what evidence supports its claims?**

The v3 prototype demonstrates a practical architecture for studying this question.

The LLM is responsible for:

* interpreting questions;
* planning;
* selecting tools;
* synthesizing responses.

Deterministic GIS tools are responsible for:

* geospatial computation;
* statistical analysis;
* hotspot detection;
* spatial data operations.

The evaluation system is responsible for:

* checking evidence;
* measuring answer correctness;
* measuring grounded correctness;
* recording execution traces;
* exposing failure modes.

In the controlled 20-task v3 experiment, GPT-OSS 20B achieved 90% grounded correctness while GPT-OSS 120B achieved 95%.

More importantly, the experiment revealed that aggregate accuracy does not tell the entire story.

The `GE-010` failure demonstrates that an agent can fail to acquire the required evidence altogether.

The `GE-019` failure demonstrates that an agent can obtain a correct numerical observation while making a stronger spatial interpretation that is not independently supported by the evaluated evidence.

These failures motivate the central research direction of GeoScout:

> **Reliable geospatial agents should be evaluated at the level of workflows, evidence, claims, and interpretations—not solely at the level of final answers.**

GeoScout v3 is therefore best viewed not as a finished environmental intelligence system, but as a controlled research instrument for studying reliability in agentic geospatial analysis.

---

# 26. References

## [1] GeoNatureAgent Benchmark

Diaz-Ireland, G., Prieto-Herráez, D., García Peces, M., Velázquez, J., & Jain, D. (2026).

**GeoNatureAgent Benchmark: Benchmarking LLM Agents for Environmental Geospatial Analysis Across Frontier and Open-Weight Foundation Models.**

Proceedings of the 34th ACM International Conference on Advances in Geographic Information Systems (SIGSPATIAL '26).

DOI: `10.1145/3841645.3844198`

## The referenced paper describes a 93-task environmental geospatial-agent benchmark spanning 18 capability categories and a 16-tool agent interface. It reports that tool selection and orchestration remain significant challenges for environmental geospatial agents.

# 27. Project Statement

GeoScout is an independent research prototype.

It is:

* not an official Darwin Geospatial project;
* not an official implementation of GeoNatureAgent;
* not a reproduction of the referenced benchmark;
* not intended to claim performance comparable to the benchmark without further experimentation.

Its purpose is to independently investigate:

> **agentic AI + geospatial computation + evidence grounding + empirical evaluation.**

The current v3 implementation provides the baseline for future experimentation.
