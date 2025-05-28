from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from app import app
from flask import render_template
from config import secret_key
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import detalhar_usuario

app.secret_key = secret_key


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

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField('Email', [
        validators.Email(),
        validators.DataRequired()
    ])
    empresa = StringField('Empresa', [
        validators.DataRequired(),
        validators.Length(min=2)
    ])


class RecoveryForm(FlaskForm):
    email_or_username = StringField('Email ou Usuário', [
        validators.DataRequired(message="Preencha este campo"),
        validators.Length(min=4, max=50)
    ])
    motivo = StringField('Motivo de recuperacao')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from utils import criar_usuario_public

    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = {
            'username': form.username.data,
            'email': form.email.data,
            'empresa': form.empresa.data,
            'status': 'pending'
        }
        criar_usuario_public(
            username=form.username.data,
            senha="12345678",
            email=form.email.data,
            empresa=form.empresa.data
        )

        assunto = "Cadastro recebido"
        corpo = f'''
<p>Olá, {form.username.data}.</p>
<p>Recebemos sua solicitação de criação de conta. Nossa equipe irá avaliá-la em breve.</p>
<p>Caso não tenha solicitado, entre em contato conosco pelos canais abaixo:</p>
<p>- Plataforma: https://site-ttsolucoes.onrender.com/recovery </p>
<p>- Whatsapp: https://wa.me/5527997516005</p>
<p>- Ligação: +55 (27) 9 9751-6005</p>
<p>Ou simplesmente responda esse e-mail.</p>
-----
</br>
<small>Atenciosamente, equipe <strong>TT SOLUÇÕES</strong></small>
</br>
<small>Transformação técnico-digital para empresas que ainda fazem milagre com planilha.</small>
</br>
<img src="https://lh3.googleusercontent.com/d/1W1llr4gNibdJwsGX11dj2jspIt633yWX" width="96" height="96" alt="Logo TT Soluções">
        '''
        enviar_email(form.email.data, assunto, corpo)
        return render_template('pages/public/conta_criada.html', novos=new_user)

    return render_template('pages/public/criar_conta.html', form=form)

@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    
    from utils import recuperar_acesso_public

    form = RecoveryForm()
    if form.validate_on_submit():
        new_user = {
            'conta': form.email_or_username.data,
            'password': form.motivo.data,
            'status': 'a validar'
        }
        res = recuperar_acesso_public(form.email_or_username.data, form.motivo.data)
        res_user = detalhar_usuario(form.email_or_username.data)
        if '@' not in form.email_or_username.data:
            email = res_user.get('email')
            user = form.email_or_username.data
        else:
            email = form.email_or_username.data
            user = res_user.get('username')
        assunto = "Recuperacao de conta recebida"
        corpo = f'''
<p>Olá, {user} .</p>

<p>Estamos entrando em contato para informar que recebemos sua solicitação de recuperar sua conta em nossa plataforma. Nosso time de suporte está avaliando sua solicitação e iremos aprovar assim que possível.</p>

<p>Caso não tenha solicitado, favor entre em contato conosco:</p>

<p>- Plataforma: https://site-ttsolucoes.onrender.com/recovery </p>

<p>- Whatsapp: https://wa.me/5527997516005</p>

<p>- Ligação: +55 (27) 9 9751-6005</p>

<p>Ou simplesmente responda esse e-mail.</p>

<p>Estamos gratos pela sua atenção e solicitação.</p>
-----
</br>
<small>Atenciosamente, equipe <strong>TT SOLUÇÕES</strong></small>
</br>
<small>Transformação técnico-digital para empresas que ainda fazem milagre com planilha.</small>
</br>
<img src="https://lh3.googleusercontent.com/d/1W1llr4gNibdJwsGX11dj2jspIt633yWX" width="96" height="96" alt="Logo TT Soluções">
        '''
        enviar_email(email, assunto, corpo)
        return render_template('pages/public/conta_recuperada.html', novos=new_user)
    return render_template('pages/public/recuperar_conta.html', form=form)
