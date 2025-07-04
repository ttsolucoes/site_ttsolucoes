from flask import request, session, render_template, g
from werkzeug.exceptions import HTTPException
from app import app
from datetime import datetime
from utils import inserir_log

@app.before_request
def load_lang():
    lang = request.cookies.get('lang')
    if lang not in ['pt', 'en']:
        lang = 'pt'
    g.lang = lang 

@app.context_processor
def inject_now():
    if 'user' not in session:
        user = { 'is_authenticated': False }
    else:
        user = { 'is_authenticated': True }

    return {
        'now': datetime.now(),
        'current_user': user,
        'lang': g.get('lang', 'pt')  # injeta o lang lido do cookie
    }


@app.route('/')
@app.route('/index')
def home():
    if 'user' not in session:
        return render_template('pages/public/home.html')
    else:
        user_data_atual = session['user']['username']
        inserir_log(user_data_atual, 'rota home', "Acessou a página inicial privada")
        return render_template('pages/private/home.html')

@app.route('/saiba_mais')
def saiba_mais():
    return render_template('pages/public/about.html')

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
@app.route('/error')
def handle_error(e=None):
    error_info = {
        'code': e.code if isinstance(e, HTTPException) else 500,
        'name': e.name if isinstance(e, HTTPException) else "Erro Interno",
        'description': e.description if isinstance(e, HTTPException) else "Ocorreu um erro inesperado",
        'path': request.path,
        'method': request.method
    }
    return render_template('pages/public/error.html', error=error_info), error_info['code']
