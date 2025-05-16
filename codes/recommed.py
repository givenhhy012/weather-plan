import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import logistic


def recommend_clothes(temp):
    if temp == None:
        return "기온 정보가 없습니다."
    
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

def show_frame(user, temperature, date_str):
    # GUI 구성
    root = tk.Tk()
    root.title("날씨 일정 관리")
    root.geometry("400x500")

    temp_label = tk.Label(root, text=f"오늘의 평균기온: {temperature}°C", font=("Arial", 14))
    temp_label.pack(pady=10)

    # 지역 변수로 선언
    result_label = tk.Label(root, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    # 드롭다운 구성
    dropdown_frame = tk.Frame(root)

    outer_var = tk.StringVar()
    outer_options = ["패딩", "코트", "자켓", "없음"]
    outer_menu = ttk.Combobox(dropdown_frame, textvariable=outer_var, values=outer_options, state="readonly", width=15)
    outer_menu.set("아우터 선택")
    outer_menu.pack()

    top_var = tk.StringVar()
    top_options = ["기모 의류", "후드티", "롱슬리브", "반팔"]
    top_menu = ttk.Combobox(dropdown_frame, textvariable=top_var, values=top_options, state="readonly", width=15)
    top_menu.set("상의 선택")
    top_menu.pack()

    bottom_var = tk.StringVar()
    bottom_options = ["기모바지", "청바지", "슬랙스", "반바지(치마)"]
    bottom_menu = ttk.Combobox(dropdown_frame, textvariable=bottom_var, values=bottom_options, state="readonly", width=15)
    bottom_menu.set("하의 선택")
    bottom_menu.pack()

    

    # ✅ 여기서 함수들을 먼저 정의합니다.
    def show_record_options():
        dropdown_frame.pack(pady=10)

    def show_recommendation():
        if temperature is None:
            messagebox.showerror("오류", "기온 정보가 없습니다.")
            return
    
        if logistic.get_max_index(user) is None:
            messagebox.showerror("오류", "사용자 actual_record가 생성되어있지 않음")
            return
        else:
            if (logistic.get_max_index(user) < 5):
                print("=== 🔹 단순 추천 시스템 ===")
                outer, top, pants = logistic.recommendation_simple(temperature)
            else:
                print("=== 🔹 머신러닝 추천 시스템 ===")
                outer, top, pants = logistic.recommendation_machine(user, temperature)
            
            print(f"\n[기온: {temperature}°C]")
            print(f"👚 아우터 추천: {outer}")
            print(f"👕 상의 추천: {top}")
            print(f"👖 하의 추천: {pants}")
        
            result_label.config(text=f"아우터 추천: {outer}, 상의 추천: {top}, 하의 추천: {pants}")
            record_btn.pack(pady=5)  # "오늘의 옷 기록하기" 버튼 보이기

    def save_clothing():
        outer = translate_choice(outer_menu.get())
        top = translate_choice(top_menu.get())
        bottom = translate_choice(bottom_menu.get())
        
        
        print(f"🔎 [DEBUG] 선택된 값 - 아우터: '{outer}', 상의: '{top}', 하의: '{bottom}'")
        
        if not outer:
            messagebox.showerror("오류", "아우터를 선택해주세요.")
            return
        if not top:
            messagebox.showerror("오류", "상의 선택해주세요.")
            return
        if not bottom:
            messagebox.showerror("오류", "하의 선택해주세요.")
            return

        try:
            logistic.save_actual_record(user, date_str, temperature, outer, top, bottom)
            messagebox.showinfo("저장 완료", f"오늘의 옷차림이 저장되었습니다.\n아우터: {outer}, 상의: {top}, 하의: {bottom}")
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {e}")

    # ✅ 함수가 정의된 후 버튼을 생성합니다.
    recommend_btn = tk.Button(root, text="옷차림 추천", command=show_recommendation)
    recommend_btn.pack(pady=5)

    record_btn = tk.Button(root, text="오늘의 옷 기록하기", command=show_record_options)
    
    

    save_btn = tk.Button(dropdown_frame, text="저장하기", command=lambda: save_clothing())
    save_btn.pack(pady=10)


def translate_choice(choice):
    if choice == "패딩":
        return "padding"
    elif choice == "코트":
        return "coat"
    elif choice == "자켓":
        return "jacket"
    elif choice == "없음":
        return "none"
    elif choice == "기모 의류":
        return "brushed"
    elif choice == "후드티":
        return "hoodie"
    elif choice == "롱슬리브":
        return "longsleeve"
    elif choice == "반팔":
        return "tshirt"
    elif choice == "기모바지":
        return "brushed"
    elif choice == "청바지":
        return "jean"
    elif choice == "슬랙스":
        return "slacks"
    elif choice == "반바지(치마)":
        return "short"
        
    # root.mainloop()

# 외부에서 호출할 수 있도록 설정
# if __name__ == "__main__":
#     show_frame()
