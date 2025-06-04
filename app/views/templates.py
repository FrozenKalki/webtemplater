import os
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from docxtpl import DocxTemplate

from .. import db
from ..models import Template, TemplateContext

bp = Blueprint('templates', __name__, url_prefix='/templates')

UPLOAD_FOLDER = 'user_templates'


@bp.route('/')
@login_required
def list_templates():
    templates = Template.query.filter_by(owner_id=current_user.id).all()
    return render_template('template_list.html', templates=templates)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_template():
    if request.method == 'POST':
        file = request.files['file']
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('templates.upload_template'))
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        tmpl = Template(filename=filename, path=path, owner=current_user)
        db.session.add(tmpl)
        db.session.commit()
        return redirect(url_for('templates.list_templates'))
    return render_template('upload_template.html')


@bp.route('/<int:template_id>/fill', methods=['GET', 'POST'])
@login_required
def fill_template(template_id):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        try:
            context = json.loads(request.form['context'])
        except json.JSONDecodeError:
            flash('Invalid JSON', 'danger')
            contexts = TemplateContext.query.filter_by(template_id=tmpl.id, owner_id=current_user.id).all()
            return render_template('fill_template.html', template=tmpl, contexts=contexts)
        doc = DocxTemplate(tmpl.path)
        doc.render(context)
        output_path = os.path.join(UPLOAD_FOLDER, f"filled_{tmpl.filename}")
        doc.save(output_path)
        return send_file(output_path, as_attachment=True)
    contexts = TemplateContext.query.filter_by(template_id=tmpl.id, owner_id=current_user.id).all()
    return render_template('fill_template.html', template=tmpl, contexts=contexts)


@bp.route('/<int:template_id>/fill_context/<int:context_id>')
@login_required
def fill_template_with_context(template_id: int, context_id: int):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    ctx = TemplateContext.query.filter_by(id=context_id, template_id=tmpl.id, owner_id=current_user.id).first_or_404()
    context = json.loads(ctx.data)
    doc = DocxTemplate(tmpl.path)
    doc.render(context)
    output_path = os.path.join(UPLOAD_FOLDER, f"filled_{tmpl.filename}")
    doc.save(output_path)
    return send_file(output_path, as_attachment=True)


@bp.route('/<int:template_id>/contexts')
@login_required
def list_contexts(template_id: int):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    contexts = TemplateContext.query.filter_by(template_id=tmpl.id, owner_id=current_user.id).all()
    return render_template('context_list.html', template=tmpl, contexts=contexts)


@bp.route('/<int:template_id>/contexts/new', methods=['GET', 'POST'])
@login_required
def create_context(template_id: int):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        name = request.form['name']
        data = request.form['data']
        try:
            json.loads(data)
        except json.JSONDecodeError:
            flash('Invalid JSON', 'danger')
            return render_template('edit_context.html', template=tmpl, context=None)
        ctx = TemplateContext(name=name, data=data, template=tmpl, owner=current_user)
        db.session.add(ctx)
        db.session.commit()
        return redirect(url_for('templates.list_contexts', template_id=tmpl.id))
    return render_template('edit_context.html', template=tmpl, context=None)


@bp.route('/<int:template_id>/contexts/<int:context_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_context(template_id: int, context_id: int):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    ctx = TemplateContext.query.filter_by(id=context_id, template_id=tmpl.id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        ctx.name = request.form['name']
        data = request.form['data']
        try:
            json.loads(data)
        except json.JSONDecodeError:
            flash('Invalid JSON', 'danger')
            return render_template('edit_context.html', template=tmpl, context=ctx)
        ctx.data = data
        db.session.commit()
        return redirect(url_for('templates.list_contexts', template_id=tmpl.id))
    return render_template('edit_context.html', template=tmpl, context=ctx)


@bp.route('/<int:template_id>/contexts/<int:context_id>/delete', methods=['POST'])
@login_required
def delete_context(template_id: int, context_id: int):
    tmpl = Template.query.filter_by(id=template_id, owner_id=current_user.id).first_or_404()
    ctx = TemplateContext.query.filter_by(id=context_id, template_id=tmpl.id, owner_id=current_user.id).first_or_404()
    db.session.delete(ctx)
    db.session.commit()
    return redirect(url_for('templates.list_contexts', template_id=tmpl.id))
