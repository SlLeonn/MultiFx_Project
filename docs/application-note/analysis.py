"""Reproduce the application note's analytical predictions using Python's standard library.

Run ``python analysis.py`` to regenerate the three data files, or append ``--check``
to verify them without writing. Values are transcribed from the identified CAD/BOM
revision below; source hashes deliberately stop a stale model after a design change.
This is a linear circuit calculation, not SPICE or physical measurement.
"""

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_COMMIT = "ad3ab214415b7b048fcca606c6cc5987dbe40415"
SOURCE_HASHES = {
    "hardware/outputs/schematics/Schematics.pdf": "8ca84faefa27fd4ee6b135daf9fe36735665aef9460b0a466e211ab99ecd2310",
    "hardware/outputs/bom/Portable_Guitar_MultiFX.xlsx": "7f89880996bfff5cceb7133e42c2d9a78308d5e62820b94bbe5d5fd937055b79",
    "hardware/altium/Portable_Guitar_MultiFX/01_Alimentacion.SchDoc": "0f19c5e620e7a3ffe55ab91afd9c6dcd0c8450b18533fdaa052896dfc289b440",
    "hardware/altium/Portable_Guitar_MultiFX/02_Entrada_Guitarra.SchDoc": "0afa9f9dee7f8117dc4836d73f45535e46383cf91221bddc2a9d9b5f5507aff1",
    "hardware/altium/Portable_Guitar_MultiFX/03_Control.SchDoc": "9388318661931a1bd532f851675be10bef32ee073a7594ae7d71ed7f4da65635",
    "hardware/altium/Portable_Guitar_MultiFX/04_Interfaces_Audio.SchDoc": "2195089ae13f3b80b9dc273b30f829c5305ffe707ea7b6d12950c2094dac8ee8",
    "hardware/altium/Portable_Guitar_MultiFX/Portable_Guitar_MultiFX.PrjPcb": "ea93ac664b46bfab62553e1210e95d6832a7dda020c8b7f50c2f508a6367ae69",
    "hardware/altium/Portable_Guitar_MultiFX/Portable_Guitar_MultiFX.PcbDoc": "7bbb6a7ddc1293db80a0ad6b51e031024b3105b0a23cf1a333f32583c36ba1ac",
    "hardware/outputs/fabrication/Gerbers.zip": "5fe040f5f471463f912fa037bc8455444d8de7e6e10d3da64e607bf70812c9d9",
}

# SI units: ohms, farads, volts, amperes. Tolerances are initial BOM tolerances.
R = {"R2": 100.0, "R3": 10e3, "R4": 10e3, "R5": 4.7e3,
     "R6": 390e3, "R7": 390e3, "R8": 226e3, "R9": 10e3,
     "R10": 10e3, "R11": 100.0, "R12": 226e3,
     "R13": 33.2e3, "R14": 73.2e3}
C = {"C3": 22e-6, "C6": 10e-6, "C7": 470e-9, "C8": 1e-6}
TOL_R = {name: (0.05 if name in {"R2", "R3", "R4", "R9", "R10", "R11"}
                        else 0.01) for name in R}
TOL_C = {"C3": 0.20, "C6": 0.10, "C7": 0.10, "C8": 0.10}

SOURCES = {
    "MCP6002": {
        "document": "Microchip DS20001733L (2020), electrical characteristics, p. 3",
        "url": "https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6001-1R-1U-2-4-1-MHz-Low-Power-Op-Amp-DS20001733L.pdf",
        "conditions": "IQ=100 uA typical / 170 uA maximum per amplifier at TA=25 C, VDD=5.5 V, VCM=5 V, IO=0; used below as scenarios, not 5 V midrail guarantees.",
    },
    "MCP1700": {
        "document": "Microchip DS20001826F (2020)",
        "url": "https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1700-Data-Sheet-20001826F.pdf",
    },
    "TSA1701": {
        "document": "TinySine TSA1701 product specifications, consulted 2026-11-26",
        "url": "https://www.tinysineaudio.com/products/tsa1701-audio-dsp-board",
        "conditions": "Published 20 kohm input and 0.9 Vrms output are module data; actual revision/loading remain to verify.",
    },
    "PAM8302A": {
        "document": "Diodes DS41333 Rev. 6-2 (May 2021), pp. 3, 7",
        "url": "https://www.diodes.com/datasheet/download/PAM8302A.pdf",
        "conditions": "23.5 dB IC gain and 2 W typical at 5 V, 4 ohm, 1 kHz, 1% THD+N; this is a conditional IC example, not a characterized commercial module.",
    },
}


