#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""이메일 설정 테스트 스크립트"""

import sys
import os

# Add dependencies to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dependencies'))

import config_production as config
from notifier import send_email

print("=" * 60)
print("Gmail SMTP 설정 테스트")
print("=" * 60)
print()

# 설정 확인
print("📧 현재 설정:")
print(f"   발신 이메일: {config.SENDER_EMAIL}")
print(f"   수신 이메일: {', '.join(config.RECEIVER_EMAIL)}")
print(f"   비밀번호 길이: {len(config.SENDER_PASSWORD)}자")

# 길이 확인
if len(config.SENDER_PASSWORD) != 16:
    print()
    print("⚠️  경고: 앱 비밀번호는 16자여야 합니다!")
    print(f"   현재: {len(config.SENDER_PASSWORD)}자")
    print()
    print("해결 방법:")
    print("1. https://myaccount.google.com/apppasswords 접속")
    print("2. 새 앱 비밀번호 생성 (16자)")
    print("3. .env 파일의 SENDER_PASSWORD 수정")
    sys.exit(1)

print()
print("✅ 비밀번호 길이 확인: 정상")
print()

# 테스트 이메일 발송
print("📤 테스트 이메일 발송 중...")
print()

test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #667eea;">✅ Hyscape 자동화 시스템 테스트</h2>
    <p>이메일 설정이 정상적으로 작동합니다!</p>
    <hr>
    <p style="color: #888; font-size: 12px;">
        이 메일은 Hyscape Daily Automation 시스템 테스트 메일입니다.
    </p>
</body>
</html>
"""

try:
    success = send_email(
        subject="[TEST] Hyscape 자동화 시스템 이메일 테스트",
        html_body=test_html
    )

    print()
    if success:
        print("=" * 60)
        print("✅ 성공! 이메일이 발송되었습니다.")
        print("=" * 60)
        print()
        print("수신 메일함을 확인하세요:")
        for email in config.RECEIVER_EMAIL:
            print(f"   📬 {email}")
        print()
    else:
        print("=" * 60)
        print("❌ 실패: 이메일 발송에 실패했습니다.")
        print("=" * 60)
        print()
        print("로그를 확인하세요:")
        print("   cat logs/unified_automation.log")
        sys.exit(1)

except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ 오류 발생: {e}")
    print("=" * 60)
    print()
    print("문제 해결:")
    print("1. 2단계 인증 활성화 확인")
    print("2. 앱 비밀번호 재생성")
    print("3. .env 파일 SENDER_PASSWORD 확인")
    sys.exit(1)
