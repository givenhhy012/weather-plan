import tkinter as tk
import requests
import json
from datetime import datetime, timedelta

# 기상청 API 키 (공공데이터포털에서 발급받은 디코딩된 키 )
API_KEY = "c9+P8KoYVHHclcwNES4SC2Iq7MZW787CxlmV+J2aXwxh7sVV4sZ76OFiOKoVgN/HDVTt689y004GqWIRvWTFmQ=="

# 기상청_지상(종관, ASOS) 일자료 조회 API 키 (공공데이터포털에서 발급받은 디코딩된 키 )
API_PAST_KEY = "c9+P8KoYVHHclcwNES4SC2Iq7MZW787CxlmV+J2aXwxh7sVV4sZ76OFiOKoVgN/HDVTt689y004GqWIRvWTFmQ=="

# 기상청 중기예보 API 키 (공공데이터포털에서 발급받은 디코딩된 키 )
API_FUTURE_KEY = "c9+P8KoYVHHclcwNES4SC2Iq7MZW787CxlmV+J2aXwxh7sVV4sZ76OFiOKoVgN/HDVTt689y004GqWIRvWTFmQ=="

# 격자 좌표 (예: 서울 종로구 -> nx=60, ny=127)
NX, NY = 60, 127

# 관측소 좌표 (과거 기온을 가져오기 위한 관측소 ID)
StnIds = "108"  # 기본값은 서울역

# 중기예보 지역 코드 (REG_ID)
REG_ID = "11B10101"  # 기본값은 서울 지역의 REG_ID (중기예보를 위한 지역 코드)

# 초단기실황 API URL
API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 단기예보 API URL
API_URL_dangi = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# 요청 URL (기상청 종관 기온 데이터: 일자료)
API_URL_PAST = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"

# 요청 URL (기상청 중기예보 데이터)
API_URL_FUTURE = "https://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"

# 지역별 좌표 설정
def set_nx_ny(region):
    global NX, NY
    if region == "서울":
        NX, NY = 60, 127
    elif region == "춘천":
        NX, NY = 62, 128
    elif region == "강릉":
        NX, NY = 66, 130
    elif region == "홍성":
        NX, NY = 58, 126
    elif region == "청주":
        NX, NY = 63, 124
    elif region == "태백":
        NX, NY = 55, 128
    elif region == "전주":
        NX, NY = 56, 126
    elif region == "대전":
        NX, NY = 63, 126
    elif region == "대구":
        NX, NY = 62, 89
    elif region == "울산":
        NX, NY = 61, 81
    elif region == "광주":
        NX, NY = 56, 80
    elif region == "창원":
        NX, NY = 58, 77
    elif region == "부산":
        NX, NY = 60, 76
    elif region == "제주":
        NX, NY = 55, 38
        
        
# 지역별 관측소 ID 설정 (과거 기온을 가져오기 위한 관측소 ID)
def set_stnIds(region):
    global StnIds
    
    if region == "서울":
        StnIds = "108"
    elif region == "춘천":
        StnIds = "105"
    elif region == "강릉":
        StnIds = "107"
    elif region == "홍성":
        StnIds = "131"
    elif region == "청주":
        StnIds = "134"
    elif region == "태백":
        StnIds = "119"
    elif region == "전주":
        StnIds = "157"
    elif region == "대전":
        StnIds = "133"
    elif region == "대구":
        StnIds = "143"
    elif region == "울산":
        StnIds = "159"
    elif region == "광주":
        StnIds = "156"
    elif region == "창원":
        StnIds = "162"
    elif region == "부산":
        StnIds = "159"
    elif region == "제주":
        StnIds = "184"
        
        
