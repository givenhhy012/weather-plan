import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
import threading
import time

import log_in
import apiusing
import recommed
import logistic

FONT_LARGE = ("맑은 고딕", 16)
FONT_MEDIUM = ("맑은 고딕", 12)
FONT_SMALL = ("맑은 고딕", 10)


calendar.setfirstweekday(calendar.SUNDAY)

# ----- 초기 설정 -----
schedule_cache = {} # {"2025-05-01": True, "2024-05-03": True, ...}
clothing_cache = {} # 옷 기록 캐시 추가
user = None
average_temp = None
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
    
    global average_temp
    
    if average is not None:
        average_temp = round(average,1)

    if average is not None:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온: {average_temp}℃"
        )
    else:
        return (
            f"{date} 날씨: {weather_condition}, 현재기온: {temperature}℃\n"
            f"최저기온: {tmin}℃, 최고기온: {tmax}℃, 평균기온 정보 없음"
        )

def show_details(date):
    global selected_date
    selected_date = date

    def save_schedule():
        if user is None:
            messagebox.showwarning("로그인 필요")
            return
        load_schedules()

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
        schedule_listbox.delete(0, tk.END)
        schedules = log_in.get_schedules_for_date(user, date)
        for item in schedules:
            schedule_listbox.insert(tk.END, item)
    
    def delete_selected_schedule():
        selected_item_index = schedule_listbox.curselection()
        if not selected_item_index:
            messagebox.showwarning("선택 필요", "삭제할 일정을 목록에서 선택해주세요.")
            return

        selected_schedule_title = schedule_listbox.get(selected_item_index)

        if messagebox.askyesno("일정 삭제 확인", f"'{selected_schedule_title}' 일정을 삭제하시겠습니까?"):
            if user:
                success = log_in.delete_schedule_item(user, selected_date, selected_schedule_title)
                if success:
                    # 캐시 업데이트 및 캘린더 UI 업데이트
                    if selected_date in schedule_cache:
                        # 해당 날짜에 다른 일정이 더 있는지 확인
                        remaining_schedules = log_in.get_schedules_for_date(user, selected_date)
                        if not remaining_schedules: # 남은 일정이 없으면 캐시에서 제거
                            del schedule_cache[selected_date]
                    update_calendar()
                    load_schedules() # 목록 새로고침
                    messagebox.showinfo("삭제 완료", "일정이 삭제되었습니다.")
                else:
                    messagebox.showerror("삭제 실패", "일정 삭제에 실패했습니다.")
            else:
                messagebox.showerror("오류", "사용자 정보가 없습니다.")

    def load_weather():
        weather_info = get_weather_info(date)
        weather_label.config(text=weather_info)
        recommend_button.config(state="normal")
        
    def load_todays_clothing():
        outer, top, pants = logistic.load_actual_choices(user, date)
        if outer and top and pants:
            recommend_label.config(text=f"오늘 입은 옷: {outer}, {top}, {pants}")
        else:
            recommend_label.config(text="오늘 입은 옷 정보 없음")
    
    def open_recommend_window_and_refresh_calendar(current_user, temp, current_date):
        recommed.show_frame(current_user, temp, current_date) #
        # 옷 추천/기록 창이 닫힌 후 달력 새로고침
        year_val = int(year_combobox.get())
        month_val = int(month_combobox.get())
        load_monthly_clothing_cache(year_val, month_val) # 현재 달의 옷 기록 캐시 업데이트
        update_calendar() # 달력 UI 업데이트

    # 새 창 생성
    details_window = tk.Toplevel(root)
    details_window.title(f"{date} 상세 정보")
    details_window.geometry("800x450")

    # 전체를 감싸는 프레임 (2열 구성)
    content_frame = tk.Frame(details_window)
    content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ----- 왼쪽 프레임: 날씨 + 일정 추가 -----
    left_frame = tk.Frame(content_frame)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # 날씨 프레임 (LabelFrame으로 테두리 강조)
    weather_frame = tk.LabelFrame(left_frame, text="날씨 정보", font=FONT_MEDIUM, bd=2, relief="groove", padx=10, pady=10)
    weather_frame.pack(fill="x", pady=(0, 10))

    # 로딩 중 메시지
    weather_label = tk.Label(weather_frame, text="날씨 정보 불러오는 중...", font=FONT_SMALL, justify="left", anchor="w")
    weather_label.pack(anchor="w")

    # 프레임 생성해서 버튼과 텍스트를 나란히 배치
    recommend_frame = tk.Frame(weather_frame)
    recommend_frame.pack(anchor="w", pady=5)

    recommend_button = tk.Button(recommend_frame, text="옷차림 추천", command=lambda: recommed.show_frame(user, average_temp, date))
    recommend_button.grid(row=0, column=0, padx=5)
    recommend_button.config(state="disabled")  # 로딩 중 비활성화

    # 🔸 오른쪽에 텍스트 추가
    recommend_label = tk.Label(recommend_frame, text="오늘 입은 옷 불러오는 중...", font=FONT_SMALL)
    recommend_label.grid(row=0, column=1, padx=5)


    # 일정 추가 프레임
    schedule_frame = tk.LabelFrame(left_frame, text="일정 추가", font=FONT_MEDIUM, bd=2, relief="groove", padx=10, pady=10)
    schedule_frame.pack(fill="x")

    schedule_label = tk.Label(schedule_frame, text="일정 내용을 입력하세요:", font=FONT_SMALL, anchor="w")
    schedule_label.pack(anchor="w", pady=(0, 5))
    schedule_entry = tk.Entry(schedule_frame, width=30)
    schedule_entry.pack(anchor="w", pady=(0, 5))
    save_button = tk.Button(schedule_frame, text="저장", command=save_schedule)
    save_button.pack(anchor="w", pady=(0, 5))

    # ----- 오른쪽 프레임: 일정 목록 -----
    schedule_list_frame = tk.LabelFrame(content_frame, text="일정 목록", font=FONT_MEDIUM, bd=2, relief="groove", padx=10, pady=10)
    schedule_list_frame.grid(row=0, column=1, sticky="nsew")

    schedule_listbox = tk.Listbox(schedule_list_frame, width=30, height=18, font=FONT_MEDIUM)
    schedule_listbox.pack(pady=(0, 5))

    #삭제 버튼 추가
    delete_button = tk.Button(schedule_list_frame, text = "선택 일정 삭제", command=delete_selected_schedule, font=FONT_SMALL)
    delete_button.pack(pady=5)

    # 열 비율 설정
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)

    # ----- 비동기 로딩 시작 -----
    threading.Thread(target=load_schedules).start()
    threading.Thread(target=load_weather).start()
    threading.Thread(target=load_todays_clothing).start()
    
