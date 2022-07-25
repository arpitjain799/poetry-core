from __future__ import annotations

import uuid

from pathlib import Path

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile

from poetry.core.pyproject.toml import PyProjectTOML


def test_pyproject_toml_simple(
    pyproject_toml: Path, build_system_section: str, poetry_section: str
) -> None:
    data = TOMLFile(pyproject_toml.as_posix()).read()
    assert PyProjectTOML(pyproject_toml).data == data


def test_pyproject_toml_no_build_system_defaults() -> None:
    pyproject_toml = (
        Path(__file__).parent.parent
        / "fixtures"
        / "project_with_build_system_requires"
        / "pyproject.toml"
    )

    build_system = PyProjectTOML(pyproject_toml).build_system
    assert build_system.requires == ["poetry-core", "Cython~=0.29.6"]

    assert len(build_system.dependencies) == 2
    assert build_system.dependencies[0].to_pep_508() == "poetry-core"
    assert build_system.dependencies[1].to_pep_508() == "Cython (>=0.29.6,<0.30.0)"


def test_pyproject_toml_build_requires_as_dependencies(pyproject_toml: Path) -> None:
    build_system = PyProjectTOML(pyproject_toml).build_system
    assert build_system.requires == ["setuptools", "wheel"]
    assert build_system.build_backend == "setuptools.build_meta:__legacy__"


def test_pyproject_toml_non_existent(pyproject_toml: Path) -> None:
    pyproject_toml.unlink()
    pyproject = PyProjectTOML(pyproject_toml)
    build_system = pyproject.build_system

    assert pyproject.data == TOMLDocument()
    assert build_system.requires == ["poetry-core"]
    assert build_system.build_backend == "poetry.core.masonry.api"


def test_pyproject_toml_save(
    pyproject_toml: Path, poetry_section: str, build_system_section: str
) -> None:
    pyproject = PyProjectTOML(pyproject_toml)

    build_backend = str(uuid.uuid4())
    build_requires = str(uuid.uuid4())

    pyproject.build_system.build_backend = build_backend
    pyproject.build_system.requires.append(build_requires)

    pyproject.save()

    pyproject = PyProjectTOML(pyproject_toml)

    assert pyproject.build_system.build_backend == build_backend
    assert build_requires in pyproject.build_system.requires
