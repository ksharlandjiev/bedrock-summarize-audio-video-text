from handlers.abstract_handler import AbstractHandler
import imaplib
import email

class EmailReaderHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        # Extract email server, port, and login credentials from the request
        email_server = request.get("imap_server")
        email_port = request.get("port", 993)  # Default to port 993 for SSL
        email_user = request.get("email_username")
        email_password = request.get("email_password")
        
        print(f"Connecting to email server {email_server} on port {email_port} with user {email_user}")

        # Read one unread email
        email_details = self.read_one_unread_email(email_server, email_port, email_user, email_password, request)
        
        if not email_details:
            print("No unread emails with suitable content found.")
            return request  # Return the request unchanged if no email is read
        
        # Update request with the email details
        request.update(email_details)
        
        return super().handle(request)

    def read_one_unread_email(self, server, port, username, password, request):
        """
        Connects to the email server using the specified port and reads the body of one unread email.
        Manages email post-processing based on request parameters and extracts additional email details.
        """
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)
        mail.select('inbox')

        # Search for unread emails
        status, email_ids = mail.search(None, '(UNSEEN)')
        if status == 'OK' and email_ids[0]:
            for email_id in email_ids[0].split():
                # Fetch the email by ID
                status, data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_msg = email.message_from_bytes(data[0][1])
                    email_details = self.extract_email_details(email_msg)
                    email_details['email_id'] = email_id  # Adding the email_id to the details
                    
                    # Manage email post-processing (delete or leave unread)
                    self.manage_email_after_processing(mail, email_id, request)
                    
                    return email_details
        return None

    def extract_email_details(self, email_msg):
        """
        Extracts the subject, from email, message ID, and the message body from the email message.
        """
        subject = email_msg.get('Subject', 'No Subject')
        from_email = email_msg.get('From', 'Unknown Sender')
        message_id = email_msg.get('Message-ID', 'No Message-ID')
        body = None

        if email_msg.is_multipart():
            for part in email_msg.walk():
                ctype = part.get_content_type()
                if ctype in ('text/plain', 'text/html') and not part.get_filename():
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = email_msg.get_payload(decode=True).decode('utf-8')

        return {'subject': subject, 'from_email': from_email, 'message_id': message_id, 'text': body}

    def manage_email_after_processing(self, mail, email_id, request):
        """
        Manages email after processing, such as marking as read, deleting, or leaving unread.
        """
        if request.get('deleteAfterRead'):
            mail.store(email_id, '+FLAGS', '\\Deleted')
            mail.expunge()
        elif request.get('leaveEmailUnread'):
            # Mark the email as unread
            mail.store(email_id, '-FLAGS', '\\Seen')