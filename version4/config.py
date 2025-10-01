# config.py

# Google Gemini AI 설정
GOOGLE_API_KEY = "AIzaSyBtsEROjvmN27jGHboUmfZTEAhk5wk1NoY"

# Gmail 발송 정보 설정
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "junghyun6555@gmail.com"     # 보내는 사람 Gmail 계정
SENDER_PASSWORD = "invg xbzj yjgq hgju"     # Gmail 2단계 인증 후 생성한 앱 비밀번호
RECEIVER_EMAIL = "fourmi103@g.skku.edu"     # 받는 사람 이메일 (test)
# RECEIVER_EMAIL = "ymkim@hyscape.co.kr"      # 받는 사람 이메일

# 스크랩할 정보 소스
KEYWORD = "수소"
RSS_URL = f"https://news.google.com/rss/search?q={KEYWORD}&hl=ko&gl=KR&ceid=KR:ko"