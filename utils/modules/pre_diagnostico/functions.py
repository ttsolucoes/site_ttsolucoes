from config.database import executar_sql
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "techttracksolucoes@gmail.com"
APP_PASSWORD = "nhuh pctp kijc pjew"

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
    else:
        email = info_pessoa.get('email')
        assunto = "Pre-diagnóstico recebido"
        corpo = f'''
<p>Olá, {info_pessoa.get('nome')}.</p>

<p>Seu pré-diagnóstico foi recebido com sucesso.</p>

<p>Estamos analisando suas respostas e entraremos em contato em breve.</p>

<p>Caso tenha dúvidas, entre em contato conosco:</p>

<p>- Plataforma: https://site-ttsolucoes.onrender.com/recovery </p>

<p>- Whatsapp: https://wa.me/5527997516005</p>

<p>- Ligação: +55 (27) 9 9751-6005</p>
-----
</br>
<small>Atenciosamente, equipe <strong>TT SOLUÇÕES</strong></small>
</br>
<small>Transformação técnico-digital para empresas que ainda fazem milagre com planilha.</small>
</br>
<img src="https://lh3.googleusercontent.com/d/1W1llr4gNibdJwsGX11dj2jspIt633yWX" width="96" height="96" alt="Logo TT Soluções">

        '''
        try:
            enviar_email(email, assunto, corpo)
        except:
            pass
    inserir_info_eixos(info_eixos, info_final, id_diagnostico)
    inserir_info_final(info_final, id_diagnostico)

    print(f"ID do diagnóstico inserido: {id_diagnostico}")
    print(f"Informações pessoais inseridas: {info_pessoa}")
    print(f"Informações dos eixos inseridas: {info_eixos}")
    print(f"Informações finais inseridas: {info_final}")

    return {'status': 'success', 'message': 'Dados salvos com sucesso', 'data': {'id_interno': id_diagnostico, 'info_final': info_final, 'info_eixos': info_eixos, 'info_pessoa': info_pessoa}}

def consultar_prediagnosticos():
    query_pessoa = "SELECT * FROM diagnostico_pessoal;"
    query_final = "SELECT * FROM diagnostico_final;"
    query_eixo = "SELECT * FROM diagnostico_eixo;"

    dados_pessoais = executar_sql(query_pessoa)
    dados_finais = executar_sql(query_final)
    dados_eixos = executar_sql(query_eixo)

    # Transformar dados em dicionários mais legíveis
    diagnosticos = []
    for pessoa in dados_pessoais:
        diagnostico_id = pessoa[0]
        dados = {
            'id': diagnostico_id,
            'nome': pessoa[1],
            'empresa': pessoa[2],
            'relacao': pessoa[3],
            'email': pessoa[4],
            'telefone': pessoa[5],
            'data': pessoa[6],
            'final': {},
            'eixos': []
        }

        for final in dados_finais:
            if final[1] == diagnostico_id:
                dados['final'] = {
                    'media_final': final[2],
                    'proposta': final[3]
                }

        for eixo in dados_eixos:
            if eixo[1] == diagnostico_id:
                dados['eixos'].append({
                    'eixo': eixo[2],
                    'media': eixo[3],
                    'respostas': eixo[4]
                })

        diagnosticos.append(dados)

    return diagnosticos
