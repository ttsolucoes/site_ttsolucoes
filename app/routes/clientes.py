from flask import render_template, request, jsonify
from app import app
from config import executar_sql, required_roles
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange

class FeedbackForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nota_satisfacao = IntegerField('Nota de Satisfação (1 a 5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comentario = TextAreaField('Comentário')

@app.route('/feedback', methods=['GET'])
def clientes():
    form = FeedbackForm()
    return render_template('pages/public/clientes.html', form=form)

@app.route('/ver_feedback', methods=['GET'])
@required_roles('admin')
def ver_feedback():

    from config import executar_sql

    query = "SELECT id, nome, email, nota_satisfacao, comentario, data_envio FROM feedback_clientes ORDER BY data_envio DESC;"
    feedback = executar_sql(query)
    resultado_feedback = [
        {
            'id': row[0],
            'nome': row[1],
            'email': row[2],
            'nota_satisfacao': int(row[3]),
            'comentario': row[4],
            'data_envio': row[5]
        }
        for row in feedback
    ]
    print(resultado_feedback)
    return render_template('pages/private/clientes.html', feedback=resultado_feedback)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    nota = data.get('nota_satisfacao')
    comentario = data.get('comentario')

    if not nota:
        return jsonify({'success': False, 'message': 'Campos obrigatórios faltando'}), 400

    query = f"""
INSERT INTO feedback_clientes (nome, email, nota_satisfacao, comentario)
VALUES ('{nome}', '{email}', {nota}, '{comentario}')
    """
    executar_sql(query)
    return jsonify({'success': True})

