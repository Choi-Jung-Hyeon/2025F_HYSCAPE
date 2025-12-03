import joblib
import pandas as pd
import os

# ==========================================
# 1. 저장된 모델 불러오기
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, '..', 'models', 'voltage_predictor_v1.pkl')

if not os.path.exists(model_path):
    print("❌ 모델 파일이 없습니다. 먼저 train.py를 실행해서 모델을 만들어주세요.")
    exit()

model = joblib.load(model_path)
print("✅ 모델 로드 완료. 시뮬레이션을 시작합니다.")

# ==========================================
# 2. 가상 조건 입력 (시뮬레이션)
# ==========================================
# 대표님이 궁금해하시는 상황을 여기에 입력하면 됩니다.
print("\n[가상 실험 조건 입력]")
print("ex) 전류: 2.0, 온도: 70, 압력: 10, 유량: 300")

# 예시 시나리오: 온도를 60도에서 80도로 올릴 때 전압 변화 예측
scenarios = [
    # [전류밀도, 온도, 압력, 유량]
    [2.0, 60, 10, 300],  # Case 1: 60도일 때
    [2.0, 70, 10, 300],  # Case 2: 70도일 때
    [2.0, 80, 10, 300],  # Case 3: 80도일 때
]

feature_names = [
    'Current Density(A/㎠)', 
    'Cell Temp(Deg C)', 
    'Anode Inlet Pressure(kpa)', 
    'Liquide Flow(ccm)'
]

# 데이터프레임으로 변환
input_data = pd.DataFrame(scenarios, columns=feature_names)

# ==========================================
# 3. 예측 결과 출력
# ==========================================
predicted_voltages = model.predict(input_data)

print("\n📊 [시뮬레이션 결과]")
print("-" * 50)
for i, voltage in enumerate(predicted_voltages):
    temp = scenarios[i][1] # 온도값
    print(f"Case {i+1} (온도 {temp}°C) -> 예상 전압: {voltage:.4f} V")
print("-" * 50)

# 효율 계산 (팁: 전압이 낮을수록 효율이 좋음)
if predicted_voltages[0] > predicted_voltages[-1]:
    print("💡 결론: 온도를 높이니 전압이 낮아져 효율이 좋아집니다.")
else:
    print("💡 결론: 온도를 높여도 전압이 높아지거나 비슷합니다.")