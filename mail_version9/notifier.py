# notifier.py
"""
이메일 발송 모듈
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT

def send_email(subject, html_body):
    """Gmail SMTP로 이메일 발송"""
    try:
        if isinstance(RECEIVER_EMAIL, list):
            receivers = RECEIVER_EMAIL
            to_header = ", ".join(RECEIVER_EMAIL)
        else:
            receivers = [RECEIVER_EMAIL]
            to_header = RECEIVER_EMAIL

        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_header
        msg['Subject'] = subject

        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print("\n이메일 발송 완료!")
        return True

    except Exception as e:
        print(f"\n이메일 발송 실패: {e}")
        return False