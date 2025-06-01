import pyrebase
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import numpy as np


# 알고리즘 설명!!

# 사용전 라이브러리 설치 필요
# pip install pyrebase4
# pip install pandas
# pip install scikit-learn


# <알고리즘 로직>
# 1. actual_records(사용자가 실제로 어떤 옷을 입었는지 기록)의 개수가 5개 이상
# 2. cloth/outer, top, pants/(해당 기온 구간) 에서 2번 이상 입은 옷 종류가 2개 이상
# 위 조건을 모두 만족해야 머신러닝 추천 시스템 사용
# 아니면 단순 추천 시스템 사용

# ===단순 추천 시스템===
# (사용자가 해당 옷을 입은 비율 * 가중치1) + (다른 사람들이 해당 옷을 입은 비율 * 가중치2) 로 계산하여 가장 높은 값을 추천으로
# 가중치는 사용자가 해당 옷을 입은 횟수에 따라 다르게 설정
# 사용자가 해당 기온 구간에서 전체 옷을 입은 횟수가 7회 미만 => 가중치1 = 사용자가 입은 횟수 / 10
# 7회 이상부터는 가중치1 = 0.6
# 가중치2 = (1 - 가중치1)
# 예시: 사용자가 전체 옷 입은 횟수가 3이면, 가중치1 = 0.3, 가중치2 = 0.7 => 사용자 데이터가 30%, 공용 데이터가 70% 반영됨

# ===머신러닝 추천 시스템===
# 1. 사용자의 actual_records를 기반으로 머신러닝 모델을 학습
# 2. 새로운 예측에 사용할 feature는 평균 기온, 해당 기온 구간에서의 옷 입은 비율(사용자, 공용 데이터) => 세가지



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
    'others_per_brushed', 'others_per_hoodie', 'others_per_longsleeve', 'others_per_tshirt',
    'users_per_brushed', 'users_per_hoodie', 'users_per_longsleeve', 'users_per_tshirt'
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

        
# 머신러닝 추천 시스템
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
    
    print (f"추천된 옷: {outer}, {top}, {pants}")
    
    return translate_choice(outer), translate_choice(top), translate_choice(pants)


# 머신러닝 돌릴 수 있는지 확인하는 함수
def check_enough_data(user, temperature):
    # 🔵 사용자의 기록 개수 확인
    if (get_max_index(user) < 5):
        print("사용자 기록이 충분하지 않습니다.")
        return False
    
    user_id = user["localId"]  # 현재 로그인한 사용자의 UID
    token = user["idToken"]  # 인증 토큰
    
    # 🔵 Firebase에서 사용자자 기록(기온 구간별 옷 입은 횟수) 가져오기
    user_outer_data = db.child("users").child(user_id).child("cloth/outer").get(token=token).val()
    user_top_data = db.child("users").child(user_id).child("cloth/top").get(token=token).val()
    user_pants_data = db.child("users").child(user_id).child("cloth/pants").get(token=token).val()
    
    # 🔵 기온 구간 찾기
    temp_range = find_temp_range(temperature)
    
    # 🔵 해당 기온 구간의 옷 입은 횟수 가져오기
    outer_count = user_outer_data.get(temp_range, {})
    top_count = user_top_data.get(temp_range, {})
    pants_count = user_pants_data.get(temp_range, {})
    
    # 두개 이상의 클래스가 2이상인 경우 True
    outer_valid = is_valid_category(outer_count)
    top_valid = is_valid_category(top_count)
    pants_valid = is_valid_category(pants_count)



    # 🔵 최종 판단:
    # 1. actual_record의 개수가 5개 이상
    # 2. 해당 기온구간에서 outer, top, pants 카테고리에서 각각 2개 이상의 클래스가 2이상
    # 위 조건을 모두 만족해야 true => 머신러닝 추천 시스템 사용 가능
    if(outer_valid and top_valid and pants_valid):
        return True
    else:
        print("충분한 데이터가 없습니다.")
        return False
    
    
