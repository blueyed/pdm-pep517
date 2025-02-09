"""
PEP-517 compliant buildsystem API
"""
from pathlib import Path
from typing import Any, List, Mapping, Optional

from pdm.pep517.editable import EditableBuilder
from pdm.pep517.metadata import Metadata
from pdm.pep517.sdist import SdistBuilder
from pdm.pep517.wheel import WheelBuilder


def get_requires_for_build_wheel(
    config_settings: Optional[Mapping[str, Any]] = None
) -> List[str]:
    """
    Returns an additional list of requirements for building, as PEP508 strings,
    above and beyond those specified in the pyproject.toml file.

    When C-extension build is needed, setuptools should be required, otherwise
    just return an empty list.
    """
    meta = Metadata(Path("pyproject.toml"))
    if meta.build:
        return ["setuptools>=40.8.0"]
    else:
        return []


def get_requires_for_build_sdist(
    config_settings: Optional[Mapping[str, Any]] = None
) -> List[str]:
    """There isn't any requirement for building a sdist at this point."""
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: Optional[Mapping[str, Any]] = None
) -> str:
    builder = WheelBuilder(Path.cwd(), config_settings)

    dist_info = Path(metadata_directory, builder.dist_info_name)
    dist_info.mkdir(exist_ok=True)
    with builder:
        if builder.meta.entry_points:
            with (dist_info / "entry_points.txt").open("w", encoding="utf-8") as f:
                builder._write_entry_points(f)

        with (dist_info / "WHEEL").open("w", encoding="utf-8") as f:
            builder._write_wheel_file(f)

        with (dist_info / "METADATA").open("w", encoding="utf-8") as f:
            builder._write_metadata_file(f)

    return dist_info.name


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Builds a wheel, places it in wheel_directory"""
    with WheelBuilder(Path.cwd(), config_settings) as builder:
        return Path(builder.build(wheel_directory)).name


def build_sdist(
    sdist_directory: str, config_settings: Optional[Mapping[str, Any]] = None
) -> str:
    """Builds an sdist, places it in sdist_directory"""
    with SdistBuilder(Path.cwd(), config_settings) as builder:
        return Path(builder.build(sdist_directory)).name


get_requires_for_build_editable = get_requires_for_build_wheel
prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel


def build_editable(
    wheel_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    with EditableBuilder(Path.cwd(), config_settings) as builder:
        return Path(builder.build(wheel_directory)).name
