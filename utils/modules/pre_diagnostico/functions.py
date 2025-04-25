from config.database import executar_sql
import json

def inserir_info_pessoal(info_pessoa: dict):
    query = f"""
INSERT INTO diagnostico_pessoal (nome, empresa, relacao, email, telefone)
VALUES (
    '{info_pessoa.get('nome')}',
    '{info_pessoa.get('empresa')}',
    '{info_pessoa.get('relacao')}',
    '{info_pessoa.get('email')}',
    '{info_pessoa.get('telefone')}'
)
RETURNING id;
    """
    return executar_sql(query)[0][0]

def inserir_info_final(info_final: dict, diagnostico_id: int):
    query = f"""
INSERT INTO diagnostico_final (diagnostico_id, media_final, proposta)
VALUES (
    {diagnostico_id},
    {info_final.get('media_final')},
    '{info_final.get('proposta')}'
);
    """
    executar_sql(query)

def inserir_info_eixos(info_eixos: dict, media_eixos: dict, diagnostico_id: int):
    try:
        if not media_eixos or not isinstance(media_eixos, dict):
            raise ValueError("media_eixos está vazio ou inválido")

        media_dict = media_eixos.get('media_eixos', {})
        if not isinstance(media_dict, dict):
            raise ValueError("media_eixos['media_eixos'] não é um dicionário")

        for eixo, respostas in info_eixos.items():
            try:
                media = media_dict.get(eixo, 0)
            except:
                try:
                    media = media_eixos.get('media_eixos').get(eixo, 0)
                except:
                    raise ValueError("media_eixos['media_eixos'] não é um dicionário")

            respostas_json = json.dumps(respostas).replace("'", "''")

            query = f"""
                INSERT INTO diagnostico_eixo (diagnostico_id, eixo, media, respostas)
                VALUES (
                    {diagnostico_id},
                    '{eixo}',
                    {media},
                    '{respostas_json}'::jsonb
                );
            """
            executar_sql(query)

    except Exception as e:
        raise ValueError(f"media_eixos['media_eixos'] esta errado: {str(e)}")

def salvar_prediagnostico(dados : dict) -> dict:

    if not dados:
        return {'status': 'error', 'message': 'Dados inválidos'}
    if not isinstance(dados, dict):
        return {'status': 'error', 'message': 'Dados inválidos'}

    info_pessoa : dict = dados.get('info_pessoa')

    info_eixos : dict = dados.get('info_eixos')

    info_eixo1 : dict = info_eixos.get('eixo1')
    info_eixo1 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo1.items() if k != 'media_eixo' or k.startswith('q') }
    info_eixo2 : dict = info_eixos.get('eixo2')
    info_eixo2 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo2.items() if k != 'media_eixo' or k.startswith('q') }
    info_eixo3 : dict = info_eixos.get('eixo3')
    info_eixo3 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo3.items() if k != 'media_eixo' or k.startswith('q') }
    info_eixo4 : dict = info_eixos.get('eixo4')
    info_eixo4 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo4.items() if k != 'media_eixo' or k.startswith('q') }
    info_eixo5 : dict = info_eixos.get('eixo5')
    info_eixo5 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo5.items() if k != 'media_eixo' or k.startswith('q') }
    info_eixo6 : dict = info_eixos.get('eixo6')
    info_eixo6 = { k: float(v) if k.startswith('media') else int(v) for k, v in info_eixo6.items() if k != 'media_eixo' or k.startswith('q') }

    info_final : dict = dados.get('info_final')

    id_diagnostico = inserir_info_pessoal(info_pessoa)
    if not id_diagnostico:
        return {'status': 'error', 'message': 'Erro ao inserir informações pessoais'}
    inserir_info_eixos(info_eixos, info_final, id_diagnostico)
    inserir_info_final(info_final, id_diagnostico)

    print(f"ID do diagnóstico inserido: {id_diagnostico}")
    print(f"Informações pessoais inseridas: {info_pessoa}")
    print(f"Informações dos eixos inseridas: {info_eixos}")
    print(f"Informações finais inseridas: {info_final}")

    return {'status': 'success', 'message': 'Dados salvos com sucesso', 'data': {'id_interno': id_diagnostico, 'info_final': info_final, 'info_eixos': info_eixos, 'info_pessoa': info_pessoa}}
