import datetime
from flask import url_for
from mongoengine.errors import NotUniqueError, DoesNotExist
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.security import Security, MongoEngineUserDatastore, \
        UserMixin, RoleMixin, login_required

from psl import db, app
from mongoengine import *

from accounts.forms import ExtendedRegisterForm, ExtendedConfirmRegisterForm, LoginForm

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=255, required=False)
    slug = db.StringField(unique=True, required=True)
    description = db.StringField(max_length=255, required=False)

    meta = {
        'indexes': ['slug']
    }

class User(db.Document, UserMixin):
    email = db.EmailField(max_length=255, required=False, unique=False, default="jackpot@phdevs.com")
    username = db.StringField(max_length=255, required=True, unique=True)
    password = db.StringField(max_length=255, required=True)
    active = db.BooleanField(default=True)

    first_name = db.StringField(max_length=255, required=False)
    last_name = db.StringField(max_length=255, required=False)
    image_url = db.StringField(max_length=255, required=False)
    is_admin = db.BooleanField(default=False)

    roles = db.ListField(db.ReferenceField(Role), default=[])

    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    last_updated = db.DateTimeField(default=datetime.datetime.now, required=True)

    # SECURITY_TRACKABLE
    last_login_at = db.DateTimeField(default=datetime.datetime.now)
    current_login_at = db.DateTimeField(default=datetime.datetime.now)
    last_login_ip = db.StringField(max_length=255)
    current_login_ip = db.StringField(max_length=255)
    login_count = db.IntField(default=0)

    added_by = db.ReferenceField("self", reverse_delete_rule = NULLIFY)
    
    def full_name(self):
        return self.name

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def set_password(self, pw_hash):
        self.password = generate_password_hash(pw_hash)

    meta = {
        'indexes': ['-created_at', 'email'],
        'ordering': ['-created_at']
    }


# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore, \
                    register_form=ExtendedRegisterForm, \
                    confirm_register_form=ExtendedConfirmRegisterForm, \
                    login_form=LoginForm)
