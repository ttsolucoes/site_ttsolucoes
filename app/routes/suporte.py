from app import app
from flask import render_template, request, jsonify, session
from config import required_roles, executar_sql
from utils import detalhar_usuario
import datetime

def is_suporte(empresa):
    return str(empresa).lower() == 'tt_solucoes'

@app.route('/api/sessoes', methods=['GET'])
@required_roles('user', 'admin')
def listar_sessoes():
    usuario_id = session['user']['id']
    empresa = session['user']['empresa']
    
    if is_suporte(empresa):
        # Suporte vê todas as conversas
        sessoes = executar_sql("""
            SELECT cs.id, cs.titulo, cs.criado_em, cs.atualizado_em, u.username as usuario_nome
            FROM chat_sessoes cs
            JOIN usuarios u ON cs.usuario_id = u.id
            ORDER BY cs.atualizado_em DESC
        """)
    else:
        # Usuário normal vê apenas suas conversas
        sessoes = executar_sql(f"""
            SELECT id, titulo, criado_em, atualizado_em, NULL as usuario_nome
            FROM chat_sessoes 
            WHERE usuario_id = {usuario_id}
            ORDER BY atualizado_em DESC
        """)
    
    sessoes_formatadas = []
    for sessao in sessoes:
        sessoes_formatadas.append({
            'id': sessao[0],
            'titulo': sessao[1] or f"Chat #{sessao[0]}",
            'criado_em': sessao[2],
            'atualizado_em': sessao[3],
            'usuario_nome': sessao[4]  # Só preenchido para suporte
        })
    
    return jsonify(sessoes_formatadas)

@app.route('/api/sessoes', methods=['POST'])
@required_roles('user', 'admin')
def criar_sessao():
    usuario_id = session['user']['id']
    titulo = request.json.get('titulo', '')
    primeira_msg = request.json.get('primeira_msg', '')
    
    # Cria a sessão - usando NOW() para timestamp do PostgreSQL
    nova_sessao = executar_sql(f"""
        INSERT INTO chat_sessoes (usuario_id, titulo) 
        VALUES ({usuario_id}, '{titulo}') 
        RETURNING id, titulo, criado_em, atualizado_em
    """)
    
    if not nova_sessao or not nova_sessao[0]:
        return jsonify({'error': 'Falha ao criar sessão'}), 500
    
    sessao_id = nova_sessao[0][0]
    
    # Se houver uma primeira mensagem, adiciona
    if primeira_msg:
        autor = session['user']['username']
        # Corrigido: usando NOW() para timestamp e garantindo que a mensagem está escapada
        msg_escaped = primeira_msg.replace("'", "''")
        executar_sql(f"""
            INSERT INTO chat_mensagens (sessao_id, autor, mensagem) 
            VALUES ({sessao_id}, '{autor}', '{msg_escaped}')
        """)
        
        # Atualiza o título se estiver vazio, usando parte da mensagem
        if not titulo:
            titulo_auto = primeira_msg[:30] + ('...' if len(primeira_msg) > 30 else '')
            titulo_escaped = titulo_auto.replace("'", "''")
            executar_sql(f"""
                UPDATE chat_sessoes 
                SET titulo = '{titulo_escaped}', atualizado_em = NOW()
                WHERE id = {sessao_id}
            """)
    
    # Retorna os dados formatados
    return jsonify({
        'id': sessao_id,
        'titulo': titulo or f"Chat #{sessao_id}",
        'criado_em': nova_sessao[0][2].isoformat(),
        'atualizado_em': nova_sessao[0][3].isoformat()
    }), 201

@app.route('/api/sessoes/<int:sessao_id>/mensagens', methods=['GET'])
@required_roles('user', 'admin')
def listar_mensagens(sessao_id):
    usuario_id = session['user']['id']
    empresa = session['user']['empresa']
    
    # Verifica se o usuário tem acesso a esta sessão
    if not is_suporte(empresa):
        acesso = executar_sql(f"""
            SELECT 1 FROM chat_sessoes 
            WHERE id = {sessao_id} AND usuario_id = {usuario_id}
        """)
        if not acesso:
            return jsonify({'error': 'Acesso não autorizado'}), 403
    
    mensagens = executar_sql(f"""
        SELECT id, sessao_id, autor, mensagem, enviada_em 
        FROM chat_mensagens 
        WHERE sessao_id = {sessao_id}
        ORDER BY enviada_em ASC
    """)
    
    mensagens_formatadas = []
    for msg in mensagens:
        mensagens_formatadas.append({
            'id': msg[0],
            'sessao_id': msg[1],
            'autor': msg[2],
            'mensagem': msg[3],
            'enviada_em': msg[4],
            'eh_suporte': is_suporte(msg[2].split('@')[-1]) if '@' in msg[2] else False
        })
    
    return jsonify(mensagens_formatadas)

@app.route('/api/sessoes/<int:sessao_id>/mensagens', methods=['POST'])
@required_roles('user', 'admin')
def enviar_mensagem(sessao_id):
    usuario_id = session['user']['id']
    empresa = session['user']['empresa']
    autor = session['user']['username']
    mensagem = request.json['mensagem']
    
    # Verifica se o usuário tem acesso a esta sessão
    if not is_suporte(empresa):
        acesso = executar_sql(f"""
            SELECT 1 FROM chat_sessoes 
            WHERE id = {sessao_id} AND usuario_id = {usuario_id}
        """)
        if not acesso:
            return jsonify({'error': 'Acesso não autorizado'}), 403
    
    # Escapa a mensagem para evitar problemas com aspas
    msg_escaped = mensagem.replace("'", "''")
    
    # Insere a mensagem
    nova_msg = executar_sql(f"""
        INSERT INTO chat_mensagens (sessao_id, autor, mensagem) 
        VALUES ({sessao_id}, '{autor}', '{msg_escaped}') 
        RETURNING id, sessao_id, autor, mensagem, enviada_em
    """)
    
    # Atualiza a data de atualização da sessão
    executar_sql(f"""
        UPDATE chat_sessoes 
        SET atualizado_em = NOW() 
        WHERE id = {sessao_id}
    """)
    
    if nova_msg and nova_msg[0]:
        return jsonify({
            'id': nova_msg[0][0],
            'sessao_id': nova_msg[0][1],
            'autor': nova_msg[0][2],
            'mensagem': nova_msg[0][3],
            'enviada_em': nova_msg[0][4].isoformat(),
            'eh_suporte': is_suporte(empresa)
        }), 201
    else:
        return jsonify({'error': 'Falha ao enviar mensagem'}), 500

@app.route('/suporte')
@required_roles('user', 'admin')
def suporte():
    user_logado = session['user']['username']
    users = detalhar_usuario(user_logado)
    empresa = users['empresa']
    return render_template('pages/private/suporte.html', 
                         users=users, 
                         empresa=empresa,
                         eh_suporte=is_suporte(empresa))