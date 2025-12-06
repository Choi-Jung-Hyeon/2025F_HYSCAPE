import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ==========================================
# 1. 환경 설정 및 데이터 로드
# ==========================================
# 현재 파일(train.py)의 위치를 기준으로 경로를 잡습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, '..', 'data', 'Sheet1.csv')
model_save_path = os.path.join(current_dir, '..', 'models')

# 모델 저장 폴더가 없으면 생성
os.makedirs(model_save_path, exist_ok=True)

print(f"Loading data from: {data_path}")
try:
    df = pd.read_csv(data_path, encoding='euc-kr')
except FileNotFoundError:
    print("❌ 에러: 데이터 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()

# ==========================================
# 2. 데이터 전처리 (수정됨: 더 강력한 청소 기능 추가)
# ==========================================
features = [
    'Current Density(A/㎠)',      # 전류 밀도
    'Cell Temp(Deg C)',           # 셀 온도
    'Anode Inlet Pressure(kpa)',  # 양극 입구 압력
    'Liquide Flow(ccm)'           # 유량
]
target = 'Cell Voltage(V)'        # 예측 목표

# [핵심 수정] 모든 데이터를 강제로 숫자로 변환합니다.
# 'Current Density(A/㎠)' 같은 글자가 섞여 있으면 NaN(빈 값)으로 바꿔버립니다.
all_cols = features + [target]
for col in all_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# NaN(빈 값)이 된 행(원래 글자가 있던 행)을 삭제합니다.
data = df[all_cols].dropna()

print(f"데이터 정제 완료! (남은 데이터: {len(data)}행)")

X = data[features]
y = data[target]

# 학습용:테스트용 = 8:2 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# 3. 모델 학습 (Random Forest)
# ==========================================
print("모델 학습을 시작합니다...")
model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# ==========================================
# 4. 성능 평가 및 저장
# ==========================================
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

print("------------------------------------------------")
print(f"✅ 모델 학습 완료!")
print(f"📊 모델 정확도 (R2 Score): {r2:.4f} (1.0에 가까울수록 좋음)")
print("------------------------------------------------")

# 모델 저장 (.pkl 파일)
model_file = os.path.join(model_save_path, 'voltage_predictor_v1.pkl')
joblib.dump(model, model_file)
print(f"💾 모델이 저장되었습니다: {model_file}")

# (옵션) 결과 시각화 이미지 저장
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions, alpha=0.3)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Voltage (V)')
plt.ylabel('Predicted Voltage (V)')
plt.title(f'Prediction Performance (R2: {r2:.2f})')
plt.savefig(os.path.join(model_save_path, 'performance_graph.png'))
print("📈 성능 그래프가 models 폴더에 저장되었습니다.")

# [추가 코드] 변수 중요도(Feature Importance) 분석
import numpy as np

# 모델이 생각하는 각 변수의 중요도 뽑기
importances = model.feature_importances_
feature_names = X.columns

# 중요도 순서대로 정렬
indices = np.argsort(importances)[::-1]

print("\n📊 [변수 중요도 분석 결과]")
print("이 모델은 전압을 예측할 때 다음 변수를 가장 중요하게 봅니다:")
for f in range(X.shape[1]):
    print(f"{f + 1}. {feature_names[indices[f]]}: {importances[indices[f]]:.4f}")

# 중요도 그래프 저장
plt.figure(figsize=(10, 6))
plt.title("Feature Importances (What affects Voltage?)")
plt.bar(range(X.shape[1]), importances[indices], align="center")
plt.xticks(range(X.shape[1]), [feature_names[i] for i in indices], rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(model_save_path, 'feature_importance.png'))
print("📊 변수 중요도 그래프가 models 폴더에 저장되었습니다.")