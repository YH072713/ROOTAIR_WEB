from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

member_bp = Blueprint('member', __name__, url_prefix='/member')

# 로그인 페이지
@member_bp.route('/login')
def login():
    return render_template('login.html')

# 회원가입 페이지
@member_bp.route('/signup')
def signup():
    return render_template('signup.html')

