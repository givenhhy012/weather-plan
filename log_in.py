import pyrebase
from datetime import datetime


# Firebase 설정
firebase_config = {
    "apiKey": "AIzaSyDDoeGp8-kJrX68624sgfIkzscKO7aHg6k",
    "authDomain": "weather-plan.firebaseapp.com",
    "databaseURL": "https://weather-plan-default-rtdb.firebaseio.com/",
    "storageBucket": "weather-plan.firebasestorage.app"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()  # Realtime Database 사용

# 회원가입
# 회원가입 및 사용자 정보 저장
def sign_up(email, password):
    try:
        # Firebase Auth에 계정 생성
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user["localId"]  # 고유 사용자 ID
        token = user["idToken"]    # 인증 토큰

        # Realtime Database에 사용자 정보 저장
        db.child("users").child(user_id).set({
            "email": email,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, token=token)

        print("회원가입 및 정보 저장 성공")
        return user
    except Exception as e:
        print("회원가입 실패:", e)
        return None
        
# 로그인
def sign_in(email, password):    
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user  # 로그인한 사용자 정보 반환
    except Exception as e:
        print("로그인 실패:", e)
        return None

# 일정 추가
def save_schedule(user, title, date):
    """사용자의 일정 저장 (idToken 포함)"""
    try:
        user_id = user["localId"]  # 현재 로그인한 사용자의 UID
        token = user["idToken"]  # 인증 토큰

        db.child("users").child(user_id).child("schedules").push(
            {"title": title, "date": date}, token=token
        )
        print("일정 저장 성공")
    except Exception as e:
        print("일정 저장 실패:", e)

# 일정 조회
def get_schedules(user):
    try:
        user_id = user["localId"]
        token = user["idToken"]
        schedules = db.child("users").child(user_id).child("schedules").get()
        if schedules.val():
            print("===== 저장된 일정 =====")
            for schedule in schedules.each():
                print(schedule.val())  # 일정 출력
        else:
            print("저장된 일정이 없습니다.")
    except Exception as e:
        print("일정 조회 실패:", e)
        
# 일정 불러오기
def get_schedules_for_date(user, date_str):
    try:
        user_id = user["localId"]
        token = user["idToken"]
        schedules = db.child("users").child(user_id).child("schedules").get(token=token)
        result = []
        if schedules.each():
            for schedule in schedules.each():
                data = schedule.val()
                if data.get("date") == date_str:
                    result.append(data.get("title"))
        return result
    except Exception as e:
        print("일정 불러오기 실패:", e)
        return []

# 한달 일정 불러오기(성능 개선)
def get_all_schedules(user):
    """사용자의 전체 일정 불러오기"""
    try:
        user_id = user["localId"]
        token = user["idToken"]
        schedules = db.child("users").child(user_id).child("schedules").get(token=token)
        result = []
        if schedules.each():
            for schedule in schedules.each():
                result.append(schedule.val())
        return result
    except Exception as e:
        print("전체 일정 불러오기 실패:", e)
        return []

