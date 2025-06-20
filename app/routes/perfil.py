from flask import render_template, session
from app import app
from utils import detalhar_usuario, log_usuario, inserir_log

@app.route('/perfil')
def perfil():

    if 'user' not in session:
        return render_template('pages/public/home.html')

    username = session['user']['username']
    inserir_log(username, 'rota perfil', "Acessou a página de perfil")

    user_data = detalhar_usuario(username)
    user_logs = log_usuario(username)
    
    return render_template('pages/private/perfil.html', user=user_data, logs=user_logs)
