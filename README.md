# mkdocs-bpmn-js

**mkdocs-bpmn-js** is a simple MkDocs plugin that enables you to embed [BPMN diagrams](https://en.wikipedia.org/wiki/Business_Process_Model_and_Notation) directly into your documentation using [`bpmn-js`](https://bpmn.io/toolkit/bpmn-js/). Diagrams are embedded just like images, using Markdown syntax.

## Installation

Install via pip:

```bash
pip install mkdocs-bpmn-js
```

Then enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - bpmn-js
```

### Plugin Options

You can configure the plugin by adding options under `bpmn-js` in `mkdocs.yml`.

```yaml
plugins:
  - bpmn-js:
      viewer_js: "assets/bpmn-navigated-viewer.production.min.js"
      viewer_css: "assets/bpmn-js.css"
      class: "mk-bpmn-js"
```

| Option              | Description                                          | Default Value                                                               |
| ------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| `render`            | Specify the render mode (`none`, `image`, `viewer`). | `viewer`                                                                    |
| `class`             | CSS class applied to each diagram container.         | `mk-bpmn-js`                                                                |
| `viewer_js`         | Path to the BPMN viewer JavaScript file.              | `assets/bpmn-navigated-viewer.production.min.js`                            |
| `viewer_css`        | Path to the BPMN viewer CSS file.                     | `assets/bpmn-js.css`                                                        |
| `viewer_initialize` | Append a script to load the diagrams.                | `True`                                                                      |
| `image_command`     | Command to call when `render` is set to `image`.     | `bpmn-to-image --no-title --no-footer $input:$output`                       |

### Local Viewer Assets

This plugin now bundles the `bpmn-js` viewer assets by default, so you don't need to rely on an external CDN or host the files manually. The files are copied to your site's `assets` directory during the build process.

The default configuration points to these local files:

```yaml
plugins:
  - bpmn-js:
      viewer_js: "assets/bpmn-navigated-viewer.production.min.js"
      viewer_css: "assets/bpmn-js.css"
```

You can still override these paths if you wish to use a different version of `bpmn-js` or host the files in a different location.

### Image rendering

To render an image instead of an interactive viewer, set the `render` config to `image`. We recommend using [bpmn-to-image](https://github.com/bpmn-io/bpmn-to-image), but you can use any script you prefer. During rendering, the plugin will call the `image_command` and replace `$input` with the absolute path to the BPMN diagram and `$output` with a temporary cache file.

For example, with the default `image_command`:

```yaml
image_command: "bpmn-to-image --no-title --no-footer $input:$output"
```

Have a look at the [example](./example/mkdocs.yml) to see how `bpmn-to-image` can be configured and used.

## Usage

Add `.bpmn` files using standard Markdown image syntax:

```markdown
<!-- Relative path to the current Markdown file -->

![Hello World](hello-world.bpmn)

<!-- Absolute path from the site root -->

![Hello World](/diagrams/hello-world.bpmn)

<!-- No alternative text -->

![](hello-world.bpmn)

<!-- With diagram options (see below for more details) -->

![](hello-world.bpmn?id=hello-world&height=400px)
```

The alternative text is optional and will be rendered as a link to the diagram file within a `noscript` element.

### Diagram Options

You can customize individual diagrams using query parameters in the image URL.

```markdown
![Custom Diagram](my-diagram.bpmn?id=my-diagram&height=500px&width=100%25)
```

| Parameter | Description                                                  | Example         |
| --------- | ------------------------------------------------------------ | --------------- |
| `id`      | Sets the HTML `id` of the viewer canvas. Useful for linking. | `id=my-diagram` |
| `width`   | Sets the diagram width. Accepts any valid CSS width value.   | `width=100%25`  |
| `height`  | Sets the diagram height. Accepts any valid CSS height value. | `height=300px`  |

## Development

This project includes the `bpmn-js` assets directly in the repository. To update the bundled assets to a new version, follow these steps:

1. **Update the version in `package.json`**:
    Modify the version number for `bpmn-js` in the `dependencies` section.

2. **Run the update script**:
    This will download the new version from npm, copy the necessary assets into the source directory, and clean up temporary files.

    ```bash
    npm install
    npm run update-assets
    ```

3. **Commit the changes**:
    Commit the updated `package.json`, `package-lock.json`, and the new asset files located in `src/mkdocs_bpmn_js/assets/`.

## Acknowledgments

- Inspired by [mkdocs-drawio](https://github.com/tuunit/mkdocs-drawio), which served as a helpful reference for embedding diagrams in MkDocs.
- Also check out [mkdocs-bpmn](https://github.com/vanchaxy/mkdocs-bpmn), an alternative implementation. Depending on your needs, it might be a better fit.
