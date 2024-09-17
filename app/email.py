from flask_mail import Message
from flask import current_app
from app import mail

def send_email(to, subject, template):
    """
    Envia um e-mail com o conteúdo fornecido.

    :param to: Endereço de e-mail do destinatário
    :param subject: Assunto do e-mail
    :param template: Conteúdo HTML do e-mail
    """
    try:
        # Cria a mensagem
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'no-reply@sanofi.com')
        )
        # Envia a mensagem
        mail.send(msg)
        print(f"E-mail enviado com sucesso para {to}.")
    except Exception as e:
        # Loga o erro para depuração
        print(f"Erro ao enviar e-mail para {to}: {e}")
