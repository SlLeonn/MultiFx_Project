# Hardware feasibility report

Reviewed: 2026-11-07. Status: historical study, superseded by the delivered PCB design.

**2026-11-26 update:** use the [current hardware guide](README.md) and [delivered schematic](outputs/schematics/Schematics.pdf) for the implemented design. The study below is preserved as written: its TLV9064 conditioner, 12 V supply candidate, procurement leads, and then-pending design work are historical, not the current BOM or status.

The available parts support a mono guitar-effects amplifier built around the user's **TSA1701**, an on-board TLV9064 input conditioner, and an STM32F030 controller. A power amplifier, speaker, and regulated supply still need to be selected and obtained. This is a documentation and analytical review, not a verified schematic or bench result.

The user now permits locally obtainable components to be soldered directly to the main PCB. This supersedes the earlier requirement to connect every non-library component externally. A purchased part still needs an exact manufacturer reference, verified symbol, footprint, electrical design, and physical availability before PCB release.

## Available components and their roles

Evidence: the screenshots supplied by the user, including the additional named components. Native Altium libraries and stock quantities have not been inspected.

| Parts shown | Useful role | Limit or unresolved item |
|---|---|---|
| STM32F030C8T6TR, LQFP48 | Buttons, LEDs, startup coordination, and DSP parameter control. | Verify both symbol units, every supply pin, and footprint. Reserve SWD and reset access. |
| TLV9064IDR | High-impedance guitar buffer, bias-reference buffer, and optional level adaptation. | SOIC-14; operates from 1.8–5.5 V. Not a speaker amplifier. |
| Resistors, capacitors, 10 kΩ TC33X trimmer | Bias, gain, coupling, decoupling, LED current limiting, and optional I²C pull-ups. | Check actual values, tolerance, dielectric, working voltage, and quantities. The trimmer is not a panel control. |
| Pushbuttons, green/red LEDs | Minimum user interface. | Debounce buttons; provide LED resistors and respect GPIO limits. |
| Headers, screw terminals, DC jack, Schottky diodes, ferrite bead | Module wiring and power entry/filtering candidates. | Verify polarity, pitch, current, voltage drop, and mechanical fit. |
| Generic buck/boost converters, 3.3 V LDO, DS8570F08 entry | Supply candidates. | Exact identities and application circuits remain unresolved; current labels do not establish usable output power. |
| TVS and generic MOSFET entries | Protection candidates. | Their labels alone do not establish clamping, leakage, gate drive, or pinout suitability. |
| ESP32-C3 module, SPI flash, USB–UART bridge, relay, TP4056, IMU, TMP102, INA139, RS-485 transceiver, RGB LED | No necessary role in the minimum product. | Leave them out unless a concrete requirement justifies them. |