def parallel(a, b):
    return a * b / (a + b)


def db(amplitude):
    return 20.0 * math.log10(abs(amplitude))


def highpass(frequency, capacitance, series_resistance, load_resistance):
    """Loaded series-C network: Vin -> series R/C -> load R to AC ground."""
    s = 2j * math.pi * frequency
    return s * capacitance * load_resistance / (
        1.0 + s * capacitance * (series_resistance + load_resistance))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated files without writing")
    args = parser.parse_args()
    for name, expected in SOURCE_HASHES.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Source changed: {name}. Review component values and source hashes before regeneration.")

    rb = R["R6"] + R["R7"] + R["R8"]
    module_input = 20e3  # Assumed frequency-independent module load, not measured.
    rl = parallel(R["R12"], module_input)
    input_attenuation = rb / (rb + R["R5"])
    output_attenuation = rl / (rl + R["R11"])
    passband = input_attenuation * output_attenuation
    input_pole = 1 / (2 * math.pi * C["C7"] * (rb + R["R5"]))
    output_pole = 1 / (2 * math.pi * C["C8"] * (rl + R["R11"]))
    gain_low = 1 + (R["R9"] * 0.95) / (R["R10"] * 1.05)
    gain_high = 1 + (R["R9"] * 1.05) / (R["R10"] * 0.95)
    vref_resistance = parallel(R["R3"], R["R4"])
    vref_tau = vref_resistance * C["C6"]
    analog_pole = 1 / (2 * math.pi * R["R2"] * C["C3"])

    # Ideal, quiet reference and ideal op-amp gain. Rs=0 generator model.
    def response(frequency, gain=1.0):
        return gain * highpass(frequency, C["C7"], R["R5"], rb) * highpass(
            frequency, C["C8"], R["R11"], rl)

    # Static analog branch scenario: two op-amp Iq currents plus divider current.
    # Ignore output/bias/leakage currents and Q1 drop; 5 V is after Q1 here.
    system_rail = 5.0
    def analog_rail(iq_per_channel):
        return (system_rail - R["R2"] * 2 * iq_per_channel) / (
            1 + R["R2"] / (R["R3"] + R["R4"]))
    va_typ = analog_rail(100e-6)
    va_scenario = analog_rail(170e-6)
    vref = va_typ / 2
    margin = 0.1  # Illustrative reserved rail margin; not a manufacturer guarantee.
    swing = min(vref - margin, va_typ - margin - vref)
    max_input_one_rms = swing / (input_attenuation * math.sqrt(2))
    amp_gain_db = 23.5
    amp_gain = 10 ** (amp_gain_db / 20)
    amp_input_rms = math.sqrt(2.0 * 4.0) / amp_gain
    amp_input_ratio = amp_input_rms / 0.9

    def divider(vbus, upper, lower):
        return vbus * lower / (upper + lower)
    # Illustrative supply scenario; not a USB compliance declaration.
    vbus_corners = [divider(v, R["R13"] * a, R["R14"] * b)
                   for v, a, b in itertools.product((4.75, 5.25), (0.99, 1.01), (0.99, 1.01))]

    values = {
        "InputResistanceM": rb / 1e6, "InputResistanceK": rb / 1e3,
        "InputPoleHz": input_pole,
        "InputPoleMinHz": input_pole / (1.01 * 1.10),
        "InputPoleMaxHz": input_pole / (0.99 * 0.90),
        "InputAttenuationDb": db(input_attenuation),
        "OutputLoadK": rl / 1e3, "OutputPoleHz": output_pole,
        "OutputPoleMinHz": 1 / (2 * math.pi * C["C8"] * 1.1 * (parallel(R["R12"] * 1.01, module_input) + R["R11"] * 1.05)),
        "OutputPoleMaxHz": 1 / (2 * math.pi * C["C8"] * 0.9 * (parallel(R["R12"] * 0.99, module_input) + R["R11"] * 0.95)),
        "OutputAttenuationDb": db(output_attenuation),
        "PassbandGainOneDb": db(passband),
        "GainTwoMin": gain_low, "GainTwoMax": gain_high,
        "VrefPoleHz": 1 / (2 * math.pi * vref_tau), "VrefTauMs": vref_tau * 1e3,
        "VrefRatioMin": 0.475, "VrefRatioMax": 0.525,
        "AnalogPoleHz": analog_pole,
        "AnalogPoleMinHz": analog_pole / (1.05 * 1.20),
        "AnalogPoleMaxHz": analog_pole / (0.95 * 0.80),
        "AnalogRailTyp": va_typ, "AnalogRailScenario": va_scenario,
        "AnalogCurrentTypMilli": (system_rail - va_typ) / R["R2"] * 1e3,
        "AnalogCurrentScenarioMilli": (system_rail - va_scenario) / R["R2"] * 1e3,
        "VrefNominal": vref, "HeadroomMarginV": margin,
        "ConditionerOutputPeak": swing,
        "ConditionerInputOneRms": max_input_one_rms,
        "ConditionerInputTwoRms": max_input_one_rms / 2,
        "ConditionerInputTwoWorstRms": max_input_one_rms / gain_high,
        "ConditionerDspOutputRms": swing * output_attenuation / math.sqrt(2),
        "VbusNominal": divider(5, R["R13"], R["R14"]),
        "VbusLow": min(vbus_corners), "VbusHigh": max(vbus_corners),
        "AmpGainDb": amp_gain_db, "AmpGainLinear": amp_gain,
        "AmpInputRms": amp_input_rms, "AmpInputRatio": amp_input_ratio,
        "AmpAttenuationDb": db(amp_input_ratio),
        "LdoPowerFiftyMilli": (5 - 3.3) * 0.05 * 1e3,
        "LdoPowerHundredMilli": (5 - 3.3) * 0.10 * 1e3,
        "IicRiseNs": 0.8473 * 4.7e3 * 200e-12 * 1e9,
        "IicCapStandardPf": 1e-6 / (0.8473 * 4.7e3) * 1e12,
        "IicCapFastPf": 300e-9 / (0.8473 * 4.7e3) * 1e12,
        "ResponseTwentyDb": db(response(20)),
        "ResponseEightyTwoDb": db(response(82.4)),
    }

    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    check("bias resistor sum and ordering", rb == 1006000 and gain_low < 2 < gain_high)
    check("loaded input half-power frequency", math.isclose(abs(highpass(input_pole, C["C7"], R["R5"], rb)), input_attenuation / math.sqrt(2), rel_tol=1e-12))
    check("loaded output half-power frequency", math.isclose(abs(highpass(output_pole, C["C8"], R["R11"], rl)), output_attenuation / math.sqrt(2), rel_tol=1e-12))
    check("high-frequency passive divider limit", math.isclose(abs(response(1e9)), passband, rel_tol=1e-10))
    check("two high-pass stages reject DC", abs(response(1e-8)) < 1e-14)
    check("low-frequency slope approaches 40 dB per decade", math.isclose(db(response(1e-4)) - db(response(1e-5)), 40, abs_tol=1e-5))
    check("gain-two scaling", math.isclose(response(1000, 2).real / response(1000).real, 2, rel_tol=1e-12))
    # Kirchhoff current residual checks use the impedances rather than pole forms.
    for f in (0.1, 20, 1000, 20000):
        v = highpass(f, C["C7"], R["R5"], rb)
        residual = (1 - v) / (R["R5"] + 1 / (2j * math.pi * f * C["C7"])) - v / rb
        check(f"input KCL at {f:g} Hz", abs(residual) < 1e-15)
    check("analog static branch KCL", math.isclose((5 - va_typ) / R["R2"], 2 * 100e-6 + va_typ / (R["R3"] + R["R4"]), rel_tol=1e-12))
    check("positive analog rail and headroom", 0 < va_scenario < va_typ < 5 and 0 < swing < va_typ / 2)
    check("divider nominal lies within exhaustive corners", min(vbus_corners) < values["VbusNominal"] < max(vbus_corners))
    check("amplifier example reconstructs 2 W", math.isclose((amp_input_rms * amp_gain) ** 2 / 4, 2, rel_tol=1e-12))
    check("all derived values finite", all(math.isfinite(v) for v in values.values()))

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["frequency", "gain_one_db", "gain_two_db", "gain_two_low_db", "gain_two_high_db"])
    for i in range(321):
        f = 10 ** (-1 + i * math.log10(20000 / 0.1) / 320)
        writer.writerow([f"{f:.9g}"] + [f"{db(response(f, g)):.9g}" for g in (1, 2, gain_low, gain_high)])

    assumptions = [
        "Ideal op-amps and quiet AC-ground reference; Rs=0 generator; no pickup/cable, finite GBW, slew, distortion, or noise model.",
        "TSA1701 input modeled as frequency-independent 20 kohm; actual input network and revision are unverified.",
        "Frequency-plot envelope varies only R9/R10 initial tolerances; pole intervals separately vary listed initial component tolerances, with module load fixed.",
        "Capacitor DC bias, temperature drift, aging, leakage, parasitics and source/measurement loading are excluded.",
        "Post-Q1 system rail assumed 5 V; analog DC scenarios use two datasheet-conditioned IQ values plus divider current, neglecting output and bias currents. They are not operating-condition guarantees.",
        "Headroom uses an illustrative 0.1 V rail reserve; it is not an MCP6002 output-swing guarantee or a clipping measurement.",
        "VBUS corner calculation assumes an illustrative 4.75-5.25 V supply interval and 1% divider resistors; no USB compliance claim.",
        "Amplifier calculation assumes the PAM8302A IC's 23.5 dB gain and a 2 W typical/1% THD+N example; commercial module gain and supply must be verified.",
        "LDO dissipation examples exclude regulator ground current; the complete system current and temperature remain unmeasured.",
        "I2C examples assume one 4.7 kohm pull-up and 200 pF total bus capacitance, not a measured module bus.",
    ]
    report = {
        "evidence_type": "analytical prediction; not simulation or measurement",
        "cad_source_commit": SOURCE_COMMIT,
        "source_sha256": SOURCE_HASHES,
        "resistances_ohm": R, "capacitances_farad": C,
        "resistor_initial_fractional_tolerances": TOL_R,
        "capacitor_initial_fractional_tolerances": TOL_C,
        "manufacturer_sources": SOURCES,
        "assumptions_and_limits": assumptions,
        "derived_values_macro_names_encode_units": {"MFX" + key: value for key, value in values.items()},
        "checks_passed": checks,
    }
    tex = "% Generated by analysis.py; analytical predictions only. Do not edit by hand.\n"
    tex += "% Units are encoded in macro names or specified in the application note.\n"
    tex += "".join("\\newcommand{\\MFX" + name + "}{" + f"{value:.7g}" + "}\n" for name, value in values.items())
    files = {"derived-values.tex": tex, "response.csv": output.getvalue(),
             "analysis-results.json": json.dumps(report, indent=2, ensure_ascii=True) + "\n"}
    for name, content in files.items():
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale or missing generated file: {path.name}; run analysis.py")
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"{len(checks)} analytical checks passed; source hashes verified; "
          f"{len(files)} generated files {'verified' if args.check else 'written'}.")


if __name__ == "__main__":
    main()
