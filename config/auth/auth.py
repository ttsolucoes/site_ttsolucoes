from functools import wraps
from flask import request, session, jsonify
import time
from app import app
from dotenv import load_dotenv
import os
load_dotenv()

secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key

SESSION_TIMEOUT = 1800

def get_authenticated_user_roles():
    """Recupera as roles do usuário autenticado via sessão."""
    if 'user' not in session:
        return None

    if time.time() - session.get('last_activity', 0) > SESSION_TIMEOUT:
        session.clear()
        return None

    session['last_activity'] = time.time()
    roles = session['user'].get('roles', [])
    return roles

def get_user_roles(username: str) -> list:
    from utils import validar_acesso, ver_usuarios
    """Retorna as roles do usuário."""
    users = ver_usuarios()  # Supondo que ver_usuarios retorna uma lista de usuários
    for user in users:
        if user['username'] == username:
            return [user['cargo']]  # Ou qualquer estrutura que defina as roles
    return []

def get_api_user_roles():
    from utils import validar_acesso, ver_usuarios
    """Recupera as roles do usuário autenticado via API (Authorization Header)."""
    auth = request.authorization
    if not auth:
        return None

    username = auth.username
    password = auth.password

    if not validar_acesso(username, password):
        return None

    return get_user_roles(username)

def required_roles(*required_roles):
    """Decorator que valida se o usuário (via sessão ou API) tem as roles necessárias."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Tenta validar via sessão
            user_roles = get_authenticated_user_roles()

            if not user_roles:
                # Se falhar, tenta via API (Authorization: Basic)
                user_roles = get_api_user_roles()

            if not user_roles:
                return jsonify({"error": "Não autenticado ou sessão expirada"}), 401

            # Verifica permissão
            if not any(role in user_roles for role in required_roles):
                return jsonify({"error": "Permissão insuficiente"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
