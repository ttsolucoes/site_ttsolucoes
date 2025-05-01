from app import app
from config import secret_key
from flask import render_template, request, session, jsonify
from config import secret_key, required_roles
from collections import defaultdict
import json

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
    return render_template('pages/public/pre_diagnostico.html')

@app.route('/detalhes_pre_diagnostico')
def detalhes_pre_diagnostico():
    return render_template('pages/public/detalhes_prediagnostico.html')

@app.route('/pre_diagnostico_detalhes')
@required_roles('admin')
def pre_diagnostico_detalhes():
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
    if not dados:
        return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400
    elif not isinstance(dados, dict):
        return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400

    dados_organizados = {
        'info_pessoa': {
            'nome': dados['step-1']['nome'],
            'empresa': dados['step-1']['empresa'],
            'relacao': dados['step-1']['cargo'],
            'email': dados['step-1']['email'],
            'telefone': dados['step-1']['telefone'],
        },
        'info_eixo1': dados['step-2'],
        'info_eixo2': dados['step-3'],
        'info_eixo3': dados['step-4'],
        'info_eixo4': dados['step-5'],
        'info_eixo5': dados['step-6'],
        'info_eixo6': dados['step-7'],
        'info_eixos': {
            'eixo1': dados['step-2'],
            'eixo2': dados['step-3'],
            'eixo3': dados['step-4'],
            'eixo4': dados['step-5'],
            'eixo5': dados['step-6'],
            'eixo6': dados['step-7'],
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

    faixa_proposta = {
    (0, 4): 'Transformação completa',
    (5, 6): 'Transformação ágil',
    (7, 8): 'Início Ágil',
    (9, 10): 'Planos sob-demanda'
    }

    media_eixo = {}
    for eixo, respostas in dados_organizados['info_eixos'].items():
        soma = sum(int(valor) for valor in respostas.values())
        media = soma * pesos[eixo]
        dados_organizados['info_eixos'][eixo]['media_eixo'] = media
        media_eixo[eixo] = media



    for faixa, proposta in faixa_proposta.items():
        if faixa[0] <= (sum(media_eixo.values()) / 6) <= faixa[1]:
            dados_organizados['info_final'] = {
                'media_final': sum(media_eixo.values()) / 6,
                'media_eixos': media_eixo,
                'proposta': proposta
            }
            break

    if 'info_final' not in dados_organizados:
        dados_organizados['info_final'] = {
            'media_final': sum(media_eixo.values()) / 6,
            'media_eixos': media_eixo,
            'proposta': 'Planos sob-demanda'
        }

    response = salvar_prediagnostico(dados_organizados)

    return response, 200
