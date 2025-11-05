import hashlib
import os
import re
import shlex
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from mkdocs.config import config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.utils import copy_file

log = get_plugin_logger(__name__)


ASSETS_DIR = Path(__file__).parent / "assets"


class BPMNPlugin(BasePlugin):
    """
    A MkDocs plugin to render BPMN diagrams using bpmn-js.
    """

    config_scheme = (
        (
            "render",
            config_options.Choice(["none", "image", "viewer"], default="viewer"),
        ),
        ("class", config_options.Type(str, default="mk-bpmn-js")),
        ("cache_dir", config_options.Type(str, default=".bpmn-cache")),
        (
            "viewer_js",
            config_options.Type(str, default="assets/bpmn-navigated-viewer.production.min.js"),
        ),
        (
            "viewer_css",
            config_options.Type(str, default="assets/bpmn-js.css"),
        ),
        ("viewer_initialize", config_options.Type(bool, default=True)),
        (
            "image_command",
            config_options.Type(
                str,
                default="bpmn-to-image --no-title --no-footer $input:$output",
            ),
        ),
    )

    render_queue = None

    def on_config(self, config):
        if self.config["render"] == "image" and not self.config["image_command"]:
            raise PluginError(
                "Render mode 'image' requires a 'image_command' to be specified."
            )

        if self.config["cache_dir"]:
            cache_dir = Path(self.config["cache_dir"])
            cache_dir.mkdir(parents=True, exist_ok=True)

        if (
            self.config["image_command"]
            and "$input" not in self.config["image_command"]
        ):
            raise PluginError("Missing '$input' placeholder in image_command.")
        if (
            self.config["image_command"]
            and "$output" not in self.config["image_command"]
        ):
            raise PluginError("Missing '$output' placeholder in image_command.")


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
        self.render_queue = {}

        for idx, diagram in enumerate(diagrams):
            log.debug(f"Embed diagram '{diagram['src']}' in page '{page.title}'")

            src = diagram["src"]
            params = {}
            if "?" in src:
                parsed_url = urlparse(src)
                params = parse_qs(parsed_url.query)
                src = parsed_url.path

            if self.config["render"] == "none":
                diagram.decompose()
                continue

            tag = None

            if self.config["render"] == "image":
                input_src = Path(config["docs_dir"]) / src
                file_hash = compute_file_hash(input_src)

                tag = html.new_tag("img")
                tag.attrs["class"] = self.config["class"]
                tag.attrs["data-src"] = src
                tag.attrs["src"] = src.replace(".bpmn", ".svg?" + file_hash)

                self.render_queue[src] = file_hash
            elif self.config["render"] == "viewer":
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

        if self.config["render"] == "viewer" and self.config["viewer_css"]:
            link_viewer = html.new_tag(
                "link",
                rel="stylesheet",
                type="text/css",
                href=self.config["viewer_css"],
            )
            html.head.append(link_viewer)

        if self.config["render"] == "viewer" and self.config["viewer_js"]:
            script_viewer = html.new_tag("script", src=self.config["viewer_js"])
            html.body.append(script_viewer)

        if self.config["render"] == "viewer" and self.config["viewer_initialize"]:
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

    def on_post_build(self, *, config):
        if self.config["render"] == "viewer":
            css_output_path = Path(config["site_dir"]) / self.config["viewer_css"]
            js_output_path = Path(config["site_dir"]) / self.config["viewer_js"]
            css_output_path.parent.mkdir(parents=True, exist_ok=True)
            js_output_path.parent.mkdir(parents=True, exist_ok=True)
            copy_file(ASSETS_DIR / "bpmn-js.css", css_output_path)
            copy_file(
                ASSETS_DIR / "bpmn-navigated-viewer.production.min.js", js_output_path
            )

        if not self.config["render"] == "image" or not self.render_queue:
            return

        docs_dir = Path(config["docs_dir"])
        site_dir = Path(config["site_dir"])
        cache_dir = Path(self.config["cache_dir"])

        for file_src, file_hash in self.render_queue.items():
            input_src = Path(file_src)

            input_file = docs_dir / input_src
            cache_file = cache_dir / f"{file_hash}.svg"
            output_file = site_dir / input_src.with_suffix(".svg")

            if not cache_file.exists():
                command = (
                    self.config["image_command"]
                    .replace("$input", str(input_file))
                    .replace("$output", str(cache_file))
                )

                try:
                    log.debug(f"Render diagram with: {command}")
                    subprocess.run(
                        shlex.split(command),
                        capture_output=True,
                        text=True,
                        check=True,
                        env=os.environ,
                    )
                except subprocess.CalledProcessError as e:
                    raise PluginError(f"Subprocess failed with error: {e.stderr}")

            copy_file(cache_file, output_file)

        self.render_queue = None


def compute_file_hash(path):
    """
    Compute a hash for the file at the given path.
    """

    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
