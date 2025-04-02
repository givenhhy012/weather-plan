import tkinter as tk
import requests
import json
from datetime import datetime

# 기상청 API 키 (공공데이터포털에서 발급받은 디코딩된 키 입력)
API_KEY = "c9+P8KoYVHHclcwNES4SC2Iq7MZW787CxlmV+J2aXwxh7sVV4sZ76OFiOKoVgN/HDVTt689y004GqWIRvWTFmQ=="

# 현재 날짜 및 최근 발표 시간 계산
now = datetime.now()
BASE_DATE = now.strftime("%Y%m%d")  # YYYYMMDD 형식
BASE_HOUR = now.hour  # 현재 시간 (정각 기준)

# 기상청 초단기실황은 10분 단위 발표, 최근 발표된 정각 기준 사용
if now.minute < 40:  # 40분 이전이면 한 시간 전 데이터 사용
    BASE_HOUR -= 1
BASE_TIME = f"{BASE_HOUR:02}00"  # HH00 형식

# 격자 좌표 (예: 서울 종로구 -> nx=60, ny=127)
NX, NY = 60, 127

# 초단기실황 API URL
API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 요청 파라미터 설정
params = {
    "serviceKey": API_KEY,  # 디코딩된 API 키 사용
    "numOfRows": 10,
    "pageNo": 1,
    "dataType": "JSON",
    "base_date": BASE_DATE,
    "base_time": BASE_TIME,
    "nx": NX,
    "ny": NY,
}

def get_temperature():
    # API 요청
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # API 응답에서 'item' 데이터 추출
        items = data["response"]["body"]["items"]["item"]

        # 현재 기온(T1H) 데이터 찾기
        for item in items:
            if item["category"] == "T1H":  # T1H: 기온 데이터
                temperature = f"{item['obsrValue']}°C"
                temperature_label.config(text=f"현재 기온: {temperature}")
                break
    else:
        temperature_label.config(text="API 요청 실패")

# Tkinter 윈도우 설정
root = tk.Tk()
root.title("현재 기온 정보")

# 라벨 설정
temperature_label = tk.Label(root, text="기온을 가져오는 중...", font=("Arial", 16))
temperature_label.pack(pady=20)

# 버튼 설정
get_temp_button = tk.Button(root, text="기온 가져오기", command=get_temperature, font=("Arial", 14))
get_temp_button.pack(pady=10)

# Tkinter 윈도우 실행
root.mainloop()
