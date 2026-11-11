# Mathematical Methodology and Assumptions

## 1. Aim and scope

BatteryMat-Lab is an early-stage, physics-informed comparison tool for lithium-ion **active electrode materials** and illustrative **capacity-balanced full-cell** configurations. It does not substitute for electrode characterization, experimental discharge testing, or a validated electrochemical cell model.

A deliberately limited model was chosen so the calculations remain transparent and independently reproducible.

## 2. Material capacity: Faraday's law

The maximum stoichiometric specific capacity of an electrode host is:

\[
 c_{\mathrm{th}} = \frac{nF}{3.6M}
\]

where:

- \(c_{\mathrm{th}}\) — theoretical specific capacity, in mAh/g;
- \(n\) — moles of transferred electrons per mole of host formula units;
- \(F = 96\,485.33212\) — Faraday constant, in coulombs per mole of electrons;
- \(M\) — molar mass of the **initial host** in g/mol;
- 3.6 converts coulombs per gram to milliampere-hours per gram because 1 mAh = 3.6 C.

**Example: LFP** — For LiFePO₄, with \(M = 157.757\) g/mol and \(n = 1\): \(c_{\mathrm{th}} \approx 169.9\) mAh/g.

**Example: graphite** — One Li inserts into six carbon atoms, \(\mathrm{C_6 + Li^+ + e^- \leftrightarrow LiC_6}\). With \(M_{\mathrm{C_6}} = 72.066\) g/mol, the theoretical capacity is approximately 372 mAh/g. Including the lithium mass in the denominator would change the reporting basis and is not the conventional graphite figure.

**Example: LTO** — \(\mathrm{Li_4Ti_5O_{12} + 3Li^+ + 3e^- \leftrightarrow Li_7Ti_5O_{12}}\), yielding approximately 175 mAh/g on the mass of initial Li₄Ti₅O₁₂.

A cathode's theoretical one-electron capacity is often substantially greater than the reversible capacity available in a specified practical voltage window. The latter is an independent input. A default reversible capacity greater than the theoretical capacity is rejected by the data loader.

## 3. Reversible electrode capacities and N/P sizing

The selected positive active mass \(m_+\) and the chosen positive reversible specific capacity \(c_+\) establish the positive reversible charge:

\[
Q_+ = m_+ c_+\quad [\mathrm{mAh}]
\]

The N/P ratio is defined as the **reversible capacity of the negative electrode divided by the reversible capacity of the positive electrode**:

\[
\mathrm{N/P}=\frac{Q_-}{Q_+}=\frac{m_-c_-}{m_+c_+}
\]

Hence:

\[
m_- = \frac{(\mathrm{N/P})m_+c_+}{c_-}
\]

where \(m_-\) is the negative active mass and \(c_-\) is its reversible specific capacity. The model uses \(\mathrm{N/P} \geq 1\), which makes the positive electrode the nominal capacity-limiting side. An N/P ratio above one increases negative active mass without increasing the modeled nominal positive-limited capacity. Other design and safety implications cannot be inferred from this ratio alone.

This is **capacity balancing**; it is not the mass ratio \(m_-/m_+\).

## 4. Estimated nominal voltage and energy

The material presets contain approximate average half-cell potentials relative to Li/Li⁺. Their difference is taken as a constant nominal full-cell voltage:

\[
V_{\mathrm{nom}} = U_+ - U_-
\]

For the positive-limited case, nominal ampere-hour capacity and energy are:

\[
C_{\mathrm{cell}} = \frac{Q_+}{1000}\quad [\mathrm{Ah}]
\]

\[
E_{\mathrm{nom}} = C_{\mathrm{cell}}V_{\mathrm{nom}}\quad [\mathrm{Wh}]
\]

A measured energy value requires \(\int V\,dQ\) over an actual discharge curve. The constant-potential calculation above is an approximation and omits voltage losses at nonzero current.

## 5. Explicit energy mass bases

**Two-active-electrode basis**:

\[
m_{\mathrm{active}}=m_+ + m_-
\]

\[
e_{\mathrm{active}}=\frac{1000E_{\mathrm{nom}}}{m_{\mathrm{active}}}\quad [\mathrm{Wh/kg}]
\]

**Assumption-based whole-cell basis**:

\[
f_{\mathrm{active}}=\frac{m_{\mathrm{active}}}{m_{\mathrm{cell,estimated}}}
\]

\[
m_{\mathrm{cell,estimated}}=\frac{m_{\mathrm{active}}}{f_{\mathrm{active}}}
\]

\[
e_{\mathrm{cell,estimated}}=\frac{1000E_{\mathrm{nom}}}{m_{\mathrm{cell,estimated}}}=e_{\mathrm{active}}f_{\mathrm{active}}
\]

The inferred remainder mass \(m_{\mathrm{cell,estimated}}-m_{\mathrm{active}}\) collectively represents inactive electrode ingredients, current collectors, electrolyte, separator, packaging, and other cell components. No separate amounts or measured cell design are provided. Changing \(f_{\mathrm{active}}\) changes the result **by assumption**, rather than by a prediction of actual electrode fabrication.

