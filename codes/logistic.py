import pyrebase
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import numpy as np


# 🔵 Firebase 설정
firebase_config = {
    "apiKey": "AIzaSyDDoeGp8-kJrX68624sgfIkzscKO7aHg6k",
    "authDomain": "weather-plan.firebaseapp.com",
    "databaseURL": "https://weather-plan-default-rtdb.firebaseio.com/",
    "storageBucket": "weather-plan.firebasestorage.app"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()


# 🔹 Feature 이름 설정
# firebase에서의 데이터 이름과 일치하도록 설정해야함
FEATURE_NAMES_OUTER = [
    'temperature',
    'others_per_coat', 'others_per_jacket', 'others_per_none', 'others_per_padding',
    'users_per_coat', 'users_per_jacket', 'users_per_none', 'users_per_padding'
]

FEATURE_NAMES_TOP = [
    'temperature',
    'others_per_brushed', 'others_per_hoodie', 'others_per_shirt', 'others_per_tshirt',
    'users_per_brushed', 'users_per_hoodie', 'users_per_shirt', 'users_per_tshirt'
]

FEATURE_NAMES_PANTS = [
    'temperature',
    'others_per_brushed', 'others_per_jean', 'others_per_slacks', 'others_per_short',
    'users_per_brushed', 'users_per_jean', 'users_per_slacks', 'users_per_short'
]


# 🔹 데이터 로딩 함수
def fetch_firebase_data(user):
    user_id = user["localId"]  # 현재 로그인한 사용자의 UID
    token = user["idToken"]  # 인증 토큰
    
    public_data = 'public/cloth/'
    users_data = 'users/' + user_id + '/cloth/'
    
    all_actual_data = db.child('users').child(user_id + '/actual_records/').get(token=token).val()
    if all_actual_data and 'record_count' in all_actual_data:
        del all_actual_data['record_count']
    
    return (
        db.child(public_data + 'outer').get(token=token).val(),
        db.child(public_data + 'top').get(token=token).val(),
        db.child(public_data + 'pants').get(token=token).val(),
        db.child(users_data + 'outer').get(token=token).val(),
        db.child(users_data + 'top').get(token=token).val(),
        db.child(users_data + 'pants').get(token=token).val(),
        all_actual_data
    )


# 🔹 기온 범위 찾기
def find_temp_range(temp):
    if temp < 5:
        return '<5'
    elif temp < 10:
        return '<10'
    elif temp < 15:
        return '<15'
    elif temp < 20:
        return '<20'
    elif temp < 25:
        return '<25'
    else:
        return '>=25'


# 🔹 비율 변환 함수
def process_cloth_data(cloth_data, temp_range):
    if temp_range in cloth_data:
        total_count = sum(cloth_data[temp_range].values())
        if total_count == 0:
            return {k: 0 for k in cloth_data[temp_range]}
        else:
            return {k: v / total_count for k, v in cloth_data[temp_range].items()}
    else:
        return {}

# 🔹 학습 데이터 준비
def prepare_training_data(all_actual_data, cloth_type):
    records = []

    for _, data in all_actual_data.items():
        temperature = data.get('temperature')
        cloth_data = data.get(cloth_type, {})
        actual_choice = data.get('actual_choice')  # 타깃값

        record = {'temperature': temperature, 'actual_choice': actual_choice}
        record.update(cloth_data)
        records.append(record)

    df = pd.DataFrame(records)
    df.fillna(0, inplace=True)

    # 🔹 타깃값 actual_choice가 문자열이면 LabelEncoder 적용
    feature_columns = [col for col in df.columns if col != 'actual_choice']
    X = df[feature_columns]
    y = df['actual_choice']
    
    if y.dtype == 'object':
        le_target = LabelEncoder()
        y = le_target.fit_transform(y)
    else:
        le_target = None

    for col in X.columns:
        if X[col].dtype == 'object':
            print(f"Warning: Column '{col}' is of type object but should be numeric.")

    # LabelEncoder와 Feature 목록 반환
    return X, y, le_target, feature_columns



# 🔹 Feature 준비
def prepare_features(temperature, public_data, user_data, feature_names):
    temp_range = find_temp_range(temperature)

    others_ratio = process_cloth_data(public_data, temp_range)
    users_ratio = process_cloth_data(user_data, temp_range)

    features = [temperature]
    for key in feature_names[1:]:
        category = key.split('_per_')[1]
        if 'others' in key:
            features.append(others_ratio.get(category, 0))
        elif 'users' in key:
            features.append(users_ratio.get(category, 0))

    # 🔹 Feature 순서 맞춰서 DataFrame 생성
    return pd.DataFrame([features], columns=feature_names)


# 🔹 모델 학습
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    return model


# 🔹 예측 실행
def predict_outfits(model, temperature, public_data, user_data, feature_names, expected_features, label_encoder):        
    features_df = prepare_features(temperature, public_data, user_data, feature_names)

    # 학습 시 feature 순서와 이름에 맞추기 위해 재정렬
    features_df = features_df.reindex(columns=expected_features, fill_value=0)

    # 🔹 예측 후 레이블 변환
    predicted_cloth_num = model.predict(features_df)[0]
    if label_encoder:
        predicted_cloth = label_encoder.inverse_transform([predicted_cloth_num])[0]
    else:
        predicted_cloth = predicted_cloth_num
    
    return predicted_cloth

        

def recommendation_machine(user, temp):
    
    print("=== 🔹 Firebase 데이터 로딩 중... ===")
    public_outer, public_top, public_pants, users_outer, users_top, users_pants, all_actual_data = fetch_firebase_data(user)
    
    print("=== 🔹 모델 학습 중... ===")
    # 학습 시 feature 이름들 받음
    X_outer, y_outer, outer_encoder, outer_features = prepare_training_data(all_actual_data, 'outer')
    outer_model = train_model(X_outer, y_outer)

    X_top, y_top, top_encoder, top_features = prepare_training_data(all_actual_data, 'top')
    top_model = train_model(X_top, y_top)

    X_pants, y_pants, pants_encoder, pants_features = prepare_training_data(all_actual_data, 'pants')
    pants_model = train_model(X_pants, y_pants)

    print("\n=== 🔹 예측 테스트 ===")

    outer = predict_outfits(outer_model, temp, public_outer, users_outer, FEATURE_NAMES_OUTER, outer_features, outer_encoder)
    top = predict_outfits(top_model, temp, public_top, users_top, FEATURE_NAMES_TOP, top_features, top_encoder)
    pants = predict_outfits(pants_model, temp, public_pants, users_pants, FEATURE_NAMES_PANTS, pants_features, pants_encoder)
    
    return outer, top, pants


# actual_record의 개수 세는 함수
def get_max_index(user):
    user_id = user["localId"]  # 현재 로그인한 사용자의 UID
    token = user["idToken"]  # 인증 토큰
    
    try:
        # 🔵 Firebase에서 사용자의 기록 개수 가져오기
        count = db.child("users").child(user_id).child('actual_records/record_count').get(token=token).val()
        
        if count is None:
            print("경로에 하위 폴더가 없습니다.")
            return None

        print(f"기록의 개수: {count}")
        return count

    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    
    
# 다른 사람들이 가장 많이 입은 옷을 반환하는 함수
def get_most_common_clothes(data, temperature):
    # 🔵 기온 구간 찾기
    temp_range = find_temp_range(temperature)
    
    # 🔵 해당 기온 구간의 옷 입은 횟수 가져오기
    outer_count = data['outer'].get(temp_range, {})
    top_count = data['top'].get(temp_range, {})
    pants_count = data['pants'].get(temp_range, {})

    # 🔵 가장 많이 입은 옷 찾기
    most_common_outer = max(outer_count, key=outer_count.get)
    most_common_top = max(top_count, key=top_count.get)
    most_common_pants = max(pants_count, key=pants_count.get)

    return most_common_outer, most_common_top, most_common_pants


# 머신러닝 돌리지 않고 단순 추천 시스템
# 입은 횟수가 동일하면 데이터 구조 상 먼저 나오는 옷을 추천
def recommendation_simple(temp):
    # 🔵 Firebase에서 공용 기록(기온 구간별 옷 입은 횟수) 가져오기
    public_data_path = 'public/cloth/'
    public_data = db.child(public_data_path).get().val()
    
    return get_most_common_clothes(public_data, temp)

