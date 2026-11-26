# Application note

**MFX-AN-001 · Revision 0.1 · Pre-fabrication**

[Read the PDF](application-note.pdf) or edit the [LaTeX source](application-note.tex). The note explains the delivered 5 V hardware, calculations, module interfaces, programming, and planned validation. It contains no fabricated measurements or claim of manufacturing approval.

## Reproduce the analysis

From this folder, using the full repository and Python 3.10 or later:

```powershell
python analysis.py --check
```

The script verifies source hashes and its calculated outputs without writing. To regenerate deliberately reviewed data, run `python analysis.py`. It uses only the Python standard library and produces `derived-values.tex`, `response.csv`, and `analysis-results.json`. The JSON records source hashes, assumptions, manufacturer references, and analytical checks. A source mismatch requires reviewing the model rather than bypassing the check.

## Build the PDF

```powershell
tectonic application-note.tex
```

The tested engine is Tectonic 0.17.0. Alternatively, upload this folder's contents to Overleaf, set `application-note.tex` as the main document, and select **XeLaTeX**. The generated values and CSV are already included; Overleaf does not need to run Python. The diagrams use TikZ/Circuitikz and PGFPlots; the actual Gerber-derived PCB view is included as a vector PDF. Re-run XeLaTeX until references resolve.

The note's circuit source is commit `ad3ab21`. The [hardware guide](../../hardware/README.md) records the BOM, library and manufacturing-output limitations. The professor's source examples and downloaded datasheets remain outside this publication package.
