import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 1. 데이터 불러오기 (파일 경로는 실제 위치에 맞게 수정하세요)
# data1.xlsx의 Sheet1 데이터 사용
df = pd.read_csv('data1.xlsx - Sheet1.csv')

# 2. 데이터 전처리
# 모델 학습에 사용할 변수(X)와 예측할 변수(y) 선택
features = [
    'Current Density(A/㎠)',      # 전류 밀도
    'Cell Temp(Deg C)',           # 셀 온도
    'Anode Inlet Pressure(kpa)',  # 압력
    'Liquide Flow(ccm)'           # 유량 (물질의 양)
]
target = 'Cell Voltage(V)'        # 예측 목표: 전압

# 결측치가 있는 행 제거 (데이터 클리닝)
data = df[features + [target]].dropna()

X = data[features]
y = data[target]

# 3. 학습용(Train)과 테스트용(Test) 데이터 분리 (8:2 비율)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. 모델 학습 (Random Forest Regressor)
# 화학적 비선형성을 잘 잡아내는 모델입니다.
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. 성능 평가
predictions = model.predict(X_test)
score = r2_score(y_test, predictions)
print(f"모델 정확도 (R2 Score): {score:.4f}") 
# 1.0에 가까울수록 완벽하게 예측한다는 뜻입니다.

# --- [대표님이 원하시는 시뮬레이션 기능] ---
# "만약 온도를 70도로 올리고, 유량을 300으로 맞추면 전압이 어떻게 될까?"
new_condition = [[2.0, 70, 10, 300]] # [전류, 온도, 압력, 유량]
new_condition_df = pd.DataFrame(new_condition, columns=features)

predicted_voltage = model.predict(new_condition_df)
print(f"\n[시뮬레이션 결과] 예측 전압: {predicted_voltage[0]:.4f} V")

# 6. 결과 시각화 (실제값 vs 예측값)
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--') # 기준선
plt.xlabel('Actual Voltage (실제값)')
plt.ylabel('Predicted Voltage (예측값)')
plt.title('Prediction Model Performance')
plt.show()