# 🔹 카테고리 유효성 검사
def is_valid_category(count_dict):
    # 2 이상의 값만 필터링
    above_one = [count for count in count_dict.values() if count > 1]
    
    # 1개만 존재하면 False, 그렇지 않으면 True
    return len(above_one) >= 2



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
    


# 머신러닝 돌리지 않고 단순 추천 시스템
# 단순 추천 시스템은 사용자의 횟수와 공용 횟수를 적절히 반영하여 추천
def recommendation_simple(user, temp):
    user_id = user["localId"]  # 현재 로그인한 사용자의 UID
    token = user["idToken"]  # 인증 토큰
    
    # 🔵 Firebase에서 사용자자 기록(기온 구간별 옷 입은 횟수) 가져오기
    user_outer_data = db.child("users").child(user_id).child("cloth/outer").get(token=token).val()
    user_top_data = db.child("users").child(user_id).child("cloth/top").get(token=token).val()
    user_pants_data = db.child("users").child(user_id).child("cloth/pants").get(token=token).val()
    
    # 🔵 Firebase에서 공용 기록 가져오기
    public_outer_data = db.child("public/cloth/outer").get(token=token).val()
    public_top_data = db.child("public/cloth/top").get(token=token).val()
    public_pants_data = db.child("public/cloth/pants").get(token=token).val()
    
    # 🔵 기온 구간 찾기
    temp_range = find_temp_range(temp)
    
    # 비율 변환
    user_outer_ratio = process_cloth_data(user_outer_data, temp_range)
    user_top_ratio = process_cloth_data(user_top_data, temp_range)
    user_pants_ratio = process_cloth_data(user_pants_data, temp_range)
    
    public_outer_ratio = process_cloth_data(public_outer_data, temp_range) 
    public_top_ratio = process_cloth_data(public_top_data, temp_range)
    public_pants_ratio = process_cloth_data(public_pants_data, temp_range)
    
    
    # 🔵 해당 기온 구간의 옷 입은 횟수 가져오기
    user_outer_count = sum(user_outer_data[temp_range].values())
    user_top_count = sum(user_top_data[temp_range].values())
    user_pants_count = sum(user_pants_data[temp_range].values())
    
    # 횟수 별 반영 비율을 다르게 설정 (최대 60%)
    if(user_outer_count < 7):
        user_outer_weight = user_outer_count / 10
    else:
        user_outer_weight = 0.6   
    if(user_top_count < 7):
        user_top_weight = user_top_count / 10
    else:
        user_top_weight = 0.6
    if(user_pants_count < 7):
        user_pants_weight = user_pants_count / 10
    else:
        user_pants_weight = 0.6
    
    # 사용자 반영 비율과 공용 비율을 고려
    user_outer_ratio = {k: v * user_outer_weight for k, v in user_outer_ratio.items()}
    public_outer_ratio = {k: v * (1-user_outer_weight) for k, v in public_outer_ratio.items()}
    
    user_top_ratio = {k: v * user_top_weight for k, v in user_top_ratio.items()}
    public_top_ratio = {k: v * (1-user_top_weight) for k, v in public_top_ratio.items()}
    
    user_pants_ratio = {k: v * user_pants_weight for k, v in user_pants_ratio.items()}
    public_pants_ratio = {k: v * (1-user_pants_weight) for k, v in public_pants_ratio.items()}
    
    # 두 반영 비율을 합침
    outer_ratio = {k: user_outer_ratio.get(k, 0) + public_outer_ratio.get(k, 0) for k in set(user_outer_ratio) | set(public_outer_ratio)}
    top_ratio = {k: user_top_ratio.get(k, 0) + public_top_ratio.get(k, 0) for k in set(user_top_ratio) | set(public_top_ratio)}
    pants_ratio = {k: user_pants_ratio.get(k, 0) + public_pants_ratio.get(k, 0) for k in set(user_pants_ratio) | set(public_pants_ratio)}
    
    # 🔵 가장 많이 입은 옷 찾기
    outer = max(outer_ratio, key=outer_ratio.get)
    top = max(top_ratio, key=top_ratio.get)
    pants = max(pants_ratio, key=pants_ratio.get)
    
    print(f"outer_ratio: {outer_ratio}, top_ratio: {top_ratio}, pants_ratio: {pants_ratio}")
    print(f"outer: {outer}, top: {top}, pants: {pants}")
    
    
    outer = translate_choice(outer)
    top = translate_choice(top)
    pants = translate_choice(pants)
    
    return outer, top, pants


