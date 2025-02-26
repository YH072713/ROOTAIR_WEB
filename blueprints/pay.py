from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

pay_bp = Blueprint('pay', __name__, url_prefix='/pay')

# 📌 예약 페이지 라우트
@pay_bp.route('/')
def pay():
    return render_template('reservation.html')
