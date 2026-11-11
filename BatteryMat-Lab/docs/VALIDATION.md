# Verification and Known Limitations

## Numerical verification

The automated tests in `tests/test_model.py` cover:

1. Dataset structure: four positive materials and two negative materials.
2. Theoretical Faraday-law capacities for LFP, LCO, LMO, NMC111, graphite and LTO.
3. Dataset preset capacities below the corresponding theoretical limits.
4. Hand-calculated LFP/graphite charge, N/P balance, voltage, energy, electrode mass and two separate specific-energy mass bases.
5. N/P mass balance and effect of increasing negative electrode excess.
6. Effect of assumed active-material mass fraction.
7. Scaling active material mass without changing specific energy.
8. Comparison of graphite and LTO under the same LFP-positive conditions.
9. Evaluation of all eight permitted chemistry pairings.
10. Rejection of invalid masses, ratios, capacities, potentials, and electrode roles.
11. Independent sensitivity scenario updates and missing dataset handling.
12. Edge cases: coincident or negative electrode potentials, non-finite inputs and theoretical-capacity limits.
13. Zero inactive mass when the hypothetical active-material fraction equals 100%.

The test suite includes additional edge-case tests for equal or negative electrode potentials, non-finite values, theoretical-capacity limits and the fully active-mass case. Run them with:

```bash
python -m pytest -q
```

## Reference case

Default inputs: LFP/graphite, positive mass = 10 g, positive reversible capacity = 155 mAh/g, negative reversible capacity = 340 mAh/g, N/P = 1.10, positive/negative potentials = 3.45/0.10 V vs Li/Li⁺, assumed active fraction = 0.55.

| Result | Expected |
|---|---:|
| Positive reversible charge | 1550 mAh |
| Negative reversible charge | 1705 mAh |
| Negative active mass | 5.0147 g |
| Nominal cell voltage | 3.35 V |
| Nominal ampere-hour capacity | 1.550 Ah |
| Nominal energy | 5.1925 Wh |
| Combined active mass | 15.0147 g |
| Inferred total cell mass | 27.2995 g |
| Two-active-electrode specific energy | 345.83 Wh/kg |
| Assumption-based whole-cell specific energy | 190.21 Wh/kg |

## Uncertainty and exclusions

- Literature values are drawn from different studies and may use different test conditions. Default reversible capacities are indicative choices, not a harmonized experimental dataset.
- Average half-cell potentials and reversible capacities are treated as constants over the discharged capacity; no integrated voltage curve is used.
- The model assumes positive-electrode-limited nominal discharge and a fixed N/P capacity balance.
- The whole-cell mass estimate is controlled by an assumed active fraction, not by validated electrode layers and cell components.
- The tool does not model kinetics, power, resistance, temperature, degradation, life, mechanical effects, safety, battery management, or cost.
- Numerical test coverage demonstrates consistency of the programmed equations, not empirical predictive accuracy.

The model should be used as an **educational and preliminary comparative analysis**, not as a basis for battery fabrication or certification.

## Streamlit interface checks

- The Cell Calculator is initially in a ready-to-calculate state. Changing material options or numerical inputs alone does not overwrite its last completed calculation.
- The sidebar **Calculate Performance** button validates and saves a result for display and CSV export.
- Four results use a two-by-two layout to avoid clipping the full-cell specific-energy unit (Wh/kg).
- Invalid potential combinations are reported to the user. The comparison and sensitivity panels retain a valid scenario instead of halting the entire application.

The numeric tests alone do not prove that all visual elements render correctly on every device. Verify the deployed app in a browser before sharing it.
