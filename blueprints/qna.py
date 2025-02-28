from flask import Blueprint, render_template, request, redirect, url_for,jsonify,send_from_directory,session
from flask_login import login_required,current_user
import os
from blueprints.utils import get_db_connection

#from flask_login import login_required, current_user
qna_bp = Blueprint('qna', __name__,url_prefix='/qna')
UPLOAD_FOLDER='static/uploads/'

# 📌 문의사항 목록 페이지 (HTML 반환)
@qna_bp.route('/')
@login_required
def qna_page():
    """문의사항 목록 페이지 렌더링"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    return render_template('qna/qna.html')  # JS에서 API 호출하여 데이터 표시

# 📌 문의사항 목록 API (JSON 반환)
@qna_bp.route('/api')
@login_required
def qna_api():
    """문의사항 데이터를 JSON으로 반환"""
    conn = get_db_connection()
    cursor = conn.cursor()

    per_page = 5  # 페이지당 문의 개수
    page = request.args.get('page', 1, type=int)  # 페이지 값 가져오기
    offset = (page - 1) * per_page  

    # 문의사항 목록 조회
    cursor.execute("""
        SELECT qna_id, title, user_id, IFNULL(is_secret, 0) AS is_secret,created_at
        FROM qna
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    qna_list = cursor.fetchall()
    print("🔥 [DEBUG] 원본 qna_list:", qna_list)

    # 전체 문의사항 개수 조회
    cursor.execute("SELECT COUNT(*) AS total FROM qna")
    total_qna = cursor.fetchone()['total']
    total_pages = (total_qna + per_page - 1) // per_page  

    # ✅ 현재 로그인한 사용자의 ID 가져오기 (세션에서 확인)
    current_user_id = current_user.user_id
    print(f"🔥 [DEBUG] 현재 로그인한 user_id: {current_user_id}")

    # ✅ 비밀글이면 제목을 "비밀글입니다."로 변경
    for qna in qna_list:
        if qna['is_secret'] and qna['user_id'] != current_user_id:
            qna['title'] = "🔒 비밀글입니다."

        # `created_at` 날짜를 문자열로 변환
        if 'created_at' in qna and qna['created_at'] is not None:
            qna['created_at'] = qna['created_at'].strftime('%Y-%m-%d')


    conn.close()
    return jsonify({'qna': qna_list, 'total_pages': total_pages,'current_user_id': current_user_id})



# 📌 나의 문의 HTML 페이지 반환
@qna_bp.route('/my')
@login_required 
def my_qna_page():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    return render_template('qna/qna_my.html')

# 📌 나의 문의 API (로그인한 사용자만 조회, JS에서 페이지네이션 처리)
@qna_bp.route('/api/my')
@login_required  
def my_qna_api():
    """나의 문의 데이터를 JSON으로 반환 (현재 로그인 필터링 미적용)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 현재 로그인한 사용자 ID 가져오기
    current_user_id = current_user.user_id
    if not current_user_id:
        conn.close()
        return jsonify({"error": "로그인이 필요합니다."}), 403

    per_page = 3  # 페이지당 개수
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    # ✅ 현재는 모든 데이터를 가져옴 (나중에 로그인 기능이 추가되면 `WHERE user_id = %s` 조건 활성화)
    cursor.execute('''
        SELECT qna_id, title, created_at
        FROM qna
        WHERE user_id = %s  
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    ''', (current_user_id,per_page, offset))
    
    qna_list = cursor.fetchall()

    # 총 문의 개수 조회 (현재 모든 문의 개수를 반환)
    cursor.execute('SELECT COUNT(*) AS total FROM qna')
    total_qna = cursor.fetchone()['total']
    total_pages = (total_qna + per_page - 1) // per_page

    conn.close()

    # ✅ 날짜 변환
    for qna in qna_list:
        if 'created_at' in qna and qna['created_at'] is not None:
            qna['created_at'] = qna['created_at'].strftime('%Y-%m-%d')

    return jsonify({'qna_list': qna_list, 'total_pages': total_pages})

# 📌 문의사항 상세 페이지 (HTML 반환)
@qna_bp.route('/<int:qna_id>')
def qna_detail_page(qna_id):
    """문의사항 상세 페이지를 렌더링하는 엔드포인트"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 올바른 컬럼명으로 수정하여 데이터 조회
    cursor.execute('''
        SELECT qna_id, title, content, user_id, comment, created_at, file
        FROM qna
        WHERE qna_id = %s
    ''', (qna_id,))
    
    qna = cursor.fetchone()
    conn.close()

    if not qna:
        return "문의사항을 찾을 수 없습니다.", 404
    
    if qna['file'] is None:
        qna['file']=""

    # ✅ HTML 페이지 렌더링 시 qna 데이터를 넘겨줌
    return render_template('qna/qna_detail.html', qna=qna, qna_id=qna_id)

