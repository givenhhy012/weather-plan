import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

#실행전 라이브러리 설치 필요
#pandas (pip install pandas)
#scikit-learn (pip install scikit-learn)

# 🔵 Firebase 서비스 계정 인증
cred = credentials.Certificate('weather-plan-firebase-adminsdk-fbsvc-b48459a49b.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://weather-plan-default-rtdb.firebaseio.com/'
})

# 🔵 Firebase에서 공용 파일(기온 구간별 옷 입은 횟수) 가져오기
public_data_ref = db.reference('public/cloth/outer')  # 예: 아우터 전체
public_data = public_data_ref.get()

# 🔵 Firebase에서 실제 기록(기온, 사용자의 실제 선택) 가져오기
actual_data_ref = db.reference('public/actual_records')  # actual_records 경로
actual_data = actual_data_ref.get()

# 실제 기록 데이터 출력
print("실제 기록 데이터:", actual_data)

# 데이터가 리스트 형식이므로, 이를 DataFrame으로 변환
actual_df = pd.DataFrame(actual_data)

# 변환된 DataFrame 확인
print("DataFrame 형태로 변환된 데이터:", actual_df)

# (1) 공용 데이터 정리
# public_data는 대략 {'padding': {'0~5': 15, '6~10': 10}, 'coat': {...}, ...} 구조
df_list = []

for cloth_type, temp_dict in public_data.items():
    for temp_range, count in temp_dict.items():
        df_list.append({'temperature_range': temp_range, 'cloth_type': cloth_type, 'count': count})

public_df = pd.DataFrame(df_list)

# 온도구간별로 pivot (cloth_type 별 column)
pivot_df = public_df.pivot_table(index='temperature_range', columns='cloth_type', values='count', fill_value=0)

# 전체 입은 횟수 계산
pivot_df['total'] = pivot_df.sum(axis=1)

# 각 옷을 입은 확률 계산
for cloth in pivot_df.columns:
    if cloth != 'total':
        pivot_df[f'{cloth}_probability'] = pivot_df[cloth] / pivot_df['total']

# 온도구간 매칭 함수
def find_temp_range(temp):
    if temp <= 5:
        return '0~5'
    elif temp <= 10:
        return '6~10'
    elif temp <= 15:
        return '11~15'
    elif temp <= 20:
        return '16~20'
    else:
        return '21~'

# 실제 기록에 온도구간 추가
actual_df['temperature_range'] = actual_df['temperature'].apply(find_temp_range)

print("기온 범위가 추가된 DataFrame:")
print(actual_df)

# (3) 공용 데이터(pivot_df)와 실제 기록(actual_df) 병합
merged_df = pd.merge(actual_df, pivot_df, on='temperature_range', how='left')

# 🔵 Feature(X)와 라벨(y) 설정
feature_columns = ['padding', 'none', 'coat', 'jacket']
X = merged_df[feature_columns].fillna(0)  # 혹시 NaN이 있으면 0으로 채움
y = merged_df['outer']  # 실제 선택한 옷 종류

# 🔵 훈련/테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔵 로지스틱 회귀 모델 생성 및 훈련
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# 🔵 예측 및 정확도 평가
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy * 100:.2f}%')

# 🔵 예시 입력값으로 옷차림 예측하기
example_temp = 6 
example_temp_range = find_temp_range(example_temp)

# 해당 구간 확률 가져오기
example_probs = pivot_df.loc[example_temp_range, feature_columns].values.reshape(1, -1)

# 🔵 feature 이름을 명시하여 DataFrame으로 변환
example_input = pd.DataFrame(example_probs, columns=feature_columns)

# 예측
predicted_clothing = model.predict(example_input)
print(f'{example_temp}도에서는 추천하는 옷차림: {predicted_clothing[0]}')