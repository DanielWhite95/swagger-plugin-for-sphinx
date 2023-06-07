# pylint: disable=missing-function-docstring,redefined-outer-name,too-many-arguments

"""Tests."""

from __future__ import annotations

import urllib.request
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable

import pytest
import jinja2
from pytest_mock import MockerFixture
from sphinx.application import Sphinx
from swagger_plugin_for_sphinx._plugin import SWAGGER_UI_CSS_DEFAULT_URI, SWAGGER_UI_BUNDLE_JS_DEFAULT_URI, PROP_TYPES_MIN_JS, REACT_DEVELOPMENT_JS, STANDALONE_BABEL_MIN_JS

SphinxRunner = Callable[..., None]

EXPECTED_PAGE_TEMPLATE = jinja2.Template(Path(__file__).parent.joinpath("expected_page.html.j2").read_text())

@pytest.fixture
def sphinx_runner(tmp_path: Path) -> SphinxRunner:
    docs = tmp_path / "docs"
    docs.mkdir()
    build = tmp_path / "build"
    build.mkdir()

    def run(
        swagger_present_uri: str | None = None,
        swagger_bundle_uri: str | None = None,
        swagger_css_uri: str | None = None,
    ) -> None:
        code = ["extensions = ['swagger_plugin_for_sphinx']"]
        if swagger_present_uri:
            code.append(f"swagger_present_uri = '{swagger_present_uri}'")
        if swagger_bundle_uri:
            code.append(f"swagger_bundle_uri = '{swagger_bundle_uri}'")
        if swagger_css_uri:
            code.append(f"swagger_css_uri = '{swagger_css_uri}'")

        conf = docs / "conf.py"
        with open(conf, "w+", encoding="utf-8") as file:
            file.write("\n".join(code))

        index_page = """

        .. toctree::
           :hidden:
           :maxdepth: 2

           openapi

        """
        index = docs / "index.rst"
        with open(index, "w+", encoding="utf-8") as file:
            file.write(index_page)

        openapi_page = """
        
        .. swagger-ui:: https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/api-with-examples.yaml

        """
        openapi = docs / "openapi.rst"
        with open(openapi, "w+", encoding="utf-8") as file:
            file.write(openapi_page)

        Sphinx(
            srcdir=str(docs),
            confdir=str(docs),
            outdir=str(build),
            doctreedir=str(build / ".doctrees"),
            buildername="html",
        ).build()

        print('build done')

    return run


def test_run_empty(sphinx_runner: SphinxRunner) -> None:
    sphinx_runner()

@pytest.mark.parametrize(
    "present_uri,bundle_uri,css_uri",
    [
        (
            None,
            None,
            None
            ),
        (
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css",
        ),
    ],
)
def test(sphinx_runner: SphinxRunner,
         tmp_path: Path,
    present_uri: str | None,
    bundle_uri: str | None,
    css_uri: str | None,
) -> None:
    sphinx_runner(present_uri, bundle_uri, css_uri)

    build = tmp_path / "build"
    static = build / "_static"
    
    with open(build / "openapi.html", encoding="utf-8") as file:
        html = file.read()

    base_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest"

    expected = EXPECTED_PAGE_TEMPLATE.render(
        babel_js_uri=STANDALONE_BABEL_MIN_JS,
        swagger_ui_css_uri=css_uri or SWAGGER_UI_CSS_DEFAULT_URI,
        standalone_react_js_uri=REACT_DEVELOPMENT_JS,
        prop_types_js_uri=PROP_TYPES_MIN_JS,
        swagger_ui_bundle_js_uri=bundle_uri or SWAGGER_UI_BUNDLE_JS_DEFAULT_URI,
        openapi_spec_uri="https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/api-with-examples.yaml"
    )

    assert dedent(expected) == dedent(html)
