from flask import Blueprint, current_app, flash, render_template, request, jsonify, session, redirect, url_for
from blueprints.utils import get_db_connection
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# 블루프린트 생성
mypage_bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@mypage_bp.route('/')
@login_required
def mypage():
    """마이페이지를 렌더링하는 엔드포인트"""

    # 🔹 Flask-Login을 사용하여 로그인 여부 확인
    if not current_user.is_authenticated:
        return redirect(url_for('member.login'))  # 로그인 페이지로 리디렉트

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 현재 로그인된 사용자 정보 가져오기
    try:
        # 현재 로그인된 사용자 정보 가져오기
        cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
        user = cursor.fetchone()
        
        cursor.execute("SELECT booking_id FROM bookings WHERE username = %s", (current_user.username,))
        flight_cnt = cursor.fetchall()
        
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return jsonify({"error": "Failed to fetch user data"}), 500

    cursor.close()
    conn.close()

    return render_template('mypage/mypage.html', user=user, flight_cnt=len(flight_cnt))  # ✅ 예약 데이터는 API에서 별도로 가져옴

# ✅ 항공권 예약 정보를 JSON으로 반환하는 API
# @mypage_bp.route('/get_tickets')
# @login_required
# def get_tickets():
    # """예약된 항공권 정보를 JSON 데이터로 반환하는 API"""
    # if 'user_id' not in session:
    #     return jsonify({"error": "user not logged in"}), 401            
    
    # conn = get_db_connection()
    # cursor = conn.cursor()

    # ✅ 사용자의 예약 정보 가져오기
    # cursor.execute("SELECT * FROM Users WHERE id = %s", (current_user.id,))
    # tickets = cursor.fetchone()

    # cursor.close()
    # conn.close()

    #processed_tickets = []
    # for ticket in tickets:
    #     # eng_name을 "성"과 "이름"으로 분리 (예: "Kim Minsoo")
    #     full_name = ticket["eng_name"]
    #     name_parts = full_name.split(" ", 1)  # 앞에서부터 최대 2부분만 분리
    #     if len(name_parts) == 2:
    #         first_name, last_name = name_parts
    #     else:
    #         # 단어가 1개만 있거나 여러 개 있을 경우 등을 처리
    #         first_name = name_parts[0]
    #         last_name = "" if len(name_parts) == 1 else " ".join(name_parts[1:])

    #     # departure_time, arrival_time을 원하는 형태로 포매팅
    #     # DB에서 DATETIME 타입으로 가져왔다고 가정 (dictionary=True 이면 datetime 객체로 반환)
    #     departure_dt = ticket["departure_time"]
    #     arrival_dt = ticket["arrival_time"]

    #     # "Fri, 17 MAY 2022" 형태로 생성 (요일, 일, 월(대문자), 연도)
    #     departure_date_str = f"{departure_dt.strftime('%a, %d')} {departure_dt.strftime('%b').upper()} {departure_dt.strftime('%Y')}"
    #     arrival_date_str = f"{arrival_dt.strftime('%a, %d')} {arrival_dt.strftime('%b').upper()} {arrival_dt.strftime('%Y')}"

    #     # "02:16" 형태 (24시간제 시:분)
    #     departure_time_str = departure_dt.strftime('%H:%M')
    #     arrival_time_str = arrival_dt.strftime('%H:%M')

    #     processed_ticket = {
    #         "booking_id": ticket["booking_id"],
    #         "reservation_code": ticket["reservation_code"],
    #         "username": ticket["username"],
    #         "first_name": first_name,  
    #         "last_name": last_name,    
    #         "airplane_name": ticket["airplane_name"],
    #         "departure_airport": ticket["departure_airport"],
    #         "arrival_airport": ticket["arrival_airport"],
    #         "price": ticket["price"],
    #         "cabin_class": ticket["cabin_class"],
    #         "age": ticket["age"],

    #         # 새로 추가한 필드
    #         "departure_date": departure_date_str,
    #         "departure_time": departure_time_str,
    #         "arrival_date": arrival_date_str,
    #         "arrival_time": arrival_time_str
    #     }
    #     processed_tickets.append(processed_ticket)
        
    # return jsonify(processed_tickets)

@mypage_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def user_edit():

    if 'user_id' not in session:
        return redirect(url_for('member.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user = cursor.fetchone()

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
            # 변경: SQL 인젝션 방지를 위해 파라미터화된 쿼리 사용
            updates = []
            values = []
            if new_password:
                updates.append("password = %s")
                # 변경: 비밀번호 해싱 추가
                values.append(generate_password_hash(new_password))
            if extra_address and extra_address.strip():
                updates.append("add_detail = %s")
                values.append(extra_address)
            if postal_code and postal_code.strip():
                updates.append("postal_code = %s")
                values.append(postal_code)
            if address and address.strip():
                updates.append("address = %s")
                values.append(address)
            
            if updates:
                # 변경: 동적 쿼리 생성 및 파라미터 사용
                query = f"UPDATE Users SET {', '.join(updates)} WHERE id = %s"
                values.append(current_user.id)
                cursor.execute(query, tuple(values))
                conn.commit()
                response = {'success': True, 'message': '회원정보가 성공적으로 업데이트되었습니다.'}
            else:
                response = {'success': False, 'message': '변경된 정보가 없습니다.'}
        except Exception as e:
            current_app.logger.error("회원정보 업데이트 중 오류 발생: %s", e, exc_info=True)
            response = {'success': False, 'message': '업데이트 중 오류가 발생했습니다.'}
        finally:
            cursor.close()
            conn.close()
        return jsonify(response)
    
    # 변경: GET 요청 처리 간소화 (이미 위에서 user 정보를 조회했으므로 중복 제거)
    return render_template('mypage/mypage_edit.html', user=user)

@mypage_bp.route('/cancel', methods=['GET', 'POST'])
@login_required
def user_cancel():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", (current_user.id,))
                user = cursor.fetchone()
            if user:
                return render_template('mypage/mypage_cancel.html', username=user['username'])
            else:
                return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
        finally:
            connection.close()

    if request.method == 'POST':
        password = request.json.get('password')

        if not password:
            return jsonify({"error": "비밀번호를 입력해주세요."}), 400

        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
                user = cursor.fetchone()

            if not user:
                return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

            if check_password_hash(user['password'], password):
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE id = %s", (current_user.id,))
                connection.commit()
                session.clear()  # 세션 정보 삭제
                return jsonify({"message": "회원 탈퇴가 완료되었습니다.", "success": True}), 200
            else:
                return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 400

        except Exception as e:
            connection.rollback()
            print(f"Error during user deletion: {str(e)}")
            return jsonify({"error": "회원 탈퇴 중 오류가 발생했습니다."}), 500
        finally:
            connection.close()

    return jsonify({"error": "Invalid request method"}), 405