# Evaluation Metrics

## 2. Core Metrics

### Accuracy

**Definition:** The proportion of evaluated cases that are correct.

$$\text{Accuracy} = \frac{\text{Correct Cases}}{\text{Total Cases}}$$

#### GeoScout example

If an agent answers 19 out of 20 benchmark tasks correctly:

$$\text{Accuracy} = \frac{19}{20} = 95\%$$

Accuracy is useful, but it does not tell us why a case was correct or whether the answer was properly supported.

---

### Answer Correctness

**Definition:** Whether the final answer matches the expected answer.

In GeoScout, this asks:

> *"Did the agent give the right answer?"*

**Example:**
* **Expected:** 9 degraded cells
* **Agent:** 9 degraded cells
* **Answer correctness:** `True`

---

### Evidence Support

**Definition:** Whether the agent actually obtained the evidence required to support the answer.

In GeoScout, evidence normally comes from deterministic GIS tool outputs.

**Example:**
* GIS tool $\rightarrow$ `degraded_cells = 9`

If the agent's answer says 9 and the required GIS observation was actually returned, the claim has evidence support.

---

### Grounded Correctness

**Definition:** The answer is correct **AND** the required evidence supports it.

Conceptually:

```text
Grounded Correctness = Answer Correctness AND Evidence Support
```

#### GeoScout example

```text
Correct answer?       YES
Required evidence?    YES
                     ───
Grounded?             YES
```

This is stricter than answer correctness alone.

---

### Claim Groundedness

**Definition:** Whether a claim made by the agent can be connected to observable evidence.

This is particularly important for agentic systems because an agent can make an additional interpretation that was never actually established by the tools.

#### GeoScout example

The agent correctly found:
> 9 degraded cells

but one run additionally described them as forming a particular spatial pattern without sufficient supporting evidence.

This illustrates:

```text
Correct observation ≠ Automatically justified interpretation
```

> [!NOTE]
> **Important GeoScout caveat:** In the v3 evaluation, claim groundedness was derived from the same semantic evidence machinery as evidence support. It was therefore not an independent metric.

---

## 3. Operational Metrics

### Latency

**Definition:** How long a system takes to complete an operation.

For an agent:

```text
Question
   ↓
Planning
   ↓
Tool execution
   ↓
Final answer
```

Latency measures the time taken across this workflow.

GeoScout recorded total run latency as well as tool and LLM execution information.

---

### Tool Calls

**Definition:** The number of external tools the agent invokes during a task.

**Example:**

```text
Question
   ↓
get_region()
   ↓
summarize_hotspots()
   ↓
Answer
```

Tool calls help us understand the agent's workflow and orchestration behaviour, not simply its final answer.

---

### LLM Calls

**Definition:** The number of times the language model is invoked during one task.

This can help measure how much model interaction is required to complete the workflow.

---

### Token Usage

**Definition:** The amount of text-token processing used by the language model.

More tokens generally mean more model computation/context usage, although token count alone does not tell us whether the reasoning was good.

---

## 4. The Most Important Lesson from GeoScout

GeoScout showed why evaluating an agent using only final-answer accuracy can be insufficient.

A useful mental model is:

```text
                 AGENT EVALUATION

        ┌──────────────────────────┐
        │   Was the answer right?  │
        │    Answer Correctness    │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │ Was evidence obtained?  │
        │    Evidence Support      │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │ Were claims grounded?    │
        │   Grounded Correctness   │
        └──────────────────────────┘

        Plus operational behaviour:

        Latency • Tool Calls • LLM Calls • Tokens
```

The key lesson is:

> **A good agent should not only produce the right answer; it should produce an answer that can be supported by an observable and appropriate workflow.**

---

## 5. GeoScout v3 Example

GeoScout evaluated two models on 20 tasks.

| Metric | GPT-OSS 20B | GPT-OSS 120B |
| :--- | :--- | :--- |
| **Answer correctness** | 95% | 100% |
| **Evidence support** | 90% | 95% |
| **Grounded correctness** | 90% | 95% |
| **Mean latency** | ~8.25 s | ~9.76 s |

The important observation is that answer correctness was higher than grounded correctness for the 20B model.

That difference is meaningful:

```text
95% answers correct
        ↓
    but only
90% were both correct AND grounded
```

So the extra 5 percentage points reveal cases where correctness alone would have hidden a grounding/workflow problem.

---

## 6. Metric Selection

When evaluating a system, first ask:

| Question | Useful Metric |
| :--- | :--- |
| Did it give the right answer? | **Answer correctness** |
| Did it obtain the required evidence? | **Evidence support** |
| Was the answer correct and supported? | **Grounded correctness** |
| Are individual claims supported? | **Claim groundedness** |
| How fast was it? | **Latency** |
| How many tools did it use? | **Tool calls** |
| How much model interaction occurred? | **LLM calls** |
| How much model processing was used? | **Token usage** |

---

## Connection to GeoScout

**`metrics-lab`** is the conceptual learning space.

**`GeoScout`** is the practical research system where these ideas are implemented and measured.

```text
metrics-lab
    │
    │ learn what the metrics mean
    ▼
GeoScout
    │
    │ apply the metrics to an actual agent
    ▼
Research results
```

The purpose is not to memorize metric names.

The purpose is to understand what question each metric answers and what it fails to tell us.