Whole-cell estimates cannot be compared directly with datasheet or experimental values without matching voltage/current conditions and mass accounting.

## 6. Preset values and their interpretation

| Positive material | Starting host | Electron count | Default reversible (mAh/g) | Approx. positive potential (V vs Li/Li⁺) |
|---|---|---:|---:|---:|
| LFP | LiFePO₄ | 1 | 155 | 3.45 |
| LCO | LiCoO₂ | 1 | 150 | 3.90 |
| LMO | LiMn₂O₄ | 1 | 115 | 4.00 |
| NMC111 | LiNi₁/₃Mn₁/₃Co₁/₃O₂ | 1 | 165 | 3.80 |

| Negative material | Starting host | Electron count | Default reversible (mAh/g) | Approx. negative potential (V vs Li/Li⁺) |
|---|---|---:|---:|---:|
| Graphite | C₆ | 1 | 340 | 0.10 |
| LTO | Li₄Ti₅O₁₂ | 3 | 160 | 1.55 |

These reversible capacities are **chosen reference inputs** representative of plausible operation, not a digitization of one consistent experimental study. Different literature sources use different formulations, voltage windows, and protocols; consequently, numerical chemistry rankings from the preset comparison are *illustrative only*.

Molar masses in `data/materials.csv` are rounded starting-host molar masses. The calculated theoretical capacities may differ fractionally from rounded values in review papers.

## 7. Sensitivity and what is held constant

For one-factor sweeps, one selected value is varied and the other values from the chosen scenario stay fixed. When positive specific capacity or N/P is changed, the negative electrode mass is **recomputed** to enforce the requested N/P capacity balance. Nominal energy depends on positive reversible charge and average voltage, not directly on N/P. Specific energy changes when mass accounting changes.

The two-parameter map varies N/P ratio and active-material mass fraction. It is not an optimization of real electrochemical safety, aging, thermal behavior, or cost.

## 8. Excluded physical effects

This model does not solve ion diffusion equations or predict charge transfer kinetics, cell polarization, SEI formation, loss of cyclable lithium, formation efficiency, voltage hysteresis, rate capability, thermal response, expansion, swelling, mechanical damage, production yield, cycle life, reliability, abuse safety, or battery pack efficiency. It does not provide cell voltage cutoffs, electrode layer thickness, porosity, electrolyte formulation, or pack construction guidance.

## 9. Literature and technical sources

1. **Merck / Sigma-Aldrich:** Electrode Materials for Li-ion Batteries. LFP's ~170 mAh/g theoretical capacity and ~3.45 V potential; foundational electrode-material context. https://www.sigmaaldrich.com/US/en/technical-documents/technical-article/materials-science-and-engineering/batteries-supercapacitors-and-fuel-cells/electrode-materials-for-lithium-ion-batteries
2. **ACS Central Science:** An Outlook on Lithium Ion Battery Technology (2017). Graphite host theoretical 372 mAh/g and ~0.1 V vs Li/Li⁺. https://pubs.acs.org/doi/10.1021/acscentsci.7b00288
3. **Communications Materials:** Navigating the minefield of battery literature (2022). Correct mass basis and comparison across electrode and cell levels. https://www.nature.com/articles/s43246-022-00251-5
4. **RSC Energy & Environmental Science:** Ti-based compounds as anode materials for Li-ion batteries (2012). LTO theoretical 175 mAh/g and 1.55 V potential. https://pubs.rsc.org/en/content/articlehtml/2012/ee/c2ee03410g
5. **Review of LCO:** High-Capacity LiCoO₂ Cathodes Beyond 220 mAh g⁻¹: Review and Prospect (2026). Theoretical ~274 mAh/g and conventional reversible capacity range. https://pmc.ncbi.nlm.nih.gov/articles/PMC13378681/
6. **Crystals (2022):** Spinel LiMn₂O₄ Cathode Materials in Wide Voltage Window: Single-Crystalline versus Polycrystalline. LMO 4 V electrochemistry and a typical practical reversible capacity of about 80–120 mAh/g; the 115 mAh/g preset is an illustrative value. https://www.mdpi.com/2073-4352/12/3/317
7. **Materials Advances (2021):** The role of metal substitutions in the development of Li batteries, part I: cathodes. Tabulates NMC111 theoretical capacity at 278 mAh/g and actual capacity at 145–175 mAh/g; the chosen preset is 165 mAh/g. https://doi.org/10.1039/D1MA00081K
8. **Frontiers in Energy Research:** Differential voltage analysis for battery manufacturing process control (2023). N/P as the negative-to-positive reversible capacity ratio. https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2023.1087269/full
9. **World Electric Vehicle Journal:** Cell Design Considerations and Impact on Energy Density (2023). Electrode loading and capacity ratio design tradeoffs. https://www.mdpi.com/2032-6653/14/10/279

The linked sources provide context for the chosen properties. Material preset values are deliberately adjustable in the app, so no single operating-condition-specific accuracy is implied.
