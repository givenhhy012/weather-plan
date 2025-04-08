import pyrebase

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
def sign_up(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        print("회원가입 실패:", e)
        
        

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
def get_schedules(user_id):
    try:
        schedules = db.child("users").child(user_id).child("schedules").get()
        if schedules.val():
            print("===== 저장된 일정 =====")
            for schedule in schedules.each():
                print(schedule.val())  # 일정 출력
        else:
            print("저장된 일정이 없습니다.")
    except Exception as e:
        print("일정 조회 실패:", e)

"""

# 실행 예제
choice = input("1. 회원가입\n2. 로그인\n선택: ")

email = input("이메일: ")
password = input("비밀번호: ")

if choice == "1":
    sign_up(email, password)
elif choice == "2":
    user = sign_in(email, password)
    if user:
        user_id = user["localId"]  # UID 가져오기
        while True:
            print("User UID:", user["localId"])
            action = input("1. 일정 추가\n2. 일정 조회\n3. 종료\n선택: ")
            if action == "1":
                title = input("일정 제목: ")
                date = input("날짜 (YYYY-MM-DD): ")
                save_schedule(user, title, date)
            elif action == "2":
                get_schedules(user_id)
            elif action == "3":
                break
                
                
                """