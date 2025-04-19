from flask import render_template, flash, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from utils import validar_acesso, detalhar_usuario, inserir_log
from app import app

class LoginForm(FlaskForm):
    username = StringField('Usuário', [
        validators.DataRequired(message="Campo obrigatório"),
        validators.Length(min=3, max=25)
    ])
    password = PasswordField('Senha', [
        validators.DataRequired(message="Campo obrigatório")
    ])

@app.route('/login', methods=['GET', 'POST'])
def login():
    import time
    form = LoginForm()
    if form.validate_on_submit():
        valid_acess = validar_acesso(form.username.data, form.password.data)
        if valid_acess:
            user = form.username.data
            session['user'] = {
                'username': user,
                'logged_in': True
            }
            dados = detalhar_usuario(user)
            session['user']['cargo'] = dados['cargo']
            session['user']['roles'] = [dados['cargo']]  # Adiciona roles aqui
            session['last_activity'] = time.time()  # Define a última atividade na sessão

            inserir_log(form.username.data, 'login', 'Login realizado com sucesso')
            return redirect(url_for('home'))  # Redireciona para a página inicial

        flash('Usuário ou senha incorretos', 'error')
    return render_template('pages/public/login.html', form=form)

@app.route('/logout')
def logout():
    usuario = session.get('user', {}).get('username')
    inserir_log(usuario, 'logout', 'Logout realizado com sucesso')
    session.clear()  # Limpa a sessão
    return redirect(url_for('home'))  # Redireciona para a página principal

