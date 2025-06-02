from flask import Flask

app = Flask(__name__)

from .routes import geral
from .routes import contas
from .routes import acessos
from .routes import perfil
from .routes import gerenciar
from .routes import pre_diagnostico
from .routes import clientes
from .routes import suporte
from api.routes.principal import api_conexao_bp

app.register_blueprint(api_conexao_bp, url_prefix='/api')

from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('nova_mensagem')
def handle_nova_mensagem(data):
    emit('atualizar_chat', data, broadcast=True)

__all__ = [
    'geral',
    'contas',
    'acessos',
    'perfil',
    'gerenciar',
    'pre_diagnostico',
    'clientes',
    'suporte'
]