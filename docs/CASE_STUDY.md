# Case Study: The Effect of Anode Choice on Nominal Energy

## Question

How do a graphite anode and an LTO anode change the modeled voltage, required negative active mass, and specific energy of a LiFePO₄-based cell when the positive active mass and N/P capacity balance are held fixed?

## Shared scenario

- Positive material: LiFePO₄ (LFP)
- Positive active mass: 10.00 g
- Positive reversible capacity: 155 mAh/g
- Positive average potential: 3.45 V vs Li/Li⁺
- N/P reversible capacity ratio: 1.10
- Assumed combined active-material fraction of full-cell mass: 55%

The positive electrode contains \(10 \times 155 = 1550\) mAh = **1.550 Ah** of modeled reversible charge.

## Option A — LFP / graphite

- Graphite reversible specific capacity: 340 mAh/g
- Graphite reference potential: 0.10 V vs Li/Li⁺
- Negative active mass: \(1.1 \times 1550 / 340 = 5.015\) g
- Nominal cell voltage: \(3.45 - 0.10 = 3.35\) V
- Nominal energy: \(1.55 \times 3.35 = 5.1925\) Wh
- Two-active-electrode specific energy: **345.8 Wh/kg**
- Assumption-based full-cell specific energy: **190.2 Wh/kg**

## Option B — LFP / LTO

- LTO reversible specific capacity: 160 mAh/g
- LTO reference potential: 1.55 V vs Li/Li⁺
- Negative active mass: \(1.1 \times 1550 / 160 = 10.656\) g
- Nominal cell voltage: \(3.45 - 1.55 = 1.90\) V
- Nominal energy: \(1.55 \times 1.90 = 2.9450\) Wh
- Two-active-electrode specific energy: **142.6 Wh/kg**
- Assumption-based full-cell specific energy: **78.4 Wh/kg**

## Interpretation

Under the defined inputs, the LTO scenario needs more negative active mass to achieve N/P = 1.10, and its larger potential relative to Li/Li⁺ reduces nominal full-cell voltage. Both effects reduce modeled Wh/kg relative to graphite. This comparison illustrates why **material-specific capacity and operating potential must be considered together**, and why comparing anodes purely by theoretical mAh/g is incomplete.

This is not an assessment of which battery is better overall: LTO can offer advantages that the present model does not quantify, such as structural stability, tolerance of rapid charge, and cycle-life characteristics. Those require independent evidence and models.

## Reproducing the numbers

Open the **Cell calculator** tab. Set LFP as positive electrode, choose graphite and then LTO as the negative electrode, and retain the default mass, N/P and active-fraction settings. Results are calculated with the pure Python `calculate_cell` function. The numerical identities are checked in `tests/test_model.py`.
