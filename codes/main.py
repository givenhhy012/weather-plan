import tkinter as tk
from tkinter import messagebox, ttk
from log_in import sign_in, save_clothes_record  # 옷차림 저장 함수 임포트
from datetime import datetime

# 가정: 로그인은 이미 되어 있고 user 정보는 아래와 같이 주어진다
user = {
    "localId": "샘플UID",
    "idToken": "샘플토큰"
}

def recommend_clothes(temp):
    if temp >= 28:
        return "반팔, 반바지 추천"
    elif 23 <= temp < 28:
        return "얇은 셔츠, 반바지 추천"
    elif 17 <= temp < 23:
        return "긴팔, 얇은 가디건 추천"
    elif 12 <= temp < 17:
        return "자켓, 니트 추천"
    elif 9 <= temp < 12:
        return "코트, 기모 후드 추천"
    else:
        return "패딩, 두꺼운 옷 추천"

def show_recommendation():
    temp = 13  # 예시 온도
    result = recommend_clothes(temp)
    result_label.config(text=f"추천 옷차림: {result}")
    record_btn.pack(pady=5)  # "오늘의 옷 기록하기" 버튼 보이기

def show_record_options():
    dropdown_frame.pack(pady=10)

def save_clothing():
    outer = outer_var.get()
    top = top_var.get()
    bottom = bottom_var.get()
    today = datetime.now().strftime("%Y-%m-%d")

    save_clothes_record(user, today, outer, top, bottom)
    messagebox.showinfo("저장 완료", "오늘의 옷차림이 저장되었습니다.")

# GUI 구성
root = tk.Tk()
root.title("날씨 일정 관리")
root.geometry("400x500")

temp_label = tk.Label(root, text="오늘의 최고기온: 13°C", font=("Arial", 14))
temp_label.pack(pady=10)

recommend_btn = tk.Button(root, text="옷차림 추천", command=show_recommendation)
recommend_btn.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

record_btn = tk.Button(root, text="오늘의 옷 기록하기", command=show_record_options)

# 드롭다운 구성
dropdown_frame = tk.Frame(root)

outer_var = tk.StringVar()
outer_options = ["패딩", "코트", "자켓", "바람막이", "가디건", "후드집업", "없음"]
outer_menu = ttk.Combobox(dropdown_frame, textvariable=outer_var, values=outer_options, state="readonly")
outer_menu.set("아우터 선택")
outer_menu.pack()

top_var = tk.StringVar()
top_options = ["기모 의류", "니트", "후드티", "맨투맨", "롱슬리브", "반팔"]
top_menu = ttk.Combobox(dropdown_frame, textvariable=top_var, values=top_options, state="readonly")
top_menu.set("상의 선택")
top_menu.pack()

bottom_var = tk.StringVar()
bottom_options = ["기모바지", "청바지", "슬랙스", "반바지(치마)"]
bottom_menu = ttk.Combobox(dropdown_frame, textvariable=bottom_var, values=bottom_options, state="readonly")
bottom_menu.set("하의 선택")
bottom_menu.pack()

save_btn = tk.Button(dropdown_frame, text="저장하기", command=save_clothing)
save_btn.pack(pady=10)

root.mainloop()
