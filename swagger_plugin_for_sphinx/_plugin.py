"""
Swagger Plugin for Sphinx Doc
============================+

This extension provides a means of embedding a Swagger UI for a given
OpenAPI spec using the directive swaggerui

    .. swagger-ui:: path/to/spec.yaml

"""
from __future__ import annotations

import urllib.request
from importlib.metadata import version
from pathlib import Path
from typing import Any

import jinja2
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective

SWAGGER_UI_CSS_DEFAULT_URI = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css"

SWAGGER_UI_BUNDLE_JS_DEFAULT_URI = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js"

SWAGGER_UI_BUNDLE_TEMPLATE = jinja2.Template(
    """
    <div id="{{ dom_id }}"{% if div_class %} class="{{ div_class }}"{% endif %}>
<script>
   window.onload = () => {
    window.ui = SwaggerUIBundle({
      url: '{{ swagger_spec_uri }}',
      dom_id: '#{{ dom_id }}',
    });
  };
</script>
</div>
"""
)


class swagger_ui(nodes.General, nodes.Element):
    pass


# TODO: I don't think this is required
def purge_altair_namespaces(
        app: Sphinx,
        env: BuildEnvironment,
        docname: str,
) -> None:
    if not hasattr(env, "_altair_namespaces"):
        return
    env._altair_namespaces.pop(docname, {})


class SwaggerUI(SphinxDirective):
    required_arguments = 1
    has_content = False

    def run(self):
        namespace_id = 'default'
        serialno = 'swagger-ui-%d' % self.env.new_serialno('swaggerui')
        rst_source = Path(self.state_machine.document['source'])
        rst_dir = rst_source.parent
        rst_name, _ = rst_source.name.split('.')
        target_id = f"{rst_name}-swagger-source-{serialno}"
        swagger_id = f"{rst_name}-swagger-ui-{serialno}"
        target_node = nodes.target('', '', ids=[target_id])
        swagger_ui_node = swagger_ui()
        swagger_ui_node['spec'] = self.arguments[0]
        swagger_ui_node['div_id'] = swagger_id
        return [target_node, swagger_ui_node]


def visit_html_swagger_ui(self, node: nodes.Element):
    """
    Add script to load Swagger UI when node is visited in HTML pages
    """
    swagger_spec = node['spec']
    swagger_div_id = node['div_id']
    html = SWAGGER_UI_BUNDLE_TEMPLATE.render(swagger_spec_uri=swagger_spec, dom_id=swagger_div_id)
    self.body.append(html)


def generic_visit_swagger_ui(self, node: nodes.Element):
    """
    Swagger UI is not rendered on non-HTML targets
    """
    raise nodes.SkipNode


def depart_swagger_ui(self, node: nodes.Element) -> None:
    return


def register_assets(app: Sphinx):
    app.add_js_file(app.config.swagger_bundle_uri)
    app.add_css_file(app.config.swagger_css_uri)


def download_assets(app: Sphinx, exception: BaseException | None) -> None:
    """Move the needed swagger file into the _static folder."""
    if exception:
        return
    if not app.builder:
        return

    static_folder = Path(app.builder.outdir) / "_static"
    urllib.request.urlretrieve(
        app.config.swagger_bundle_uri, str(static_folder / "swagger-ui-bundle.js")
    )
    urllib.request.urlretrieve(
        app.config.swagger_css_uri, str(static_folder / "swagger-ui.css")
    )


def setup(app: Sphinx) -> dict[str, Any]:
    """Setup this plugin."""
    app.add_config_value(
        "swagger_bundle_uri",
        SWAGGER_UI_BUNDLE_JS_DEFAULT_URI,
        "html",
    )
    app.add_config_value(
        "swagger_css_uri",
        SWAGGER_UI_CSS_DEFAULT_URI,
        "html",
    )

    app.add_directive("swagger-ui", SwaggerUI)
    app.add_node(swagger_ui,
                 html=(visit_html_swagger_ui, depart_swagger_ui),
                 latex=(generic_visit_swagger_ui, depart_swagger_ui),
                 text=(generic_visit_swagger_ui, depart_swagger_ui),
                 man=(generic_visit_swagger_ui, depart_swagger_ui),
                 texinfo=(generic_visit_swagger_ui, depart_swagger_ui)
                 )

    app.connect('builder-inited', register_assets)

    return {
        "version": version("swagger_plugin_for_sphinx"),
    }
