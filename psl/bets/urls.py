from flask import Blueprint
from bets.views import *

bets = Blueprint('bets', __name__, template_folder='templates')

bets.add_url_rule('/bets', view_func=IndexView.as_view('index'))
# BETS
bets.add_url_rule('/bets/create', view_func=CreateBetView.as_view('create'))
bets.add_url_rule('/bets/<bet_id>/delete', view_func=DeleteBetView.as_view('delete'))
bets.add_url_rule('/bets/settings', view_func=SettingsView.as_view('settings'))

bets.add_url_rule('/bets/daily', view_func=DailyBetsView.as_view('daily-bets'))
bets.add_url_rule('/bets/place-bets', view_func=PlaceBetsView.as_view('place-bets'))
bets.add_url_rule('/bets/<bet_id>/place-bets/manual', view_func=ManualPlaceBetsView.as_view('manual-place-bets'))
bets.add_url_rule('/bets/<day>', view_func=ShowBetsView.as_view('show-bets'))
bets.add_url_rule('/bets/transaction/create', view_func=CreateTransactionView.as_view('create-transaction'))
