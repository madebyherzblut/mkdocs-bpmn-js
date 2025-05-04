import re

from bs4 import BeautifulSoup
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin, get_plugin_logger

from urllib.parse import urlparse
from urllib.parse import parse_qs

log = get_plugin_logger(__name__)


class BPMNPlugin(BasePlugin):
    """
    A MkDocs plugin to render BPMN diagrams using bpmn-js.
    """

    config_scheme = (
        (
            "viewer_js",
            config_options.Type(
                str,
                default="https://unpkg.com/bpmn-js@18/dist/bpmn-navigated-viewer.production.min.js",
            ),
        ),
        (
            "viewer_css",
            config_options.Type(
                str,
                default="https://unpkg.com/bpmn-js@18/dist/assets/bpmn-js.css",
            ),
        ),
        ("viewer_initialize", config_options.Type(bool, default=True)),
        ("class", config_options.Type(str, default="mk-bpmn-js")),
    )

    def on_post_page(self, output, config, page, **kwargs):
        if ".bpmn" not in output:
            return output

        html = BeautifulSoup(output, "html.parser")
        diagrams = html.find_all(
            "img", src=re.compile(r".*\.bpmn(\?.*)?$", re.IGNORECASE)
        )

        if not diagrams:
            return output

        used_ids = set()

        for idx, diagram in enumerate(diagrams):
            log.debug(f"Embed diagram '{diagram['src']}' in page '{page.title}'")

            src = diagram["src"]
            params = {}
            if "?" in src:
                parsed_url = urlparse(src)
                params = parse_qs(parsed_url.query)
                src = parsed_url.path

            tag = html.new_tag("span")
            tag.attrs["class"] = self.config["class"]
            tag.attrs["data-src"] = src

            if diagram["alt"]:
                tag.attrs["data-alt"] = diagram["alt"]

                link = html.new_tag("a")
                link.attrs["href"] = src
                link.attrs["download"] = ""
                link.append(diagram["alt"])

                noscript = html.new_tag("noscript")
                noscript.append(link)

                tag.append(noscript)

            if "id" in params:
                tag.attrs["id"] = params["id"][0]
            else:
                tag.attrs["id"] = "mk-bpmn-" + str(idx + 1)

            if tag.attrs["id"] in used_ids:
                log.error(
                    f"Duplicate ID '{tag.attrs['id']}' found in page '{page.title}'. "
                    "Please ensure that each diagram has a unique ID."
                )

            used_ids.add(tag.attrs["id"])

            if "width" in params:
                tag.attrs["data-width"] = params["width"][0]

            if "height" in params:
                tag.attrs["data-height"] = params["height"][0]

            diagram.replace_with(tag)

        if self.config["viewer_css"]:
            link_viewer = html.new_tag(
                "link",
                rel="stylesheet",
                type="text/css",
                href=self.config["viewer_css"],
            )
            html.head.append(link_viewer)

        if self.config["viewer_js"]:
            script_viewer = html.new_tag("script", src=self.config["viewer_js"])
            html.body.append(script_viewer)

        if self.config["viewer_initialize"]:
            script = html.new_tag("script", type="text/javascript")
            script.string = """
                document.addEventListener('DOMContentLoaded', async function() {
                    try {
                        const elements = document.querySelectorAll('.%s');
                        for (const element of elements) {
                            const src = element.getAttribute('data-src');
                            const xml = await fetch(src)
                                .then(response => response.text())
                                .catch(err => console.error('Error fetching BPMN XML:', err));

                            const options = {}
                            if (element.hasAttribute('data-width')) {
                                options.width = element.getAttribute('data-width');
                            }
                            if (element.hasAttribute('data-height')) {
                                options.height = element.getAttribute('data-height');
                            }

                            const viewer = new BpmnJS({ container: element, ...options });
                            await viewer.importXML(xml);
                            viewer.get('canvas').zoom('fit-viewport');
                        }
                    } catch (err) {
                        console.error('Error rendering BPMN diagram:', err);
                    }
                });
            """ % (self.config["class"])

            html.body.append(script)

        return str(html)
