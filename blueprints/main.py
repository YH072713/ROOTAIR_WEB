from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime 
from blueprints.utils import get_db_connection
from flask_login import login_required, current_user
import uuid

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
    # URL 쿼리스트링에서 검색 조건을 가져옴
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


    # flights 테이블에서 조건에 맞는 항공편을 조회하는 SQL 쿼리
    query = """
        SELECT flight_id, departure_airport, arrival_airport, DATE(departure_time) as departure_time,
               seat_class, price, passenger_count
        FROM flights
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
    cursor.execute("SELECT * FROM flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()

    if not flight:
        return "해당 항공편이 존재하지 않습니다.", 404

    # URL 쿼리 파라미터에서 탑승객 수 가져옴
    passenger_count = request.args.get('passengers', 1, type=int)

    return render_template('main/main_list_detail.html', flight=flight, passenger_count=passenger_count)

# 예약(구매) 처리 라우트
@main_bp.route('/book', methods=['POST'])
@login_required
def book_flight():
    # POST 데이터에서 flight_id와 탑승객들의 영문 이름 리스트를 가져옴
    flight_id = request.form.get('flight_id', type=int)
    eng_names = request.form.getlist('eng_name[]')

    # 로그인된 사용자의 user_id 확인
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    if not flight_id or not eng_names:
        return "필수 예약 정보가 누락되었습니다.", 400

    conn = get_db_connection()
    cursor = conn.cursor()


    # users 테이블에서 id에 해당하는 username 조회
    cursor.execute("SELECT username FROM users WHERE id = %s", (current_user.id,))
    user = cursor.fetchone()
    if not user:
        return "사용자 정보를 찾을 수 없습니다.", 404
    username = user["username"]


    # 예약 대상 항공편 정보를 조회
    cursor.execute("SELECT * FROM flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()
    if not flight:
        return "해당 항공편이 존재하지 않습니다.", 404

    # 예약 가능한 좌석 수 확인
    available_seats = flight["passenger_count"]
    if available_seats < len(eng_names):
        return "예약 가능한 좌석이 부족합니다.", 400

    # ★ 단일 예약 ID를 미리 생성 (모든 탑승객 예약에 동일하게 사용)
    booking_id = str(uuid.uuid4())[:20]

    # 각 탑승객에 대해 예약 정보 bookings 테이블에 삽입 (username에 session에서 가져온 값 사용)
    for eng_name in eng_names:
        cursor.execute("""
            INSERT INTO bookings (booking_id, user_id, username, eng_name, airplane_name, payment_status,
                                departure_airport, arrival_airport, departure_time, arrival_time, price)
            VALUES (%s, %s, %s, %s, %s, 'Unpaid', %s, %s, %s, %s, %s)
        """, (
            booking_id,
            current_user.id,  # ✅ user_id 추가
            username,
            eng_name,
            flight["airplane_name"],
            flight["departure_airport"],
            flight["arrival_airport"],
            flight["departure_time"],
            flight["arrival_time"],
            flight["price"]
        ))

    # 예약 후 해당 항공편의 남은 좌석 수 업데이트
    cursor.execute("""
        UPDATE flights SET passenger_count = passenger_count - %s WHERE flight_id = %s
    """, (len(eng_names), flight_id))
    conn.commit()

    # ★ 사용자 정보 조회
    cursor.execute("SELECT mileage FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    if user_data:
        total_mileage = user_data["mileage"]
    else:
        total_mileage = 0

    # 1인 운임
    seat_price = flight["price"]

    # 모든 탑승객 합산 운임
    total_price = seat_price * len(eng_names)

    # 적립 마일리지는 총 결제 금액의 10%
    earned_mileage = int(total_price * 0.1)

    return render_template(
        'pay/pay.html',
        booking_id=booking_id,
        total_mileage=total_mileage,
        earned_mileage=earned_mileage,
        total_price=total_price,      # 전체 운임
        seat_price=seat_price,        # 1인 운임
        airplane_name=flight["airplane_name"],
        departure_airport=flight["departure_airport"],
        arrival_airport=flight["arrival_airport"],
        seat_class=flight["seat_class"],
        passenger_count=len(eng_names),
        passenger_eng_names=eng_names
    )