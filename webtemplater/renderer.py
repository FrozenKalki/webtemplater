from pathlib import Path
from typing import Any, Mapping

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    """Render Jinja2 templates from a directory."""

    def __init__(self, template_dir: str | Path):
        template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render(self, template_name: str, context: Mapping[str, Any]) -> str:
        """Render a template with the given context and return the string."""
        template = self.env.get_template(template_name)
        return template.render(**context)
