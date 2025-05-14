import tkinter as tk
from tkinter import messagebox, ttk
import calendar
from datetime import datetime

import log_in
import apiusing

calendar.setfirstweekday(calendar.SUNDAY)

# ----- 초기 설정 -----
schedule_cache = {}  # {"2025-05-01": True, "2024-05-03": True, ...}
user = None
root = tk.Tk()
root.title("Login and Calendar")
root.geometry("1280x720")

region = None

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
    global user
    email = id_entry.get()
    password = pw_entry.get()
    user = log_in.sign_in(email, password)
    if user:   
        show_region()
    else:
        messagebox.showerror("Login Failed", "로그인 실패")

def sign_up_calendar():
    global user
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
    
    average = (float(tmin) + float(tmax)) / 2 if tmin is not None and tmax is not None else None

    if average is not None:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온: {round(average,1)}℃"
        )
    else:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온 정보 없음"
        )

# ----- 옷차림 추천 -----
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

    log_in.save_clothes_record(user, today, outer, top, bottom)
    messagebox.showinfo("저장 완료", "오늘의 옷차림이 저장되었습니다.")

# ----- 일정 및 날씨 창 -----
def show_details(date):
    global selected_date
    selected_date = date
    
    def save_schedule():
        if user is None:
            messagebox.showwarning("로그인 필요")
            return
            
        event = schedule_entry.get()
        if event:
            schedule_cache[selected_date] = True
            log_in.save_schedule(user, event, selected_date)
            update_calendar()
            messagebox.showinfo("Schedule Added", f"일정 저장: {date} - {event}")
            details_window.destroy()
        else:
            messagebox.showwarning("Empty Schedule", "일정을 입력해주세요.")
            
    def load_schedules():
        """해당 날짜의 일정을 Firebase에서 불러와 목록에 출력"""
        global user
        user_id = user["localId"]
        schedules = log_in.get_schedules_for_date(user, date)
        for item in schedules:
            schedule_listbox.insert(tk.END, item)

    details_window = tk.Toplevel(root)
    details_window.title(f"{date} 상세 정보")
    details_window.geometry("800x400")
    
    # 날씨 프레임
    weather_frame = tk.Frame(details_window, padx=10, pady=10)
    weather_frame.grid(row=0, column=0, sticky="nsew")
    weather_info = get_weather_info(date)
    weather_label = tk.Label(weather_frame, text=weather_info, font=FONT_MEDIUM)
    weather_label.pack() 
    
    # 일정 입력 프레임
    schedule_frame = tk.Frame(details_window, padx=10, pady=10)
    schedule_frame.grid(row=0, column=1, sticky="nsew")
    schedule_label = tk.Label(schedule_frame, text="일정 추가:", font=FONT_MEDIUM)
    schedule_label.pack(pady=5)
    schedule_entry = tk.Entry(schedule_frame, width=20)
    schedule_entry.pack(pady=5)
    save_button = tk.Button(schedule_frame, text="저장", command=save_schedule)
    save_button.pack(pady=5)
    
    # 일정 목록 프레임
    schedule_list_frame = tk.Frame(details_window, padx=10, pady=10)
    schedule_list_frame.grid(row=0, column=2, sticky="nsew")
    list_label = tk.Label(schedule_list_frame, text="일정 목록", font=FONT_MEDIUM)
    list_label.pack(pady=5)
    schedule_listbox = tk.Listbox(schedule_list_frame, width=30, height=10, font=FONT_MEDIUM)
    schedule_listbox.pack()
    
    # 일정 목록 초기 출력
    load_schedules()

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
                fg_color = "red" if j == 0 else ("blue" if j == 6 else "black")
                bg_color = "lightyellow" if date == f"{now.year}-{now.month:02d}-{now.day:02d}" else "white"

                btn = tk.Button(
                    calendar_frame,
                    text=text,
                    command=lambda d=date: show_details(d),
                    width=10,
                    height=4,
                    fg=fg_color,
                    bg=bg_color,
                    font=FONT_MEDIUM
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

# ----- 지역 선택 -----
def show_region():
    login_frame.pack_forget()
    control_frame.pack_forget()
    region_frame.pack(pady=10)
    region_label = tk.Label(region_frame, text="지역을 선택하세요", font=FONT_LARGE)
region_label.pack(pady=10)

regions = [
    "서울", "춘천", "강릉", "청주", "홍성", "태백",
    "전주", "대전", "대구", "울산", "광주", "창원", "부산", "제주"
]

def fetch_weather_for_region(region):
    global region
    region_label.config(text=f"지역: {region}날씨")
    result = apiusing.get_weather(region)
    region_label.config(text=f"{region}의 날씨는 {result['weather']}입니다")

for region in regions:
    btn = tk.Button(region_frame, text=region, font=FONT_MEDIUM, width=10, height=3, command=lambda r=region: fetch_weather_for_region(r))
    btn.pack(side=tk.LEFT, padx=5, pady=5)
year_combobox = ttk.Combobox(root, values=[now.year, now.year+1], state="readonly", font=FONT_LARGE)
year_combobox.set(now.year)

month_combobox = ttk.Combobox(root, values=list(range(1, 13)), state="readonly", font=FONT_LARGE)
month_combobox.set(now.month)

control_frame = tk.Frame(root)
control_frame.pack(pady=10)

month_label = tk.Label(control_frame, text=f"{now.year}년 {now.month}월", font=FONT_LARGE)
month_label.pack(side=tk.LEFT, padx=10)

prev_month_button = tk.Button(control_frame, text="◀", font=FONT_LARGE, command=lambda: change_month(-1))
prev_month_button.pack(side=tk.LEFT, padx=10)

next_month_button = tk.Button(control_frame, text="▶", font=FONT_LARGE, command=lambda: change_month(1))
next_month_button.pack(side=tk.LEFT, padx=10)

go_today_button = tk.Button(control_frame, text="오늘", font=FONT_LARGE, command=go_to_today)
go_today_button.pack(side=tk.LEFT, padx=10)

region_frame = tk.Frame(root)
