import pyrebase
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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

user_id = 'users/user123'  # 사용자 ID 설정


# 학습 시 사용된 Feature 이름을 명확히 설정
FEATURE_NAMES = [
    'temperature',
    'others_per_coat', 'others_per_jacket', 'others_per_none', 'others_per_padding',
    'users_per_coat', 'users_per_jacket', 'users_per_none', 'users_per_padding'
]

# # actual_record의 개수 세는 함수였었던것
# def count_subfolders(path):
#     try:
#         # shallow()를 사용해 키만 가져오기
#         data = db.child(path).shallow().get()
        
#         if data.val() is None:
#             print("경로에 하위 폴더가 없습니다.")
#             return 0

#         # 키의 개수만 세기 때문에 매우 빠르게 처리됨
#         subfolder_count = len(data.val())
#         print(f"하위 폴더의 개수: {subfolder_count}")
#         return subfolder_count

#     except Exception as e:
#         print(f"오류 발생: {e}")
#         return 0
    
    
# actual_record의 개수 세는 함수
def get_max_index(path):
    try:
        # limitToLast(1)을 사용하여 가장 마지막 키만 가져옵니다.
        data = db.child(path).order_by_key().limit_to_last(1).get()

        if data.val() is None:
            print("경로에 하위 폴더가 없습니다.")
            return None

        # 마지막으로 가져온 데이터의 키를 추출
        max_index = list(data.val().keys())[0]
        print(f"가장 큰 번호: {max_index}")
        return int(max_index)

    except Exception as e:
        print(f"오류 발생: {e}")
        return None



# 🔹 Firebase 데이터 로딩 함수
def fetch_firebase_data():
    # Public 데이터 로딩
    public_data = 'public/cloth/'
    public_outer_data = db.child(public_data + 'outer').get().val()
    public_top_data = db.child(public_data + 'top').get().val()
    public_pants_data = db.child(public_data + 'pants').get().val()
    
    # User 데이터 로딩
    users_data = user_id + '/cloth/'
    users_outer_data = db.child(users_data + 'outer').get().val()
    users_top_data = db.child(users_data + 'top').get().val()
    users_pants_data = db.child(users_data + 'pants').get().val()
    
    # Actual Records 로딩
    actual_data = user_id + '/actual_records/'
    all_actual_data = db.child(actual_data).get().val()
    
    return (public_outer_data, public_top_data, public_pants_data, 
            users_outer_data, users_top_data, users_pants_data, 
            all_actual_data)

# 🔹 학습 데이터 생성 함수
def prepare_training_data(all_actual_data):
    records = []

    for key, data in all_actual_data.items():
        temperature = data.get('temperature')
        temp_range = find_temp_range(temperature)

        # 🔹 Outer Features
        outer_data = data.get('outer', {})
        outer_record = {
            'temperature': temperature,
            'outer': outer_data.get('actual_choice'),
        }
        for key, value in outer_data.items():
            if key.startswith('others_per_') or key.startswith('users_per_'):
                outer_record[key] = value
        
        records.append(outer_record)
    
    # 🔹 DataFrame 생성
    df = pd.DataFrame(records)
    df.fillna(0, inplace=True)  # 결측치 처리

    # 🔹 Features와 Labels 분리
    feature_columns = [col for col in df.columns if col not in ['outer', 'temperature']]
    X = df[['temperature'] + feature_columns]
    y = df['outer']
    
    return X, y

# 🔹 모델 학습 함수
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    
    # 🔹 모델 평가
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    return model


# 🔹 예측 함수
def predict_outfit(model, temperature, public_data, user_data):
    """
    주어진 기온과 데이터로 모델을 이용해 추천 의상을 예측합니다.
    """
    features_df = prepare_features(temperature, public_data, user_data)

    # 예측
    prediction = model.predict(features_df)  # 모델 예측

    return prediction




# 🔹 전체 실행 함수
def run_recommendation_system():
    (public_outer_data, public_top_data, public_pants_data, 
     users_outer_data, users_top_data, users_pants_data, 
     all_actual_data) = fetch_firebase_data()
    
    # 🔹 학습 데이터 준비
    X, y = prepare_training_data(all_actual_data)

    # 🔹 모델 학습
    model = train_model(X, y)

    # 🔹 예측 실행 (예시)
    temperature = 18.8
    others_ratio = {'others_per_coat': 0.05, 'others_per_jacket': 0.65, 'others_per_none': 0.2, 'others_per_padding': 0.1}
    users_ratio = {'users_per_coat': 0.05, 'users_per_jacket': 0.7, 'users_per_none': 0.15, 'users_per_padding': 0.1}
    
    recommended_outer = predict_outfit(model, temperature, others_ratio, users_ratio)
    print(f"추천 아우터: {recommended_outer}")


