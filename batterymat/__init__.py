"""BatteryMat-Lab: electrode material comparison and nominal cell modelling."""

from .catalog import Material, load_materials
from .model import CellInputs, CellResult, calculate_cell, preset_config, replace_parameter

__all__ = [
    "Material",
    "load_materials",
    "CellInputs",
    "CellResult",
    "calculate_cell",
    "preset_config",
    "replace_parameter",
]
