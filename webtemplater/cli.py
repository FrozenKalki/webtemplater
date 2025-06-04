"""Command line interface for rendering templates."""

import json
from pathlib import Path

import click

from .renderer import TemplateRenderer


@click.group()
@click.option('--templates', '-t', default='templates', show_default=True,
              help='Directory with Jinja2 templates.')
@click.pass_context
def cli(ctx: click.Context, templates: str):
    """Render HTML pages from templates."""
    ctx.obj = TemplateRenderer(templates)


@cli.command()
@click.argument('template')
@click.argument('context_file')
@click.argument('output')
@click.pass_obj
def render(renderer: TemplateRenderer, template: str, context_file: str, output: str):
    """Render TEMPLATE using data from CONTEXT_FILE into OUTPUT."""
    with open(context_file, 'r', encoding='utf-8') as f:
        context = json.load(f)
    result = renderer.render(template, context)
    Path(output).write_text(result, encoding='utf-8')
    click.echo(f"Generated {output}")


if __name__ == '__main__':
    cli()
