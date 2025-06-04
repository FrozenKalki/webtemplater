import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_required, current_user

from .. import db
from ..models import VariableDictionary, DictionaryVariable

bp = Blueprint('dicts', __name__, url_prefix='/dicts')


@bp.route('/')
@login_required
def list_dictionaries():
    dictionaries = VariableDictionary.query.filter_by(owner_id=current_user.id).all()
    return render_template('dictionary_list.html', dictionaries=dictionaries)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_dictionary():
    if request.method == 'POST':
        name = request.form['name']
        d = VariableDictionary(name=name, owner=current_user)
        db.session.add(d)
        db.session.commit()
        return redirect(url_for('dicts.list_dictionaries'))
    return render_template('edit_dictionary.html', dictionary=None)


@bp.route('/<int:dict_id>')
@login_required
def view_dictionary(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    variables = DictionaryVariable.query.filter_by(dictionary_id=d.id).all()
    return render_template('variable_list.html', dictionary=d, variables=variables)


@bp.route('/<int:dict_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dictionary(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        d.name = request.form['name']
        db.session.commit()
        return redirect(url_for('dicts.list_dictionaries'))
    return render_template('edit_dictionary.html', dictionary=d)


@bp.route('/<int:dict_id>/delete', methods=['POST'])
@login_required
def delete_dictionary(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    db.session.delete(d)
    db.session.commit()
    return redirect(url_for('dicts.list_dictionaries'))


@bp.route('/<int:dict_id>/variables/new', methods=['GET', 'POST'])
@login_required
def add_variable(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        key = request.form['key']
        value = request.form['value']
        var = DictionaryVariable(key=key, value=value, dictionary=d)
        db.session.add(var)
        db.session.commit()
        return redirect(url_for('dicts.view_dictionary', dict_id=d.id))
    return render_template('edit_variable.html', dictionary=d, variable=None)


@bp.route('/<int:dict_id>/variables/<int:var_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_variable(dict_id: int, var_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    var = DictionaryVariable.query.filter_by(id=var_id, dictionary_id=d.id).first_or_404()
    if request.method == 'POST':
        var.key = request.form['key']
        var.value = request.form['value']
        db.session.commit()
        return redirect(url_for('dicts.view_dictionary', dict_id=d.id))
    return render_template('edit_variable.html', dictionary=d, variable=var)


@bp.route('/<int:dict_id>/variables/<int:var_id>/delete', methods=['POST'])
@login_required
def delete_variable(dict_id: int, var_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    var = DictionaryVariable.query.filter_by(id=var_id, dictionary_id=d.id).first_or_404()
    db.session.delete(var)
    db.session.commit()
    return redirect(url_for('dicts.view_dictionary', dict_id=d.id))


@bp.route('/<int:dict_id>/export')
@login_required
def export_dictionary(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    data = {v.key: v.value for v in d.variables}
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(json_data, mimetype='application/json', headers={'Content-Disposition': f'attachment; filename={d.name}.json'})


@bp.route('/<int:dict_id>/import', methods=['GET', 'POST'])
@login_required
def import_dictionary(dict_id: int):
    d = VariableDictionary.query.filter_by(id=dict_id, owner_id=current_user.id).first_or_404()
    if request.method == 'POST':
        data = request.form['data']
        mode = request.form.get('mode', 'add')
        try:
            values = json.loads(data)
        except json.JSONDecodeError:
            flash('Invalid JSON', 'danger')
            return render_template('import_dictionary.html', dictionary=d)
        if mode == 'replace':
            DictionaryVariable.query.filter_by(dictionary_id=d.id).delete()
        for key, value in values.items():
            var = DictionaryVariable.query.filter_by(dictionary_id=d.id, key=key).first()
            if var:
                var.value = value
            else:
                db.session.add(DictionaryVariable(key=key, value=value, dictionary=d))
        db.session.commit()
        return redirect(url_for('dicts.view_dictionary', dict_id=d.id))
    return render_template('import_dictionary.html', dictionary=d)
