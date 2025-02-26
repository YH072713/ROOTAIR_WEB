from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

member_bp = Blueprint('member', __name__, url_prefix='/member')

# 📌 
@member_bp.route('/')
def login():
    return render_template('reservation.html')

# 📌 
@member_bp.route('/')
def signup():
    return render_template('reservation.html')