The [TLV906x datasheet, SBOS839N](https://www.ti.com/lit/ds/symlink/tlv9064.pdf) supports the low-voltage buffer proposal. Its typical 50 mA short-circuit current is not an audio-output rating: even 1 W into 8 Ω requires `sqrt(1/8) = 0.354 A RMS`.

## Proposed interconnection

```mermaid
flowchart LR
    Guitar[Guitar] --> Jack[Instrument jack]
    Jack --> Input[Main PCB: TLV9064 conditioner]
    Input --> DSP[TSA1701: ADC → DSP → DAC]
    DSP --> Amp[Selected power amplifier]
    Amp --> Speaker[Selected speaker]
    Buttons[Buttons] -.-> MCU[Main PCB: STM32F030]
    MCU -. 3.3 V I2C parameters .-> DSP
    MCU -.-> LEDs[Indicators]
    Pots[TSA1701 potentiometers] -.-> DSP
```

Solid arrows carry analog audio outside the DSP module; dashed arrows carry controls. Power wiring is described below. The STM32 does not carry audio samples. No additional audio codec or audio connection to the STM32 ADC is needed.

### Guitar to DSP

TinySine publishes the following [TSA1701 module specifications](https://www.tinysineaudio.com/products/tsa1701-audio-dsp-board):

| Interface | Published value or identification |
|---|---|
| Analog input | 20 kΩ input resistance; 2 Vrms signal range. |
| Analog output | 0.9 Vrms output level; DAC0–DAC3. |
| Supply options | 5 V through microUSB, or 9–30 V through the DC input. |
| Local controls | Four potentiometers. |
| Board outline | 72 × 50 mm; mounting details still to verify. |

These figures describe the manufacturer's module, not measurements of the user's board. TSA1702B assumptions in the earlier architecture report do not establish this board's interfaces.

For a passive pickup, a 20 kΩ load can change both level and tonal response. Propose an approximately 1 MΩ instrument input, followed by a low-impedance buffer driving the module's **audio connector**. Existing values can form `390 kΩ + 390 kΩ + 226 kΩ = 1.006 MΩ` nominal; a missing single 1 MΩ resistor does not block the design.

Use AC coupling, a quiet buffered midpoint reference, suitable protection, and a selected buffer/gain stage. On a proposed 5 V analog rail, the local midpoint would be approximately 2.5 V. Keep that bias out of the grounded instrument cable and do not assume access to the DSP chip's internal reference. Configure unused op-amp channels in a defined stable state.

Choose gain from guitar peaks, op-amp headroom, and module clipping, then verify it. Even an ideal 5 V midpoint-biased stage cannot pass more than about `2.5/sqrt(2) = 1.77 Vrms` of symmetrical sine output; the real limit is lower and load dependent. The module's published 2 Vrms input range is not a reason to demand 2 Vrms from this conditioner. Digital drive should occur in the DSP while the ADC remains unclipped.

Use one documented input channel and route the selected mono DSP output to one amplifier input. Do not short DAC channels together. If panel potentiometers replace the on-board controls, follow TinySine's required solder-link changes first.

### STM32 to DSP and programmers

The [STM32F030 datasheet, DS9773 Rev. 5](https://www.st.com/resource/en/datasheet/stm32f030c8.pdf) and [AN4325 Rev. 2](https://www.st.com/resource/en/application_note/dm00089834-getting-started-with-stm32f030xx-and-stm32f070xx-series-hardware-development-stmicroelectronics.pdf) support a 3.3 V controller with an internal clock. An external crystal, SPI flash, and USB interface are unnecessary for the proposed minimum.

- Connect verified SDA, SCL, and ground between the controller and module. Use open-drain signaling and confirm the module's actual pull-ups are compatible with 3.3 V; a 5 V module supply does not imply 5 V control signals.
- Inspect existing pull-ups before fitting more. The available 4.7 kΩ resistors are candidates, not automatically correct values. Start with a conservative bus rate and check rise time against total bus capacitance; see [TI SLVA689A](https://www.ti.com/lit/pdf/slva689).
- The DSP becomes an I²C master during EEPROM self-boot. Keep the MCU off the bus until startup completes, and prevent concurrent MCU/USBi access during programming. Provide a service disconnect or jumpers. Do not tie independent programmer and product supply outputs together.
- Verify that SDA, SCL, and reset cannot feed an unpowered MCU or module through pull-ups or protection diodes. Document the allowed DC/microUSB/USBi power combinations; firmware inactivity alone does not prevent back-powering.
- With self-boot enabled, ADI's `0x68` write / `0x69` read address bytes correspond to the 7-bit address `0x34`. Confirm the actual configuration and the MCU API's address convention. See [ADI AN-923](https://www.analog.com/en/resources/app-notes/an-923.html).
- Export parameter addresses and encoding from the deployed SigmaStudio project. Use the [ADAU1701 safeload mechanism](https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1701.pdf) where coherent live updates require it. Define whether each parameter belongs to a physical pot or the MCU to avoid competing writes.
- Reserve SWDIO, SWCLK, NRST, ground, and target-voltage reference for an appropriate STM32 programmer. USBi programs the DSP; it does not replace an STM32 SWD programmer.

The IC documentation establishes capability. It does **not** identify the TSA1701 debug connector's numerical pin order. Confirm that order, connector orientation, reset access, and programmer power wiring on the actual board before committing a PCB connector.

### DSP to speaker and power

Select the amplifier, speaker impedance/power, supply, and enclosure together. Match the DSP output to amplifier sensitivity and input impedance; provide attenuation or buffering only if required. For any BTL amplifier, neither speaker terminal is ground, and output channels must not be paralleled unless explicitly supported.

A commercially assembled amplifier module is the initial integration preference if obtainable locally. Direct integration of a purchased amplifier IC is also permitted, but requires its complete application circuit, thermal layout, and footprint before manufacturing. The [Electrónicos Caldas audio catalogue](https://www.electronicoscaldas.com/es/30-circuitos-integrados-para-audio-sonido-amplificadores-controles) lists LM380 and LM386 as in stock when consulted; this is a procurement lead, not a reservation or a selected BOM. No particular class-D module or suitable speaker was confirmed locally. Telemundo stock was not verified.

The [LM380 datasheet](https://www.ti.com/lit/ds/symlink/lm380.pdf) illustrates a possible low-power IC route, with supply, fixed gain, output coupling, and PCB heat spreading to account for. Its headline output is not guaranteed at an arbitrary supply or distortion. This review does not select it.

That route also exposes a passive-component gap: a single-ended output coupled through the listed 100 µF capacitor into an idealized 8 Ω load has `fc = 1/(2πRC) ≈ 199 Hz`, attenuating a guitar's low E. A nominal 20 Hz coupling corner would require approximately 1000 µF, subject to the actual load and voltage rating. Source the appropriate capacitor or use an amplifier topology that does not require this output coupling; a module may already include the required parts.

Keep distinct power branches for the amplifier, DSP module, analog conditioner, and 3.3 V controller. A 12 V main rail with a verified step-down stage for low-voltage circuitry is one candidate, **not a selected supply**. Use the TSA1701's documented power input for the chosen voltage. Its potentiometer connector's 3.3 V output has no established spare-current budget for powering the main PCB.

Do not connect 9/12 V directly to the TLV9064 or STM32. Do not assume a generic LDO solves the problem: dissipation is approximately `(Vin - Vout) × Iout`; at 100 mA, 12 → 3.3 V dissipates 0.87 W, versus 0.17 W for 5 → 3.3 V, excluding quiescent current. Converter and LDO selection must include stability, ripple, startup, dropout, and thermal conditions.

## Inventory issues to resolve

- `Res_191k...` is described as **191 Ω** in the screenshot. Confirm the actual value rather than trusting the item name.
- `DCDC_SW_BOOST_4A...` is described as a **buck**. The generic 3.3 V LDO and MOSFET entries also lack exact identities. Do not infer topology or pinouts.
- The additional `DS8570F08` name needs confirmation. The manufacturer's indexed [DS8570 data](https://www.dstech.com.cn/Upload/images/20240731/133668811407440985.pdf) specifies a low-voltage LDO with separate input/bias supplies limited to 5.5 V operation. If this is the supplied part, it cannot accept a 9/12 V input. Full PDF retrieval failed during this review; confirm the exact variant and full document before using it.
- The 100 nF capacitor is **Y5V**, with a wide stated tolerance. Avoid relying on its nominal value for precise filters or minimum regulator capacitance. Obtain suitable X7R decouplers if effective capacitance cannot be established; X5R parts also need DC-bias checks. See [Murata's DC-bias guidance](https://www.murata.com/en-sg/support/faqs/capacitor/ceramiccapacitor/char/0005).
- Do not place 6.3 V or 10 V capacitors on a 12 V rail. Recheck every capacitor against the chosen node voltage and transients.
- The `TVS_3V3` description lists a 14.1 V surge-clamping value. A 3.3 V label does not establish adequate pin protection. Confirm exact clamping conditions, leakage, capacitance, and protected-device limits.

## Local procurement candidates

Website listings consulted on 2026-11-07; retrieved pages may be cached. These are candidates for evaluation, not a selected BOM or confirmation of physical stock. Confirm the exact supplied part, package, quantity, and collection availability with the shop before fixing PCB interfaces.

| Need | Local listing | Assessment |
|---|---|---|
| Power amplifier | Electrónicos Caldas lists [LM380 in its audio catalogue](https://www.electronicoscaldas.com/es/30-circuitos-integrados-para-audio-sonido-amplificadores-controles) and [LM386N-1, DIP-8](https://www.electronicoscaldas.com/es/circuitos-integrados-para-audio-sonido-amplificadores-controles/338-amplificador-de-audio-mono-lm386n-1.html) as in stock. | Potential low-power IC routes. LM386N-1 is a demonstration alternative; suitability for the intended practice volume remains unresolved. Neither is a drop-in replacement for a complete amplifier module. |
| Main supply | [M-1220 adapter, 12 V / 2 A](https://www.electronicoscaldas.com/es/fuentes-adaptadores-baterias/1200-adaptador-de-voltaje-12v-2a.html), listed in stock. | Candidate only if the chosen amplifier and total power budget fit. The advertised center-positive 5.5 × 2.5 mm plug differs from the library jack's 2.1 mm designation; verify mating dimensions and polarity. |
| Low-voltage conversion | [MOD-XL4015E1 step-down module](https://www.electronicoscaldas.com/es/reguladores-referencias-conversores-de-voltaje/407-modulo-con-conversor-buck-step-down-xl4015.html), listed in stock. | A possible alternative to unidentified library converters. Check mounting, ripple, startup, thermal behavior, and usable current before selection; the advertised 5 A is not a validated system rating. |

A suitable speaker, 6.35 mm instrument jack, larger output-coupling capacitor if required, and a specific class-D amplifier module remain unconfirmed locally. Telemundo inventory has not been verified. Obtain these items or their exact drawings before designing their PCB connections; do not reserve an unspecified footprint.

## Before manufacturing

1. Obtain the native library and physical part references. Compare symbols, pin numbers, footprints, polarity, and mounting dimensions against manufacturer drawings and actual parts, including a 1:1 footprint check.
2. Obtain the amplifier, speaker, supply, instrument jack, necessary cables/connectors, and suitable programmers. Close the supply tree, gain structure, load, power budget, and thermal requirements.
3. Demonstrate a clean guitar/audio path, autonomous DSP startup, and one STM32-controlled parameter change with the actual module. Record connections, firmware/DSP versions, test levels, clipping points, startup timing, and results. Recheck the path with power amplification operating.
4. Complete and review the schematic and PCB: all MCU power pins, decoupling, boot/reset, service jumpers, amplifier mute if available, test points, current returns, and mechanical clearances. Keep switching/high-current loops away from the high-impedance input and use a deliberate ground-return layout.
5. Run ERC/DRC using the chosen fabricator's rules and inspect fabrication outputs. Release only when unresolved interfaces have been closed or explicitly removed from scope.

The immediate next step is a constrained schematic based on identified parts and interfaces. A final fabrication-ready PCB cannot yet be justified by the supplied screenshots alone.
