from flask import Blueprint
from reports.views import *

reports = Blueprint('reports', __name__, template_folder='templates')

reports.add_url_rule('/reports', view_func=ReportsView.as_view('index'))