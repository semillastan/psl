from flask import Blueprint, request, redirect, render_template, url_for, flash, make_response
from flask.views import View, MethodView
from flask.ext.mongoengine.wtf import model_form
from flask.ext.login import login_user, logout_user, current_user, login_required
from mongoengine.errors import NotUniqueError, DoesNotExist, MultipleObjectsReturned
from mongoengine.queryset import Q

from datetime import datetime, timedelta
from psl import app as current_app
from psl import login_manager

from utils import flash_errors
from accounts.models import User
from bets.models import JackpotEntry, BetSettings, Transaction
from bets.forms import BetForm, BetSettingsForm

import arrow, calendar

def get_bet_settings():
    return BetSettings.objects.first().params

def get_today_format():
    utc = arrow.utcnow()
    local = utc.to('Asia/Manila')
    return local.format('MMDDYYYY')

class IndexView(MethodView):

    def get_context(self):
        context = {}

        utc = arrow.utcnow()
        local = utc.to('Asia/Manila')
        end_day = calendar.monthrange(int(local.format('YYYY')), int(local.format('MM')))

        year = int(local.format('YYYY'))
        month = int(local.format('MM'))

        start = datetime(year, month, 1, 0, 0)
        end = datetime(year, month, end_day[1], 0, 0)
        cal_events = []
        bets_today = []

        for r in arrow.Arrow.span_range('day', start, end):
            events = JackpotEntry.objects(bet_id__contains=r[0].format('MMDDYYYY'))

            for event in events:
                if local.format('MMDDYYYY') in event.bet_id:
                    bets_today.append(event)

                entry = {'start': arrow.get(event.start_dt).isoformat(), 'title': str(int(event.total_bets()))}
                cal_events.append(entry)

        context['events'] = cal_events
        context['bets'] = bets_today
        
        bet_settings = get_bet_settings()
        context['time_value'] = bet_settings
        context['time_type'] = bet_settings
        context['bet_form'] = BetForm(request.form)

        return context

    @login_required
    def get(self):
        context = self.get_context()
        return render_template('bets/index.html', **context)

class DailyBetsView(MethodView):
    @login_required
    def get(self):
        day_format = get_today_format()
        jackpot_entries = JackpotEntry.objects(bet_id__contains=day_format)
        
        return render_template('bets/daily-bets.html', jackpot_entries=jackpot_entries)

    @login_required
    def post(self):
        return redirect(url_for('bets.index'))

    def generate_daily_combinations(self):
        day_format = get_today_format()

        entry = JackpotEntry(bet_id=day_format)
        
        for i in range(10000):
            code = "%04d" % (i,)
            code_entry = {'code': code, 'bet': 0}
            entry.entries.append(code_entry)

        try:
            entry.save()
        except NotUniqueError:
            pass

class PlaceBetsView(MethodView):
    @login_required
    def get(self):
        context = {}
        day_format = get_today_format()

        jackpot_entries = JackpotEntry.objects(bet_id=day_format)

        bet_settings = get_bet_settings()
        context['time_value'] = bet_settings
        context['time_type'] = bet_settings
        return render_template('bets/place-bets.html', jackpot_entries=jackpot_entries, **context)

    @login_required
    def post(self):
        day_format = get_today_format()
        jackpot_entry = JackpotEntry.objects(bet_id=day_format).first()
        transaction = Transaction(jackpot_entry=jackpot_entry)
        max_code = get_bet_settings()['max_code']

        entries = []
        for i in range(int(max_code)):
            code = "%04d" % (i,)
            code_format = "bets_{0}".format(code)
            amount = request.form.getlist(code_format)[0]
            if amount != '':
                entries.append({'code': code, 'amount': int(amount)})

        transaction.entries = entries
        transaction.placed_by = current_user.to_dbref()
        transaction.save()

        changed = False
        for entry in transaction.entries:
            for jackpot in jackpot_entry.entries:
                if jackpot['code'] == entry['code']:
                    jackpot['bet'] += entry['amount']
                    changed = True

        if changed:
            jackpot_entry.save()

        return redirect(url_for('bets.daily-bets'))

class ManualPlaceBetsView(MethodView):
    @login_required
    def get(self, bet_id):
        context = {}
        day_format = get_today_format()

        try:
            jackpot_entry = JackpotEntry.objects.get(bet_id=bet_id)
        except MultipleObjectsReturned:
            flash("Multiple Bet IDs")
            return redirect(url_for('bets.daily-bets'))
        except DoesNotExist:
            flash("Does Not Exist")
            return redirect(url_for('bets.daily-bets'))

        context['bet_settings'] = get_bet_settings()
        return render_template('bets/manual-place-bets.html', jackpot_entry=jackpot_entry, **context)

    @login_required
    def post(self, bet_id):
        day_format = get_today_format()
        jackpot_entry = JackpotEntry.objects(bet_id=bet_id).first()
        transaction = Transaction(jackpot_entry=jackpot_entry)
        
        entries = []
        for k in request.form.keys():
            if "code_" in k:
                code = k.replace("code_", "")
                if len(code) == 4:
                    for i in request.form.keys():
                        if "bets_{0}".format(code) == i:
                            amount = request.form.get(i)
                            if amount != '':
                                entry = {'code': code, 'amount': int(amount)}
                                entries.append(entry)

        transaction.entries = entries
        transaction.placed_by = current_user.to_dbref()
        transaction.save()

        changed = False
        for entry in transaction.entries:
            if jackpot_entry.has_code(entry['code']):
                for jackpot in jackpot_entry.entries:
                    if jackpot['code'] == entry['code']:
                        jackpot['bet'] += entry['amount']
                        changed = True
            else:
                jackpot_entry.entries.append({'code': entry['code'], 'bet': entry['amount']})
                changed = True

        if changed:
            jackpot_entry.save()

        return redirect(url_for('bets.daily-bets'))

