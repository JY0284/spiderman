# notifier/email_notifier.py

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, Any
import logging
import os

class EmailNotifier:
    def __init__(self, config: Dict[str, Any]):
        self.server_address = config['Email']['server_address']
        self.server_port = int(config['Email']['server_port'])
        self.sender_email = config['Email']['sender_email']
        self.sender_password = config['Email']['sender_password']
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_html_content_with_image(self, plain_text_body: str, table_path) -> str:
        """
        Create an HTML version of the body with embedded image.
        """
        # Read the HTML file content
        with open(table_path, 'r') as html_file:
            html_table_content = html_file.read()

        # Combine the HTML table and the image
        html_content = f"""
        <html>
        <body>
            <p>{plain_text_body}</p>
            <img src="cid:listing_deal_plot" alt="Listing Deal Plot" style="width:100%;height:auto;">
            {html_table_content}
        </body>
        </html>
        """
        return html_content

    def send_email(self, subject: str, body: str, to_email: str, image_path: str = None, table_path: str = None):
        """
        Sends an email with a subject, body, and optional embedded image and HTML content.
        
        Parameters:
        - subject: The subject of the email.
        - body: The plain text body of the email.
        - to_email: The recipient's email address.
        - image_file: Path to the image file to embed in the email (optional).
        - html_file: Path to the HTML file to use as the email body (optional).
        """
        try:
            # Construct the email
            msg = MIMEMultipart('related')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            html_content = body
            if image_path and table_path:
                with open(image_path, 'rb') as img:
                    img_data = img.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    image.add_header('Content-ID', '<listing_deal_plot>')
                    msg.attach(image)
                html_content = self._get_html_content_with_image(body, table_path)

            msg.attach(MIMEText(html_content, 'html'))

            # Define retry logic
            max_retries = 1
            retries = 0

            while retries < max_retries:
                try:
                    server = smtplib.SMTP_SSL(host=self.server_address, port=self.server_port)
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, to_email, msg.as_string())
                    self.logger.info(f"Email sent to {to_email}.")
                    server.quit()
                    time.sleep(10)
                    return  # Exit function on success
                except smtplib.SMTPException as e:
                    retries += 1
                    self.logger.error(f"Attempt {retries}: Failed to send email to {to_email}: {e}")
                    time.sleep(60 * 10)  # Wait before retrying

            # Log failure after exceeding retries
            self.logger.error(f"All {max_retries} attempts failed. Could not send email to {to_email}.")

        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while preparing email to {to_email}: {e}")
        
