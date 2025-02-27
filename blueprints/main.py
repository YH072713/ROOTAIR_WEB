from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime 
from blueprints.utils import get_db_connection
import uuid
import traceback

# '/main'하에 모든 라우트가 위치
main_bp = Blueprint('main', __name__, url_prefix='/main')

# 메인 페이지 라우트
@main_bp.route('/')
def main():
    # 템플릿 경로를 수정하여 templates 폴더 내의 "main.html"을 사용
    return render_template('main/main.html')

# 항공권 조회 페이지 라우트
@main_bp.route('/list', methods=['GET'])
def search_results():
    # URL 쿼리승트링에서 검색 조건을 가져옴
    departure_airport = request.args.get('departure_airport')
    arrival_airport = request.args.get('arrival_airport')
    departure_date_raw = request.args.get('departure_date')
    seat_class = request.args.get('seat_class', '이코노미')
    passenger_count = request.args.get('passenger_count', 1, type=int)

    # 필수 항목 누락 검사
    if not departure_airport or not arrival_airport or not departure_date_raw:
        return "필수 선택값이 누락되었습니다.", 400

    try:
        # 입력받은 날짜 문자열을 날짜 객체로 변환 (YYYY-MM-DD 형식)
        departure_date = datetime.strptime(departure_date_raw, "%Y-%m-%d").date()
    except ValueError:
        return "잘못된 날짜 형식입니다.", 400

    # 데이터베이스 연결 및 커서 생성
    conn = get_db_connection()
    cursor = conn.cursor()


    # Flights 테이블에서 조건에 맞는 항공편을 조회하는 SQL 쿼리
    query = """
        SELECT flight_id, departure_airport, arrival_airport, DATE(departure_time) as departure_time,
               seat_class, price, passenger_count
        FROM Flights
        WHERE departure_airport = %s
          AND arrival_airport = %s
          AND DATE(departure_time) = %s
          AND seat_class = %s
          AND passenger_count >= %s
    """
    cursor.execute(query, (departure_airport, arrival_airport, departure_date, seat_class, passenger_count))
    flights = cursor.fetchall()

    # 사용 후 커서와 연결 종료
    cursor.close()
    conn.close()

    return render_template('main/main_list.html', results=flights)
    

# 항공편 상세정보 및 예약 폼 페이지 라우트
@main_bp.route('/list/detail/<int:flight_id>', methods=['GET'])
def flight_detail(flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 선택한 flight_id에 해당하는 항공편 정보를 조회
    cursor.execute("SELECT * FROM Flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()

    if not flight:
        return "해당 항공편이 존재하지 않습니다.", 404

    # URL 쿼리 파라미터에서 탑승객 수 가져옴
    passenger_count = request.args.get('passengers', 1, type=int)

    return render_template('main/main_list_detail.html', flight=flight, passenger_count=passenger_count)

# 예약(구매) 처리 라우트
from flask import jsonify

from flask import session


@main_bp.route('/book', methods=['POST'])
def book_flight():
    flight_id = request.form.get('flight_id', type=int)
    eng_names = request.form.getlist("eng_name[]")  # ✅ 리스트로 가져오기

    print(f"DEBUG: 받은 eng_names 원본 값 = {request.form.getlist('eng_name')}")  # 🔥 원본 데이터 확인
    print(f"DEBUG: 받은 flight_id 값 = {flight_id}")  # 🔥 flight_id 확인

    # ✅ 로그인된 사용자 정보 가져오기
    user_id = 'user001'  # ✅ 테스트용 ID 설정

    if not user_id:
        return "로그인이 필요합니다.", 403

    if not flight_id or not eng_names or eng_names == [""]:  # ✅ 빈 리스트 필터링
        print("ERROR: 필수 예약 정보가 누락되었습니다.")
        return "필수 예약 정보가 누락되었습니다.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 사용자 `username`, `balance` 조회
    cursor.execute("SELECT username, mileage, balance FROM Users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    if not user_data:
        return "사용자 정보를 찾을 수 없습니다.", 404

    username = user_data["username"]
    total_mileage = user_data["mileage"]
    balance = user_data["balance"]

    # ✅ 예약 대상 항공편 정보 조회
    cursor.execute("SELECT * FROM Flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()
    if not flight:
        return "해당 항공편이 존재하지 않습니다.", 404

    # ✅ 단일 예약 ID 생성
    booking_id = str(uuid.uuid4())[:20]

    # ✅ 총 결제 금액 계산
    price = flight["price"]
    total_price = price * len(eng_names)
    earned_mileage = int(total_price * 0.1)

    cursor.close()
    conn.close()

    print(f"DEBUG: 변환된 eng_name = {', '.join(eng_names)}")  # ✅ 변환된 값 확인

    return render_template(
        'pay/pay.html',
        booking_id=booking_id,
        username=username,
        eng_name=", ".join(eng_names) if eng_names != [""] else "Unknown",  # ✅ 빈 리스트 방지
        total_mileage=total_mileage,
        earned_mileage=earned_mileage,
        price=price,
        total_price=total_price,
        flight_id=flight_id,
        balance=balance,
        seat_class=flight["seat_class"],
        passenger_count=len(eng_names),
        airplane_name=flight["airplane_name"],
        departure_airport=flight["departure_airport"],
        arrival_airport=flight["arrival_airport"],
        departure_time=flight["departure_time"],
        arrival_time=flight["arrival_time"]
    )

