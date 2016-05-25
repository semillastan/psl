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

import operator

class ApiView(MethodView):

    def get_context(self):
        context = {}
        return context

    @login_required
    def get(self):
        context = self.get_context()
        return jsonify(**context)

class TopTenCodesView(MethodView):

    def get_context(self, bet_id):
        results = JackpotEntry.objects(bet_id__contains=bet_id).only('bet_id', 'entries', 'entries.code', 'entries.bet')
        entries = []
        codes = []
        for result in results:
            for entry in result['entries']:
                if entry['code'] in codes:
                    for item in entries:
                        if item['code'] == entry['code']:
                            item['bet'] += entry['bet']
                else:
                    e = {'code': entry['code'], 'bet': entry['bet']}
                    entries.append(e)

        context = {
            'entries': sorted(entries, key=lambda k: k['bet'], reverse=True)[:10]
        }
        return context

    @login_required
    def get(self, bet_id):
        context = self.get_context(bet_id)
        return jsonify(**context)

class LowestTenCodesView(MethodView):

    def get_context(self, bet_id):
        results = JackpotEntry.objects(bet_id__contains=bet_id).only('bet_id', 'entries', 'entries.code', 'entries.bet')
        entries = []
        codes = []
        for result in results:
            for entry in result['entries']:
                if entry['code'] in codes:
                    for item in entries:
                        if item['code'] == entry['code']:
                            item['bet'] += entry['bet']
                else:
                    e = {'code': entry['code'], 'bet': entry['bet']}
                    entries.append(e)

        if len(entries) == 1:
            entries = []
        else:
            entries = sorted(entries, key=lambda k: k['bet'])[:10]
        
        context = {
            'entries': entries
        }
        return context

    @login_required
    def get(self, bet_id):
        context = self.get_context(bet_id)
        return jsonify(**context)