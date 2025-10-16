# notifier.py (v3.0)
"""
이메일 발송 모듈
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT

def send_email(subject, html_body):
    """
    Gmail SMTP로 이메일 발송
    - 다중 수신자 지원
    """
    try:
        # 수신자 처리 (리스트 또는 문자열)
        if isinstance(RECEIVER_EMAIL, list):
            receivers = RECEIVER_EMAIL
            to_header = ", ".join(RECEIVER_EMAIL)
        else:
            receivers = [RECEIVER_EMAIL]
            to_header = RECEIVER_EMAIL
        
        # 이메일 메시지 생성
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_header
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