from flask import Flask

app = Flask(__name__)

from .routes import geral
from .routes import contas
from .routes import acessos
from .routes import perfil
from .routes import gerenciar
from api.routes.principal import api_conexao_bp

app.register_blueprint(api_conexao_bp, url_prefix='/api')


__all__ = [
    'geral',
    'contas',
    'acessos',
    'perfil',
    'gerenciar'
]