class ShowBetsView(MethodView):
    @login_required
    def get(self, bet_id):
        jackpot_entries = JackpotEntry.objects(bet_id=day)
        return render_template('bets/show-bets.html', jackpot_entries=jackpot_entries)

    @login_required
    def post(self):
        return redirect(url_for('bets.index'))

class CreateTransactionView(MethodView):
    @login_required
    def get(self):
        return render_template('bets/create-transaction.html')

class CreateBetView(MethodView):
    def get_context(self):
        context = {}
        context['bet_settings'] = get_bet_settings()
        context['form'] = BetForm(request.form)
        return context

    @login_required
    def get(self):
        return render_template('bets/create.html')

    @login_required
    def post(self):
        context = self.get_context()
        form = context['form']

        if form.validate():
            try:
                start_datetime = arrow.get(request.form.get('start_datetime'), 'YYYY-MM-DD HH:mm')
                end_datetime = self.set_end_time(start_datetime, context['bet_settings'])
                bet_id = start_datetime.format("MMDDYYYYHHmm")

                existing_bets = JackpotEntry.objects(Q(start_dt__gte=start_datetime.datetime, start_dt__lte=end_datetime.datetime) | Q(end_dt__gte=start_datetime.datetime, end_dt__lte=end_datetime.datetime))

                if existing_bets:
                    flash("Invalid time. Bet already exists during the selected time.")
                else:
                    jackpot_entry = JackpotEntry(bet_id=bet_id, start_dt=start_datetime.datetime, end_dt=end_datetime.datetime, created_by=current_user.id)
                    jackpot_entry.save()
                    flash("Bet created.")
            
            except NotUniqueError:
                flash("Bet already exists.")
            
            return redirect(url_for('bets.index'))
        else:
            flash_errors(form)
            return render_template('bets/create.html')

    def set_end_time(self, start_datetime, params):
        temp_dt = start_datetime
        end_datetime = temp_dt.replace(minutes=+59, seconds=+59)
        if params['betting_time_unit'] == 'minutes':
            end_datetime = temp_dt.replace(minutes=+(params['betting_time'] - 1), seconds=+59)
        elif params['betting_time_unit'] == 'hours':
            end_datetime = temp_dt.replace(hours=+(params['betting_time'] - 1), minutes=+59, seconds=+59)
        elif params['betting_time_unit'] == 'seconds':
            end_datetime = temp_dt.replace(seconds=+(params['betting_time'] - 1))

        return end_datetime

class DeleteBetView(MethodView):
    @login_required
    def get(self, bet_id):
        if current_user.is_admin:
            jackpot_entries = JackpotEntry.objects(bet_id=bet_id)
            for entry in jackpot_entries:
                entry.delete()
            return redirect(url_for('bets.index'))
        else:
            return redirect(url_for('pages.401'))

class SettingsView(MethodView):
    def get_context(self):
        context = {}
        context['form'] = BetSettingsForm(request.form)
        
        bet_settings = BetSettings.objects.first()
        if bet_settings:
            context['form'] = BetSettingsForm(betting_time=bet_settings['params']['betting_time'], betting_time_unit=bet_settings['params']['betting_time_unit'], encoding_time=bet_settings['params']['encoding_time'], encoding_time_unit=bet_settings['params']['encoding_time_unit'])

        return context
        
    @login_required
    def get(self):
        if current_user.is_admin:
            context = self.get_context()
            return render_template('bets/settings.html', **context)
        else:
            return redirect(url_for('pages.401'))

    @login_required
    def post(self):
        if current_user.is_admin:
            context = self.get_context()
            form = context['form']
            if form.validate():
                bet_settings = BetSettings.objects.first()
                if bet_settings == None:
                    bet_settings = BetSettings()

                params = {}
                params['betting_time'] = form['betting_time'].data
                params['betting_time_unit'] = form['betting_time_unit'].data

                params['encoding_time'] = form['encoding_time'].data
                params['encoding_time_unit'] = form['encoding_time_unit'].data

                bet_settings.params = params
                bet_settings.save()
                return redirect(url_for('bets.index'))
            else:
                flash_errors(form)
                return render_template('bets/settings.html', **context)
        else:
            return redirect(url_for('pages.401'))
