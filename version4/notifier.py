# notifier.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT, KEYWORD

def send_email(html_content):
    if not SENDER_PASSWORD:
        print("[오류] Gmail 앱 비밀번호가 config.py에 설정되지 않았습니다.")
        print("이메일 발송 실패")
        return False

    today_str = datetime.now().strftime('%Y-%m-%d')
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"[{KEYWORD} 뉴스 브리핑] {today_str}"

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        print(f"SMTP 서버({SMTP_SERVER}:{SMTP_PORT})에 연결하여 이메일 발송을 시도합니다.")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # TLS 암호화
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ 성공: '{RECEIVER_EMAIL}' 로 뉴스 브리핑을 발송했습니다.")
        return True
    except Exception as e:
        print(f"❗️[오류] 이메일 발송에 실패했습니다: {e}")
        return False

# --- 단위 테스트 코드 ---
if __name__ == '__main__':
    print("--- notifier.py 단위 테스트 시작 ---")

    # 테스트용 HTML 본문 생성
    test_html = """
    <h1>📧 테스트 이메일</h1>
    <p>이 메일은 notifier.py가 정상적으로 작동하는지 확인하기 위한 테스트 메일입니다.</p>
    <hr>
    <p><b>[AI 요약]</b><br>테스트 요약 내용입니다.</p>
    <p><b>[키워드]</b><br>테스트, 이메일, 성공</p>
    """
    
    # 함수가 정상적으로 작동하는지 테스트합니다.
    send_email(test_html)
        
    print("--- 단위 테스트 종료 ---")