import datetime
from flask import url_for
from mongoengine.errors import NotUniqueError, DoesNotExist

from psl import db, app
from mongoengine import *

from accounts.models import User

class BetSettings(db.Document):
    params = db.DictField()
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    last_updated = db.DateTimeField(default=datetime.datetime.now, required=True)
    

class JackpotEntry(db.Document):
    bet_id = db.StringField(max_length=12, required=True)
    start_dt = db.DateTimeField(default=datetime.datetime.now, required=True)
    end_dt = db.DateTimeField(default=datetime.datetime.now, required=True)
    entries = db.ListField(db.DictField())

    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    last_updated = db.DateTimeField(default=datetime.datetime.now, required=True)
    created_by = db.ReferenceField(User)

    def total_bets(self):
        total = 0
        for entry in self.entries:
            total += float(entry['bet'])
        return total

    def combinations_with_bets(self):
        total = 0
        for entry in self.entries:
            if int(entry['bet']) != 0:
                total += 1
        return total

    def has_code(self, kode):
        for code in self.entries:
            if code == kode:
                return True
        return False

    def __unicode__(self):
        return "{0}: {1} - {2}".format(self.bet_id, self.start_dt, self.end_dt)

    meta = {
        'indexes': ['bet_id']
    }

class Transaction(db.Document):
    jackpot_entry = db.ReferenceField(JackpotEntry)
    entries = db.ListField(db.DictField())
    placed_by = db.ReferenceField(User)
    placed_at = db.DateTimeField(default=datetime.datetime.now, required=True)
