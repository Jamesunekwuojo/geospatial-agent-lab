# Metrics Lab

A small learning/reference lab for understanding evaluation metrics used in
AI agents, machine learning systems, and research experiments.

This lab uses **GeoScout** as the main practical reference so that the
definitions are connected to a real project rather than learned only
theoretically.

---

## 1. The Main Idea

A metric is simply a way of measuring some aspect of a system.

Different metrics answer different questions:

```text
Did it get the answer right?
        ↓
Answer Correctness

Did it obtain the required evidence?
        ↓
Evidence Support

Was the answer both correct AND supported?
        ↓
Grounded Correctness

How long did it take?
        ↓
Latency

How much work did the agent perform?
        ↓
Tool Calls / LLM Calls / Tokens
```

Therefore:

**One metric rarely tells the whole story.**

GeoScout demonstrated this directly: a model can produce a correct-looking
answer while failing to acquire the evidence required to support it.