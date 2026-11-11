"""Interactive electrode material and nominal lithium-ion cell explorer."""

from __future__ import annotations


import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from batterymat import CellInputs, calculate_cell, load_materials, replace_parameter


st.set_page_config(
    page_title="BatteryMat-Lab | Materials Performance Explorer",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.75rem; max-width: 1320px;}
      .hero {
        background: linear-gradient(115deg, #172C43 0%, #0F3C48 55%, #0B5D60 100%);
        border: 1px solid #2B707A; border-radius: 16px;
        padding: 24px 28px; margin-bottom: 16px;
      }
      .hero h1 {margin: 0; color: #F4FAFF; letter-spacing: -0.04em; font-size: 2.15rem;}
      .hero p {margin: 8px 0 0; color: #C5E6E6; font-size: 1.04rem;}
      .eyebrow {text-transform: uppercase; letter-spacing: 0.15em;
        font-size: 0.73rem; color: #8AE1D3; font-weight: 800; margin-bottom: 5px;}
      .minor {font-size: 0.88rem; color: #B5C6D3;}
      div[data-testid="stMetric"] {background: #17283B; padding: 15px 16px;
        border: 1px solid #2A4054; border-radius: 12px;}
      div[data-testid="stMetricLabel"] {color: #BDCDD9;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Computational materials engineering</div>
      <h1>BatteryMat-Lab</h1>
      <p>Battery Materials Performance Explorer · Capacity balancing · Energy estimates · Sensitivity analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def get_catalog():
    return load_materials()


catalog = get_catalog()
positive_materials = [m for m in catalog if m.role == "positive"]
negative_materials = [m for m in catalog if m.role == "negative"]

with st.sidebar:
    st.header("Cell design inputs")
    positive = st.selectbox(
        "Positive electrode (cathode)", positive_materials,
        format_func=lambda m: f"{m.name.split(' (')[0]} ({m.id.upper()})",
    )
    negative = st.selectbox(
        "Negative electrode (anode)", negative_materials,
        format_func=lambda m: m.name,
    )
    st.caption("Potentials are approximate average values relative to Li/Li⁺.")

    # Group numerical inputs so the Cell Calculator runs on explicit submission.
    # Material selectors remain outside the form so the corresponding editable
    # capacity and potential defaults can be refreshed when a material changes.
    with st.form("cell_design_form"):
        positive_mass_g = st.number_input(
            "Positive active-material mass (g)", min_value=0.1,
            max_value=100000.0, value=10.0, step=1.0,
            help="Mass of the selected positive active compound, excluding binders and foil.",
        )
        np_ratio = st.slider(
            "Negative / positive capacity ratio (N/P)", 1.0, 1.4, 1.10, 0.01,
            help="Ratio of the reversible capacities of the negative and positive electrodes, not their masses.",
        )
        active_fraction_percent = st.slider(
            "Total-cell active-material mass fraction (%)", 20, 85, 55, 1,
            help="Assumed combined mass of both active electrodes divided by estimated whole-cell mass.",
        )

        with st.expander("Edit electrochemical assumptions", expanded=False):
            st.caption("Preset values are illustrative; measurements depend on conditions and voltage limits.")
            positive_capacity = st.number_input(
                "Positive reversible capacity (mAh/g)",
                min_value=1.0,
                max_value=float(round(positive.theoretical_capacity_mah_g, 3)),
                value=float(positive.default_reversible_capacity_mah_g),
                step=1.0, key=f"capacity_p_{positive.id}",
            )
            negative_capacity = st.number_input(
                "Negative reversible capacity (mAh/g)",
                min_value=1.0,
                max_value=float(round(negative.theoretical_capacity_mah_g, 3)),
                value=float(negative.default_reversible_capacity_mah_g),
                step=1.0, key=f"capacity_n_{negative.id}",
            )
            positive_potential = st.number_input(
                "Positive average potential (V vs Li/Li⁺)",
                min_value=0.1, max_value=6.0,
                value=float(positive.potential_v_vs_li), step=0.05,
                key=f"potential_p_{positive.id}",
            )
            negative_potential = st.number_input(
                "Negative average potential (V vs Li/Li⁺)",
                min_value=0.0, max_value=4.5,
                value=float(negative.potential_v_vs_li), step=0.05,
                key=f"potential_n_{negative.id}",
            )

        calculate_clicked = st.form_submit_button(
            "Calculate Performance", type="primary", use_container_width=True,
        )

    st.caption("Click Calculate Performance to apply the inputs to the Cell Calculator.")
    st.divider()
    st.caption("Educational, constant-voltage model. No kinetic, thermal, aging or safety predictions.")

candidate_scenario = CellInputs(
    positive=positive,
    negative=negative,
    positive_mass_g=float(positive_mass_g),
    positive_capacity_mah_g=float(positive_capacity),
    negative_capacity_mah_g=float(negative_capacity),
    negative_to_positive_ratio=float(np_ratio),
    active_mass_fraction=float(active_fraction_percent) / 100,
    positive_potential_v=float(positive_potential),
    negative_potential_v=float(negative_potential),
)

# Comparison and sensitivity views continue to respond to their own controls.
# Their baseline tracks the latest valid sidebar values; the Cell Calculator
# displays only the most recently submitted, validated result.
if "analysis_scenario" not in st.session_state:
    st.session_state["analysis_scenario"] = candidate_scenario
try:
    calculate_cell(candidate_scenario)
except ValueError:
    # An invalid unsaved configuration must not crash the other tabs.
    pass
else:
    st.session_state["analysis_scenario"] = candidate_scenario

if calculate_clicked:
    try:
        calculated_result = calculate_cell(candidate_scenario)
    except ValueError as error:
        st.session_state["cell_error"] = str(error)
        st.session_state.pop("cell_result", None)
        st.session_state.pop("cell_scenario", None)
    else:
        st.session_state["cell_result"] = calculated_result
        st.session_state["cell_scenario"] = candidate_scenario
        st.session_state["cell_error"] = None

scenario = st.session_state["analysis_scenario"]
result = st.session_state.get("cell_result")
cell_scenario = st.session_state.get("cell_scenario")
cell_error = st.session_state.get("cell_error")
if cell_error:
    st.sidebar.error(f"Unable to calculate: {cell_error}")
    st.sidebar.caption("Comparison and sensitivity views retain the latest valid baseline.")


def result_export_row(inputs: CellInputs, calculated) -> dict[str, float | str]:
    return {
        "positive_material": inputs.positive.name,
        "negative_material": inputs.negative.name,
        "positive_formula": inputs.positive.formula,
        "negative_formula": inputs.negative.formula,
        "positive_active_mass_g": inputs.positive_mass_g,
        "positive_reversible_capacity_mAh_g": inputs.positive_capacity_mah_g,
        "negative_reversible_capacity_mAh_g": inputs.negative_capacity_mah_g,
        "positive_potential_V_vs_Li": inputs.positive_potential_v,
        "negative_potential_V_vs_Li": inputs.negative_potential_v,
        "NP_capacity_ratio": inputs.negative_to_positive_ratio,
        "active_material_mass_fraction": inputs.active_mass_fraction,
        "nominal_voltage_V": calculated.voltage_v,
        "nominal_capacity_Ah": calculated.nominal_capacity_ah,
        "nominal_energy_Wh": calculated.nominal_energy_wh,
        "negative_active_mass_g": calculated.negative_mass_g,
        "total_active_mass_g": calculated.total_active_mass_g,
        "other_cell_mass_g_assumed": calculated.estimated_other_mass_g,
        "estimated_total_cell_mass_g": calculated.estimated_cell_mass_g,
        "two_electrode_specific_energy_Wh_kg": calculated.two_electrode_specific_energy_wh_kg,
        "assumption_based_cell_specific_energy_Wh_kg": calculated.estimated_cell_specific_energy_wh_kg,
    }


def make_comparison_table():
    records = []
    for cathode in positive_materials:
        for anode in negative_materials:
            config = CellInputs(
                positive=cathode,
                negative=anode,
                positive_mass_g=scenario.positive_mass_g,
                positive_capacity_mah_g=cathode.default_reversible_capacity_mah_g,
                negative_capacity_mah_g=anode.default_reversible_capacity_mah_g,
                negative_to_positive_ratio=scenario.negative_to_positive_ratio,
                active_mass_fraction=scenario.active_mass_fraction,
                positive_potential_v=cathode.potential_v_vs_li,
                negative_potential_v=anode.potential_v_vs_li,
            )
            cell = calculate_cell(config)
            records.append({
                "Chemistry": f"{cathode.id.upper()} / {anode.id.upper()}",
                "Nominal voltage (V)": cell.voltage_v,
                "Nominal energy (Wh)": cell.nominal_energy_wh,
                "Two-electrode energy (Wh/kg)": cell.two_electrode_specific_energy_wh_kg,
                "Estimated cell energy (Wh/kg)": cell.estimated_cell_specific_energy_wh_kg,
                "Negative active mass (g)": cell.negative_mass_g,
            })
    return pd.DataFrame(records).sort_values("Estimated cell energy (Wh/kg)", ascending=False)


def style_plot(fig, height=410):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=16, r=20, t=35, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        hovermode="closest",
    )
    return fig


tab_design, tab_compare, tab_sensitivity, tab_library, tab_methods = st.tabs(
    ["🔋 Cell calculator", "📊 Chemistry comparison", "📈 Sensitivity lab", "🧪 Material library", "📖 Method & sources"]
)

with tab_design:
    if cell_error:
        st.error(f"Please correct the inputs and click Calculate Performance: {cell_error}")
    elif result is None:
        st.info("Choose your electrode materials and parameters in the sidebar, then click **Calculate Performance** to display the results.")
    else:
        st.subheader(f"{cell_scenario.positive.id.upper()} / {cell_scenario.negative.id.upper()} · Nominal cell scenario")
        m1, m2 = st.columns(2)
        m1.metric("Nominal voltage", f"{result.voltage_v:.2f} V")
        m2.metric("Nominal capacity", f"{result.nominal_capacity_ah:.3f} Ah")
        m3, m4 = st.columns(2)
        m3.metric("Nominal energy", f"{result.nominal_energy_wh:.3f} Wh")
        m4.metric("Estimated cell-specific energy*", f"{result.estimated_cell_specific_energy_wh_kg:.1f} Wh/kg")

        st.info(
            "*The full-cell specific energy is an illustrative mass-based estimate, "
            "not a performance prediction for a manufactured battery. "
            "It depends directly on the active-material mass fraction entered in the sidebar."
        )

        left, right = st.columns([1.15, 1], gap="large")
        with left:
            st.markdown("#### Electrode and cell mass balance")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Positive active material", x=["Estimated mass"],
                y=[cell_scenario.positive_mass_g], marker_color="#13B3A1",
                hovertemplate="%{y:.3f} g<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                name="Negative active material", x=["Estimated mass"],
                y=[result.negative_mass_g], marker_color="#60A5FA",
                hovertemplate="%{y:.3f} g<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                name="Other cell components (assumed)", x=["Estimated mass"],
                y=[result.estimated_other_mass_g], marker_color="#8A94A8",
                hovertemplate="%{y:.3f} g<extra></extra>",
            ))
            fig.update_layout(barmode="stack", yaxis_title="Mass (g)", legend=dict(orientation="h", y=-0.22))
            st.plotly_chart(style_plot(fig, 350), use_container_width=True)
        with right:
            st.markdown("#### Calculated results")
            details = pd.DataFrame([
                ("Positive theoretical capacity", f"{cell_scenario.positive.theoretical_capacity_mah_g:.1f} mAh/g"),
                ("Negative theoretical capacity", f"{cell_scenario.negative.theoretical_capacity_mah_g:.1f} mAh/g"),
                ("Positive capacity utilization", f"{result.positive_theoretical_utilization_percent:.1f}%"),
                ("Negative capacity utilization", f"{result.negative_theoretical_utilization_percent:.1f}%"),
                ("Positive available charge", f"{result.positive_charge_mah:.1f} mAh"),
                ("Negative available charge", f"{result.negative_charge_mah:.1f} mAh"),
                ("Negative active mass", f"{result.negative_mass_g:.3f} g"),
                ("Total active mass", f"{result.total_active_mass_g:.3f} g"),
                ("Estimated whole-cell mass", f"{result.estimated_cell_mass_g:.3f} g"),
                ("Two-electrode specific energy", f"{result.two_electrode_specific_energy_wh_kg:.1f} Wh/kg"),
            ], columns=["Quantity", "Value"])
            st.dataframe(details, hide_index=True, use_container_width=True)

        with st.expander("Show worked equations for this scenario"):
            st.latex(r"C_{\mathrm{th}}=\frac{nF}{3.6M}\quad[\mathrm{mAh\,g^{-1}}]")
            st.latex(r"Q_{+}=m_{+}\,c_{+};\qquad m_{-}=\frac{(N/P)\,Q_{+}}{c_{-}}")
            st.latex(r"V_{\mathrm{cell}}=U_{+}-U_{-};\qquad E_{\mathrm{nom}}=\frac{Q_{+}}{1000}V_{\mathrm{cell}}")
            st.latex(r"e_{\mathrm{active}}=\frac{1000E_{\mathrm{nom}}}{m_{+}+m_{-}}")
            st.latex(r"m_{\mathrm{cell,est}}=\frac{m_{+}+m_{-}}{f_{\mathrm{active}}};\quad e_{\mathrm{cell,est}}=f_{\mathrm{active}}e_{\mathrm{active}}")
            st.write(
                f"Using the selected scenario: Q₊ = {cell_scenario.positive_mass_g:.3f} × "
                f"{cell_scenario.positive_capacity_mah_g:.2f} = {result.positive_charge_mah:.2f} mAh; "
                f"m₋ = {result.negative_mass_g:.3f} g; V = {result.voltage_v:.2f} V."
            )

        export = pd.DataFrame([result_export_row(cell_scenario, result)])
        st.download_button(
            "Download scenario calculations (CSV)",
            data=export.to_csv(index=False).encode("utf-8"),
            file_name="batterymat_scenario.csv", mime="text/csv",
        )

with tab_compare:
    st.subheader("Compare eight illustrative material pairings")
    st.caption(
        "All pairings use the same positive-active-material mass, N/P ratio and "
        "active-mass fraction; each material uses its own default reversible capacity "
        "and reference potential. Custom capacity edits in the sidebar do not change this preset comparison."
    )
    comparison = make_comparison_table()
    fig = go.Figure(go.Bar(
        x=comparison["Estimated cell energy (Wh/kg)"],
        y=comparison["Chemistry"],
        orientation="h", marker_color="#13B3A1",
        text=[f"{x:.0f}" for x in comparison["Estimated cell energy (Wh/kg)"]],
        textposition="outside",
        hovertemplate="%{y}<br>%{x:.1f} Wh/kg<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Assumption-based whole-cell specific energy (Wh/kg)",
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(style_plot(fig, 485), use_container_width=True)
    st.dataframe(comparison.round(2), hide_index=True, use_container_width=True)
    st.download_button(
        "Download chemistry comparison (CSV)",
        data=comparison.to_csv(index=False).encode("utf-8"),
        file_name="batterymat_comparison.csv", mime="text/csv",
    )
    st.caption("A higher estimate does not establish better safety, cycle life, power capability, cost, or manufacturability.")

with tab_sensitivity:
    st.subheader("One-factor sensitivity analysis")
    st.caption(
        "For each point, the negative active mass is rebalanced to the chosen N/P ratio. "
        "All other assumptions are held fixed."
    )
    parameter_options = {
        "N/P capacity ratio": "negative_to_positive_ratio",
        "Active-material mass fraction": "active_mass_fraction",
        "Positive reversible capacity": "positive_capacity_mah_g",
        "Positive average potential": "positive_potential_v",
    }
    selected_label = st.selectbox("Vary this parameter", list(parameter_options))
    parameter = parameter_options[selected_label]
    baseline = float(getattr(scenario, parameter))
    if parameter == "negative_to_positive_ratio":
        values = [1.0 + 0.02 * i for i in range(21)]
        xlabel = "N/P capacity ratio"
    elif parameter == "active_mass_fraction":
        values = [0.25 + 0.025 * i for i in range(25)]
        xlabel = "Active-material mass fraction"
    elif parameter == "positive_capacity_mah_g":
        lo = max(1.0, 0.65 * baseline)
        hi = min(scenario.positive.theoretical_capacity_mah_g, 1.25 * baseline)
        values = [lo + (hi - lo) * i / 24 for i in range(25)]
        xlabel = "Positive reversible capacity (mAh/g)"
    else:
        lo = max(scenario.negative_potential_v + 0.05, baseline - 0.3)
        hi = min(6.0, baseline + 0.3)
        values = [lo + (hi - lo) * i / 24 for i in range(25)]
        xlabel = "Positive average potential (V vs Li/Li⁺)"

    sensitivity = []
    for value in values:
        trial = replace_parameter(scenario, parameter, value)
        r = calculate_cell(trial)
        sensitivity.append({
            "parameter": selected_label,
            "input_value": value,
            "estimated_cell_specific_energy_Wh_kg": r.estimated_cell_specific_energy_wh_kg,
            "two_electrode_specific_energy_Wh_kg": r.two_electrode_specific_energy_wh_kg,
            "nominal_energy_Wh": r.nominal_energy_wh,
        })
    sensitivity_df = pd.DataFrame(sensitivity)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sensitivity_df["input_value"],
        y=sensitivity_df["estimated_cell_specific_energy_Wh_kg"],
        mode="lines+markers", line=dict(color="#13B3A1", width=3),
        marker=dict(size=6), name="Cell mass basis",
        hovertemplate="Input: %{x:.3f}<br>Cell energy: %{y:.1f} Wh/kg<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=sensitivity_df["input_value"],
        y=sensitivity_df["two_electrode_specific_energy_Wh_kg"],
        mode="lines", line=dict(color="#60A5FA", width=2, dash="dot"),
        name="Both active electrodes",
    ))
    fig.add_vline(x=baseline, line_dash="dash", line_color="#FFA85D")
    fig.update_layout(xaxis_title=xlabel, yaxis_title="Specific energy (Wh/kg)")
    st.plotly_chart(style_plot(fig), use_container_width=True)
    st.caption(f"Dashed vertical line: current baseline ({baseline:.3f}).")
    st.download_button(
        "Download sensitivity data (CSV)",
        data=sensitivity_df.to_csv(index=False).encode("utf-8"),
        file_name="batterymat_sensitivity.csv", mime="text/csv",
    )

    st.divider()
    st.subheader("Two-parameter design map")
    st.caption("Illustrates how N/P and the assumed non-active mass burden interact; it is not a design validation map.")
    np_grid = [1.0 + i * 0.025 for i in range(17)]
    fraction_grid = [0.25 + i * 0.025 for i in range(25)]
    z = []
    for fraction in fraction_grid:
        row = []
        for npr in np_grid:
            trial = replace_parameter(
                replace_parameter(scenario, "negative_to_positive_ratio", npr),
                "active_mass_fraction", fraction,
            )
            row.append(calculate_cell(trial).estimated_cell_specific_energy_wh_kg)
        z.append(row)
    heatmap = go.Figure(go.Heatmap(
        x=np_grid, y=[100 * x for x in fraction_grid], z=z,
        colorscale="Tealgrn", colorbar=dict(title="Wh/kg"),
        hovertemplate="N/P: %{x:.3f}<br>Active share: %{y:.1f}%<br>Estimate: %{z:.1f} Wh/kg<extra></extra>",
    ))
    heatmap.update_layout(xaxis_title="N/P capacity ratio", yaxis_title="Active-material mass fraction (%)")
    st.plotly_chart(style_plot(heatmap), use_container_width=True)

with tab_library:
    st.subheader("Electrode material dataset")
    st.caption(
        "Theoretical capacities are calculated from molar mass and electron transfer. "
        "Reversible capacities and potentials are editable reference scenarios, not universal constants."
    )
    library_rows = []
    for material in catalog:
        library_rows.append({
            "Material": material.name,
            "Role": material.role,
            "Formula / capacity basis": material.formula,
            "Structure": material.structure,
            "Molar mass (g/mol)": material.molar_mass_g_mol,
            "Electrons (n)": material.electrons_per_formula,
            "Theoretical (mAh/g)": material.theoretical_capacity_mah_g,
            "Default reversible (mAh/g)": material.default_reversible_capacity_mah_g,
            "Potential (V vs Li/Li⁺)": material.potential_v_vs_li,
        })
    library_df = pd.DataFrame(library_rows)
    st.dataframe(library_df.round(2), hide_index=True, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Theoretical", x=[m.id.upper() for m in catalog],
        y=[m.theoretical_capacity_mah_g for m in catalog], marker_color="#60A5FA",
    ))
    fig.add_trace(go.Bar(
        name="Default reversible", x=[m.id.upper() for m in catalog],
        y=[m.default_reversible_capacity_mah_g for m in catalog], marker_color="#13B3A1",
    ))
    fig.update_layout(barmode="group", yaxis_title="Specific capacity (mAh/g)")
    st.plotly_chart(style_plot(fig), use_container_width=True)

    st.warning(
        "Theoretical cathode capacity is not normally fully accessible within a practical voltage window. "
        "For graphite, the denominator is the mass of the unlithiated C₆ host; "
        "for LTO, it is the mass of the initial Li₄Ti₅O₁₂ host."
    )
    st.download_button(
        "Download material properties (CSV)",
        data=library_df.to_csv(index=False).encode("utf-8"),
        file_name="batterymat_materials.csv", mime="text/csv",
    )

with tab_methods:
    st.subheader("Model, assumptions and interpretation")
    st.markdown(
        """
        **1. Theoretical specific capacity.** Faraday's law gives the charge transferred per
        unit mass of the *starting electrode host*: n electrons per formula unit, molar mass M
        in g/mol, and the Faraday constant F = 96,485.33212 C/mol.
        """
    )
    st.latex(r"c_{\mathrm{th}}=\frac{nF}{3.6M}\;[\mathrm{mAh/g}]")
    st.markdown(
        """
        **2. Practical reversible capacity.** The default capacities are illustrative operating
        inputs below the theoretical limits. They vary with formulation, current, temperature,
        state-of-charge limits, and cycle history.

        **3. Electrode capacity balance.** The reversible negative-to-positive ratio (N/P)
        is based on *capacities*, not on electrode masses. The negative active mass is sized
        to meet that ratio. This simple model assumes positive-electrode-limited capacity.

        **4. Nominal voltage and energy.** Average half-cell potentials relative to Li/Li⁺
        are subtracted to approximate full-cell voltage. This is a constant-voltage estimate,
        not an integrated experimental discharge curve.

        **5. Mass basis.** Two-electrode specific energy divides Wh by the combined active
        material mass. Estimated full-cell specific energy divides the same energy by an
        assumed whole-cell mass. The inferred whole-cell mass includes a lumped remainder
        for electrolyte, foils, binders, separator, casing and other inactive materials.
        That assumed fraction is *not calibrated* to a specific battery construction.
        """
    )
    st.warning(
        "Not included: first-cycle irreversible losses, lithium inventory constraints, "
        "polarization or current dependence, voltage curves, electrode density/porosity, "
        "mechanical degradation, thermal effects, safety, cycle life, manufacturing, or costs. "
        "Do not use these results to certify, purchase or physically design a battery."
    )
    st.markdown("#### Source references")
    for material in catalog:
        st.markdown(f"- **{material.id.upper()}** — [{material.name}]({material.source_url})")
    st.markdown(
        """
        - [Graphite capacity mass basis and full-cell energy reporting — *Communications Materials*](https://www.nature.com/articles/s43246-022-00251-5)
        - [N/P ratio as the ratio of reversible electrode capacities — *Frontiers in Energy Research*](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2023.1087269/full)
        - [Practical cell mass and electrochemical design considerations — *World Electric Vehicle Journal*](https://www.mdpi.com/2032-6653/14/10/279)
        """
    )
    st.caption("Dataset rationale and fully worked baseline example are provided in docs/METHODOLOGY.md.")

st.divider()
st.caption("BatteryMat-Lab · An educational computational engineering project by Chibuzor Victor Obih · v1.1")
