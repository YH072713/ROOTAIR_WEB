from flask import Flask, Blueprint, current_app, render_template, request, jsonify, session, redirect, url_for, flash
from blueprints.utils import get_db_connection

# 블루프린트 생성
mypage_bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@mypage_bp.route('/')
def mypage():
    """마이페이지를 렌더링하는 엔드포인트"""
    user_id = session.get('user_id', 'minsoo_kim')
    username = session.get('username', '김민수')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 현재 로그인된 사용자 정보 가져오기
    cursor.execute(f"SELECT * FROM Users WHERE user_id = '{user_id}';")
    user = cursor.fetchone()
    
    cursor.execute(f"SELECT booking_id FROM Bookings WHERE username = '{username}';")
    flight_cnt = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('mypage/mypage.html', user=user, flight_cnt=len(flight_cnt))  # ✅ 예약 데이터는 API에서 별도로 가져옴

# ✅ 항공권 예약 정보를 JSON으로 반환하는 API
@mypage_bp.route('/get_tickets')
def get_tickets():
    """예약된 항공권 정보를 JSON 데이터로 반환하는 API"""
    username = session.get('username', '김민수')

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 사용자의 예약 정보 가져오기
    cursor.execute(f"SELECT * FROM Bookings WHERE username = '{username}';")
    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    processed_tickets = []
    for ticket in tickets:
        # eng_name을 "성"과 "이름"으로 분리 (예: "Kim Minsoo")
        full_name = ticket["eng_name"]
        name_parts = full_name.split(" ", 1)  # 앞에서부터 최대 2부분만 분리
        if len(name_parts) == 2:
            first_name, last_name = name_parts
        else:
            # 단어가 1개만 있거나 여러 개 있을 경우 등을 처리
            first_name = name_parts[0]
            last_name = "" if len(name_parts) == 1 else " ".join(name_parts[1:])

        # departure_time, arrival_time을 원하는 형태로 포매팅
        # DB에서 DATETIME 타입으로 가져왔다고 가정 (dictionary=True 이면 datetime 객체로 반환)
        departure_dt = ticket["departure_time"]
        arrival_dt = ticket["arrival_time"]

        # "Fri, 17 MAY 2022" 형태로 생성 (요일, 일, 월(대문자), 연도)
        departure_date_str = f"{departure_dt.strftime('%a, %d')} {departure_dt.strftime('%b').upper()} {departure_dt.strftime('%Y')}"
        arrival_date_str = f"{arrival_dt.strftime('%a, %d')} {arrival_dt.strftime('%b').upper()} {arrival_dt.strftime('%Y')}"

        # "02:16" 형태 (24시간제 시:분)
        departure_time_str = departure_dt.strftime('%H:%M')
        arrival_time_str = arrival_dt.strftime('%H:%M')

        processed_ticket = {
            "booking_id": ticket["booking_id"],
            "reservation_code": ticket["reservation_code"],
            "username": ticket["username"],
            "first_name": first_name,  
            "last_name": last_name,    
            "airplane_name": ticket["airplane_name"],
            "departure_airport": ticket["departure_airport"],
            "arrival_airport": ticket["arrival_airport"],
            "price": ticket["price"],
            "cabin_class": ticket["cabin_class"],
            "age": ticket["age"],

            # 새로 추가한 필드
            "departure_date": departure_date_str,
            "departure_time": departure_time_str,
            "arrival_date": arrival_date_str,
            "arrival_time": arrival_time_str
        }
        processed_tickets.append(processed_ticket)
        
    return jsonify(processed_tickets)

@mypage_bp.route('/edit', methods=['GET', 'POST'])
def user_edit():
    user_id = session.get('user_id', 'minsoo_kim')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        extra_address = request.form.get('extra_address')
        postal_code = request.form.get('postal_code')
        address = request.form.get('address')
        
        # 비밀번호가 입력된 경우 확인 검사
        if new_password and new_password != confirm_password:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '비밀번호가 일치하지 않습니다.'})
        
        try:
            # 비밀번호 업데이트 (입력된 경우)
            if new_password:
                cursor.execute(f"UPDATE Users SET password = '{new_password}' WHERE user_id = '{user_id}';")
            # 상세 주소 업데이트 (입력된 경우)
            if extra_address and extra_address.strip() != "":
                cursor.execute(f"UPDATE Users SET add_detail = '{extra_address}' WHERE user_id = '{user_id}';")
            # 우편번호 업데이트 (입력된 경우)
            if postal_code and postal_code.strip() != "":
                cursor.execute(f"UPDATE Users SET postal_code = '{postal_code}' WHERE user_id = '{user_id}';")
            # 주소 업데이트 (입력된 경우)
            if address and address.strip() != "":
                cursor.execute(f"UPDATE Users SET address = '{address}' WHERE user_id = '{user_id}';")
            conn.commit()
            response = {'success': True, 'message': '회원정보가 성공적으로 업데이트되었습니다.'}
        except Exception as e:
            current_app.logger.error("회원정보 업데이트 중 오류 발생: %s", e, exc_info=True)
            response = {'success': False, 'message': '업데이트 중 오류가 발생했습니다.'}
        finally:
            cursor.close()
            conn.close()
        return jsonify(response)
    
    # GET 요청 처리: 사용자 정보 조회 후 edit.html 렌더링
    try:
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
    except Exception as e:
        current_app.logger.error("사용자 정보 조회 중 오류 발생: %s", e, exc_info=True)
        user = None

    cursor.close()
    conn.close()
    return render_template('mypage/mypage_edit.html', user=user)

@mypage_bp.route('/cancel', methods=['GET', 'POST'])
def user_cancel():
    user_id = session.get('user_id', '테스트용')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'POST':
            input_password = request.form.get('password')
            
            # 현재 로그인한 사용자의 비밀번호 조회
            cursor.execute(f"SELECT password FROM users WHERE user_id = '{user_id}';")
            user = cursor.fetchone()
            
            if user is None:
                current_app.logger.error("회원 정보를 찾을 수 없습니다. user_id: %s", user_id)
                return jsonify({'success': False, 'message': "회원 정보를 찾을 수 없습니다. 다시 시도해 주십시오."})
            
            stored_password = user['password']
            
            if input_password == stored_password:
                cursor.execute(f"DELETE FROM Users WHERE user_id = '{user_id}';")
                conn.commit()
                session.pop('user_id', None)
                return jsonify({'success': True, 'message': "회원 탈퇴가 완료되었습니다."})
            else:
                return jsonify({'success': False, 'message': "입력하신 비밀번호가 일치하지 않습니다. 다시 시도해 주십시오."})
        else:
            cursor.execute(f"SELECT password FROM Users WHERE user_id = '{user_id}';")
            user = cursor.fetchone()
            return render_template('mypage/mypage_cancel.html', user=user)
    except Exception as e:
        current_app.logger.error("회원 탈퇴 처리 중 오류 발생: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': "요청 처리 중 오류가 발생했습니다."}), 500
    finally:
        cursor.close()
        conn.close()
