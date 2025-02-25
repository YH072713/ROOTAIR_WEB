from flask import Blueprint, render_template, request, jsonify
from blueprints.utils import get_db_connection

# 블루프린트 생성
notices_bp = Blueprint('notices', __name__, url_prefix='/notices')

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

    return jsonify(notice)