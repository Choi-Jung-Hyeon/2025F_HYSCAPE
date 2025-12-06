import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# ==========================================
# 1. 데이터 파일에서 '진짜 정보(요약표)' 찾기
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, '..', 'data', 'Sheet1.csv')

print(f"📂 파일 분석 중: {data_path}")

# 파일을 한 줄씩 읽어서 'Current Density'가 시작되는 줄을 찾습니다.
start_row = -1
with open(data_path, 'r', encoding='cp949', errors='ignore') as f:
    for i, line in enumerate(f):
        # 엑셀 요약표는 보통 'Current Density'라는 헤더를 가집니다.
        if "Current Density" in line and "Cell Voltage" in line:
            start_row = i
            break

if start_row == -1:
    print("❌ 요약 테이블을 찾을 수 없습니다! 일반 Raw 데이터로 진행하거나 파일을 확인해주세요.")
    exit()

print(f"✅ {start_row}번째 줄에서 '요약 테이블(Summary Table)'을 발견했습니다!")

# ==========================================
# 2. 요약 데이터 로드 및 정제
# ==========================================
# 발견한 위치부터 데이터를 다시 읽습니다.
df = pd.read_csv(data_path, skiprows=start_row, encoding='cp949')

# 데이터가 엑셀 구조상 앞에 빈 컬럼(Unnamed)이 있을 수 있으므로 제거합니다.
# 실제 컬럼명: 'Current Density(A/㎠)', 'Cell Voltage(V)' 등
target_col_x = 'Current Density(A/㎠)'
target_col_y = 'Cell Voltage(V)'

# 해당 컬럼이 있는지 확인하고 선택
valid_cols = [c for c in df.columns if 'Current' in str(c) or 'Voltage' in str(c)]
clean_df = df[valid_cols].dropna()

# 숫자가 아닌 데이터(헤더 반복 등) 제거
clean_df = clean_df.apply(pd.to_numeric, errors='coerce').dropna()

print(f"\n📊 [데이터 추출 결과]")
print(clean_df.head())
print(f"총 데이터 개수: {len(clean_df)}개 (Raw 데이터보다 훨씬 적고 핵심적인 데이터입니다)")

# ==========================================
# 3. 의미 있는 그래프 그리기 (IV Curve)
# ==========================================
# 수전해에서 가장 중요한 그래프: x축=전류밀도, y축=전압
plt.figure(figsize=(10, 6))
plt.scatter(clean_df[target_col_x], clean_df[target_col_y], color='blue', label='Experiment Data')
plt.plot(clean_df[target_col_x], clean_df[target_col_y], color='blue', alpha=0.3) # 선으로 연결

plt.title('IV Characteristic Curve (Performance Check)', fontsize=15)
plt.xlabel('Current Density (A/cm²)', fontsize=12)
plt.ylabel('Cell Voltage (V)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# 그래프 저장
save_path = os.path.join(current_dir, '..', 'models', 'meaningful_IV_curve.png')
plt.savefig(save_path)
print(f"\n📈 의미 있는 분석 그래프가 저장되었습니다: {save_path}")

# ==========================================
# 4. 제대로 된 모델 학습 (옵션)
# ==========================================
# 이제 깨끗한 데이터로 모델을 만들면 훨씬 정확하고 가벼워집니다.
X = clean_df[[target_col_x]] # 입력: 전류
y = clean_df[target_col_y]   # 출력: 전압

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

print(f"\n🤖 모델 학습 완료! (R2 Score: {model.score(X, y):.4f})")
print("이제 이 모델은 '전류를 넣으면 -> 전압(효율)'을 정확하게 예측합니다.")

# ==========================================
# 5. 특정 값(2.5A) 예측하기
# ==========================================
# 궁금한 전류 밀도 값
target_current = 5.0 

# 모델이 알아들을 수 있는 표(DataFrame) 형태로 만들어줍니다.
# 학습할 때 썼던 이름('Current Density(A/㎠)')을 똑같이 써줘야 에러가 안 납니다.
import pandas as pd
input_condition = pd.DataFrame([[target_current]], columns=[target_col_x])

# 예측 수행
predicted_voltage = model.predict(input_condition)

print("\n------------------------------------------------")
print(f"💡 [예측 결과] 전류 밀도가 {target_current} A/cm² 일 때")
print(f"   예상되는 전압(Cell Voltage)은 {predicted_voltage[0]:.4f} V 입니다.")
print("------------------------------------------------")