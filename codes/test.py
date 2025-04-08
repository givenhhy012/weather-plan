import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import random  # 날씨 데이터를 임의로 생성하기 위한 라이브러리
from datetime import datetime

import log_in
import apiusing

# 메인 창 생성
root = tk.Tk()
root.title("Login and Calendar")
root.geometry("1280x720")  # 16:9 비율로 설정

# 일정 저장을 위한 딕셔너리
schedule = {}

# 현재 날짜를 기준으로 초기값 설정
now = datetime.now()
current_year = now.year
current_month = now.month

# 로그인 프레임 생성
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

# 폰트 설정
FONT_LARGE = ("Helvetica", 16)


# ID 입력
id_label = tk.Label(login_frame, text="ID: ")
id_label.grid(row=0, column=0, padx=5, pady=5)
id_entry = tk.Entry(login_frame)
id_entry.grid(row=0, column=1, padx=5, pady=5)

# PW 입력
pw_label = tk.Label(login_frame, text="PW: ")
pw_label.grid(row=1, column=0, padx=5, pady=5)
pw_entry = tk.Entry(login_frame, show="*")
pw_entry.grid(row=1, column=1, padx=5, pady=5)


def sign_in_calendar():
    email = id_entry.get()
    password = pw_entry.get()

    # 로그인 처리
    user = log_in.sign_in(email, password)
    if user:
        show_calendar()  # 로그인 성공 시 캘린더 표시
    else:
        messagebox.showerror("Login Failed", "로그인 실패")
        
def sign_up_calendar():
    email = id_entry.get()
    password = pw_entry.get()

    # 회원가입 처리
    user = log_in.sign_up(email, password)
    if user:
        messagebox.showinfo("Sign Up Success", "회원가입 성공")
        show_calendar()  # 회원가입 성공 시 캘린더 표시
    else:
        messagebox.showerror("Sign Up Failed", "회원가입 실패")

# 날씨 정보 생성 함수 (예제용)
def get_weather_info(date):
    weather_conditions = ["맑음", "흐림", "비", "눈", "폭풍"]
    temperature = apiusing.get_temperature()  # apiusing 모듈에서 기온 가져오기
    condition = random.choice(weather_conditions)
    return f"{date} 날씨: {condition}, {temperature}℃"

# 일정 및 날씨 창 생성 함수
def show_details(date):
    def save_schedule():
        event = schedule_entry.get()
        if event:
            schedule[date] = event
            messagebox.showinfo("Schedule Added", f"일정이 저장되었습니다: {date} - {event}")
            details_window.destroy()
        else:
            messagebox.showwarning("Empty Schedule", "일정을 입력해주세요.")

    # 일정 및 날씨 창 생성
    details_window = tk.Toplevel(root)
    details_window.title(f"{date} 상세 정보")
    details_window.geometry("400x200")  # 창 크기 설정

    # 날씨 정보 출력 (왼쪽)
    weather_frame = tk.Frame(details_window, padx=10, pady=10)
    weather_frame.grid(row=0, column=0, sticky="nsew")  # 왼쪽에 배치
    weather_info = get_weather_info(date)
    weather_label = tk.Label(weather_frame, text=weather_info, font=("Arial", 12))
    weather_label.pack()

    # 일정 추가 버튼 (오른쪽)
    schedule_frame = tk.Frame(details_window, padx=10, pady=10, relief="solid", bd=1)
    schedule_frame.grid(row=0, column=1, sticky="nsew")  # 오른쪽에 배치
    schedule_label = tk.Label(schedule_frame, text="일정 추가:", font=("Arial", 12))
    schedule_label.pack(pady=5)
    schedule_entry = tk.Entry(schedule_frame, width=20)
    schedule_entry.pack(pady=5)
    save_button = tk.Button(schedule_frame, text="저장", command=save_schedule)
    save_button.pack(pady=5)

    # 열 구분 비율 설정
    details_window.grid_columnconfigure(0, weight=1)
    details_window.grid_columnconfigure(1, weight=1)

# 캘린더 업데이트 함수
def update_calendar(*args):
    year = int(year_combobox.get())
    month = int(month_combobox.get())
    month_label.config(text=f"{year}년 {month}월")
    cal = calendar.monthcalendar(year, month)

    # 기존 버튼 제거
    for widget in calendar_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    # 날짜 버튼 생성
    for i, week in enumerate(cal):
        for j, day in enumerate(week):
            if day != 0:  # 날짜가 존재하는 경우
                date = f"{year}-{month:02d}-{day:02d}"
                btn = tk.Button(calendar_frame, text=str(day), command=lambda d=date: show_details(d), width=5)
                btn.grid(row=i+2, column=j)

# 달력 표시 함수
def show_calendar():
    login_frame.pack_forget()  # 로그인 프레임 숨기기
    control_frame.pack(pady=10)  # 연도/월 선택 프레임 표시
    calendar_frame.pack(pady=20)  # 달력 프레임 표시
    update_calendar()

# 연도 및 월 선택 프레임
control_frame = tk.Frame(root)
year_label = tk.Label(control_frame, text="연도:")
year_label.grid(row=0, column=0, padx=5)

# 연도 선택 콤보박스
year_combobox = ttk.Combobox(control_frame, values=list(range(2000, 2101)), state="readonly", width=8)
year_combobox.set(current_year)
year_combobox.grid(row=0, column=1, padx=5)
year_combobox.bind("<<ComboboxSelected>>", update_calendar)

month_label = tk.Label(control_frame, text="월:")
month_label.grid(row=0, column=2, padx=5)

# 월 선택 콤보박스
month_combobox = ttk.Combobox(control_frame, values=list(range(1, 13)), state="readonly", width=5)
month_combobox.set(current_month)
month_combobox.grid(row=0, column=3, padx=5)
month_combobox.bind("<<ComboboxSelected>>", update_calendar)

# 캘린더 프레임 생성
calendar_frame = tk.Frame(root)
month_label = tk.Label(calendar_frame, font=("Arial", 16))
month_label.grid(row=0, column=0, columnspan=7)

# 로그인 버튼
login_button = tk.Button(login_frame, text="Login", command=sign_in_calendar)
login_button.grid(row=2, column=0, columnspan=2, pady=10)

# 회원가입 버튼
signup_button = tk.Button(login_frame, text="Sign Up", command=sign_up_calendar)
signup_button.grid(row=3, column=0, columnspan=2, pady=10)

# 메인 루프 시작
root.mainloop()