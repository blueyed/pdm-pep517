import email
import zipfile

import pytest

from pdm.pep517 import api
from tests.testutils import build_fixture_project, get_tarball_names, get_wheel_names


def test_build_single_module(tmp_path):
    with build_fixture_project("demo-module"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert api.get_requires_for_build_sdist() == []
        assert api.get_requires_for_build_wheel() == []
        assert sdist_name == "demo-module-0.1.0.tar.gz"
        assert wheel_name == "demo_module-0.1.0-py3-none-any.whl"
        tar_names = get_tarball_names(tmp_path / sdist_name)
        for name in [
            "foo_module.py",
            "bar_module.py",
            "LICENSE",
            "pyproject.toml",
            "PKG-INFO",
            "README.md",
        ]:
            assert f"demo-module-0.1.0/{name}" in tar_names

        zip_names = get_wheel_names(tmp_path / wheel_name)
        for name in ["foo_module.py", "bar_module.py"]:
            assert name in zip_names

        for name in ("pyproject.toml", "LICENSE"):
            assert name not in zip_names


def test_build_package(tmp_path):
    with build_fixture_project("demo-package"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-package-0.1.0.tar.gz"
        assert wheel_name == "demo_package-0.1.0-py2.py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        assert "demo-package-0.1.0/my_package/__init__.py" in tar_names
        assert "demo-package-0.1.0/my_package/data.json" in tar_names
        assert "demo-package-0.1.0/single_module.py" not in tar_names
        assert "demo-package-0.1.0/data_out.json" in tar_names

        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "my_package/__init__.py" in zip_names
        assert "my_package/data.json" in zip_names
        assert "single_module.py" not in zip_names
        assert "data_out.json" not in zip_names


def test_build_src_package(tmp_path):
    with build_fixture_project("demo-src-package"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-package-0.1.0.tar.gz"
        assert wheel_name == "demo_package-0.1.0-py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "demo-package-0.1.0/src/my_package/__init__.py" in tar_names
        assert "demo-package-0.1.0/src/my_package/data.json" in tar_names

        assert "my_package/__init__.py" in zip_names
        assert "my_package/data.json" in zip_names


def test_build_package_include(tmp_path):
    with build_fixture_project("demo-package-include"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-package-0.1.0.tar.gz"
        assert wheel_name == "demo_package-0.1.0-py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        zip_names = get_wheel_names(tmp_path / wheel_name)

        assert "demo-package-0.1.0/my_package/__init__.py" in tar_names
        assert "demo-package-0.1.0/my_package/data.json" not in tar_names
        assert "demo-package-0.1.0/requirements.txt" in tar_names
        assert "demo-package-0.1.0/data_out.json" in tar_names

        assert "my_package/__init__.py" in zip_names
        assert "my_package/data.json" not in zip_names
        assert "requirements.txt" in zip_names
        assert "data_out.json" in zip_names


def test_namespace_package_by_include(tmp_path):
    with build_fixture_project("demo-pep420-package"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-package-0.1.0.tar.gz"
        assert wheel_name == "demo_package-0.1.0-py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "demo-package-0.1.0/foo/my_package/__init__.py" in tar_names
        assert "demo-package-0.1.0/foo/my_package/data.json" in tar_names

        assert "foo/my_package/__init__.py" in zip_names
        assert "foo/my_package/data.json" in zip_names


def test_build_explicit_package_dir(tmp_path):
    with build_fixture_project("demo-explicit-package-dir"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-package-0.1.0.tar.gz"
        assert wheel_name == "demo_package-0.1.0-py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "demo-package-0.1.0/foo/my_package/__init__.py" in tar_names
        assert "demo-package-0.1.0/foo/my_package/data.json" in tar_names

        assert "my_package/__init__.py" in zip_names
        assert "my_package/data.json" in zip_names


def test_prepare_metadata(tmp_path):
    with build_fixture_project("demo-package"):
        dist_info = api.prepare_metadata_for_build_wheel(tmp_path.as_posix())
        assert dist_info == "demo_package-0.1.0.dist-info"
        for filename in ("WHEEL", "METADATA"):
            assert (tmp_path / dist_info / filename).is_file()


@pytest.mark.xfail
def test_build_legacypackage(tmp_path):
    with build_fixture_project("demo-legacy"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert sdist_name == "demo-legacy-0.1.0.tar.gz"
        assert wheel_name == "demo_legacy-0.1.0-py3-none-any.whl"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        assert "demo-legacy-0.1.0/my_package/__init__.py" in tar_names
        assert "demo-legacy-0.1.0/my_package/data.json" in tar_names
        assert "demo-legacy-0.1.0/single_module.py" not in tar_names
        assert "demo-legacy-0.1.0/data_out.json" not in tar_names

        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "my_package/__init__.py" in zip_names
        assert "my_package/data.json" in zip_names
        assert "single_module.py" not in zip_names
        assert "data_out.json" not in zip_names


def test_build_package_with_modules_in_src(tmp_path):
    with build_fixture_project("demo-src-pymodule"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())

        tar_names = get_tarball_names(tmp_path / sdist_name)
        assert "demo-module-0.1.0/src/foo_module.py" in tar_names

        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "foo_module.py" in zip_names


def test_build_with_cextension(tmp_path):
    with build_fixture_project("demo-cextension"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())
        assert api.get_requires_for_build_sdist() == []
        assert api.get_requires_for_build_wheel() == ["setuptools>=40.8.0"]

        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "my_package/__init__.py" in zip_names
        assert (
            "my_package/hellomodule.c" not in zip_names
        ), "Not collect c files while building wheel"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        assert "demo-package-0.1.0/my_package/__init__.py" in tar_names
        assert (
            "demo-package-0.1.0/my_package/hellomodule.c" in tar_names
        ), "Collect c files while building sdist"
        assert not any(
            path.startswith("build") for path in tar_names
        ), 'Not collect c files in temporary directory "./build"'


def test_build_with_cextension_in_src(tmp_path):
    with build_fixture_project("demo-cextension-in-src"):
        wheel_name = api.build_wheel(tmp_path.as_posix())
        sdist_name = api.build_sdist(tmp_path.as_posix())

        zip_names = get_wheel_names(tmp_path / wheel_name)
        assert "my_package/__init__.py" in zip_names
        assert (
            "my_package/hellomodule.c" not in zip_names
        ), "Not collect c files while building wheel"

        tar_names = get_tarball_names(tmp_path / sdist_name)
        assert "demo-package-0.1.0/src/my_package/__init__.py" in tar_names
        assert (
            "demo-package-0.1.0/src/my_package/hellomodule.c" in tar_names
        ), "Collect c files while building sdist"
        assert not any(
            path.startswith("build") for path in tar_names
        ), 'Not collect c files in temporary directory "./build"'


def test_build_editable(tmp_path):
    with build_fixture_project("demo-package") as project:
        wheel_name = api.build_editable(tmp_path.as_posix())
        assert api.get_requires_for_build_editable() == []
        with zipfile.ZipFile(tmp_path / wheel_name) as zf:
            namelist = zf.namelist()
            assert "demo_package.pth" in namelist
            assert "_demo_package.py" in namelist

            metadata = email.message_from_bytes(
                zf.read("demo_package-0.1.0.dist-info/METADATA")
            )
            assert "editables" in metadata.get_all("Requires-Dist", [])

            pth_content = zf.read("demo_package.pth").decode("utf-8").strip()
            assert pth_content == "import _demo_package"

            proxy_module = zf.read("_demo_package.py").decode("utf-8").strip()
            assert proxy_module == (
                "from editables.redirector import RedirectingFinder as F\n"
                "F.install()\n"
                "F.map_module('my_package', {0!r})".format(
                    str((project / "my_package" / "__init__.py").resolve())
                )
            )


def test_build_editable_src(tmp_path):
    with build_fixture_project("demo-src-package-include") as project:
        wheel_name = api.build_editable(tmp_path.as_posix())

        with zipfile.ZipFile(tmp_path / wheel_name) as zf:
            namelist = zf.namelist()
            assert "demo_package.pth" in namelist
            assert "_demo_package.py" in namelist
            assert "my_package/data.json" not in namelist
            assert "data_out.json" in namelist

            pth_content = zf.read("demo_package.pth").decode("utf-8").strip()
            assert pth_content == "import _demo_package"

            proxy_module = zf.read("_demo_package.py").decode("utf-8").strip()
            assert proxy_module == (
                "from editables.redirector import RedirectingFinder as F\n"
                "F.install()\n"
                "F.map_module('my_package', {0!r})".format(
                    str((project / "sub" / "my_package" / "__init__.py").resolve())
                )
            )


def test_build_editable_pep420(tmp_path):
    with build_fixture_project("demo-pep420-package") as project:
        wheel_name = api.build_editable(tmp_path.as_posix())

        with zipfile.ZipFile(tmp_path / wheel_name) as zf:
            namelist = zf.namelist()
            assert "demo_package.pth" in namelist
            assert "_demo_package.py" not in namelist

            metadata = email.message_from_bytes(
                zf.read("demo_package-0.1.0.dist-info/METADATA")
            )
            assert "editables" not in metadata.get_all("Requires-Dist", [])

            pth_content = zf.read("demo_package.pth").decode("utf-8").strip()
            assert pth_content == str(project.resolve())
