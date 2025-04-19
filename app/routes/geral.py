from flask import request, session, render_template
from werkzeug.exceptions import HTTPException
from app import app
from datetime import datetime

@app.context_processor
def inject_now():

    if 'user' not in session:
        user = { 'is_authenticated': False }
    else:
        user = { 'is_authenticated': True }

    return {'now': datetime.now(), 'current_user': user}

@app.route('/')
@app.route('/index')
def home():
    if 'user' not in session:
        return render_template('pages/public/home.html')
    else:
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
