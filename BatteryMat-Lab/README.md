# BatteryMat-Lab
### Battery Materials Performance Explorer

**BatteryMat-Lab** is an interactive computational engineering application for exploring lithium-ion electrode materials, sizing capacity-balanced electrode pairs, and estimating nominal cell energy on clearly stated mass bases.

Built with **Python, Streamlit, pandas, and Plotly**.

**Developer:** Chibuzor Victor Obih

## What the app does

- **Material explorer:** calculates theoretical specific capacity from Faraday's law and compares it with illustrative reversible-capacity values.
- **Cell calculator:** pairs four positive-electrode materials (LFP, LCO, LMO, NMC111) with two negative-electrode materials (graphite, LTO), with an explicit **Calculate Performance** button.
- **Capacity balancing:** calculates the negative electrode mass required for a specified negative-to-positive *reversible capacity* ratio (N/P).
- **Energy and mass basis:** reports nominal voltage (V), capacity (Ah), energy (Wh), two-active-electrode specific energy (Wh/kg), and an assumption-based whole-cell specific energy (Wh/kg).
- **Chemistry comparison:** compares eight material pairings under consistent fixed assumptions.
- **Sensitivity analysis:** explores positive capacity, positive potential, N/P ratio, active material fraction, and a two-parameter design map.
- **Exports:** downloads the selected scenario, comparison tables, material properties, and sensitivity data as CSV files.

## Quick start

Requirements: Python 3.11 or 3.12 recommended. From a terminal in the project folder:

```bash
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux, then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address shown in your terminal (normally `http://localhost:8501`).

### Operating the calculator

1. In the **sidebar**, select a positive material and a negative material.
2. Set the positive active-material mass, N/P capacity ratio and assumed active-material mass fraction. Expand **Edit electrochemical assumptions** to adjust the preset capacities or potentials.
3. Click **Calculate Performance**. The **Cell Calculator** tab then displays the results, mass-balance graph, equations and CSV download.
4. Edit the values and click **Calculate Performance** again to recalculate. Editing a field alone does **not** replace the last submitted Cell Calculator result.
5. Use **Chemistry Comparison** and **Sensitivity Lab** independently: their graphs update when their own controls change, and they use the latest valid sidebar baseline. Invalid sidebar combinations show an error rather than causing an application-wide crash.

The four performance cards use two rows, so the specific-energy unit **Wh/kg** remains readable at typical window sizes.

## Deploy on Streamlit Community Cloud

1. Create a **public GitHub repository** named `BatteryMat-Lab`.
2. Upload the **contents of this extracted folder** to the repository, retaining the folder structure. In particular, `app.py`, `requirements.txt`, `data/`, and `batterymat/` must remain in their present locations.
3. Visit [Streamlit Community Cloud](https://share.streamlit.io/), sign in using GitHub, and select **Create app**.
4. Select your GitHub repository and branch (`main`). Enter `app.py` as the entrypoint.
5. Choose a Python version supported by your dependencies (Python 3.12 is recommended) and deploy.

> Uploading the ZIP itself to GitHub is **not** the same as uploading the application files. Extract the ZIP first. See [the deployment walkthrough](docs/DEPLOYMENT.md).

## Model in brief

Theoretical electrode-specific capacity uses the mass of the initial electrode host:

\[
c_{\mathrm{th}} = \frac{nF}{3.6M}\qquad [\mathrm{mAh\,g^{-1}}]
\]

The chosen positive active mass \(m_+\) and reversible positive specific capacity \(c_+\) give:

\[
Q_+ = m_+ c_+; \qquad m_- = \frac{(N/P)Q_+}{c_-}
\]

With average electrode potentials \(U_+\) and \(U_-\) relative to Li/Li⁺:

\[
V_{\mathrm{nom}} = U_+ - U_-; \qquad E_{\mathrm{nom}} = \frac{Q_+}{1000}V_{\mathrm{nom}}
\]

Two-active-electrode specific energy divides nominal energy by the sum of both active masses. An *illustrative* whole-cell estimate divides by a whole-cell mass inferred from the entered active-material mass fraction. This is a **mass-accounting scenario, not a commercial battery performance prediction**.

## Dataset and model boundaries

The six materials are stored in [`data/materials.csv`](data/materials.csv). Each record includes the formula, starting-host molar mass, charge-transfer electron count, preset reversible capacity, approximate half-cell potential, and a technical reference.

Reversible capacities and potentials are **editable starting values** and are not universal constants. Their values change with voltage window, rate, temperature, electrode formulation, and testing conditions. The model does not simulate concentration gradients, diffusion, rate-dependent voltage, electrochemical aging, lithium loss, heat, pack electronics, or safety.

The graphite theoretical capacity is based on the **unlithiated C₆ host**, rather than the mass of LiC₆. For LTO, the initial Li₄Ti₅O₁₂ host reacts with three inserted lithium ions. These denominators matter when reporting mAh/g.

See [Methodology](docs/METHODOLOGY.md), [Case Study](docs/CASE_STUDY.md), and [Validation Notes](docs/VALIDATION.md).

## Folder layout

```text
BatteryMat-Lab/
├── app.py                     # Streamlit interface
├── batterymat/
│   ├── __init__.py
│   ├── catalog.py             # Material dataset loader and Faraday-law capacity
│   └── model.py               # Capacity and energy calculations
├── data/
│   └── materials.csv          # Curated editable material presets
├── docs/
│   ├── CASE_STUDY.md
│   ├── DEPLOYMENT.md
│   ├── METHODOLOGY.md
│   └── VALIDATION.md
├── tests/
│   ├── conftest.py
│   └── test_model.py
├── .streamlit/config.toml     # Interface theme
├── .github/workflows/tests.yml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── LICENSE
```

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The test suite checks reference capacities, a hand-calculated LFP/graphite example, mass-balance and energy identities, all eight chemistry combinations, sensitivity trends, unit scaling, and invalid inputs, including equal electrode potentials and non-finite values.

## Sources

The scientific reference links in the dataset and [Methodology](docs/METHODOLOGY.md) provide the basis for the selected chemistry properties and N/P definition. Relevant overview papers include:

- [Electrode Materials for Li-ion Batteries — Merck/Sigma-Aldrich](https://www.sigmaaldrich.com/US/en/technical-documents/technical-article/materials-science-and-engineering/batteries-supercapacitors-and-fuel-cells/electrode-materials-for-lithium-ion-batteries)
- [Navigating the minefield of battery literature — *Communications Materials*](https://www.nature.com/articles/s43246-022-00251-5)
- [Differential voltage analysis for battery manufacturing process control — *Frontiers in Energy Research*](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2023.1087269/full)
- [An Outlook on Lithium Ion Battery Technology — *ACS Central Science*](https://pubs.acs.org/doi/10.1021/acscentsci.7b00288)

## License

MIT License. See [`LICENSE`](LICENSE).
