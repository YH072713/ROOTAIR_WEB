from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

qna_bp = Blueprint('qna', __name__, url_prefix='/qna')

# 📌 예시
@qna_bp.route('/')
def main():
    return render_template('reservation.html')
