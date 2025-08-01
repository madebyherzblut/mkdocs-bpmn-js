# Changelog

## 0.2.0

- Add new config value `render`:
  - `none`: Removes the diagram from the output.
  - `viewer`: Renders the diagram with `bpmn-js`.
  - `image`: Renders the diagram to a SVG image.
- Add new config value `render_command`: Command to call to render a diagram to an image. Defaults to `bpmn-to-image --no-title --no-footer $input:$output`.

## 0.1.0

Initial version.
