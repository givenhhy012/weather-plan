import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import random
from datetime import datetime

import log_in
import apiusing


calendar.setfirstweekday(calendar.SUNDAY)

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
    weather_condition = apiusing.get_weather_condition(date)
    temperature = apiusing.get_temperature(date)
    
    tmin, tmax = apiusing.get_min_max_temperature(date)
    
    average = (tmin + tmax) / 2 if tmin and tmax else None
    # 자정~05:00까지는 예보 데이터 없음 => 최고, 최저, 평균 안나옴
    if average is not None:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온: {average}℃"
        )
    else:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온 정보 없음"
        )

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
    details_window.geometry("800x400")

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

    for widget in calendar_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    for idx, day in enumerate(weekdays):
        fg_color = "red" if day == "일" else ("blue" if day == "토" else "black")
        label = tk.Label(calendar_frame, text=day, font=FONT_MEDIUM, fg=fg_color)
        label.grid(row=1, column=idx)

    for i, week in enumerate(cal):
        for j, day in enumerate(week):
            if day != 0:
                date = f"{year}-{month:02d}-{day:02d}"
                text = f"{day}"
                if date in schedule:
                    num_stars = len(schedule[date].split(","))
                    text += "★" * num_stars
                fg_color = "red" if j == 0 else ("blue" if j == 6 else "black")
                bg_color = "lightyellow" if date == f"{now.year}-{now.month:02d}-{now.day:02d}" else "white"

                btn = tk.Button(
                    calendar_frame,
                    text=text,
                    command=lambda d=date: show_details(d),
                    width=10,
                    height=4,
                    fg=fg_color,
                    bg=bg_color
                )
                btn.grid(row=i+2, column=j, padx=2, pady=2)

# ----- 월 변경 함수 -----
def change_month(direction):
    month = int(month_combobox.get())
    year = int(year_combobox.get())

    month += direction
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    month_combobox.set(month)
    year_combobox.set(year)
    update_calendar()

# ----- 오늘로 이동 함수 -----
def go_to_today():
    year_combobox.set(now.year)
    month_combobox.set(now.month)
    update_calendar()

# ----- 캘린더 표시 -----
def show_calendar():
    login_frame.pack_forget()
    control_frame.pack(pady=10)
    calendar_frame.pack(pady=20)
    update_calendar()

# ----- 로그인/회원가입 버튼 -----
login_button = tk.Button(login_frame, text="Login", command=sign_in_calendar)
login_button.grid(row=2, column=0, columnspan=2, pady=10)

signup_button = tk.Button(login_frame, text="Sign Up", command=sign_up_calendar)
signup_button.grid(row=3, column=0, columnspan=2, pady=10)

# ----- 연도/월 선택 프레임 -----
control_frame = tk.Frame(root)

prev_button = tk.Button(control_frame, text="<", font=FONT_LARGE, command=lambda: change_month(-1))
prev_button.grid(row=0, column=0, padx=10)

month_label = tk.Label(control_frame, text="", font=FONT_LARGE)
month_label.grid(row=0, column=1, padx=10)

next_button = tk.Button(control_frame, text=">", font=FONT_LARGE, command=lambda: change_month(1))
next_button.grid(row=0, column=2, padx=10)

year_combobox = ttk.Combobox(control_frame, values=list(range(2000, 2101)), state="readonly", width=8)
year_combobox.set(current_year)
year_combobox.grid(row=0, column=3, padx=5)

month_combobox = ttk.Combobox(control_frame, values=list(range(1, 13)), state="readonly", width=5)
month_combobox.set(current_month)
month_combobox.grid(row=0, column=4, padx=5)

# 오늘로 이동 버튼
today_button = tk.Button(control_frame, text="오늘로 이동", font=FONT_MEDIUM, command=go_to_today)
today_button.grid(row=0, column=5, padx=10)

# 콤보박스 이벤트 바인딩
year_combobox.bind("<<ComboboxSelected>>", update_calendar)
month_combobox.bind("<<ComboboxSelected>>", update_calendar)

# ----- 캘린더 프레임 -----
calendar_frame = tk.Frame(root)

# ----- 초기 실행 -----
year_combobox.set(current_year)
month_combobox.set(current_month)
update_calendar()

root.mainloop()
