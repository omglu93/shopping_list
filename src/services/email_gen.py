from flask_mail import Mail, Message
from flask import render_template

flask_mail = Mail()

def flask_send_email(subject, sender, recipients, text_body):
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = render_template("email.html", token=text_body)
    
    flask_mail.send(msg)