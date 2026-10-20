# 00 — Project baseline

Date: 2026-10-20 · Status: active

## Purpose and confirmed constraints

Develop a compact guitar practice amplifier with digital effects, progressing toward an integrated prototype and a clear engineering portfolio. This baseline distills the initial project context; architectural choices remain revisable unless explicitly constrained below.

- The main PCB may use only components from the professor's Altium library.
- Other components must be physically obtainable and connected externally through headers. The design must not depend on waiting for overseas component orders.
- Use of a DSP module is accepted. The allowed component set is a design constraint, not an invitation to substitute unrestricted catalog parts.
- Maintained repository content is in English. Preserve original local source documents unchanged.

The library inventory in the historical context came from screenshots; native Altium library files have not been inspected in the recorded evidence. Exact part identities, ratings, and footprints require confirmation before design release.

## Provisional engineering baseline

| Area | Working proposal | Still to establish |
|---|---|---|
| Audio input | External active high-impedance guitar conditioner. | Circuit, available parts, input range, noise, and protection. |
| Audio processing | TSA1702B / ADAU1701, programmed using SigmaStudio and USBi. | Actual board revision, programming connection, clean audio, and autonomous boot. |
| Control | STM32F030C8T6 for buttons, indicators, and DSP parameter control over I2C. | Accessible bus, logic levels, addressing, boot coordination, and programming access. |
| Output | Commercial power amplifier and speaker. | Exact models, supply requirements, loading, and clean output. |
| Main PCB | Control, supply distribution, and connections to external modules. | Native library, interfaces, mechanical dimensions, and power design. |

The STM32 does not carry audio samples. The DSP module performs audio conversion and processing; I2C carries control transactions.

The proposed minimum is mono clean and drive modes with EQ, two buttons, LED feedback, module potentiometers, and operation without a computer after programming. An external regulated supply is the starting approach; its voltage and current rating remain open until the actual loads are known. A battery, display, persistent presets, and additional effects are outside this minimum.

Earlier ESP32-S3 / ES8388 proposals are historical alternatives, not the current BOM. Historical prices, supply estimates, and schedule references are not current commitments. No audio quality, latency, power, or thermal performance figure has been validated.

## Evidence at baseline

| Information | Evidence level |
|---|---|
| Component restrictions and DSP-module acceptance | Reported project constraints, retained as firm. |
| TSA1702B and USBi availability | Reported by the user; not a compatibility or operating test. |
| STM32F030C8T6 in the allowed library | Recorded from the historical library inventory; verify against native files. |
| Proposed architecture and minimum features | Planning context; open to improvement. |
| Complete audio chain, deployed controller firmware, MultiFX PCB, system power budget | No completed validation recorded. |

The source material is a technical continuity document dated 2026-10-20 and Elecia White's *Making Embedded Systems*, 2024 edition. The former supplies project history; the latter supplies engineering guidance, not evidence that this hardware works. This baseline contains no new bench measurements.

## Open questions and next objective

Establish a verified audio and control foundation before committing to a main PCB:

1. Identify the physical DSP board, USBi programmer, accessible connectors, and native library components. Resolve ambiguous part names against exact manufacturer documentation.
2. Confirm safe supplies, audio levels, and programming connections for the actual module. Define the test input range and measured pass criteria before testing clean audio.
3. Verify that the DSP retains and starts the intended program without the computer. Establish when an external controller can access I2C without interfering with startup or USBi.
4. Demonstrate an externally commanded DSP parameter change. Confirm the controller and its programming/debug interface from that result.
5. Select obtainable conditioning, amplification, speaker, and supply parts using documented interface requirements. Calculate and then measure the resulting power budget; define the relevant thermal conditions.

Budget, deadline, audio performance targets, final enclosure, and available measurement equipment must be confirmed when they affect these decisions. No schematic or pinout should be finalized from a generic library label or an assumed module revision.

## Phase closure

Close this phase when the actual module and allowed library are identified, clean audio and autonomous startup have recorded results, and external parameter control is either demonstrated or replaced by an explicitly justified architecture decision.

Record hardware identity, software versions, connections, test conditions, expected behavior, measurements, and outcome with each bench result. Keep remaining power, thermal, procurement, and integration work explicit; passing an isolated module test does not validate the complete amplifier.

Add a brief outcome and remaining questions here before opening the next `NN-phase-name.md` context file, then update the current-phase link in the README. Technical artifacts and durable explanations belong in their relevant subsystem directories as they appear.
