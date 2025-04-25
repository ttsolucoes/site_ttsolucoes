from config.database import executar_sql

def salvar_prediagnostico(dados : dict) -> dict:

    if not dados:
        return {'status': 'error', 'message': 'Dados inválidos'}
    if not isinstance(dados, dict):
        return {'status': 'error', 'message': 'Dados inválidos'}

    info_pessoa = dados.get('info_pessoa')

    info_eixos : dict = dados.get('info_eixos')

    info_eixo1 = info_eixos.get('info_eixo1')
    info_eixo2 = info_eixos.get('info_eixo2')
    info_eixo3 = info_eixos.get('info_eixo3')
    info_eixo4 = info_eixos.get('info_eixo4')
    info_eixo5 = info_eixos.get('info_eixo5')
    info_eixo6 = info_eixos.get('info_eixo6')

    info_final = dados.get('info_final')
