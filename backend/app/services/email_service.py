"""
Email Service для отправки писем верификации
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', self.smtp_user)
        self.from_name = getattr(settings, 'FROM_NAME', 'Felend')
    
    def _create_verification_email(self, code: str, recipient_email: str) -> MIMEMultipart:
        """Создать HTML письмо с кодом верификации"""
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify your Felend account"
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = recipient_email
        
        # Текстовая версия
        text = f"""
        Welcome to Felend!
        
        Your verification code is: {code}
        
        This code will expire in 15 minutes.
        
        If you didn't register for Felend, please ignore this email.
        """
        
        # HTML версия
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #667eea;
                    padding: 20px;
                    text-align: center;
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 5px;
                    color: #667eea;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Felend!</h1>
                </div>
                <div class="content">
                    <p>Thank you for registering with Felend. To complete your registration, please use the following verification code:</p>
                    <div class="code-box">
                        {code}
                    </div>
                    <p><strong>This code will expire in 15 minutes.</strong></p>
                    <p>If you didn't register for Felend, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Felend. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        return message
    
    def send_verification_code(self, email: str, code: str) -> bool:
        """Отправить код верификации на email"""
        try:
            # Если нет настроек SMTP, логируем код вместо отправки (для разработки)
            if not self.smtp_user or not self.smtp_password:
                logger.warning(f"SMTP not configured. Verification code for {email}: {code}")
                print(f"\n{'='*60}")
                print(f"📧 EMAIL VERIFICATION CODE")
                print(f"{'='*60}")
                print(f"To: {email}")
                print(f"Code: {code}")
                print(f"{'='*60}\n")
                return True
            
            message = self._create_verification_email(code, email)
            
            # Подключение к SMTP серверу
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Verification email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            # В production можно выбросить исключение, в dev - просто логируем
            if settings.DEBUG:
                logger.warning(f"Development mode: Verification code for {email}: {code}")
                print(f"\n{'='*60}")
                print(f"📧 EMAIL VERIFICATION CODE (Error fallback)")
                print(f"{'='*60}")
                print(f"To: {email}")
                print(f"Code: {code}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")
                return True
            return False
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Маскировать email для безопасности (us***@ex***.com)"""
        try:
            local, domain = email.split('@')
            if len(local) <= 2:
                masked_local = local[0] + '*'
            else:
                masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
            
            domain_parts = domain.split('.')
            if len(domain_parts[0]) <= 2:
                masked_domain = domain_parts[0][0] + '*'
            else:
                masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 2) + domain_parts[0][-1]
            
            masked_domain = masked_domain + '.' + '.'.join(domain_parts[1:])
            return f"{masked_local}@{masked_domain}"
        except:
            return "***@***.***"


# Singleton instance
email_service = EmailService()
