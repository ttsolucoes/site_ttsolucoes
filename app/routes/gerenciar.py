from app import app
from config import secret_key, required_roles
from flask import render_template, request, session, jsonify
from utils import (
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
from typing import Dict, List, Union
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "techttracksolucoes@gmail.com"
APP_PASSWORD = "nhuh pctp kijc pjew"
app.secret_key = secret_key

def enviar_email(destinatario = "", assunto = "Assunto Padrão", corpo = "<p>Corpo do e-mail padrão</p>"):
    destinatario = destinatario
    assunto = assunto
    corpo = corpo

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, "html"))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
            smtp.send_message(msg)
        return "Email enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {str(e)}"

def get_solicitacoes() -> List[Dict[str, Union[int, str, bool]]]:
    usuarios_public = ver_usuarios_public()
    recuperar_acesso_public = ver_recuperaracesso_public()

    usuarios_public_formatado = [{
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'cargo': 'user',
        'senha': "********",
        'motivo': 'CRIAR NOVO USUÁRIO',
        'origem': 'novos_usuarios'
    } for user in usuarios_public]

    recuperar_acesso_formatado = [{
        'id': user['id'],
        'username': user['username'],
        'email': detalhar_usuario(user['username'])['email'] if detalhar_usuario(user['username']) else None,
        'cargo': detalhar_usuario(user['username'])['cargo'] if detalhar_usuario(user['username']) else None,
        'senha': "********",
        'motivo': detalhar_recuperar_acesso(user['id'])['motivo'] if detalhar_recuperar_acesso(user['id']) else None,
        'origem': 'recuperar_acesso'
    } for user in recuperar_acesso_public]

    return usuarios_public_formatado + recuperar_acesso_formatado

@app.route('/usuarios')
@required_roles('admin')
def gerenciar_usuarios():

    user_atual = session['user']['username']
    inserir_log(user_atual, 'rota usuarios', "Acessou a página de gerenciamento de usuários")

    usuarios_internos = ver_usuarios()
    usuarios_publicos = get_solicitacoes()
    return render_template(
        'pages/private/gerenciar_usuarios.html',
        usuarios_internos=usuarios_internos,
        usuarios_publicos=usuarios_publicos
    )

