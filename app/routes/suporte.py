from app import app
from flask import render_template, request, jsonify, session, redirect
from config import required_roles, executar_sql
from utils import detalhar_usuario
import datetime

def calcular_metricas(sessao_id):
    # Obtém os tempos de início e fim do incidente
    dados_sessao = executar_sql(f"""
        SELECT MIN(cm.enviada_em), MAX(cm.enviada_em)
        FROM chat_mensagens cm
        WHERE cm.sessao_id = {sessao_id}
    """)
    
    if not dados_sessao or not dados_sessao[0]:
        return
    
    inicio_incidente, fim_incidente = dados_sessao[0]
    
    # Calcula tempo de resolução (MTTR)
    tempo_resolucao = fim_incidente - inicio_incidente
    
    # Calcula tempo desde o último incidente (MTBF)
    ultimo_incidente = executar_sql(f"""
        SELECT MAX(sm.incidente_resolvido_em)
        FROM suporte_metricas sm
        JOIN chat_sessoes cs ON sm.sessao_id = cs.id
        WHERE cs.usuario_id = (
            SELECT usuario_id FROM chat_sessoes WHERE id = {sessao_id}
        )
        AND sm.incidente_resolvido_em IS NOT NULL
        AND sm.sessao_id != {sessao_id}
    """)
    
    tempo_entre_falhas = None
    if ultimo_incidente and ultimo_incidente[0] and ultimo_incidente[0][0]:
        tempo_entre_falhas = inicio_incidente - ultimo_incidente[0][0]
    
    # Verifica se já existe registro para esta sessão
    existe_registro = executar_sql(f"""
        SELECT 1 FROM suporte_metricas WHERE sessao_id = {sessao_id}
    """)
    
    if existe_registro and existe_registro[0]:
        # Atualiza registro existente
        executar_sql(f"""
            UPDATE suporte_metricas SET
                tempo_resolucao = '{tempo_resolucao}',
                tempo_entre_falhas = {f"'{tempo_entre_falhas}'" if tempo_entre_falhas else 'NULL'},
                incidente_resolvido_em = '{fim_incidente}'
            WHERE sessao_id = {sessao_id}
        """)
    else:
        # Insere novo registro
        executar_sql(f"""
            INSERT INTO suporte_metricas (
                sessao_id, 
                tempo_resolucao, 
                tempo_entre_falhas,
                incidente_iniciado_em,
                incidente_resolvido_em
            )
            VALUES (
                {sessao_id}, 
                '{tempo_resolucao}', 
                {f"'{tempo_entre_falhas}'" if tempo_entre_falhas else 'NULL'},
                '{inicio_incidente}',
                '{fim_incidente}'
            )
        """)

def is_suporte(empresa):
    return str(empresa).lower() == 'tt_solucoes'

@app.route('/api/metricas/mttr', methods=['GET'])
@required_roles('user', 'admin')  # Apenas administradores/suporte podem acessar
def calcular_mttr():
    empresa = session['user']['empresa']
    periodo = int(request.args.get('periodo', 30))
    agente_id = request.args.get('agente', 'todos')

    parametros = []
    condicoes = ["sm.tempo_resolucao IS NOT NULL"]
    joins = ["JOIN chat_sessoes cs ON sm.sessao_id = cs.id"]

    # Filtro por empresa (se não for suporte)
    if not is_suporte(empresa):
        joins.append("JOIN usuarios u ON cs.usuario_id = u.id")
        condicoes.append("u.empresa = %s")
        parametros.append(empresa)

    # Filtro por agente (se diferente de 'todos')
    if agente_id != 'todos':
        condicoes.append("cs.usuario_id = %s")
        parametros.append(agente_id)

    # Filtro por intervalo de tempo
    condicoes.append("sm.incidente_resolvido_em >= NOW() - INTERVAL %s")
    parametros.append(f"{periodo} days")

    sql = f"""
        SELECT 
            ROUND(AVG(EXTRACT(EPOCH FROM sm.tempo_resolucao)/60), 1) AS mttr_minutos,
            COUNT(sm.sessao_id) AS total_incidentes,
            DATE_TRUNC('day', sm.incidente_resolvido_em) AS dia
        FROM suporte_metricas sm
        {' '.join(joins)}
        WHERE {' AND '.join(condicoes)}
        GROUP BY dia
        ORDER BY dia
    """

    resultados = executar_sql(sql, tuple(parametros))

    dados_formatados = [
        {
            'dia': row[2].strftime('%Y-%m-%d'),
            'mttr_minutos': float(row[0]),
            'total_incidentes': row[1]
        }
        for row in resultados
    ]

    return jsonify(dados_formatados)