# 📌 문의사항 상세 API (JSON 반환)
@qna_bp.route('/api/<int:qna_id>')
@login_required
def qna_detail_api(qna_id):
    """문의사항 상세 데이터를 JSON으로 반환하는 API"""

    if not current_user.is_authenticated:
        return jsonify({'error': '로그인이 필요합니다.'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT qna_id, title, content, user_id, comment, created_at,file,is_secret
        FROM qna
        WHERE qna_id = %s
    ''', (qna_id,))
    
    qna = cursor.fetchone()
    conn.close()

    if not qna:
        return jsonify({'error': '문의사항을 찾을 수 없습니다.'}), 404
    
    # ✅ 현재 로그인한 사용자 ID 가져오기
    current_user_id = current_user.user_id
    print(f"🔥 [DEBUG] 현재 로그인한 user_id: {current_user_id}, 글 작성자 user_id: {qna['user_id']}")

    # ✅ 비밀글 접근 권한 확인
    if qna['is_secret'] and qna['user_id'] != current_user_id:
        print(f"🚨 [ERROR] 비밀글 접근 차단: current_user: {current_user_id}, 글쓴이: {qna['user_id']}")
        return jsonify({'error': '비밀글은 작성자만 볼 수 있습니다.'}), 403

    current_user_id = current_user.user_id
    # ✅ JSON 직렬화를 위해 날짜 변환
    if 'created_at' in qna and qna['created_at']:
        qna['created_at'] = qna['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    # ✅ 파일이 있는 경우 파일 경로 추가
    file_url = None
    if qna['file']:
        file_url = url_for('qna.download_file', filename=os.path.basename(qna['file']))  

    return jsonify({
        'qna_id': qna['qna_id'],
        'title': qna['title'],
        'content': qna['content'],
        'user_id': qna['user_id'],
        'current_user_id': current_user_id,
        'is_secret': qna['is_secret'],
        'comment': qna['comment'],
        'created_at': qna['created_at'],
        'file_url': file_url  # ✅ 파일 다운로드 URL 추가
    })

# 📌 파일 다운로드 API
@qna_bp.route('/download/<filename>')
def download_file(filename):
    """업로드된 파일을 다운로드하는 API"""
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# 📌 문의사항 등록 페이지 (입력 폼)
@qna_bp.route('/create',methods=['GET'])
def qna_create_page():
    return render_template('qna/qna_create.html')

# 📌 문의사항 등록 API (POST 요청)
@qna_bp.route('/api/create', methods=['POST'])
def qna_create_api():
    """문의사항을 DB에 등록하는 API"""
    print(f"🔍 [DEBUG] 세션 user_id: {current_user.user_id}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 로그인한 사용자 ID 가져오기
    session_user_id = current_user.user_id
    if not session_user_id:
        conn.close()
        return jsonify({'error': '로그인이 필요합니다.'}), 403
 
    # ✅ users 테이블에서 실제 user_id 가져오기
    # cursor.execute("SELECT user_id FROM users WHERE id = %s", (current_user.id,))
    # user_data = cursor.fetchone()

    # if not user_data:
    #     conn.close()
    #     return jsonify({'error': '유효하지 않은 사용자입니다.'}), 403

    # user_id = user_data['user_id']  # users 테이블의 user_id 가져오기
    user_id = current_user.user_id  # 이제 user_id 직접 사용 가능!


    # ✅ 요청 데이터 가져오기
    data = request.form
    title = data.get('title')
    content = data.get('content')
    file = request.files.get('file')  # 파일 업로드 처리

    # ✅ 요청된 isSecret 값 확인
    is_secret_raw = data.get('isSecret')
    print("🔥 [DEBUG] 요청된 isSecret 값:", is_secret_raw)

    # ✅ 문자열 값을 0 또는 1로 변환하여 저장
    is_secret = 1 if is_secret_raw == "true" else 0
    print("🔥 [DEBUG] 변환된 is_secret 값:", is_secret)   
  
    # ✅ 필수 필드 확인
    if not title or not content:
        conn.close()
        return jsonify({'error': '제목과 내용을 입력하세요.'}), 400

    # ✅ 파일 저장 (파일이 있을 경우)
    file_url = None
    if file:
        file_path = f"static/uploads/{file.filename}"
        file.save(file_path)
        file_url = file_path

    # ✅ DB에 저장
    cursor.execute('''
        INSERT INTO qna (user_id, title, content, file, is_secret, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    ''', (user_id, title, content, file_url, is_secret))

    # 필수 필드 확인
    if not title or not content:
        return jsonify({'error': '제목과 내용을 입력하세요.'}), 400

    conn.commit()
    conn.close()
    print(f"✅ [DEBUG] 문의사항 등록 완료 (is_secret={is_secret})")

    # ✅ 문의사항 목록 페이지로 리디렉트
    return jsonify({'message': '문의사항이 성공적으로 등록되었습니다.', 'redirect_url': url_for('qna.qna_page')})

# 📌 문의사항 수정 페이지 (HTML 반환)
@qna_bp.route('/edit/<int:qna_id>', methods=['GET'])
def qna_edit_page(qna_id):
    """문의사항 수정 페이지 렌더링"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT qna_id, title, content, file, is_secret
        FROM qna
        WHERE qna_id = %s
    ''', (qna_id,))
    
    qna = cursor.fetchone()
    conn.close()

    if not qna:
        return "문의사항을 찾을 수 없습니다.", 404

    return render_template('qna/qna_edit.html', qna=qna)


# 📌 문의사항 수정 API (POST 요청)
@qna_bp.route('/api/edit/<int:qna_id>', methods=['POST'])
def qna_edit_api(qna_id):
    """문의사항을 수정하는 API"""
    print(f"수정할 문의사항 ID: {qna_id}")

    if not current_user.is_authenticated:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

   # user_id = current_user.user_id
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 해당 글이 존재하는지 확인 (그리고 user_id 가져오기)
    cursor.execute("SELECT user_id FROM qna WHERE qna_id = %s", (qna_id,))
    inquiry = cursor.fetchone()

    if not inquiry:
        conn.close()
        return jsonify({'error': '문의사항을 찾을 수 없습니다.'}), 404

    # inquiry_user_id = inquiry['user_id']  # ✅ 글 작성자의 user_id 가져오기

    # ✅ 본인이 작성한 글인지 확인
    # if user_id != inquiry_user_id:
    #     conn.close()
    #     return jsonify({'error': '본인이 작성한 글만 수정할 수 있습니다.'}), 403

    # 요청 데이터 가져오기
    data = request.form
    title = data.get('title')
    content = data.get('content')
    is_private = data.get('isPrivate') == "true"

    # 필수 필드 확인
    if not title or not content:
        return jsonify({'error': '제목과 내용을 입력하세요.'}), 400

    # ✅ 기존 파일 유지
    cursor.execute("SELECT file FROM qna WHERE qna_id = %s", (qna_id,))
    existing_file_data = cursor.fetchone()
    existing_file = existing_file_data['file'] if existing_file_data else None

    file = request.files.get('file')
    file_url = existing_file

    if file:
        filename = file.filename  # 원본 파일명 유지
        file_path = f"static/uploads/{filename}"
        file.save(file_path)
        file_url = file_path  # 새로운 파일 저장

    # ✅ 기존 글 수정
    cursor.execute('''
        UPDATE qna
        SET title = %s, content = %s, file = %s, is_secret = %s
        WHERE qna_id = %s
    ''', (title, content, file_url, is_private, qna_id))

    conn.commit()

    # ✅ 수정이 정상적으로 이루어졌는지 확인
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': '문의사항 수정에 실패했습니다. 해당 ID가 존재하지 않습니다.'}), 404


    conn.close()

    return jsonify({'message': '문의사항이 성공적으로 수정되었습니다.', 'redirect_url': url_for('qna.qna_page')})

# 📌 문의사항 삭제 API 
@qna_bp.route('/api/delete/<int:qna_id>', methods=['DELETE'])
def qna_delete_api(qna_id):
    """문의사항 삭제 API"""
    print(f"🔍 삭제 요청 받음: 문의 ID {qna_id}")  # ✅ 로그 추가

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 먼저 해당 글이 존재하는지 확인
    cursor.execute("SELECT * FROM qna WHERE qna_id = %s", (qna_id,))
    qna = cursor.fetchone()

    if not qna:
        conn.close()
        return jsonify({'error': '삭제할 게시글을 찾을 수 없습니다.'}), 404

    # ✅ 문의사항 삭제
    cursor.execute("DELETE FROM qna WHERE qna_id = %s", (qna_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        print(f"⚠️ 삭제 실패: 문의사항 {qna_id} 삭제되지 않음")  # ✅ 로그 추가
        return jsonify({'error': '삭제 실패. 다시 시도해주세요.'}), 40
    conn.close()

    print(f"✅ 문의사항 {qna_id} 삭제 완료!")  # 디버깅용 로그 추가

    return jsonify({'message': '문의사항이 성공적으로 삭제되었습니다.', 'redirect_url': url_for('qna.qna_page')})


# 📌 문의사항 관리자 답변 API
@qna_bp.route('/api/comment/<int:qna_id>', methods=['POST'])
def add_comment(qna_id):
    """관리자가 문의사항에 답변을 등록하는 API"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 관리자라고 가정
    is_admin = True  # ❗️ 실제 시스템에서는 세션이나 인증으로 체크해야 함

    if not is_admin:
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403

    # 요청 데이터 가져오기
    data = request.get_json()
    comment = data.get('comment')

    if not comment:
        return jsonify({'error': '답변을 입력하세요.'}), 400

    # ✅ 해당 문의사항이 존재하는지 확인
    cursor.execute("SELECT * FROM qna WHERE qna_id = %s", (qna_id,))
    qna = cursor.fetchone()

    if not qna:
        conn.close()
        return jsonify({'error': '문의사항을 찾을 수 없습니다.'}), 404

    # ✅ DB에 답변 업데이트
    cursor.execute('''
        UPDATE qna
        SET comment = %s
        WHERE qna_id = %s
    ''', (comment, qna_id))

    conn.commit()
    conn.close()

    print(f"✅ 문의 {qna_id}에 대한 답변이 등록됨: {comment}")  # 로그 확인

    return jsonify({'message': '답변이 성공적으로 등록되었습니다.', 'comment': comment})
