# Aurion Offline RL Lab

This directory is an isolated research surface for reinforcement-learning experiments that consume exported Aurion observations and produce candidate policies or evaluation results.

## Hard boundary

- No code in this directory is imported by the Echoes of Aurion runtime.
- No write path back into Aurion exists.
- Experiments must work from exported fixtures, logs, or datasets.
- Training output is never production truth.
- Any result proposed for Aurion must pass the normal deterministic implementation, runtime, regression, and evidence gates in the Aurion repository.

## Minimal flow

1. Aurion exports deterministic observations outside its runtime path.
2. This lab trains or evaluates an agent offline.
3. Results are written as evidence artifacts.
4. Humans or tooling may translate validated findings into deterministic Aurion logic.
5. Aurion remains authoritative; this repository never becomes a runtime dependency.

## External services

The boundary is designed to work without a hosted Hugging Face job, Space, endpoint, or other remote service. Hosted compute may be added later as an optional accelerator, not as a runtime dependency.
