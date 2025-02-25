from flask import Blueprint, render_template, request, jsonify
from blueprints.utils import get_db_connection

# 블루프린트 생성
notices_bp = Blueprint('notices', __name__, url_prefix='/notices')

# 📌 공지사항 목록 페이지 (HTML 반환)
@notices_bp.route('/')
def notices_page():
    """공지사항 목록 페이지를 렌더링하는 엔드포인트"""
    return render_template('notices/notices.html')  # JS에서 API 호출하여 데이터 표시

