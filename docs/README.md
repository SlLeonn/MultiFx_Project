# Documentation

The [hardware guide](../hardware/README.md) and [schematic PDF](../hardware/outputs/schematics/Schematics.pdf) describe the delivered PCB design. Fabrication, assembly, and physical validation are pending.

## Application note

[MFX-AN-001 — PDF](application-note/application-note.pdf) / [LaTeX and reproducible analysis](application-note/README.md): an 11-page pre-fabrication guide to the 5 V MCP6002/STM32/TSA1701/PAM8302 design. It includes analytical response and margins, verified board-side connections, staged bring-up, PCB implementation, and a planned test protocol. Calculations and manufacturer specifications are distinguished from measurements that remain pending.

## Earlier studies

| Document | Scope and status |
|---|---|
| [System architecture — PDF](system_architecture.pdf) / [LaTeX source](system-architecture.tex) | Initial context, block, and software-dependency diagrams. The PDF has three pages. Its TSA1702B identity and component-placement restriction are superseded; retain it as project history. |
| [Hardware feasibility report](../hardware/feasibility-report.md) | 7 November 2026 component and interface study. The delivered design uses MCP6002 and a 5 V input rather than its TLV9064 / 12 V candidate. |

The [PCB preview](media/pcb-top.svg) is rendered from the supplied top-side Gerber layers, profile, and plated drill files. Colors are illustrative. Its embedded metadata records source hashes; it represents the fabrication snapshot, not an assembled board or a DRC result.

Original reports and generated engineering files are preserved. Current hardware decisions should be checked against the delivered schematic and editable Altium project.
