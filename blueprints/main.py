from flask import Blueprint, render_template
from blueprints.utils import get_db_connection

main_bp = Blueprint('main', __name__, url_prefix='/main')

@main_bp.route('/')
def main():
    return render_template('main/main.html')
