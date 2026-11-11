"""Pure functions for the two-electrode, capacity-balanced cell model."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .catalog import Material


@dataclass(frozen=True)
class CellInputs:
    positive: Material
    negative: Material
    positive_mass_g: float
    positive_capacity_mah_g: float
    negative_capacity_mah_g: float
    negative_to_positive_ratio: float
    active_mass_fraction: float
    positive_potential_v: float
    negative_potential_v: float


@dataclass(frozen=True)
class CellResult:
    voltage_v: float
    positive_charge_mah: float
    negative_charge_mah: float
    nominal_capacity_ah: float
    negative_mass_g: float
    total_active_mass_g: float
    estimated_other_mass_g: float
    estimated_cell_mass_g: float
    nominal_energy_wh: float
    two_electrode_specific_energy_wh_kg: float
    estimated_cell_specific_energy_wh_kg: float
    positive_theoretical_utilization_percent: float
    negative_theoretical_utilization_percent: float


def _check_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")


def calculate_cell(config: CellInputs) -> CellResult:
    """Balance active electrode capacities and estimate energy by mass basis.

    Approximations: constant average half-cell potentials, fixed reversible
    specific capacities, positive-capacity-limited operation, no kinetic or
    aging losses. Total-cell mass is inferred from a user-specified fraction.
    """
    if config.positive.role != "positive" or config.negative.role != "negative":
        raise ValueError("Select a positive electrode and a negative electrode.")

    for name, value in (
        ("Positive active mass", config.positive_mass_g),
        ("Positive reversible capacity", config.positive_capacity_mah_g),
        ("Negative reversible capacity", config.negative_capacity_mah_g),
        ("N/P capacity ratio", config.negative_to_positive_ratio),
        ("Active-material mass fraction", config.active_mass_fraction),
    ):
        _check_positive(name, value)

    if config.negative_to_positive_ratio < 1.0:
        raise ValueError("The model requires a negative/positive capacity ratio of at least 1.0.")
    if config.active_mass_fraction > 1.0:
        raise ValueError("Active-material mass fraction cannot exceed 1.0.")
    if config.positive_capacity_mah_g > config.positive.theoretical_capacity_mah_g + 1e-8:
        raise ValueError("Positive reversible capacity exceeds its theoretical limit.")
    if config.negative_capacity_mah_g > config.negative.theoretical_capacity_mah_g + 1e-8:
        raise ValueError("Negative reversible capacity exceeds its theoretical limit.")
    if not math.isfinite(config.positive_potential_v) or not math.isfinite(config.negative_potential_v):
        raise ValueError("Half-cell potentials must be finite.")
    if config.negative_potential_v < 0 or config.positive_potential_v <= config.negative_potential_v:
        raise ValueError("Positive electrode potential must exceed negative electrode potential.")

    positive_charge_mah = config.positive_mass_g * config.positive_capacity_mah_g
    negative_charge_mah = config.negative_to_positive_ratio * positive_charge_mah
    negative_mass_g = negative_charge_mah / config.negative_capacity_mah_g
    total_active_mass_g = config.positive_mass_g + negative_mass_g
    estimated_cell_mass_g = total_active_mass_g / config.active_mass_fraction
    estimated_other_mass_g = estimated_cell_mass_g - total_active_mass_g
    voltage_v = config.positive_potential_v - config.negative_potential_v
    nominal_capacity_ah = positive_charge_mah / 1000.0
    nominal_energy_wh = nominal_capacity_ah * voltage_v

    return CellResult(
        voltage_v=voltage_v,
        positive_charge_mah=positive_charge_mah,
        negative_charge_mah=negative_charge_mah,
        nominal_capacity_ah=nominal_capacity_ah,
        negative_mass_g=negative_mass_g,
        total_active_mass_g=total_active_mass_g,
        estimated_other_mass_g=estimated_other_mass_g,
        estimated_cell_mass_g=estimated_cell_mass_g,
        nominal_energy_wh=nominal_energy_wh,
        two_electrode_specific_energy_wh_kg=nominal_energy_wh / (total_active_mass_g / 1000.0),
        estimated_cell_specific_energy_wh_kg=nominal_energy_wh / (estimated_cell_mass_g / 1000.0),
        positive_theoretical_utilization_percent=(
            100.0 * config.positive_capacity_mah_g / config.positive.theoretical_capacity_mah_g
        ),
        negative_theoretical_utilization_percent=(
            100.0 * config.negative_capacity_mah_g / config.negative.theoretical_capacity_mah_g
        ),
    )


def preset_config(
    positive: Material,
    negative: Material,
    positive_mass_g: float = 10.0,
    negative_to_positive_ratio: float = 1.1,
    active_mass_fraction: float = 0.55,
) -> CellInputs:
    """Build a consistent scenario from the published-in-project defaults."""
    return CellInputs(
        positive=positive,
        negative=negative,
        positive_mass_g=positive_mass_g,
        positive_capacity_mah_g=positive.default_reversible_capacity_mah_g,
        negative_capacity_mah_g=negative.default_reversible_capacity_mah_g,
        negative_to_positive_ratio=negative_to_positive_ratio,
        active_mass_fraction=active_mass_fraction,
        positive_potential_v=positive.potential_v_vs_li,
        negative_potential_v=negative.potential_v_vs_li,
    )


def replace_parameter(config: CellInputs, parameter: str, value: float) -> CellInputs:
    """Create a modified scenario without mutating the original scenario."""
    from dataclasses import replace

    allowed = {
        "negative_to_positive_ratio",
        "active_mass_fraction",
        "positive_capacity_mah_g",
        "positive_potential_v",
    }
    if parameter not in allowed:
        raise ValueError(f"Unsupported sensitivity parameter: {parameter}.")
    return replace(config, **{parameter: value})