# actual_record 기록 + cloth 횟수 업데이트
def save_actual_record(user, date_str, temperature, outer, top, pants):
    temp_range = find_temp_range(temperature)

    user_id = user["localId"]  # 현재 로그인한 사용자의 UID
    token = user["idToken"]  # 인증 토큰
    
    public_outer_data = db.child("public/cloth/outer").get(token=token).val()
    public_top_data = db.child("public/cloth/top").get(token=token).val()
    public_pants_data = db.child("public/cloth/pants").get(token=token).val()
    
    public_outer_ratio = process_cloth_data(public_outer_data, temp_range)
    public_top_ratio = process_cloth_data(public_top_data, temp_range)
    public_pants_ratio = process_cloth_data(public_pants_data, temp_range)
    
    user_outer_data = db.child("users").child(user_id).child("cloth/outer").get(token=token).val()
    user_top_data = db.child("users").child(user_id).child("cloth/top").get(token=token).val()
    user_pants_data = db.child("users").child(user_id).child("cloth/pants").get(token=token).val()
    
    user_outer_ratio = process_cloth_data(user_outer_data, temp_range)
    user_top_ratio = process_cloth_data(user_top_data, temp_range)
    user_pants_ratio = process_cloth_data(user_pants_data, temp_range)
    
    outer_template = {
        "actual_choice": outer,
        "others_per_coat": round(public_outer_ratio.get("coat", 0), 2),
        "others_per_jacket": round(public_outer_ratio.get("jacket", 0), 2),
        "others_per_none": round(public_outer_ratio.get("none", 0), 2),
        "others_per_padding": round(public_outer_ratio.get("padding", 0), 2),
        "users_per_coat": round(user_outer_ratio.get("coat", 0), 2),
        "users_per_jacket": round(user_outer_ratio.get("jacket", 0), 2),
        "users_per_none": round(user_outer_ratio.get("none", 0), 2),
        "users_per_padding": round(user_outer_ratio.get("padding", 0), 2)
    }

    top_template = {
        "actual_choice": top,
        "others_per_brushed": round(public_top_ratio.get("brushed", 0), 2),
        "others_per_hoodie": round(public_top_ratio.get("hoodie", 0), 2),
        "others_per_longsleeve": round(public_top_ratio.get("longsleeve", 0), 2),
        "others_per_tshirt": round(public_top_ratio.get("tshirt", 0), 2),
        "users_per_brushed": round(user_top_ratio.get("brushed", 0), 2),
        "users_per_hoodie": round(user_top_ratio.get("hoodie", 0), 2),
        "users_per_longsleeve": round(user_top_ratio.get("longsleeve", 0), 2),
        "users_per_tshirt": round(user_top_ratio.get("tshirt", 0), 2)
    }

    pants_template = {
        "actual_choice": pants,
        "others_per_brushed": round(public_pants_ratio.get("brushed", 0), 2),
        "others_per_jean": round(public_pants_ratio.get("jean", 0), 2),
        "others_per_slacks": round(public_pants_ratio.get("slacks", 0), 2),
        "others_per_short": round(public_pants_ratio.get("short", 0), 2),
        "users_per_brushed": round(user_pants_ratio.get("brushed", 0), 2),
        "users_per_jean": round(user_pants_ratio.get("jean", 0), 2),
        "users_per_slacks": round(user_pants_ratio.get("slacks", 0), 2),
        "users_per_short": round(user_pants_ratio.get("short", 0), 2)
    }

    
    if db.child("users").child(user_id).child('actual_records').child(date_str.replace("-","")).get(token=token).val() is None:
        record_count = db.child("users").child(user_id).child('actual_records/record_count').get(token=token).val()
        print(f"기록 개수: {record_count}")
    
        db.child("users").child(user_id).child('actual_records').child('record_count').set(record_count + 1, token=token)
    
    # 🔵 Firebase에 데이터 저장
    db.child("users").child(user_id).child('actual_records').child(date_str.replace("-","")).set({
        "temperature": temperature,
        "outer": outer_template,
        "top": top_template,
        "pants": pants_template,
    }, token=token)
    
    print("기록 저장 완료")
    
    
    # cloth 횟수 업데이트 하는 부분
    
    #user
    try:
        # outer
        user_outer_path = f"users/{user_id}/cloth/outer/{temp_range}/{outer}"
        user_outer_count = db.child(user_outer_path).get(token=token).val()
        db.child(user_outer_path).set(user_outer_count + 1, token=token)
        # top
        user_top_path = f"users/{user_id}/cloth/top/{temp_range}/{top}"
        user_top_count = db.child(user_top_path).get(token=token).val()
        db.child(user_top_path).set(user_top_count + 1, token=token)
        # pants
        user_pants_path = f"users/{user_id}/cloth/pants/{temp_range}/{pants}"
        user_pants_count = db.child(user_pants_path).get(token=token).val()
        db.child(user_pants_path).set(user_pants_count + 1, token=token)
        
        print("유저 옷 횟수 업데이트 완료")
    except Exception as e:
        print(f"유저 옷 횟수 업데이트 실패: {e}")
    
    
    # public
    try:
        # outer
        public_outer_path = f"public/cloth/outer/{temp_range}/{outer}"
        public_outer_count = db.child(public_outer_path).get(token=token).val()
        db.child(public_outer_path).set(public_outer_count + 1, token=token)
        # top
        public_top_path = f"public/cloth/top/{temp_range}/{top}"
        public_top_count = db.child(public_top_path).get(token=token).val()
        db.child(public_top_path).set(public_top_count + 1, token=token)
        # pants
        public_pants_path = f"public/cloth/pants/{temp_range}/{pants}"
        public_pants_count = db.child(public_pants_path).get(token=token).val()
        db.child(public_pants_path).set(public_pants_count + 1, token=token)
        
        print("공용 옷 횟수 업데이트 완료")
    except Exception as e:
        print(f"공용 옷 횟수 업데이트 실패: {e}")
        
        