# # 🔹 공용 데이터를 DataFrame으로 변환
# def process_public_data(public_data):
#     df_list = []
#     for temp_range, count in public_data.items():
#         df_list.append({'temperature_range': temp_range, 'count': count})
#     return pd.DataFrame(df_list)


def find_temp_range(temp):
    if temp < 5:
        return '<5'
    elif temp < 10:
        return '<10'
    elif temp < 15:
        return '<15'
    elif temp < 20:
        return '<20'
    else:
        return '>=20'


def process_cloth_data(cloth_data, temp_range):
    """
    특정 기온 구간에 해당하는 옷 착용 횟수를 비율로 변환합니다.
    """
    if temp_range in cloth_data:
        total_count = sum(cloth_data[temp_range].values())
        if total_count == 0:
            return {k: 0 for k in cloth_data[temp_range]}
        else:
            return {k: v / total_count for k, v in cloth_data[temp_range].items()}
    else:
        return {}
    

def prepare_features(temperature, public_data, user_data):
    """
    주어진 기온에 맞는 공용 데이터와 사용자 데이터를 비율로 변환하여 Feature로 생성합니다.
    """
    temp_range = find_temp_range(temperature)

    # 🔹 비율로 변환
    others_ratio = process_cloth_data(public_data, temp_range)
    users_ratio = process_cloth_data(user_data, temp_range)

    # 🔹 Feature Vector 생성
    features = [temperature]

    # 🔹 공용 비율을 'others_per_' prefix를 붙여서 생성
    for cloth in ['coat', 'jacket', 'none', 'padding']:  # 예시로 나열된 옷 종류 사용
        features.append(others_ratio.get(cloth, 0))  # 해당 옷의 비율 추가, 없으면 0

    # 🔹 사용자 비율을 'users_per_' prefix를 붙여서 생성
    for cloth in ['coat', 'jacket', 'none', 'padding']:  # 예시로 나열된 옷 종류 사용
        features.append(users_ratio.get(cloth, 0))  # 해당 옷의 비율 추가, 없으면 0

    # 🔹 DataFrame으로 변환하여 반환
    return pd.DataFrame([features], columns=FEATURE_NAMES)



# def create_pivot(df, user_data=None, example_temp=None):
#     pivot_df = df.pivot_table(index='temperature_range', columns='cloth_type', values='count', fill_value=0)
#     pivot_df['total'] = pivot_df.sum(axis=1)
    
#     if user_data is not None:
#         for cloth in pivot_df.columns:
#             if cloth != 'total':
#                 pivot_df[f'{cloth}_user_probability'] = user_data.get(cloth, 0) / pivot_df['total']
    
#     if example_temp is not None:
#         temp_range = find_temp_range(example_temp)
#         example_probabilities = pivot_df.loc[temp_range, :].values.reshape(1, -1)
#         example_input = pd.DataFrame(example_probabilities, columns=pivot_df.columns)
        
#         return pivot_df, example_input

#     for cloth in pivot_df.columns:
#         if cloth != 'total':
#             pivot_df[f'{cloth}_probability'] = pivot_df[cloth] / pivot_df['total']
    
#     return pivot_df


# def train_model(X_train, y_train):
#     model = LogisticRegression(max_iter=200)
#     model.fit(X_train, y_train)
#     return model


# def evaluate_model(model, X_test, y_test):
#     y_pred = model.predict(X_test)
#     accuracy = accuracy_score(y_test, y_pred)
#     return accuracy

    
# def recommendation_system_machine_learning(temperature):
#     public_outer_data, public_top_data, public_pants_data, users_outer_data, users_top_data, users_pants_data, actual_outer_data, actual_top_data, actual_pants_data = fetch_firebase_data()
    
#     # 🔵 실제 기록 데이터프레임 생성
#     actual_outer_df = pd.DataFrame({'outer': actual_outer_data})
#     actual_top_df = pd.DataFrame({'top': actual_top_data})
#     actual_pants_df = pd.DataFrame({'pants': actual_pants_data})

#     # 🔵 공용 데이터 프레임 생성
#     public_outer_df = process_public_data(public_outer_data)
#     public_top_df = process_public_data(public_top_data)
#     public_pants_df = process_public_data(public_pants_data)

