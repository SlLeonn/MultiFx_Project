# Working principles - MultiFX

## Priorities

1. Engineering rigor: keep theory, explanation, and implementation consistent, and check them against real system behavior. An elegant solution must be correct within explicit limits.
2. Controlled minimalism: use the least complexity that preserves correctness, clarity, and verifiability. Every file, dependency, and abstraction must earn its place.

## Project context and constraints

- Start with [README.md](README.md) and the phase context it identifies as current. Read earlier phases and local references when the task depends on them.
- Treat the original project context as revisable background. Architecture, goals, and numerical estimates may improve as evidence develops.
- The component boundary is fixed: use only the professor's Altium library components on the main PCB. Other physically obtainable components must connect externally through headers. DSP module use has been accepted. Do not relax this restriction to simplify a design.
- Identify exact parts, pinouts, footprints, and electrical limits before relying on them. A library label or reported availability is not an electrical validation.
- Original source documents live in the Git-ignored `references/` directory. They may be consulted; preserve their names and contents unless the user explicitly requests changes. Maintained documentation must stand on its own when local references are absent.

## Engineering work

- Before a substantial technical change, establish the intended behavior and how to check it. Separate confirmed requirements, assumptions, and decision-relevant unknowns.
- Choose the simplest solution that meets those requirements. Explain decisions through their effect on the system and identify material tradeoffs.
- For changes affecting functional behavior, use [engineering-review](.agents/skills/engineering-review/SKILL.md) during design or review. Scale the depth to the impact.
- Consult primary sources when a decision depends on external specifications; identify the relevant version and conditions. Do not invent capabilities, values, or results.
- Run the relevant checks available in the environment. Distinguish analytical prediction, simulation, software tests, and physical measurement; state what remains unverified.
- Create folders and tools when they have a concrete use. Keep durable technical explanations beside their artifacts, avoiding duplicate accounts across documents.
- Delegate independent analysis when useful, define its scope, and integrate the findings into a coherent result.

## Documentation and communication

- Write maintained repository content and technical deliverables in English. Preserve component identifiers and original source documents as supplied.
- Lead with the result, then give the reasoning and evidence needed to assess it. Explain mechanisms and limits; use equations, examples, or diagrams when they clarify a decision.
- Maintain one `context/NN-phase-name.md` document per phase. Update it during the phase; record outcomes, decisions, evidence, and remaining work at closure. Keep the README's current-phase link accurate.
- Use context notes for continuity and the README for public presentation. Describe proposed and measured behavior distinctly. Add portfolio visuals when real diagrams, photographs, or results support them.
- Ask when missing information materially changes the design; continue independent work and disclose reasonable assumptions.
- Close with what changed, how it was checked, and any remaining limitation that affects use. Keep explanations proportional to the work.

## Codex integration

This file holds the general working rules. The local `$engineering-review` skill provides the technical review procedure. `.codex/config.toml` contains project preferences.

Open Codex at the repository root. Project instructions load when a session starts; restart if a renamed skill does not appear. Local configuration requires project trust, and session options or managed policies may take precedence.