# ----- add cache function -------

def load_monthly_schedule_cache(year, month):
    global schedule_cache
    if user is None:
        return
    schedule_cache = {}  # 이전 캐시 초기화
    all_schedules = log_in.get_all_schedules(user)  # 한 번에 모든 일정 불러오기

    for item in all_schedules:
        date = item.get("date")
        if date:
            try:
                d = datetime.strptime(date, "%Y-%m-%d")
                if d.year == year and d.month == month:
                    schedule_cache[date] = True
            except:
                continue

def load_monthly_clothing_cache(year, month):
    global clothing_cache
    if user is None:
        return
    clothing_cache = {} # 새 달에 대한 캐시 초기화
    dates_with_records = log_in.get_dates_with_clothing_records(user, year, month) #
    for date_str in dates_with_records:
        clothing_cache[date_str] = True

# ----- 캘린더 업데이트 -----
def update_calendar(*args):
    year = int(year_combobox.get())
    month = int(month_combobox.get())

    load_monthly_schedule_cache(year, month)
    load_monthly_clothing_cache(year, month) # 옷 기록 캐시 로드 호출 추가

    month_label.config(text=f"{year}년 {month}월")
    cal = calendar.monthcalendar(year, month)

    for widget in calendar_frame.winfo_children():
        if isinstance(widget, tk.Button): 
            widget.destroy()

    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    for idx, day_name in enumerate(weekdays):
        fg_color = "red" if day_name == "일" else ("blue" if day_name == "토" else "black")
        label = tk.Label(calendar_frame, text=day_name, font=FONT_MEDIUM, fg=fg_color)
        label.grid(row=1, column=idx)

    for i, week in enumerate(cal):
        for j, day_val in enumerate(week):
            if day_val != 0:
                date = f"{year}-{month:02d}-{day_val:02d}"

                fg_color = "red" if j == 0 else ("blue" if j == 6 else "black")
                bg_color = "lightyellow" if date == f"{now.year}-{now.month:02d}-{now.day:02d}" else "white"

                has_schedule = schedule_cache.get(date, False) #
                has_clothing = clothing_cache.get(date, False) #

                icons = []
                if has_schedule:
                    icons.append("🗓")
                if has_clothing:
                    icons.append("👕")

                display_text = f"{day_val}"
                if icons:
                    display_text += f"\n{''.join(icons)}"


                btn = tk.Button(
                    calendar_frame,
                    text=display_text,
                    command=lambda d=date: show_details(d),
                    width=10, 
                    height=4, # 두 줄 표시에 적합하도록 높이 조정
                    fg=fg_color,
                    bg=bg_color,
                    font=FONT_MEDIUM,
                    justify="center" 
                )
                btn.grid(row=i + 2, column=j, padx=2, pady=2)

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
    
def show_region():
    login_frame.pack_forget()
    control_frame.pack_forget()
    calendar_frame.pack_forget()

    regions_text = "서울,춘천,강릉,홍성,청주,태백,전주,대전,대구,울산,광주,창원,부산,제주"
    regions = regions_text.split(',')

    frame = tk.Frame(root)
    frame.pack(pady=20)

    label = tk.Label(frame, text="지역을 선택하세요:", font=FONT_MEDIUM)
    label.pack(pady=10)

    region_combobox = ttk.Combobox(frame, values=regions, state="readonly", font=FONT_MEDIUM)
    region_combobox.pack(pady=10)
    region_combobox.set("서울")  # 기본값

    def confirm_region():
        selected = region_combobox.get()
        set_region(selected)

    confirm_button = tk.Button(frame, text="선택 완료", font=FONT_MEDIUM, command=confirm_region)
    confirm_button.pack(pady=10)

    
    
def set_region(text):
    global region
    region = text
    
    apiusing.set_nx_ny(region)
    apiusing.set_stnIds(region)
    show_calendar()

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