@app.route('/api/metricas/mtbf', methods=['GET'])
@required_roles('user', 'admin')  # Apenas administradores/suporte podem acessar
def calcular_mtbf():
    empresa = session['user']['empresa']
    parametros = []
    joins = ["JOIN chat_sessoes cs ON sm.sessao_id = cs.id"]
    condicoes = ["sm.tempo_entre_falhas IS NOT NULL"]

    if not is_suporte(empresa):
        joins.append("JOIN usuarios u ON cs.usuario_id = u.id")
        condicoes.append("u.empresa = %s")
        parametros.append(empresa)

    sql = f"""
        SELECT 
            AVG(EXTRACT(EPOCH FROM sm.tempo_entre_falhas)/3600) AS mtbf_horas,
            DATE_TRUNC('week', sm.incidente_resolvido_em) AS semana
        FROM suporte_metricas sm
        {' '.join(joins)}
        WHERE {' AND '.join(condicoes)}
        GROUP BY semana
        ORDER BY semana
    """

    resultados = executar_sql(sql, tuple(parametros))

    dados_formatados = [
        {
            'semana': row[1].strftime('%Y-%m-%d'),
            'mtbf_horas': float(row[0])
        }
        for row in resultados
    ]

    return jsonify(dados_formatados)

@app.route('/api/sessoes', methods=['GET'])
@required_roles('user', 'admin')
def listar_sessoes(sessao_id=0):
    usuario_id = session['user']['id']
    empresa = session['user']['empresa']

    if is_suporte(empresa):
        sql = """
            SELECT cs.id, cs.titulo, cs.criado_em, cs.atualizado_em, u.username
            FROM chat_sessoes cs
            JOIN usuarios u ON cs.usuario_id = u.id
            ORDER BY cs.atualizado_em DESC
        """
        params = None
    else:
        sql = """
            SELECT cs.id, cs.titulo, cs.criado_em, cs.atualizado_em, NULL
            FROM chat_sessoes cs
            WHERE cs.usuario_id = %s
            ORDER BY cs.atualizado_em DESC
        """
        params = (usuario_id,)

    sessoes = executar_sql(sql, params) or []
    resultado = [{
        'id': s[0],
        'titulo': s[1] or f"Chat #{s[0]}",
        'criado_em': s[2].isoformat(),
        'atualizado_em': s[3].isoformat(),
        'usuario_nome': s[4]
    } for s in sessoes]

    return jsonify(resultado)

@app.route('/api/sessoes', methods=['POST'])
@required_roles('user', 'admin')
def criar_sessao():
    usuario_id = session['user']['id']
    titulo = request.json.get('titulo', '').strip()
    primeira_msg = request.json.get('primeira_msg', '').strip()

    sql = """
        INSERT INTO chat_sessoes (usuario_id, titulo)
        VALUES (%s, %s)
        RETURNING id, titulo, criado_em, atualizado_em
    """
    sessao = executar_sql(sql, (usuario_id, titulo)) or []
    if not sessao:
        return jsonify({'error': 'Falha ao criar sessão'}), 500

    sessao_id, tit, criado, atualizado = sessao[0]
    if primeira_msg:
        autor = session['user']['username']
        msg_sql = """
            INSERT INTO chat_mensagens (sessao_id, autor, mensagem)
            VALUES (%s, %s, %s)
        """
        executar_sql(msg_sql, (sessao_id, autor, primeira_msg))

        if not titulo:
            novo_titulo = primeira_msg[:30] + ('...' if len(primeira_msg) > 30 else '')
            atualizar_sql = """
                UPDATE chat_sessoes
                SET titulo = %s, atualizado_em = NOW()
                WHERE id = %s
            """
            executar_sql(atualizar_sql, (novo_titulo, sessao_id))
            tit = novo_titulo

    response = {
        'id': sessao_id,
        'titulo': tit or f"Chat #{sessao_id}",
        'criado_em': criado.isoformat(),
        'atualizado_em': atualizado.isoformat()
    }
    return jsonify(response), 201

