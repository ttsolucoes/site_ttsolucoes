from app import app
from flask import render_template, request, jsonify, session
from config import required_roles
from utils import detalhar_usuario

@app.route('/suporte')
@required_roles('user', 'admin')
def suporte():
    user_logado = session['user']['username']
    users = detalhar_usuario(user_logado)
    empresa = users['empresa']
    return render_template('pages/private/suporte.html', users=users, empresa=empresa)