#     # 🔵 각 항목에 대해 Pivot 생성
#     pivot_outer_df, _ = create_pivot(public_outer_df, user_data=users_outer_data, example_temp=temperature)
#     pivot_top_df, _ = create_pivot(public_top_df, user_data=users_top_data, example_temp=temperature)
#     pivot_pants_df, _ = create_pivot(public_pants_df, user_data=users_pants_data, example_temp=temperature)

#     # 🔵 실제 기록에 온도구간 추가
#     actual_outer_df['temperature_range'] = actual_outer_df['outer'].apply(find_temp_range)
#     actual_top_df['temperature_range'] = actual_top_df['top'].apply(find_temp_range)
#     actual_pants_df['temperature_range'] = actual_pants_df['pants'].apply(find_temp_range)

#     # 🔵 병합
#     merged_outer_df = pd.merge(actual_outer_df, pivot_outer_df, on='temperature_range', how='left')
#     merged_top_df = pd.merge(actual_top_df, pivot_top_df, on='temperature_range', how='left')
#     merged_pants_df = pd.merge(actual_pants_df, pivot_pants_df, on='temperature_range', how='left')

#     # 🔵 Feature(X)와 Label(y) 설정
#     outer_feature_columns = ['padding', 'none', 'coat', 'jacket']
#     top_feature_columns = ['brushed', 'hoodie', 'long-sleeve', 't-shirts']
#     pants_feature_columns = ['brushed', 'jean', 'slacks', 'shorts']

#     X_outer = merged_outer_df[outer_feature_columns].fillna(0)
#     y_outer = merged_outer_df['outer']

#     X_top = merged_top_df[top_feature_columns].fillna(0)
#     y_top = merged_top_df['top']

#     X_pants = merged_pants_df[pants_feature_columns].fillna(0)
#     y_pants = merged_pants_df['pants']

#     # 🔵 훈련/테스트 데이터 분리
#     X_outer_train, X_outer_test, y_outer_train, y_outer_test = train_test_split(X_outer, y_outer, test_size=0.2, random_state=42)
#     X_top_train, X_top_test, y_top_train, y_top_test = train_test_split(X_top, y_top, test_size=0.2, random_state=42)
#     X_pants_train, X_pants_test, y_pants_train, y_pants_test = train_test_split(X_pants, y_pants, test_size=0.2, random_state=42)

#     # 🔵 모델 학습
#     model_outer = train_model(X_outer_train, y_outer_train)
#     model_top = train_model(X_top_train, y_top_train)
#     model_pants = train_model(X_pants_train, y_pants_train)

#     # 🔵 예측을 위한 데이터 준비
#     temperature_range = find_temp_range(temperature)

#     example_outer_probs = pivot_outer_df.loc[temperature_range, outer_feature_columns].values.reshape(1, -1)
#     example_top_probs = pivot_top_df.loc[temperature_range, top_feature_columns].values.reshape(1, -1)
#     example_pants_probs = pivot_pants_df.loc[temperature_range, pants_feature_columns].values.reshape(1, -1)

#     example_outer_input = pd.DataFrame(example_outer_probs, columns=outer_feature_columns)
#     example_top_input = pd.DataFrame(example_top_probs, columns=top_feature_columns)
#     example_pants_input = pd.DataFrame(example_pants_probs, columns=pants_feature_columns)

#     # 🔵 예측
#     predicted_outer = model_outer.predict(example_outer_input)
#     predicted_top = model_top.predict(example_top_input)
#     predicted_pants = model_pants.predict(example_pants_input)

#     print(f'{temperature}도에서는 추천하는 아우터: {predicted_outer[0]}')
#     print(f'{temperature}도에서는 추천하는 상의: {predicted_top[0]}')
#     print(f'{temperature}도에서는 추천하는 하의: {predicted_pants[0]}')
    
#     return predicted_outer[0], predicted_top[0], predicted_pants[0]



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
def recommendation_system_simple(temperature):
    # 🔵 Firebase에서 공용 기록(기온 구간별 옷 입은 횟수) 가져오기
    public_data_path = 'public/cloth/'
    public_data = db.child(public_data_path).get().val()
    
    return get_most_common_clothes(public_data, temperature)


# # 데이터 재 구조화를 위한 함수였었던것
# def restructure_data():
#     path = f'users/user123/actual_records'
    
#     try:
#         # 1️⃣ 기존 데이터를 모두 가져오기
#         data = db.child(path).get()
        
#         if data.val() is None:
#             print("기존 데이터가 없습니다.")
#             return
        
