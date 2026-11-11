"""Numerical and physical consistency tests for BatteryMat-Lab."""

from dataclasses import replace
from pathlib import Path

import pytest

from batterymat import calculate_cell, load_materials, preset_config, replace_parameter


@pytest.fixture(scope="module")
def materials():
    return {m.id: m for m in load_materials()}


@pytest.fixture(scope="module")
def example(materials):
    return preset_config(materials["lfp"], materials["graphite"])


def test_expected_catalog_contents(materials):
    assert len(materials) == 6
    assert {m.id for m in materials.values() if m.role == "positive"} == {
        "lfp", "lco", "lmo", "nmc111"
    }
    assert {m.id for m in materials.values() if m.role == "negative"} == {
        "graphite", "lto"
    }


@pytest.mark.parametrize("id_,target,tolerance", [
    ("lfp", 170.0, 0.5),
    ("lco", 274.0, 0.5),
    ("lmo", 148.2, 0.5),
    ("nmc111", 277.9, 0.5),
    ("graphite", 372.0, 0.5),
    ("lto", 175.1, 0.5),
])
def test_faraday_theoretical_capacities(materials, id_, target, tolerance):
    assert materials[id_].theoretical_capacity_mah_g == pytest.approx(target, abs=tolerance)


def test_all_catalog_default_values_respect_theoretical_limit(materials):
    for material in materials.values():
        assert 0 < material.default_reversible_capacity_mah_g < material.theoretical_capacity_mah_g


def test_hand_worked_lfp_graphite(example):
    result = calculate_cell(example)
    assert result.voltage_v == pytest.approx(3.35)
    assert result.positive_charge_mah == pytest.approx(1550.0)
    assert result.negative_charge_mah == pytest.approx(1705.0)
    assert result.negative_mass_g == pytest.approx(1705.0 / 340.0)
    assert result.nominal_capacity_ah == pytest.approx(1.55)
    assert result.nominal_energy_wh == pytest.approx(5.1925)
    active_mass = 10.0 + 1705 / 340
    assert result.total_active_mass_g == pytest.approx(active_mass)
    assert result.estimated_cell_mass_g == pytest.approx(active_mass / 0.55)
    assert result.two_electrode_specific_energy_wh_kg == pytest.approx(5.1925 * 1000 / active_mass)
    assert result.estimated_cell_specific_energy_wh_kg == pytest.approx(5.1925 * 1000 / active_mass * 0.55)


def test_capacity_ratio_matches_model_definition(example):
    result = calculate_cell(example)
    assert result.negative_charge_mah / result.positive_charge_mah == pytest.approx(
        example.negative_to_positive_ratio
    )


def test_larger_np_decreases_specific_energy(example):
    smaller = calculate_cell(example)
    larger = calculate_cell(replace(example, negative_to_positive_ratio=1.25))
    assert larger.negative_mass_g > smaller.negative_mass_g
    assert larger.nominal_energy_wh == pytest.approx(smaller.nominal_energy_wh)
    assert larger.estimated_cell_specific_energy_wh_kg < smaller.estimated_cell_specific_energy_wh_kg


def test_fraction_scales_cell_specific_energy_but_not_active_specific_energy(example):
    base = calculate_cell(example)
    changed = calculate_cell(replace(example, active_mass_fraction=0.80))
    assert changed.two_electrode_specific_energy_wh_kg == pytest.approx(
        base.two_electrode_specific_energy_wh_kg
    )
    assert changed.estimated_cell_specific_energy_wh_kg == pytest.approx(
        base.two_electrode_specific_energy_wh_kg * 0.8
    )


def test_mass_scaling_preserves_specific_energy(example):
    base = calculate_cell(example)
    doubled = calculate_cell(replace(example, positive_mass_g=20.0))
    assert doubled.nominal_energy_wh == pytest.approx(base.nominal_energy_wh * 2)
    assert doubled.estimated_cell_mass_g == pytest.approx(base.estimated_cell_mass_g * 2)
    assert doubled.estimated_cell_specific_energy_wh_kg == pytest.approx(
        base.estimated_cell_specific_energy_wh_kg
    )


