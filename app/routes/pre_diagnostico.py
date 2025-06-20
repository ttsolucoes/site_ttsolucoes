from app import app
from config import secret_key
from flask import render_template, request, session, jsonify
from config import secret_key, required_roles
from collections import defaultdict
import json
from utils import inserir_log

def _consultar():

    from config import executar_sql
    query_eixos = "SELECT * FROM diagnostico_eixo"
    dados_eixos = executar_sql(query_eixos)

    eixos_por_diagnostico = defaultdict(list)

    for linha in dados_eixos:
        diagnostico_id = linha[1]
        eixo = linha[2]
        media = round(linha[3], 2)
        respostas = linha[4]  # Já é um dict, não é necessário fazer json.loads

        respostas_convertidas = {k: int(v) for k, v in respostas.items() if k.startswith("q")}
        eixos_por_diagnostico[diagnostico_id].append({
            'id': diagnostico_id,
            'eixo': eixo,
            'media': media,
            'respostas': respostas_convertidas
        })
    return eixos_por_diagnostico

app.secret_key = secret_key

@app.route('/pre_diagnostico')
def pre_diagnostico():

    if 'user' in session:
        user_data_atual = session['user']['username']
        inserir_log(user_data_atual, 'rota pre_diagnostico', "Acessou a página de pré-diagnóstico")
        return render_template('pages/public/pre_diagnostico.html')

    return render_template('pages/public/pre_diagnostico.html')

@app.route('/detalhes_pre_diagnostico')
def detalhes_pre_diagnostico():

    if 'user' in session:
        user_data_atual = session['user']['username']
        inserir_log(user_data_atual, 'rota detalhes_pre_diagnostico', "Acessou a página de detalhes do pré-diagnóstico")
        return render_template('pages/public/detalhes_prediagnostico.html')

    return render_template('pages/public/detalhes_prediagnostico.html')

@app.route('/pre_diagnostico_detalhes')
@required_roles('admin')
def pre_diagnostico_detalhes():

    user_data_atual = session['user']['username']
    inserir_log(user_data_atual, 'rota pre_diagnostico_detalhes', "Acessou a página de detalhes do pré-diagnóstico")
    
    from config import executar_sql
    query = """
SELECT d.id, d.nome, d.empresa, d.relacao, d.email, d.telefone, d.data,f.media_final, f.proposta
FROM diagnostico_pessoal d
JOIN diagnostico_final f ON d.id = f.diagnostico_id
ORDER BY d.data DESC;
    """
    dados = executar_sql(query)

    columns = ['ID', 'Nome', 'Empresa', 'Relação', 'Email', 'Telefone', 'Data', 'Média Final', 'Proposta']
    data = []
    for d in dados:
        row = [
            d[0], d[1], d[2], d[3], d[4], d[5],
            str(d[6])[:19],
            round(d[7], 2),
            d[8]
        ]
        data.append(row)

    detalhes = _consultar()

    return render_template(
        "pages/private/pre_diagnostico_detalhes.html",
        columns=columns,
        data=data,
        eixos_por_diagnostico=detalhes,
        pagination=None
    )


@app.route('/pre_diagnostico_salvar', methods=['POST'])
def pre_diagnostico_salvar():
    from utils import salvar_prediagnostico
    dados = request.get_json()

    if not dados or not isinstance(dados, dict):
        return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400

    # Organiza os dados recebidos
    dados_organizados = {
        'info_pessoa': {
            'nome': dados['step-1']['nome'],
            'empresa': dados['step-1']['empresa'],
            'relacao': dados['step-1']['cargo'],
            'email': dados['step-1']['email'],
            'telefone': dados['step-1']['telefone'],
        },
        'info_eixos': {
            f'eixo{i}': dados[f'step-{i+1}']
            for i in range(1, 7)
        }
    }

    pesos = {
        'eixo1': 0.15,
        'eixo2': 0.20,
        'eixo3': 0.20,
        'eixo4': 0.15,
        'eixo5': 0.15,
        'eixo6': 0.15
    }

    # Calcular a média ponderada dos eixos (0 a 10)
    media_eixo = {}
    for eixo, respostas in dados_organizados['info_eixos'].items():
        respostas_int = [int(v) for v in respostas.values() if v.isdigit()]
        media = (sum(respostas_int) / len(respostas_int)) * pesos[eixo]
        media_eixo[eixo] = round(media, 2)
        respostas['media_eixo'] = media  # armazena para persistência

    media_final = round(sum(media_eixo.values()), 2)

    faixa_proposta = [
        ((0, 4.5), 'Transformação completa'),
        ((4.5, 6.5), 'Transformação ágil'),
        ((6.5, 8.5), 'Início Ágil'),
        ((8.5, 10.5), 'Planos sob-demanda')
    ]

    proposta = 'Indefinido'
    for faixa, label in faixa_proposta:
        if faixa[0] <= media_final <= faixa[1]:
            proposta = label
            break

    dados_organizados['info_final'] = {
        'media_final': media_final,
        'media_eixos': media_eixo,
        'proposta': proposta
    }

    response = salvar_prediagnostico(dados_organizados)
    return jsonify(response), 200

