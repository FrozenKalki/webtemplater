# Webtemplater

Prototype web service for uploading DOCX templates and generating documents per user.  
The repository also contains a small Jinja2 based CLI tool for rendering static HTML from templates.

## Setup

1. Create virtual environment and install requirements:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python run.py
```

The application uses SQLite database `webtemplater.db` by default.

## CLI Usage

The `webtemplater` package provides a simple command line interface for
rendering Jinja2 templates into HTML files.

Render a template using a JSON context file:

```bash
python -m webtemplater.cli render templates/hello.html.j2 context.json output.html
```

The `--templates` option can be used to specify a custom templates directory.

## Notes on Specification

The provided UI specification references a library called `pydoctemplater`,
which could not be found on PyPI. Instead, this project uses [`docxtpl`](https://github.com/elapouya/python-docx-template)
for DOCX templating.

This repository implements only basic functionality:

- User registration and login with hashed passwords.
- Uploading DOCX templates, stored per user.
- Listing templates and generating a filled document from JSON context.

The full specification includes many additional modules (RBAC, admin interface,
integrations, etc.) which are out of scope for this initial prototype.