def test_lto_has_lower_voltage_than_graphite_with_same_cathode(example, materials):
    graphite = calculate_cell(example)
    lto = calculate_cell(preset_config(materials["lfp"], materials["lto"]))
    assert lto.voltage_v == pytest.approx(1.90)
    assert lto.voltage_v < graphite.voltage_v
    assert lto.estimated_cell_specific_energy_wh_kg < graphite.estimated_cell_specific_energy_wh_kg


def test_every_catalog_pair_can_be_evaluated(materials):
    positive = [m for m in materials.values() if m.role == "positive"]
    negative = [m for m in materials.values() if m.role == "negative"]
    for cathode in positive:
        for anode in negative:
            result = calculate_cell(preset_config(cathode, anode))
            assert result.nominal_energy_wh > 0
            assert result.estimated_cell_specific_energy_wh_kg > 0


@pytest.mark.parametrize("field,value", [
    ("positive_mass_g", 0),
    ("positive_mass_g", float("nan")),
    ("negative_capacity_mah_g", -3),
    ("negative_to_positive_ratio", 0.95),
    ("active_mass_fraction", 0),
    ("active_mass_fraction", 1.1),
    ("positive_potential_v", 0.05),
    ("negative_potential_v", float("inf")),
    ("positive_capacity_mah_g", 1000.0),
    ("negative_capacity_mah_g", 999.0),
])
def test_invalid_inputs_raise_value_error(example, field, value):
    with pytest.raises(ValueError):
        calculate_cell(replace(example, **{field: value}))


def test_swapped_electrodes_are_rejected(example):
    with pytest.raises(ValueError):
        calculate_cell(replace(example, positive=example.negative, negative=example.positive))


def test_sensitivity_replacement_is_immutable(example):
    altered = replace_parameter(example, "negative_to_positive_ratio", 1.2)
    assert example.negative_to_positive_ratio == 1.1
    assert altered.negative_to_positive_ratio == 1.2
    with pytest.raises(ValueError):
        replace_parameter(example, "unknown", 2)


def test_missing_catalog_raises_error(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_materials(tmp_path / "not_found.csv")


def test_equal_electrode_potentials_are_rejected(example):
    invalid = replace(example, positive_potential_v=example.negative_potential_v)
    with pytest.raises(ValueError, match="must exceed"):
        calculate_cell(invalid)


def test_negative_electrode_potential_cannot_be_below_zero(example):
    with pytest.raises(ValueError, match="must exceed"):
        calculate_cell(replace(example, negative_potential_v=-0.1))


def test_active_fraction_one_has_zero_inactive_mass(example):
    result = calculate_cell(replace(example, active_mass_fraction=1.0))
    assert result.estimated_other_mass_g == pytest.approx(0.0)
    assert result.estimated_cell_specific_energy_wh_kg == pytest.approx(
        result.two_electrode_specific_energy_wh_kg
    )


def test_nan_and_infinite_positive_electrode_values_rejected(example):
    for field, value in [
        ("positive_capacity_mah_g", float("nan")),
        ("positive_capacity_mah_g", float("inf")),
        ("positive_mass_g", float("inf")),
        ("positive_potential_v", float("nan")),
    ]:
        with pytest.raises(ValueError):
            calculate_cell(replace(example, **{field: value}))


def test_positive_theoretical_capacity_limit_is_enforced(example):
    slightly_above_limit = example.positive.theoretical_capacity_mah_g + 0.001
    with pytest.raises(ValueError, match="theoretical limit"):
        calculate_cell(replace(example, positive_capacity_mah_g=slightly_above_limit))


def test_negative_theoretical_capacity_limit_is_enforced(example):
    slightly_above_limit = example.negative.theoretical_capacity_mah_g + 0.001
    with pytest.raises(ValueError, match="theoretical limit"):
        calculate_cell(replace(example, negative_capacity_mah_g=slightly_above_limit))
