from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from app import app
from flask import render_template
from config import secret_key

app.secret_key = secret_key

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField('Email', [
        validators.Email(),
        validators.DataRequired()
    ])
    password = PasswordField('Senha', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Senhas devem ser iguais')
    ])
    confirm = PasswordField('Repita a Senha')

class RecoveryForm(FlaskForm):
    email_or_username = StringField('Email ou Usuário', [
        validators.DataRequired(message="Preencha este campo"),
        validators.Length(min=4, max=50)
    ])
    motivo = StringField('Motivo de recuperacao')

@app.route('/register', methods=['GET', 'POST'])
def register():

    from utils import criar_usuario_public

    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'status': 'pending'
        }
        criar_usuario_public(form.username.data, form.password.data, form.email.data)
        return render_template('pages/public/conta_criada.html', novos=new_user)
    return render_template('pages/public/criar_conta.html', form=form)

@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    
    from utils import recuperar_acesso_public

    form = RecoveryForm()
    if form.validate_on_submit():
        new_user = {
            'conta': form.email_or_username.data,
            'password': form.motivo.data,
            'status': 'pending'
        }
        recuperar_acesso_public(form.email_or_username.data, form.motivo.data)
        return render_template('pages/public/conta_recuperada.html', novos=new_user)
    return render_template('pages/public/recuperar_conta.html', form=form)
