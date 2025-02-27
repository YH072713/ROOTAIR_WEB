from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, session
from flask_mail import Message
from blueprints.utils import get_db_connection  # utils.py에서 함수 가져오기
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
import smtplib
import datetime
from flask_login import UserMixin

# Blueprint 생성
member_bp = Blueprint('member', __name__, url_prefix='/member')

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, user_id, password=None):
        self.id = id
        self.user_id = user_id
        self.password = password

@member_bp.route('/protected')
@login_required
def protected():
    return jsonify({"message": f"Welcome, {current_user.user_id}! This is a protected page."})

@member_bp.route('/')
def main():
    return render_template('member/member_email.html')

# OTP 생성 함수
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@member_bp.route('/email-confirm', methods=['GET'])
@login_required
def email_confirm_page():
    return render_template('member/member_email.html')

# 이메일 인증 요청 API
@member_bp.route('/request-verification', methods=['POST'])
def request_verification():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 이메일 중복 확인
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_email = cursor.fetchone()

            if existing_email:
                return jsonify({"error": "Email already registered"}), 400

            otp = generate_otp()

            # OTP 저장 (기존 값이 있으면 업데이트)
            cursor.execute("""
                INSERT INTO verifications (email, otp, verified)
                VALUES (%s, %s, FALSE)
                ON DUPLICATE KEY UPDATE otp = %s, verified = FALSE
            """, (email, otp, otp))
            connection.commit()

            #이메일 전송 로직 (생략 가능)
            msg = Message('이메일 인증 코드', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'귀하의 인증 코드는 {otp}입니다.'
            current_app.extensions['mail'].send(msg)

        return jsonify({"message": "Verification code sent"}), 200

    except Exception as e:
        current_app.logger.error(f"Error in request_verification: {str(e)}")
        return jsonify({"error": "An error occurred. Please try again later."}), 500

    finally:
        try:
            if connection:
                connection.close()
        except Exception as e:
            current_app.logger.error(f"Error closing database connection: {str(e)}")

# 이메일 인증 확인 API
@member_bp.route('/verify', methods=['POST'])
def verify():
    email = request.json.get('email')
    user_otp = request.json.get('otp')

    if not email or not user_otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT otp FROM verifications WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result and result['otp'] == user_otp:
                cursor.execute("UPDATE verifications SET verified = TRUE WHERE email = %s", (email,))
                connection.commit()
                session['verified_email'] = email
                return jsonify({
                    "message": "Verification successful",
                    "email": email,
                    "redirect_url": url_for('member.signup')
                }), 200

        return jsonify({"error": "Invalid OTP"}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    finally:
        connection.close()

###########회원가입##############
@member_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:  # Flask-Login을 사용하는 경우, 로그인사용자의 경우 마이페이지로 보낸다다
        return redirect(url_for('mypage.mypage'))
    
    if request.method == 'GET':
        verified_email = session.get('verified_email')
        if not verified_email:
            return redirect(url_for('member.main'))  # 이메일 인증 페이지로 리다이렉션
        return render_template('member/member_signup.html', email=verified_email)
    
    if request.method == 'POST':
        data = request.json
        required_fields = ['email', 'username', 'user_id', 'password', 'password_confirm', 'postal_code', 'address', 'add_detail', 'phone_number']
        
        if not all(data.get(field) for field in required_fields):
            return jsonify({"error": "All fields are required"}), 400
        
        if data['password'] != data['password_confirm']:
            return jsonify({"error": "Passwords do not match"}), 400
        
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT verified FROM verifications WHERE email = %s", (data['email'],))
                result = cursor.fetchone()
                if not result or not result['verified']:
                    return jsonify({"error": "Email not verified"}), 400

                hashed_password = generate_password_hash(data['password'])
                
                cursor.execute("""
                    INSERT INTO users (username, user_id, email, password, postal_code, address, add_detail, phone_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['username'], data['user_id'], data['email'], hashed_password,
                    data['postal_code'], data['address'], data['add_detail'], data['phone_number']
                ))
                connection.commit()
                return jsonify({"message": "Sign up successful"}), 200

        except Exception as e:
            connection.rollback()
            return jsonify({"error": f"An error occurred during sign up: {str(e)}"}), 500
        finally:
            connection.close()

@member_bp.route('/check-id', methods=['POST'])
def check_id():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
            existing_id = cursor.fetchone()

            if existing_id:
                return jsonify({"available": False, "message": "이미 사용 중인 아이디입니다."}), 200
            else:
                return jsonify({"available": True, "message": "사용 가능한 아이디입니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

######################로그인#########################
@member_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:  # Flask-Login을 사용하는 경우, 로그인사용자의 경우 마이페이지로 보낸다다
        return redirect(url_for('mypage.mypage'))
    return render_template('member/member_login.html')

@member_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, user_id, password FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()

            if user_data and check_password_hash(user_data['password'], password):
                user = User(id=user_data['id'], user_id=user_data['user_id'])
                login_user(user, remember=True)
                session['user_id'] = user_data['id']
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid user ID or password"}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred during login: {str(e)}"}), 500
    finally:
        connection.close()

@member_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

#####################회원정보 수정#########################################
# @member_bp.route('/edit_info', methods=['GET', 'POST'])
# @login_required
# def edit_info():
#     if 'user_id' not in session:
#         return jsonify({"error": "User not logged in"}), 401
    
#     current_user_id = session['user_id']
    
#     if request.method == 'GET':
#         try:
#             connection = get_db_connection()
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT * FROM users WHERE id = %s", (current_user_id,))
#                 user = cursor.fetchone()
            
#             if not user:
#                 return jsonify({"error": "User not found"}), 404
            
#             return render_template('member/edit_info.html', user=user)
#         finally:
#             connection.close()
    
#     if request.method == 'POST':
#         data = request.json
#         updates = {}
#         if 'new_password' in data and data['new_password']:
#             updates['password'] = generate_password_hash(data['new_password'])
#         if 'address' in data:
#             updates['address'] = data['address']
#         if 'postal_code' in data:
#             updates['postal_code'] = data['postal_code']
#         if 'add_detail' in data:
#             updates['add_detail'] = data['add_detail']

#         if updates:
#             try:
#                 connection = get_db_connection()
#                 with connection.cursor() as cursor:
#                     update_query = "UPDATE users SET " + ", ".join([f"{key} = %s" for key in updates.keys()]) + " WHERE id = %s"
#                     cursor.execute(update_query, list(updates.values()) + [current_user_id])
#                 connection.commit()
#                 return jsonify({"success": True, "message": "프로필이 성공적으로 업데이트되었습니다."})
#             except Exception as e:
#                 connection.rollback()
#                 print(f"Profile update error: {str(e)}")
#                 return jsonify({"success": False, "message": f"프로필 업데이트 중 오류가 발생했습니다: {str(e)}"}), 500
#             finally:
#                 connection.close()
#         else:
#             return jsonify({"success": True, "message": "변경된 내용이 없습니다."})

#     return jsonify({"error": "Invalid request method"}), 405

# ################회원 탈퇴##########################
# @member_bp.route('/user_delete', methods=['GET', 'POST'])
# @login_required
# def user_delete():
#     if 'user_id' not in session:
#         return redirect(url_for('member.login'))  # 로그인 페이지로 리다이렉트

#     current_user_id = session['user_id']

#     if request.method == 'GET':
#         try:
#             connection = get_db_connection()
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT username FROM users WHERE id = %s", (current_user_id,))
#                 user = cursor.fetchone()
#             if user:
#                 return render_template('member/user_delete.html', username=user['username'])
#             else:
#                 return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
#         finally:
#             connection.close()

#     if request.method == 'POST':
#         password = request.json.get('password')

#         if not password:
#             return jsonify({"error": "비밀번호를 입력해주세요."}), 400

#         try:
#             connection = get_db_connection()
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT * FROM users WHERE id = %s", (current_user_id,))
#                 user = cursor.fetchone()

#             if not user:
#                 return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

#             if check_password_hash(user['password'], password):
#                 with connection.cursor() as cursor:
#                     cursor.execute("DELETE FROM users WHERE id = %s", (current_user_id,))
#                 connection.commit()
#                 session.clear()  # 세션 정보 삭제
#                 return jsonify({"message": "회원 탈퇴가 완료되었습니다.", "success": True}), 200
#             else:
#                 return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 400

#         except Exception as e:
#             connection.rollback()
#             print(f"Error during user deletion: {str(e)}")
#             return jsonify({"error": "회원 탈퇴 중 오류가 발생했습니다."}), 500
#         finally:
#             connection.close()

#     return jsonify({"error": "Invalid request method"}), 405

###########################비밀번호 찾기##########################################

# 인증코드 생성 함수
def generate_otp():
    """6자리 인증 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))



# ✅ HTML 페이지 렌더링
@member_bp.route('/forgot_password')
def forgot_password():
    return render_template('member/member_find.html')

# step 1
@member_bp.route('/request-reset-code', methods=['POST'])
def request_reset_code():
    """사용자가 입력한 아이디를 확인하고 인증 코드 발송"""
    data = request.json
    user_id = data.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ DB에서 해당 아이디의 이메일 조회
    cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    print("🔹 조회된 사용자 정보:", user)  # 🔍 디버깅 출력

    if not user:
        conn.close()
        return jsonify({"success": False, "message": "아이디를 찾을 수 없습니다."})

    email = user["email"]
    otp = generate_otp()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # 10분 유효


    # 2️⃣ 기존 인증 코드 삭제 후 새 코드 삽입
    cursor.execute("DELETE FROM verifications WHERE email = %s", (email,))
    cursor.execute(
    "INSERT INTO verifications (email, otp, expires_at) VALUES (%s, %s, NOW() + INTERVAL 10 MINUTE)",
    (email, otp),
)

    conn.commit()
    conn.close()

    session["email"] = email  # 세션 저장
    print("세션 저장됨:", session.get("email"))

    # 3️⃣ 실제 이메일 발송 로직 (이메일 서버 필요)
    msg = Message('이메일 인증 코드', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'귀하의 인증 코드는 {otp}입니다.'
    current_app.extensions['mail'].send(msg)

    return jsonify({"success": True, "message": "인증 코드가 이메일로 전송되었습니다."})


# step 2
@member_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """사용자가 입력한 인증 코드 검증"""
    data = request.json
    email = session.get("email") # step1에 email 세션사용 및 OTP 검증용으로 사용용
    otp_input = data.get("otp")

    if not email or not otp_input:
        return jsonify({"success": False, "message": "잘못된 요청입니다."})

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ 사용자 이메일 가져오기

    # 2️⃣ OTP 검증
    cursor.execute(
        "SELECT otp, expires_at FROM verifications WHERE email = %s", (email,)
    )
    otp_record = cursor.fetchone()
    

    if not otp_record:
        conn.close()
        return jsonify({"success": False, "message": "인증 코드가 존재하지 않습니다."})


    
    # 인증 코드 만료기간 확인 mysql에서 쿼리문으로 비교하는방법
    cursor.execute(
        "SELECT COUNT(*) AS valid FROM verifications WHERE email = %s AND expires_at > NOW()",
        (email,),
    )
    otp_valid = cursor.fetchone()["valid"]

    if otp_valid == 0:
        conn.close()
        return jsonify({"success": False, "message": "인증 코드가 만료되었습니다."})

    # DB에 저장된 otp를 가져와 stored_otp에 저장
    stored_otp = otp_record["otp"]
    #인증 코드 맞는지 틀린지 비교
    if stored_otp != otp_input:
        conn.close()
        return jsonify({"success": False, "message": "인증 코드가 일치하지 않습니다."})

    # 3️⃣ 인증 코드 사용 후 삭제
    cursor.execute("DELETE FROM verifications WHERE email = %s", (email,))
    conn.commit()
    conn.close()

    session["verified"] = True  # ✅ Step 3 진행 가능하도록 세션 저장
    print("✅ Step 2 인증 완료, 세션 저장:", session.get("verified"))  # 디버깅용 출력

    return jsonify({"success": True, "message": "인증이 완료되었습니다."})

#step3
@member_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = session.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return jsonify({"success": False, "message": "잘못된 요청입니다."})
    
    if not session.get("verified"):
        return jsonify({"success": False, "message": "인증이 완료되지 않았습니다. Step 2를 먼저 수행하세요."})
    
    try:
        # 비밀번호 해싱
        hashed_password = generate_password_hash(new_password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 비밀번호 업데이트
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if affected_rows > 0:
            return jsonify({"success": True, "message": "비밀번호가 성공적으로 변경되었습니다."})
        else:
            return jsonify({"success": False, "message": "비밀번호 변경에 실패했습니다. 사용자를 찾을 수 없습니다."})
    
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        return jsonify({"success": False, "message": "비밀번호 변경 중 오류가 발생했습니다."})