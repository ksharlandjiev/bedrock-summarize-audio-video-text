import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from handlers.abstract_handler import AbstractHandler

class EmailSenderHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        # Email setup
        smtp_server = request.get("smtp_server")
        smtp_port = request.get("smtp_port", 465)  # Using port 465 for SMTPS
        smtp_user = request.get("email_username")
        smtp_password = request.get("email_password")
        from_email = request.get("email_username")

        to_email = request.get("from_email")
        subject = "Re: " + request.get("subject")
        message_body = request.get("text")
        message_id = request.get("message_id")

        print(f"Sending email to {to_email} using server {smtp_server}")

        try:
            self.send_email(smtp_server, smtp_port, smtp_user, smtp_password, from_email, to_email,
                            subject, message_body, message_id)
            print("Reply sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
            return request  # Optional: decide how to handle failed sends

        return super().handle(request)

    def send_email(self, server, port, username, password, from_email, to_email,
                   subject, body, original_message_id):
        """
        Sends an email using SMTPS (SMTP over SSL) with the provided parameters, including handling for threading.
        """
        message = MIMEMultipart()
        message['From'] = formataddr(('AI Assistant', from_email))
        message['To'] = to_email
        message['Subject'] = subject
        message['In-Reply-To'] = original_message_id
        message['References'] = original_message_id
        message.attach(MIMEText(body, 'plain'))

        try:
            smtp_server = smtplib.SMTP_SSL(server, port, timeout=10)  # Using SMTP_SSL for SSL connection
            smtp_server.login(username, password)
            smtp_server.sendmail(from_email, to_email, message.as_string())
            smtp_server.quit()
        except smtplib.SMTPException as e:
            raise Exception(f"SMTP error: {e}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
