---
name: engineering-review
description: Design or review functional changes in MultiFX by checking the theoretical model, implementation, and evidence. Use for architecture, calculations, circuits, firmware, or DSP as applicable; skip purely editorial or organizational changes.
---

# Engineering review

Apply the principles in [AGENTS.md](../../../AGENTS.md) and stay within the task's scope. This procedure guides the analysis; it does not require a separate report or additional files.

1. **Define testable behavior.** Identify inputs, outputs, interfaces, operating range, and acceptance criteria. If a decisive parameter is missing, request it or make the conclusion conditional on it.
2. **Build the smallest sufficient model.** State assumptions, quantities, units, and limits of validity. Check dimensions, signs, orders of magnitude, and relevant boundary cases. Derive only the relationships needed to support the decision.
3. **Compare model and implementation.** Follow signals, data, and resources between blocks. Examine constraints that could invalidate the prediction:
   - For circuits: supply, bias, impedance, tolerances, noise, bandwidth, and saturation, as applicable.
   - For firmware and DSP: sampling, numerical scales, quantization, stability, memory, concurrency, execution budget, and latency, as applicable.
   - For interfaces: compatible levels, units, formats, timing, and error behavior. Examine integration as well as each block in isolation.
4. **Look for an observable discrepancy.** Choose the most direct check that could refute the model or expose an integration fault: an independent calculation, simulation, test, or measurement. Compare expected and observed behavior under explicit conditions and tolerances. A software test does not replace physical validation.
5. **Resolve and communicate.** Correct contradictions and repeat the affected checks. If verification is unavailable, qualify the conclusion and identify the remaining check. Summarize the decision, rationale, evidence, and relevant limitation in the space the task warrants.

When several defects exist, prioritize their effect on operation and support each finding with its mechanism, location, and available evidence. Recommend the smallest correction that addresses the cause.