#         # 2️⃣ 날짜 순으로 정렬된 키를 리스트로 저장
#         sorted_keys = sorted(data.val().keys())
        
#         # 3️⃣ 새로운 구조로 저장
#         for new_index, old_key in enumerate(sorted_keys):
#             old_path = f"{path}/{old_key}"
#             new_path = f"{path}/{new_index}"

#             # 데이터 읽어서 새로운 위치에 저장
#             record_data = db.child(old_path).get().val()
#             db.child(new_path).set(record_data)
            
#             # 기존 데이터 삭제
#             db.child(old_path).remove()
        
#         print("데이터 재구조화가 완료되었습니다.")
    
#     except Exception as e:
#         print(f"오류 발생: {e}")


# # 새로운 키와 값을 추가하는 함수였었던것
# def add_key_value_to_temperature_path(user_id, new_key, new_value):
#     path = f'users/{user_id}/actual_records/0'
    
#     try:
#         # Firebase 경로에 새로운 키와 값을 추가
#         update_data = {new_key: new_value}
#         db.child(path).update(update_data)
#         print(f"'{new_key}': '{new_value}'가 추가되었습니다.")
    
#     except Exception as e:
#         print(f"오류 발생: {e}")


# # 데이터 재구조화를 위한 함수였었던것
# def reformat_keys():
#     try:
#         # Firebase 데이터 참조: 'users/user123/actual_records' 경로에서 데이터 가져오기
#         data = db.child('users/user123/actual_records').get()

#         if data.val() is None:
#             print("데이터가 존재하지 않습니다.")
#             return

#         # 새로운 형식으로 변환된 데이터를 저장할 딕셔너리
#         new_data = {}

#         # 데이터가 리스트일 경우
#         if isinstance(data.val(), list):
#             for idx, value in enumerate(data.val()):
#                 # 숫자형 인덱스를 3자리 문자열로 변환
#                 new_key = str(idx).zfill(3)  # 예: 0 -> '000', 1 -> '001'
#                 new_data[new_key] = value
#         else:
#             # 데이터가 딕셔너리일 경우
#             for key, value in data.val().items():
#                 # 기존의 숫자형 키를 3자리 문자열로 변환
#                 new_key = str(int(key)).zfill(3)  # 예: 0 -> '000', 1 -> '001'
#                 new_data[new_key] = value

#         # Firebase에 새로운 데이터 저장
#         db.child('users/user123/actual_records').set(new_data)
#         print("키가 성공적으로 재구성되었습니다.")

#     except Exception as e:
#         print(f"오류 발생: {e}")


# # 알고리즘 예시 실행
# example_temperature = 12

# if int(get_max_index('users/user123/actual_records/')) <15:
#     outer,top,pants = recommendation_system_simple(example_temperature)
    
#     print(f"추천 아우터: {outer}")
#     print(f"추천 상의: {top}")
#     print(f"추천 하의: {pants}")
    
# else:
#     outer,top,pants = recommendation_system_machine_learning(example_temperature)
    
#     print(f"추천 아우터: {outer}")
#     print(f"추천 상의: {top}")
#     print(f"추천 하의: {pants}")


# 🔹 테스트 코드
# 🔹 테스트 코드
def test_recommendation_system():
    print("=== 🔹 Firebase 데이터 로딩 중... ===")
    (public_outer_data, public_top_data, public_pants_data, 
     users_outer_data, users_top_data, users_pants_data, 
     all_actual_data) = fetch_firebase_data()
    
    print("=== 🔹 학습 데이터 준비 중... ===")
    X, y = prepare_training_data(all_actual_data)

    print("=== 🔹 모델 학습 중... ===")
    model = train_model(X, y)

    print("\n=== 🔹 예측 테스트 ===")
    test_cases = [
        {"temperature": 3, "public_data": public_outer_data, "user_data": users_outer_data},
        {"temperature": 12, "public_data": public_top_data, "user_data": users_top_data},
        {"temperature": 18.8, "public_data": public_pants_data, "user_data": users_pants_data}
    ]

    for idx, case in enumerate(test_cases, 1):
        print(f"\n[테스트 케이스 {idx}]")
        print(f"🌡️ 기온: {case['temperature']}도")
        
        prediction = predict_outfit(model, case['temperature'], case['public_data'], case['user_data'])
        print(f"👚 추천 의류: {prediction}")
    
    print("\n=== 🔹 모든 테스트 완료 ===")

# 🔹 테스트 실행
test_recommendation_system()
