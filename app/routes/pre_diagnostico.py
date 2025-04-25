from app import app
from config import secret_key
from flask import render_template, request, session, jsonify

app.secret_key = secret_key

@app.route('/pre_diagnostico')
def pre_diagnostico():
    return render_template('pages/public/pre_diagnostico.html')

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
