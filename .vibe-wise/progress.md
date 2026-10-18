# Learning Progress

Learning mode was paused by the user on 2026-10-16. Design choices made while paused were picked from options Claude recommended; they are not designs the learner reasoned out. Learning mode resumed on 2026-10-18.

## Detection: agent vs. workflow (PENDING Build checkpoint, opened 2026-10-18)
- Concept explained: workflow (code decides the steps, LLM called at fixed points) vs. agent (LLM loop picks tools and decides the next step).
- Learner's position: wants detection to be an agent. Stated reason: past experience that hardcoding too much leads to a bad system.
- Open question: the difference between hardcoding judgment and hardcoding control flow; which decisions the model should own; latency and cost on every navigation.
- Not yet decided: no design confirmed.
- The learner asked Claude to choose. Claude proposed a hybrid: a fixed pipeline for clear cases, plus a bounded agent only for unclear cases (read-only tools, step and call limits, a forced verdict at the limit). Goal chat and Convince Me are conversational LLM features. This is Claude's proposal, not the learner's reasoned design.

## Build order (PENDING Build checkpoint, opened 2026-10-18)
- Status: pending. The learner asked what to build first. The spec gives no build order.
- Concept explained: vertical slice (walking skeleton) vs. building the riskiest piece first vs. building layer by layer.
- Waiting on: the learner's reasoning about which piece to build first, and why.
