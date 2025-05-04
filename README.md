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
      viewer_js: "https://unpkg.com/bpmn-js@18/dist/bpmn-navigated-viewer.production.min.js"
      viewer_css: "https://unpkg.com/bpmn-js@18/dist/assets/bpmn-js.css"
      class: "mk-bpmn-js"
```

| Option              | Description                                  | Default Value                                                                   |
| ------------------- | -------------------------------------------- | ------------------------------------------------------------------------------- |
| `viewer_js`         | URL to the BPMN viewer JavaScript file.      | `https://unpkg.com/bpmn-js@18/dist/bpmn-navigated-viewer.production.min.js`     |
| `viewer_css`        | URL to the BPMN viewer CSS file.             | `https://unpkg.com/bpmn-js@18/dist/assets/bpmn-js.css`                          |
| `viewer_initialize` | Append a script to load the diagrams.        | `True`                                                                          |
| `class`             | CSS class applied to each diagram container. | `mk-bpmn-js`                                                                    |

### Local viewer assets

If you prefer not to load assets from a CDN, you can host the required BPMN viewer files yourself.

```bash
mkdir -p theme/js theme/css
curl -L https://unpkg.com/bpmn-js@18/dist/bpmn-navigated-viewer.production.min.js > theme/js/bpmn.js
curl -L https://unpkg.com/bpmn-js@18/dist/assets/bpmn-js.css > theme/css/bpmn.css
```

Override the default theme to include your local assets by creating a custom `theme/main.html` template.
Refer to the [MkDocs guide on customizing themes](https://www.mkdocs.org/user-guide/customizing-your-theme/#overriding-template-blocks) for more details.

```html
{% extends "base.html" %}

{% block styles %}
  {{ super() }}
  <link rel="stylesheet" href="{{ base_url }}/css/bpmn.css" />
{% endblock %}

{% block libs %}
  {{ super() }}
  <script src="{{ base_url }}/js/bpmn.js"></script>
{% endblock %}
```

Finally, disable the default CDN links by setting the plugin options to empty strings in `mkdocs.yml`:

```yaml
plugins:
  - bpmn-js:
      viewer_js: ""
      viewer_css: ""
```

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

## Acknowledgments

* Inspired by [mkdocs-drawio](https://github.com/tuunit/mkdocs-drawio), which served as a helpful reference for embedding diagrams in MkDocs.
* Also check out [mkdocs-bpmn](https://github.com/vanchaxy/mkdocs-bpmn), an alternative implementation. Depending on your needs, it might be a better fit.