# 중기예보를 
def set_REG_ID(region):
    global REG_ID
    
    if region == "서울":
        REG_ID = "11B10101"
    elif region == "춘천":
        REG_ID = "11B20101"
    elif region == "강릉":
        REG_ID = "11B30101"
    elif region == "홍성":
        REG_ID = "11B40101"
    elif region == "청주":
        REG_ID = "11B50101"
    elif region == "태백":
        REG_ID = "11B60101"
    elif region == "전주":
        REG_ID = "11B70101"
    elif region == "대전":
        REG_ID = "11B80101"
    elif region == "대구":
        REG_ID = "11B90101"
    elif region == "울산":
        REG_ID = "11H20101"
    elif region == "광주":
        REG_ID = "11F20501"
    elif region == "창원":
        REG_ID = "11H20301"
    elif region == "부산":
        REG_ID = "11H20201"
    elif region == "제주":
        REG_ID = "11G00201"



# 현재기온 가져오는 함수 => 오늘을 제외한 다른 날들은 정보 없음
def get_temperature(date_str):
    now = datetime.now()
    
    if date_str.replace("-", "") != now.strftime("%Y%m%d"):
        return "기온 정보 없음"
    
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
    base_date = now - timedelta(days=1) 
    base_time = "2300"      # 전날 23:00 발표자료 기준
    
    if date_str.replace("-", "") <= base_date.strftime("%Y%m%d"):
        return "날씨 정보 없음"
    
    
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date.strftime("%Y%m%d"),  # YYYYMMDD
        "base_time": base_time,    # 05:00 발표자료 기준
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
    base_date = now - timedelta(days=1) 
    base_time = "2300"      # 전날 23:00 발표자료 기준
    
    future_date = now + timedelta(days=3)  # 중기예보는 3일 뒤부터 가능
    
    yesterday = now - timedelta(days=1)
    
    if date_str.replace("-", "") <= yesterday.strftime("%Y%m%d"):
        return get_past_temperature(date_str)
    
    if date_str.replace("-", "") > future_date.strftime("%Y%m%d"):
        return get_mid_temp_forecast(date_str)
        
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date.strftime("%Y%m%d"),  # YYYYMMDD
        "base_time": base_time,    
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
    
    
# 과거 기온 가져오는 함수 (최저, 최고 기온)
def get_past_temperature(date_str):
    params = {
        "serviceKey": API_PAST_KEY,
        "numOfRows": 500,
        "pageNo": 1,
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "DAY",
        "startDt": date_str.replace("-", ""),  # YYYYMMDD
        "endDt": date_str.replace("-", ""),    # YYYYMMDD
        "stnIds": StnIds,
    }
    
    try:
        response = requests.get(API_URL_PAST, params=params)

        if response.status_code == 200:
            data = response.json()
            if "response" in data and "body" in data["response"]:
                items = data["response"]["body"]["items"]["item"]
                if items:
                    for item in items:
                        return item["minTa"], item["maxTa"]
                else:
                    print("응답에 기온 정보가 없습니다.")
                    return None, None
            else:
                print("API 응답 형식이 올바르지 않습니다.")
                return None, None
        else:
            print(f"API 호출 실패: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None
    

# 중기예보 api 활용해 3~10일 사이의 최고, 최저 기온을 가져오는 함수
def get_mid_temp_forecast(date_str):
    # 발표 기준시각: 오늘 오전 6시
    now = datetime.now()
    tmFc = now.replace(hour=6, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H%M")
    
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = target_date - today
    offset = delta.days
    
    global REG_ID

    params = {
        "serviceKey": API_FUTURE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "dataType": "JSON",
        "regId": REG_ID,
        "tmFc": tmFc,
    }

    try:
        response = requests.get(API_URL_FUTURE, params=params)
        if response.status_code == 200:
            data = response.json()
            item = data["response"]["body"]["items"]["item"][0]

            min_key = f"taMin{offset}"
            max_key = f"taMax{offset}"
            
            tmin = float(item[min_key])
            tmax = float(item[max_key])
            return tmin, tmax
        else:
            print(f"API 호출 실패: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None
