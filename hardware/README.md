# Hardware

The delivered design is a five-sheet hierarchical schematic and a two-layer PCB for guitar input conditioning, user controls, and external audio-module integration. Fabrication and assembly are pending, as confirmed on 2026-11-26. This guide describes the CAD handoff; it does not certify electrical operation or manufacturing approval.

## Open the project

Open [Portable_Guitar_MultiFX.PrjPcb](altium/Portable_Guitar_MultiFX/Portable_Guitar_MultiFX.PrjPcb) in Altium Designer. The supplied Gerber headers identify **Altium Designer 26.9.1** as the export tool. The editable design remains unchanged by repository organization.

Keep `altium/Portable_Guitar_MultiFX/` and `altium/Draftsman/` as siblings. The project references the drawing through `../Draftsman/Portable_Guitar_MultiFX.PCBDwf`; the existing project output subdirectory is also preserved.

| Sheet | Responsibility |
|---|---|
| `00_main.SchDoc` | Top-level hierarchy and interconnections. |
| `01_Alimentacion.SchDoc` | 5 V power entry, protection, distribution, and 3.3 V regulation. |
| `02_Entrada_Guitarra.SchDoc` | MCP6002 guitar-input conditioner and gain selection. |
| `03_Control.SchDoc` | STM32, USB–UART interface, buttons, and indicators. |
| `04_Interfaces_Audio.SchDoc` | TSA1701, amplifier, and speaker interfaces. |

Original CAD filenames and schematic labels are retained as supplied.

## Design and interfaces

| Function | Implemented in the supplied schematic |
|---|---|
| Main power | 5 V input; AP2301 P-channel MOSFET protection. |
| Logic supply | MCP1700-3302E/TO regulator for the 3.3 V controller rail. |
| Guitar input | MCP6002-I/P conditioner with approximately 1 MΩ bias resistance. JP3 selects gain ×1 when closed or ×2 when open. |
| Controller | STM32F030C8T6TR. |
| USB interface | Mini-B connector, CP2102N-A02-GQFN20R USB–UART bridge, and USBLC6-2SC6 protection. |
| DSP module | External TSA1701; ADC0/DAC0 analog audio and a 3.3 V I²C control interface. |
| DSP power | J4 supplies the TSA1701 through a cable to its microUSB power input. |
| Programming access | BOOT/reset controls and UART hardware. JP4/JP5 isolate MCU I²C during USBi programming; do not assume an additional SWD header. |
| Power output | External PAM8302 module. The schematic specifies a 4 Ω / 5 W speaker between OUT+ and OUT−; neither speaker terminal is ground. The speaker rating is not a measured amplifier output. |

These describe circuit intent, not measured values. Verify jumper settings, cable orientation, supply polarity, levels, and the actual module revisions before applying power. USBi programs the DSP; the controller has a separate programming path. Firmware and the SigmaStudio project were not supplied.

## Outputs and provenance

| Artifact | Location |
|---|---|
| Schematics | [PDF](outputs/schematics/Schematics.pdf) — five pages. |
| Bill of materials | [XLSX](outputs/bom/Portable_Guitar_MultiFX.xlsx). |
| Fabrication files | [Gerber and drill ZIP](outputs/fabrication/Gerbers.zip). |
| Raw fabrication outputs | [Original output folder](<altium/Portable_Guitar_MultiFX/Project Outputs for Portable_Guitar_MultiFX/>). |
| Assembly drawing | [Draftsman source](altium/Draftsman/Portable_Guitar_MultiFX.PCBDwf); no separate drawing PDF was supplied. |
| Mechanical model | [STEP](outputs/3d/MultiFX.step). |
| Original submission | [Entrega_MultiFX.zip](archive/Entrega_MultiFX.zip). |
| Earlier exported CAD copies | [Altium snapshot](archive/Altium/) and [mixed delivery snapshot](archive/Gerbers/). |

The 20 files inside the fabrication ZIP match the corresponding raw project outputs by SHA-256. The package contains top/bottom copper, solder mask, silkscreen, paste, mechanical plots, plated round and slotted drill files, and supporting reports. Keep the distinction between the `.GM` profile and the additional `.GM2` plot; they are different files, not interchangeable outline definitions.

The schematic PDF matches the PDF retained inside the Altium project. The original submission ZIP and nested CAD archive were also checked against their supplied copies. Original archives were not repacked.

The PCB and project copies in `archive/Altium/` and `archive/Gerbers/` differ from the authoritative source. They are retained for traceability and must not replace the editable project. The output-generation report is dated **15 November 2026, 14:47**; the authoritative PCB file has a later last-write time. Timestamps alone do not prove an electrical difference, but export-to-source equivalence is not established.

## Remaining handoff checks

- **Libraries:** symbols reference `shared_lib.IntLib` and Altium Content Vault. Standalone component libraries were not included; existing placed objects are preserved. Restore the appropriate library sources before library-driven updates or replacements.
- **Output paths:** the original `.OutJob` includes absolute paths to the former repository-root project folder. Set the PDF destination for the current checkout before regenerating outputs. No source configuration was silently rewritten.
- **Auxiliary references:** the project mentions `CAMtastic1.Cam`, `CAMtastic2.Cam`, and a generated DRC HTML report that were not supplied. A clean DRC result cannot be inferred from these references or from successful file export.
- **BOM:** the supplied spreadsheet contains 27 groups / 59 listed parts, omits JP1–JP8, and leaves U1/U2 manufacturer/ordering fields blank. Their schematic comments identify MCP1700-3302E/TO and MCP6002-I/P. Reconcile the assembly quantities and ordering fields before procurement; the original spreadsheet is unchanged.
- **Manufacturing:** confirm the authoritative PCB revision, regenerate or explicitly reconcile its outputs, run ERC/DRC with the intended fabricator's rules, and inspect the layer/drill mapping before placing an order.
- **Bring-up:** document supply/current checks, controller programming, DSP self-boot and external control, then audio, clipping, power, and thermal measurements. These results are not included in the handoff.

Altium `History`, `__Previews`, project logs, and hierarchy caches remain local and are ignored by Git. Fabrication outputs, source documents, BOM, STEP, and submission snapshots are retained for publication.

The [7 November feasibility report](feasibility-report.md) is historical: its TLV9064 conditioner and 12 V supply candidate are superseded by the delivered MCP6002 / 5 V design.
