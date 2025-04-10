import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import random
from datetime import datetime

import log_in
import apiusing

# ----- 초기 설정 -----
root = tk.Tk()
root.title("Login and Calendar")
root.geometry("1280x720")

schedule = {}  # 일정 저장용 딕셔너리
now = datetime.now()
current_year = now.year
current_month = now.month

FONT_LARGE = ("Helvetica", 16)
FONT_MEDIUM = ("Helvetica", 12)

# ----- 로그인 프레임 -----
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

id_label = tk.Label(login_frame, text="ID (email): ", font=FONT_MEDIUM)
id_label.grid(row=0, column=0, padx=5, pady=5)
id_entry = tk.Entry(login_frame, font=FONT_MEDIUM, width=20)
id_entry.grid(row=0, column=1, padx=5, pady=5)

pw_label = tk.Label(login_frame, text="PW (6자 이상): ", font=FONT_MEDIUM)
pw_label.grid(row=1, column=0, padx=5, pady=5)
pw_entry = tk.Entry(login_frame, show="*", font=FONT_MEDIUM, width=20)
pw_entry.grid(row=1, column=1, padx=5, pady=5)

# ----- 로그인/회원가입 기능 -----
def sign_in_calendar():
    email = id_entry.get()
    password = pw_entry.get()
    user = log_in.sign_in(email, password)
    if user:
        show_calendar()
    else:
        messagebox.showerror("Login Failed", "로그인 실패")

def sign_up_calendar():
    email = id_entry.get()
    password = pw_entry.get()
    user = log_in.sign_up(email, password)
    if user:
        messagebox.showinfo("Sign Up Success", "회원가입 성공")
        show_calendar()
    else:
        messagebox.showerror("Sign Up Failed", "회원가입 실패")

# ----- 날씨 정보 -----
def get_weather_info(date):
    weather_conditions = ["맑음", "흐림", "비", "눈", "폭풍"]
    temperature = apiusing.get_temperature()
    condition = random.choice(weather_conditions)
    return f"{date} 날씨: {condition}, {temperature}℃"

# ----- 일정 및 날씨 창 -----
def show_details(date):
    def save_schedule():
        event = schedule_entry.get()
        if event:
            schedule[date] = event
            update_calendar()
            messagebox.showinfo("Schedule Added", f"일정 저장: {date} - {event}")
            details_window.destroy()
        else:
            messagebox.showwarning("Empty Schedule", "일정을 입력해주세요.")

    details_window = tk.Toplevel(root)
    details_window.title(f"{date} 상세 정보")
    details_window.geometry("400x200")

    weather_frame = tk.Frame(details_window, padx=10, pady=10)
    weather_frame.grid(row=0, column=0, sticky="nsew")
    weather_info = get_weather_info(date)
    weather_label = tk.Label(weather_frame, text=weather_info, font=FONT_MEDIUM)
    weather_label.pack()

    schedule_frame = tk.Frame(details_window, padx=10, pady=10)
    schedule_frame.grid(row=0, column=1, sticky="nsew")
    schedule_label = tk.Label(schedule_frame, text="일정 추가:", font=FONT_MEDIUM)
    schedule_label.pack(pady=5)
    schedule_entry = tk.Entry(schedule_frame, width=20)
    schedule_entry.pack(pady=5)
    save_button = tk.Button(schedule_frame, text="저장", command=save_schedule)
    save_button.pack(pady=5)

# ----- 캘린더 업데이트 -----
def update_calendar(*args):
    year = int(year_combobox.get())
    month = int(month_combobox.get())
    month_label.config(text=f"{year}년 {month}월")
    cal = calendar.monthcalendar(year, month)

    # 기존 버튼 제거
    for widget in calendar_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    # 요일 라벨
    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    for idx, day in enumerate(weekdays):
        fg_color = "red" if day == "일" else ("blue" if day == "토" else "black")
        label = tk.Label(calendar_frame, text=day, font=FONT_MEDIUM, fg=fg_color)
        label.grid(row=1, column=idx)

    # 날짜 버튼
    for i, week in enumerate(cal):
        for j, day in enumerate(week):
            if day != 0:
                date = f"{year}-{month:02d}-{day:02d}"
                text = f"{day}"
                if date in schedule:
                    text += "★"
                fg_color = "red" if j == 0 else ("blue" if j == 6 else "black")
                btn = tk.Button(
                    calendar_frame,
                    text=text,
                    command=lambda d=date: show_details(d),
                    width=10,
                    height=4,
                    fg=fg_color
                )
                btn.grid(row=i+2, column=j, padx=2, pady=2)

# ----- 캘린더 표시 -----
def show_calendar():
    login_frame.pack_forget()
    control_frame.pack(pady=10)
    calendar_frame.pack(pady=20)
    update_calendar()

# ----- 연도/월 선택 프레임 -----
control_frame = tk.Frame(root)
year_label = tk.Label(control_frame, text="연도:")
year_label.grid(row=0, column=0, padx=5)

year_combobox = ttk.Combobox(control_frame, values=list(range(2000, 2101)), state="readonly", width=8)
year_combobox.set(current_year)
year_combobox.grid(row=0, column=1, padx=5)
year_combobox.bind("<<ComboboxSelected>>", update_calendar)

month_label_select = tk.Label(control_frame, text="월:")
month_label_select.grid(row=0, column=2, padx=5)

month_combobox = ttk.Combobox(control_frame, values=list(range(1, 13)), state="readonly", width=5)
month_combobox.set(current_month)
month_combobox.grid(row=0, column=3, padx=5)
month_combobox.bind("<<ComboboxSelected>>", update_calendar)

# ----- 캘린더 프레임 -----
calendar_frame = tk.Frame(root)
month_label = tk.Label(calendar_frame, font=("Arial", 16))
month_label.grid(row=0, column=0, columnspan=7)

# ----- 로그인/회원가입 버튼 -----
login_button = tk.Button(login_frame, text="Login", command=sign_in_calendar)
login_button.grid(row=2, column=0, columnspan=2, pady=10)

signup_button = tk.Button(login_frame, text="Sign Up", command=sign_up_calendar)
signup_button.grid(row=3, column=0, columnspan=2, pady=10)

# ----- 초기 실행 -----
year_combobox.set(current_year)
month_combobox.set(current_month)
update_calendar()

root.mainloop()
