from flask import render_template, flash, session
from app import app
from config import secret_key
from utils import detalhar_usuario, log_usuario

app.secret_key = secret_key

@app.route('/perfil')
def perfil():

    if 'user' not in session:
        return render_template('pages/public/home.html')
    
    username = session['user']['username']
    user_data = detalhar_usuario(username)
    user_logs = log_usuario(username)
    
    return render_template('pages/private/perfil.html', user=user_data, logs=user_logs)