@app.route('/api/sessoes/<int:sessao_id>', methods=['GET'])
@required_roles('user', 'admin')
def obter_sessao(sessao_id):
    usuario_id = session['user']['id']
    empresa = session['user']['empresa']
    eh_suporte = is_suporte(empresa)

    # Verifica se o usuário tem acesso a esta sessão
    if not eh_suporte:
        acesso = executar_sql(f"""
            SELECT 1 FROM chat_sessoes 
            WHERE id = {sessao_id} AND usuario_id = {usuario_id}
        """)
        if not acesso:
            return jsonify({'error': 'Acesso não autorizado'}), 403

    # Obtém os dados básicos da sessão
    sessao_sql = f"""
        SELECT 
            cs.id, 
            cs.titulo, 
            cs.criado_em, 
            cs.atualizado_em, 
            cs.status,
            cs.tags,
            u.username AS usuario_nome,
            u.empresa AS usuario_empresa
        FROM chat_sessoes cs
        JOIN usuarios u ON cs.usuario_id = u.id
        WHERE cs.id = {sessao_id}
    """
    sessao_data = executar_sql(sessao_sql)
    
    if not sessao_data:
        return jsonify({'error': 'Sessão não encontrada'}), 404

    sessao_row = sessao_data[0]
    
    # Obtém as mensagens da sessão
    mensagens_sql = f"""
        SELECT 
            id, 
            autor, 
            mensagem, 
            enviada_em
        FROM chat_mensagens
        WHERE sessao_id = {sessao_id}
        ORDER BY enviada_em ASC
    """
    mensagens_data = executar_sql(mensagens_sql) or []
    
    # Formata as mensagens
    mensagens = []
    for msg in mensagens_data:
        msg_autor = msg[1]
        mensagens.append({
            'id': msg[0],
            'autor': msg_autor,
            'mensagem': msg[2],
            'enviada_em': msg[3].isoformat(),
            'eh_suporte': is_suporte(msg_autor.split('@')[-1]) if '@' in msg_autor else False
        })

    # Formata a resposta
    resposta = {
        'id': sessao_row[0],
        'titulo': sessao_row[1] or f"Chat #{sessao_row[0]}",
        'criado_em': sessao_row[2].isoformat(),
        'atualizado_em': sessao_row[3].isoformat(),
        'status': sessao_row[4] or 'ABERTO',
        'tags': sessao_row[5] or [],
        'usuario_nome': sessao_row[6],
        'usuario_empresa': sessao_row[7],
        'mensagens': mensagens,
        'total_mensagens': len(mensagens)
    }

    # Adiciona métricas se for suporte
    if eh_suporte:
        metricas_sql = f"""
            SELECT 
                tempo_resolucao,
                tempo_entre_falhas,
                incidente_iniciado_em,
                incidente_reconhecido_em,
                incidente_resolvido_em
            FROM suporte_metricas
            WHERE sessao_id = {sessao_id}
        """
        metricas_data = executar_sql(metricas_sql)
        
        if metricas_data and metricas_data[0]:
            metricas_row = metricas_data[0]
            resposta['metricas'] = {
                'tempo_resolucao': str(metricas_row[0]) if metricas_row[0] else None,
                'tempo_entre_falhas': str(metricas_row[1]) if metricas_row[1] else None,
                'incidente_iniciado_em': metricas_row[2].isoformat() if metricas_row[2] else None,
                'incidente_reconhecido_em': metricas_row[3].isoformat() if metricas_row[3] else None,
                'incidente_resolvido_em': metricas_row[4].isoformat() if metricas_row[4] else None
            }

    return jsonify(resposta)

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

