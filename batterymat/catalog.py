"""Transparent electrode material dataset and theoretical capacity calculations."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

FARADAY_CONSTANT_C_PER_MOL = 96485.33212
DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "materials.csv"


@dataclass(frozen=True)
class Material:
    id: str
    name: str
    role: str
    formula: str
    molar_mass_g_mol: float
    electrons_per_formula: float
    default_reversible_capacity_mah_g: float
    potential_v_vs_li: float
    structure: str
    description: str
    source_url: str

    @property
    def theoretical_capacity_mah_g(self) -> float:
        """n F / (3.6 M), using starting-material mass as the denominator."""
        return (
            self.electrons_per_formula
            * FARADAY_CONSTANT_C_PER_MOL
            / (3.6 * self.molar_mass_g_mol)
        )


def _positive_finite(value: float, label: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a finite, positive number.")


def load_materials(path: Path | str = DEFAULT_CATALOG_PATH) -> list[Material]:
    """Load and validate the local CSV; no web requests are required."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError("The materials dataset is empty.")

    materials: list[Material] = []
    seen_ids: set[str] = set()
    for row in rows:
        item = Material(
            id=row["id"].strip(),
            name=row["name"].strip(),
            role=row["role"].strip(),
            formula=row["formula"].strip(),
            molar_mass_g_mol=float(row["molar_mass_g_mol"]),
            electrons_per_formula=float(row["electrons_per_formula"]),
            default_reversible_capacity_mah_g=float(row["default_reversible_capacity_mah_g"]),
            potential_v_vs_li=float(row["potential_v_vs_li"]),
            structure=row["structure"].strip(),
            description=row["description"].strip(),
            source_url=row["source_url"].strip(),
        )
        if not item.id or item.id in seen_ids:
            raise ValueError(f"Missing or duplicate material ID: {item.id!r}")
        if item.role not in {"positive", "negative"}:
            raise ValueError(f"Invalid role for {item.id}.")
        if not all((item.name, item.formula, item.structure, item.source_url)):
            raise ValueError(f"Incomplete metadata for {item.id}.")
        for label, value in (
            ("Molar mass", item.molar_mass_g_mol),
            ("Reaction electrons", item.electrons_per_formula),
            ("Reversible capacity", item.default_reversible_capacity_mah_g),
        ):
            _positive_finite(value, f"{label} ({item.id})")
        if not math.isfinite(item.potential_v_vs_li) or item.potential_v_vs_li < 0:
            raise ValueError(f"Invalid reference potential for {item.id}.")
        if item.default_reversible_capacity_mah_g > item.theoretical_capacity_mah_g + 0.01:
            raise ValueError(f"Default capacity exceeds Faraday-law limit for {item.id}.")
        seen_ids.add(item.id)
        materials.append(item)

    if not any(m.role == "positive" for m in materials):
        raise ValueError("At least one positive material is required.")
    if not any(m.role == "negative" for m in materials):
        raise ValueError("At least one negative material is required.")
    return materials
