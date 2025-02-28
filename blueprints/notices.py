from flask import Blueprint, render_template, request, jsonify, url_for,jsonify,send_from_directory
from blueprints.utils import get_db_connection
from datetime import datetime
import pytz  # ✅ 한국 시간 변환을 위한 라이브러리 추가
import os

# 블루프린트 생성
notices_bp = Blueprint('notices', __name__, url_prefix='/notices')

UPLOAD_FOLDER='static/uploads/'

# 📌 공지사항 목록 페이지 (HTML 반환)
@notices_bp.route('/')
def notices_page():
    """공지사항 목록 페이지를 렌더링하는 엔드포인트"""
    return render_template('notices/notices.html')  # JS에서 API 호출하여 데이터 표시

# 📌 공지사항 목록 API (JSON 반환)
@notices_bp.route('/api')
def notices_api():
    """공지사항 데이터를 JSON으로 반환하는 API 엔드포인트"""
    conn = get_db_connection()
    cursor = conn.cursor()

    per_page = 5  
    page = request.args.get('page', 1, type=int)  
    offset = (page - 1) * per_page  

    # 공지사항 목록 조회
    cursor.execute('SELECT notice_id, title, file, created_at FROM notices ORDER BY created_at DESC LIMIT %s OFFSET %s', (per_page, offset))
    notices = cursor.fetchall()

    # 전체 공지사항 개수 조회
    cursor.execute('SELECT COUNT(*) AS total FROM notices')
    total_notices = cursor.fetchone()['total']
    total_pages = (total_notices + per_page - 1) // per_page  

    conn.close()

    # ✅ `created_at`을 문자열로 변환 (JSON 직렬화 오류 방지)
    for notice in notices:
        if 'created_at' in notice and notice['created_at'] is not None:
            notice['created_at'] = notice['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({'notices': notices, 'total_pages': total_pages})

# 📌 공지사항 상세 페이지 (HTML 반환)
@notices_bp.route('/<int:notice_id>')
def notice_detail_page(notice_id):
    """공지사항 상세 페이지를 렌더링하는 엔드포인트"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT notice_id, title, content, created_at FROM notices WHERE notice_id = %s', (notice_id,))
    notice = cursor.fetchone()
    conn.close()

    if notice is None:
        return "Notice Not Found", 404
    return render_template('notices/notice_detail.html', notice=notice)

# 📌 공지사항 상세 API (JSON 반환)
@notices_bp.route('/api/<int:notice_id>')
def notice_detail_api(notice_id):
    """공지사항 상세 데이터를 JSON으로 반환하는 API 엔드포인트"""
    print('여기까지가 공지사항 api')# 여기오니?
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT notice_id, title, content, created_at FROM notices WHERE notice_id = %s', (notice_id,))
    notice = cursor.fetchone()
    conn.close()

    if notice is None:
        return jsonify({'error': 'Notice Not Found'}), 404

    # ✅ `created_at`을 문자열로 변환
    if 'created_at' in notice and notice['created_at'] is not None:
        notice['created_at'] = notice['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    # ✅ 파일이 있는 경우 파일 경로 추가
    file_url = None
    if notice['file']:
        file_url = url_for('notices.download_file', filename=os.path.basename(notice['file']))  

        return jsonify({
            'notice_id': notice['notice_id'],
            'title': notice['title'],
            'content': notice['content'],
            'created_at': notice['created_at'],
            'file_url': file_url  # ✅ 파일 다운로드 URL 추가
        })

    return jsonify(notice)

#📌 공지사항 등록부분📌

# 📌 파일 다운로드 API
@notices_bp.route('/download/<filename>')
def download_file(filename):
    """업로드된 파일을 다운로드하는 API"""
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# 공지사항 등록 페이지 (입력 폼)
@notices_bp.route('/create',methods=['GET'])
def notice_create_page():
    return render_template('notices/notice_create.html')

# 📌 공지사항 등록 API (POST 요청)
@notices_bp.route('/api/create', methods=['POST'])
def notice_create_api():
    """공지사항을 DB에 등록하는 API"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 요청 데이터 가져오기
    data = request.form
    title = data.get('title')
    content = data.get('content')
    file = request.files.get('file')  # 파일 업로드 처리

    # ✅ 파일 저장 (파일이 있을 경우)
    file_url = None
    if file:
        file_path = f"static/uploads/{file.filename}"
        file.save(file_path)
        file_url = file_path

    # ✅ 한국 시간(KST)으로 현재 시간 설정
    kst = pytz.timezone('Asia/Seoul')  # 한국 시간대
    created_at = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')  # MySQL 포맷

    # ✅ DB에 저장
    cursor.execute('''
        INSERT INTO notices (title, content, file, created_at)
        VALUES (%s, %s, %s, %s)
    ''', (title, content, file_url, created_at))  # ✅ 플레이스홀더 개수와 값 개수 맞춤

    # 필수 필드 확인
    if not title or not content:
        return jsonify({'error': '제목과 내용을 입력하세요.'}), 400

    conn.commit()
    conn.close()

    # ✅ 공지사항 목록 페이지로 리디렉트
    return jsonify({'message': '공지사항이 성공적으로 등록되었습니다.', 'redirect_url': url_for('notices.notices_page')})