@app.route('/api/sessoes/<int:sessao_id>/status', methods=['POST'])
@required_roles('user', 'admin')
def atualizar_status_sessao(sessao_id):
    novo_status = request.json.get('status')
    if novo_status not in ['ABERTO', 'FINALIZADO', 'REABERTO']:
        return jsonify({'error': 'Status inválido'}), 400

    update_sql = "UPDATE chat_sessoes SET status = %s, atualizado_em = NOW() WHERE id = %s"
    executar_sql(update_sql, (novo_status, sessao_id))

    if novo_status == 'FINALIZADO':
        try:
            calcular_metricas(sessao_id)
        except Exception as e:
            app.logger.error(f"Erro ao calcular métricas: {e}")

    return jsonify({'status': novo_status})

@app.route('/api/sessoes/<int:sessao_id>/tags', methods=['POST', 'DELETE'])
@required_roles('admin')
def gerenciar_tags(sessao_id):
    tag = request.json.get('tag', '').strip()
    if not tag:
        return jsonify({'error': 'Tag inválida'}), 400

    if request.method == 'POST':
        sql = "UPDATE chat_sessoes SET tags = array_append(tags, %s) WHERE id = %s"
    else:
        sql = "UPDATE chat_sessoes SET tags = array_remove(tags, %s) WHERE id = %s"

    executar_sql(sql, (tag, sessao_id))
    return jsonify({'success': True})

@app.route('/api/sessoes/<int:sessao_id>/reconhecimento', methods=['POST'])
@required_roles('admin')
def registrar_reconhecimento(sessao_id):
    check_sql = "SELECT 1 FROM suporte_metricas WHERE sessao_id = %s"
    existe = bool(executar_sql(check_sql, (sessao_id,)))

    if not existe:
        sql = """
            INSERT INTO suporte_metricas (sessao_id, incidente_reconhecido_em)
            VALUES (%s, NOW())
        """
        executar_sql(sql, (sessao_id,))
    else:
        sql = """
            UPDATE suporte_metricas
            SET incidente_reconhecido_em = COALESCE(incidente_reconhecido_em, NOW())
            WHERE sessao_id = %s
        """
        executar_sql(sql, (sessao_id,))

    return jsonify({'success': True})

@app.route('/api/equipes')
@required_roles('user', 'admin')
def listar_equipes():
    user_logado = session['user']['username']
    usuario = detalhar_usuario(user_logado)
    empresa = usuario['empresa']

    projetos_por_empresa = {
        "tt_solucoes": ["ExtractRFB", "URA_GOOGLE", "GJ_GUADALUPE"],
        "Invertus": ["ExtractRFB", "URA_GOOGLE"],
        "gj_guadalupe": ["GJ_GUADALUPE"]
    }

    equipes = projetos_por_empresa.get(empresa, [])
    return jsonify(equipes)

@app.route('/projetos_gerencia')
@required_roles('user', 'admin')
def projetos_gerencia():
    user_logado = session['user']['username']
    users = detalhar_usuario(user_logado)
    return render_template('pages/private/projetos_gerencia.html', 
                         users=users,
                         empresa=users['empresa'],
                         eh_suporte=is_suporte(users['empresa']))

@app.route('/suporte_gerencia')
@required_roles('admin')
def suporte_gerencia():
    if not is_suporte(session['user']['empresa']):
        return redirect('/suporte')
    
    return render_template('pages/private/suporte_gerencia.html', 
                         users=session['user'],
                         eh_suporte=True)

@app.route('/suporte')
@required_roles('user', 'admin')
def suporte():
    user_logado = session['user']['username']
    users = detalhar_usuario(user_logado)
    empresa = users['empresa']
    print(is_suporte(empresa))
    return render_template('pages/private/suporte.html', 
                         users=users, 
                         empresa=empresa,
                         eh_suporte=is_suporte(empresa))