@app.route('/usuarios/<username>', methods=['PUT'])
@required_roles('admin')
def atualizar_usuario(username):
    try:
        username = str(username).strip()
        data = request.get_json() or {}
        tipo = data.get('tipo', 'privado')

        if tipo != 'privado':
            return jsonify({"success": False, "message": "Tipo inválido para esta rota."}), 400

        if 'email' in data:
            atualizar_email_usuario(username, data.get('email'))

        if 'cargo' in data:
            promover_usuario(username, tipo=tipo, novo_cargo=data.get('cargo'))

        if 'senha_nova' in data:
            atualizar_senha_usuario(username, data.get('senha_nova'))

        inserir_log(session['user']['username'], 'alterar_usuario', f'Atualizou {username} ({tipo})')

        return jsonify({"success": True, "message": f"Usuário {username} atualizado com sucesso."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/usuarios/<username>', methods=['DELETE'])
@required_roles('admin')
def excluir_usuario(username):
    try:
        data = request.get_json() or {}
        tipo = data.get('tipo', 'publicos')
        remover_usuario(username, tipo)
        inserir_log(session['user']['username'], 'remover_usuario', f'Usuário {username} ({tipo}) removido')
        return jsonify({"success": True, "message": f"Usuário {username} removido com sucesso."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/solicitacao/<origem>/<int:id_solicitacao>', methods=['GET'])
@required_roles('admin')
def detalhar_solicitacao(origem, id_solicitacao):
    try:
        if origem == 'novos_usuarios':
            solicitacoes = ver_usuarios_public()
            detalhe = next((user for user in solicitacoes if user['id'] == id_solicitacao), None)
            if detalhe:
                return jsonify({"success": True, "data": detalhe})

        elif origem == 'recuperar_acesso':
            detalhe = detalhar_recuperar_acesso(id_solicitacao)
            if detalhe:
                return jsonify({"success": True, "data": detalhe})

        return jsonify({"success": False, "message": "Solicitação não encontrada."}), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao detalhar: {str(e)}"}), 500

@app.route('/solicitacao/novo_usuario/<int:id_solicitacao>', methods=['PUT'])
@required_roles('admin')
def aprovar_novo_usuario(id_solicitacao):
    try:
        solicitacoes = ver_usuarios_public()
        user = next((u for u in solicitacoes if u['id'] == id_solicitacao), None)

        if not user:
            return jsonify({"success": False, "message": "Solicitação não encontrada."}), 404

        criar_usuario(
            username=user['username'],
            email=user['email'],
            empresa=user['empresa'],
            senha='123456',
            cargo='user'
        )

        assunto = "Cadastro confirmado"
        corpo = f'''

<p>Olá, {user['username']}.</p>

<p>Estamos entrando em contato para informar que sua solicitação foi aprovada e que sua conta está aprovada em nossa plataforma. Seguem credenciais:</p>

<p>- Website: https://site-ttsolucoes.onrender.com/login</p>

<p>- Usuário: {user['username']}</p>

<p>- Senha: 123456</p>

<p>( existem dados sensíveis, nunca compartilhe com quem tu não confia, a TT Soluções está comprometida em construir um mundo digital mais seguro para todos, todas e todxs  )</p>

<p>Caso não tenha solicitado, favor entre em contato conosco:</p>

<p>- Plataforma: https://site-ttsolucoes.onrender.com/recovery </p>

<p>- Whatsapp: https://wa.me/5527997516005 </p>

<p>- Ligação: +55 (27) 9 9751-6005</p>

<p>Ou simplesmente responda esse e-mail.</p>

<p>Estamos gratos pela sua atenção e solicitação. Esperamos que nossa jornada juntos seja positiva e adorável!</p>
-----
</br>
<small>Atenciosamente, equipe <strong>TT SOLUÇÕES</strong></small>
</br>
<small>Transformação técnico-digital para empresas que ainda fazem milagre com planilha.</small>
</br>
<img src="https://lh3.googleusercontent.com/d/1W1llr4gNibdJwsGX11dj2jspIt633yWX" width="96" height="96" alt="Logo TT Soluções">
        '''
        enviar_email(user['email'], assunto, corpo)

        remover_usuario(user['username'], tipo='publicos')
        inserir_log(session['user']['username'], 'aprovar_novo_usuario', f"Novo usuário {user['username']} aprovado.")
        return jsonify({"success": True, "message": f"Usuário {user['username']} criado com sucesso."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao aprovar usuário: {str(e)}"}), 500

@app.route('/usuario_novo', methods=['GET', 'POST'])
@required_roles('admin')
def usuario_novo():
    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            criar_usuario(
                username=data['username'],
                email=data['email'],
                senha=data['senha'],
                cargo=data.get('cargo', 'user'),
                acesso_api=data.get('acesso_api', False)
            )
            inserir_log(
                session['user']['username'],
                'criar_usuario',
                f'Criou usuário {data.get("username")} com cargo {data.get("cargo", "user")}'
            )
            return jsonify({"success": True, "message": "Usuário criado com sucesso."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao criar usuário: {str(e)}"}), 500

    return render_template('pages/private/criar_usuario.html')

@app.route('/recuperar_acesso/<username>', methods=['PUT'])
@required_roles('admin')
def recuperar_acesso(username):
    data = request.get_json() or {}
    tipo = data.get('tipo')
    id_solicitacao = data.get('id_solicitacao')

    try:
        if tipo == 'aprovar_senha':
            nova_senha = data.get('nova_senha')
            sucesso = acao_recuperar_acesso(username, id_solicitacao, tipo, nova_senha=nova_senha)
        else:
            return jsonify({"success": False, "message": "Tipo inválido para recuperação de acesso."}), 400

        if sucesso:
            inserir_log(session['user']['username'], 'recuperar_acesso', f"Acesso de {username} atualizado ({tipo}).")
            return jsonify({"success": True, "message": f"Acesso de {username} atualizado com sucesso."})
        else:
            return jsonify({"success": False, "message": "Não foi possível concluir a ação."}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@app.route('/logs_usuario/<username>')
@required_roles('admin')
def logs_usuario(username):
    from utils import log_usuario
    try:
        logs = log_usuario(username)  # Isso deve retornar uma lista de dicionários
        
        # Formate cada log para uma string legível
        logs_formatados = [
            f"{log['data_hora']} - {log['acao']}: {log.get('detalhes', '')}" 
            for log in logs
        ]
        
        return jsonify({"success": True, "logs": logs_formatados})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar logs: {str(e)}"}), 500
