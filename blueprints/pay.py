from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

pay_bp = Blueprint('pay', __name__, url_prefix='/pay')

# 📌 예시
@pay_bp.route('/')
def main():
    return render_template('reservation.html')