# 해당 날짜에 입었던 옷을 불러오는 함수
def load_actual_choices(user, date_str):
    user_id = user["localId"]
    token = user["idToken"]
    
    try:
        # 날짜 경로까지 전체 데이터 가져오기
        data = db.child("users").child(user_id).child('actual_records').child(date_str.replace("-", "")).get(token=token).val()
        
        if data is None:
            print("해당 날짜의 기록이 없습니다.")
            return None, None, None
        
        # outer, top, pants 각각의 actual_choice 값 추출
        outer_choice = data.get('outer', {}).get('actual_choice')
        top_choice = data.get('top', {}).get('actual_choice')
        pants_choice = data.get('pants', {}).get('actual_choice')
        
        return translate_choice(outer_choice), translate_choice(top_choice), translate_choice(pants_choice)
    
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None, None

def translate_choice(choice):
    if choice == "coat":
        return "코트"
    elif choice == "jacket":
        return "자켓"
    elif choice == "none":
        return "없음"
    elif choice == "padding":
        return "패딩"
    elif choice == "brushed":
        return "브러쉬드"
    elif choice == "hoodie":
        return "후드티"
    elif choice == "longsleeve":
        return "긴팔티"
    elif choice == "tshirt":
        return "반팔티"
    elif choice == "jean":
        return "청바지"
    elif choice == "slacks":
        return "슬랙스"
    elif choice == "short":
        return "반바지"
    else:
        return None