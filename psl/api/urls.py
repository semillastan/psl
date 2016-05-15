from flask import Blueprint
from api.views import *

api = Blueprint('api', __name__, template_folder='templates')

api.add_url_rule('/api', view_func=ApiView.as_view('api'))
api.add_url_rule('/api/top-ten-codes/<bet_id>', view_func=TopTenCodesView.as_view('api-top-ten-codes'))
api.add_url_rule('/api/low-ten-codes/<bet_id>', view_func=LowestTenCodesView.as_view('api-low-ten-codes'))