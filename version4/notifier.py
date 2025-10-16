# notifier.py (v3.0)
"""
이메일 발송 모듈
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

def send_email(subject, html_body):
    """
    Gmail SMTP로 이메일 발송
    """
    try:
        # 이메일 메시지 생성
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        
        # HTML 본문 추가
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Gmail SMTP 서버 연결
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print("\n✅ 이메일 발송 완료!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  이메일 발송 실패: {e}")
        return False

if __name__ == "__main__":
    # 테스트
    test_subject = "테스트 이메일"
    test_body = "<h1>테스트</h1><p>이메일 발송 테스트입니다.</p>"
    send_email(test_subject, test_body)