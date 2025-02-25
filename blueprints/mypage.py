from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

mypage_bp = Blueprint('mypage', __name__, url_prefix='/mypage')

# 📌 예약 페이지 라우트
@mypage_bp.route('/')
def main():
    return render_template('reservation.html')
