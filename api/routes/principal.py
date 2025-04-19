from flask import Blueprint, jsonify, request
from config.auth.auth import required_roles
from utils import (
    remover_usuario,
    log_usuario,
    ver_usuarios,
    ver_usuarios_public,
    promover_usuario,
    remover_usuario,
    inserir_log,
    criar_usuario,
    aprovar_usuario_publico,
    ver_recuperaracesso_public,
    detalhar_recuperar_acesso,
    detalhar_usuario,
    acao_recuperar_acesso,
    atualizar_senha_usuario,
    atualizar_email_usuario
)

api_conexao_bp = Blueprint('api_conexao', __name__)

@api_conexao_bp.route('/verificar_conexao', methods=['GET'])
@required_roles('admin', 'api_user')
def verificar_conexao():
    return jsonify({"status": "Conexão bem-sucedida", "user": "Autenticado e autorizado"}), 200

@api_conexao_bp.route('/usuarios_publicos_criar', methods=['POST'])
@required_roles('admin')
def api_criar_usuario_public():
    dados = request.get_json()
    
    # Validações explícitas
    username = dados.get('username')
    senha = dados.get('senha')
    email = dados.get('email')
    
    if not username or not senha or not email:
        return jsonify({
            "status": "erro", 
            "message": "Campos obrigatórios faltando", 
            "details": "Os campos username, senha e email são obrigatórios"
        }), 400

    try:
        if criar_usuario(username, senha, email):
            return jsonify({
                "status": "sucesso", 
                "message": "Usuário público criado com sucesso."
            }), 201
        else:
            return jsonify({
                "status": "erro", 
                "message": "Erro ao criar usuário público", 
                "details": "Verifique os dados fornecidos"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro inesperado ao criar usuário", 
            "details": str(e)
        }), 500

@api_conexao_bp.route('/usuarios_publicos_ver', methods=['GET'])
@required_roles('admin')
def api_ver_usuarios_publicos():
    try:
        resultado = ver_usuarios_public()
        return jsonify({
            "status": "sucesso", 
            "message": "Usuários públicos listados com sucesso.", 
            "data": resultado
        }), 200
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro ao listar usuários públicos", 
            "details": str(e)
        }), 500

@api_conexao_bp.route('/usuarios/<username>', methods=['PUT'])
@required_roles('admin')
def api_atualizar_usuario(username):
    dados = request.get_json()

    try:
        tipo = dados.get('tipo', 'privado')
        if tipo != 'privado':
            return jsonify({
                "status": "erro", 
                "message": "Tipo inválido para esta rota", 
                "details": "O tipo 'privado' é o único permitido"
            }), 400
        
        # Atualizar email
        if 'email' in dados:
            atualizar_email_usuario(username, dados.get('email'))

        # Atualizar cargo
        if 'cargo' in dados:
            promover_usuario(username, tipo=tipo, novo_cargo=dados.get('cargo'))

        # Atualizar senha
        if 'senha_nova' in dados:
            atualizar_senha_usuario(username, dados.get('senha_nova'))

        return jsonify({
            "status": "sucesso", 
            "message": f"Usuário {username} atualizado com sucesso"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro ao atualizar o usuário", 
            "details": str(e)
        }), 500

@api_conexao_bp.route('/usuarios/<username>/promover', methods=['PUT'])
@required_roles('admin')
def api_promover_usuario(username):
    dados = request.get_json()
    
    tipo = dados.get('tipo')
    cargo = dados.get('cargo')

    if not tipo or not cargo:
        return jsonify({
            "status": "erro", 
            "message": "Campos obrigatórios faltando", 
            "details": "Os campos tipo e cargo são obrigatórios"
        }), 400

    try:
        if promover_usuario(username, tipo=tipo, novo_cargo=cargo):
            return jsonify({
                "status": "sucesso", 
                "message": f"Usuário {username} promovido para o cargo {cargo} com sucesso."
            }), 200
        else:
            return jsonify({
                "status": "erro", 
                "message": "Erro ao promover usuário", 
                "details": "Verifique os dados fornecidos"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro inesperado ao promover usuário", 
            "details": str(e)
        }), 500

@api_conexao_bp.route('/usuarios/<username>', methods=['DELETE'])
@required_roles('admin')
def api_deletar_usuario(username):
    try:
        if remover_usuario(username, 'internos'):
            return jsonify({
                "status": "sucesso", 
                "message": f"Usuário {username} deletado com sucesso."
            }), 200
        else:
            return jsonify({
                "status": "erro", 
                "message": "Erro ao deletar usuário", 
                "details": "Verifique o nome de usuário fornecido"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro inesperado ao deletar usuário", 
            "details": str(e)
        }), 500

@api_conexao_bp.route('/usuarios_recuperacao/<username>', methods=['PUT'])
@required_roles('admin')
def api_aprovar_recuperacao_acesso(username):
    from utils import acao_recuperar_acesso
    try:
        if acao_recuperar_acesso(username):
            return jsonify({
                "status": "sucesso", 
                "message": f"Solicitação de recuperação de acesso para o usuário {username} aprovada."
            }), 200
        else:
            return jsonify({
                "status": "erro", 
                "message": "Erro ao aprovar recuperação de acesso", 
                "details": "Verifique o nome de usuário fornecido"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "erro", 
            "message": "Erro inesperado ao aprovar recuperação de acesso", 
            "details": str(e)
        }), 500
