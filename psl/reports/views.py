from flask import Blueprint, request, redirect, render_template, url_for, flash, g, session, jsonify
from flask.ext.mongoengine.wtf import model_form
from flask.views import MethodView, View
from mongoengine.errors import NotUniqueError, DoesNotExist
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_wtf import Form
from datetime import datetime

from psl import app, login_manager
from accounts.models import *
from bets.models import *
from bets.views import get_today_format

class ReportsView(MethodView):

    def get_context(self):
        result = JackpotEntry.objects(bet_id__contains=get_today_format()).first()
        highest_bet = 0
        lowest_bet = 9999999
        total_bets = 0
        no_of_bets = 0

        no_bets = []
        sorted_arr = []
        codes = []

        if result:
            if result['entries']:
                sorted_arr = sorted(result['entries'], key=lambda k: k['bet'], reverse=True)
                
                for item in result['entries']:
                    codes.append(item['code'])

                    if item['bet'] >= highest_bet:
                        highest_bet = item['bet']

                    if item['bet'] <= lowest_bet and item['bet'] != 0:
                        lowest_bet = item['bet']

                    total_bets += item['bet']

                    if item['bet'] != 0:
                        no_of_bets += 1

        if lowest_bet == 9999999:
            lowest_bet = 0

        if lowest_bet == highest_bet:
            lowest_bet = 0

        for i in range(10000):
            code = "%04d" % (i,)
            if not code in codes:
                no_bets.append(code)

        len_no_bets = int(len(no_bets)) / 4

        context = {
            'result': result,
            'total_bets': total_bets,
            'highest_bet': highest_bet,
            'lowest_bet': lowest_bet,
            'no_of_bets': no_of_bets,
            'no_bets': no_bets,
            'len_no_bets': len_no_bets
        }
        return context

    @login_required
    def get(self):
        context = self.get_context()
        return render_template('reports/index.html', **context)