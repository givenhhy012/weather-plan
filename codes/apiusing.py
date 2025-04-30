import tkinter as tk
import requests
import json
from datetime import datetime

# 기상청 API 키 (공공데이터포털에서 발급받은 디코딩된 키 입력)
API_KEY = "c9+P8KoYVHHclcwNES4SC2Iq7MZW787CxlmV+J2aXwxh7sVV4sZ76OFiOKoVgN/HDVTt689y004GqWIRvWTFmQ=="

# 격자 좌표 (예: 서울 종로구 -> nx=60, ny=127)
NX, NY = 60, 127

# 초단기실황 API URL
API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 단기예보 API URL
API_URL_dangi = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"


# 현재기온 가져오는 함수 => 오늘을 제외한 다른 날들은 정보 없음
def get_temperature(date_str):
    now = datetime.now()
    base_time_hour = now.hour
    if now.minute < 40:
        base_time_hour -= 1
    base_time = f"{base_time_hour:02}00"

    params = {
        "serviceKey": API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": date_str.replace("-", ""),  # YYYYMMDD
        "base_time": base_time,
        "nx": NX,
        "ny": NY,
    }
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data["response"]["body"]["items"]["item"]:
                if item["category"] == "T1H":
                    return item["obsrValue"]
    except Exception as e:
        return "기온 정보 없음"
        
   
# 날씨 정보 가져오는 함수(맑음, 비 등) => 3일뒤 까지만 예보가 존재
def get_weather_condition(date_str):
    now = datetime.now()    
    
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": now.strftime("%Y%m%d"),  # YYYYMMDD
        "base_time": "0500",    # 05:00 발표자료 기준
        "nx": NX,
        "ny": NY,
    }

    response = requests.get(API_URL_dangi, params=params)
    
    try:
        if response.status_code == 200:
            items = response.json()["response"]["body"]["items"]["item"]
            pty, sky = None, None
            for item in items:
                if item["fcstDate"] == date_str.replace("-", "") and item["fcstTime"] == "0900":
                    if item["category"] == "PTY":
                        pty = item["fcstValue"]
                    elif item["category"] == "SKY":
                        sky = item["fcstValue"]
            return interpret_weather(pty, sky)
    except Exception as e:
        print("날씨 정보 오류:", e)
        return "오류 발생"


def interpret_weather(pty, sky):
    if pty == "1":
        return "비"
    elif pty == "2":
        return "비 또는 눈"
    elif pty == "3":
        return "눈"
    elif pty == "4":
        return "소나기"
    else:
        if sky == "1":
            return "맑음"
        elif sky == "3":
            return "구름 많음"
        elif sky == "4":
            return "흐림"
    return "정보 없음"
    
    
def get_min_max_temperature(date_str):
    now = datetime.now()
    
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": now.strftime("%Y%m%d"),  # YYYYMMDD
        "base_time": "0500",    # 05:00 발표자료 기준
        "nx": NX,
        "ny": NY,
    }
    
    response = requests.get(API_URL_dangi, params=params)
    
    try:
        if response.status_code == 200:
            items = response.json()["response"]["body"]["items"]["item"]
            tmin, tmax = None, None
            for item in items:
                if item["fcstDate"] == date_str.replace("-", ""):
                    if item["category"] == "TMX":
                        tmax = float(item["fcstValue"])
                    elif item["category"] == "TMN":
                        tmin = float(item["fcstValue"])
            return tmin, tmax
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None
    