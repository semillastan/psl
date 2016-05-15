from flask import Blueprint, request, redirect, render_template, url_for, flash, g, session, jsonify
from flask.ext.mongoengine.wtf import model_form
from flask.views import MethodView, View
from mongoengine.errors import NotUniqueError, DoesNotExist
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_wtf import Form
from werkzeug import secure_filename
from werkzeug.security import check_password_hash
from datetime import datetime

from psl import app, login_manager
from utils import flash_errors
from accounts.models import User
from accounts.forms import ForgotPasswordForm, ChangePasswordForm, LoginForm, ExtendedRegisterForm

@app.before_request
def before_request():
    g.user = current_user

class RenderTemplateView(View):
    def __init__(self, template_name):
        self.template_name = template_name
    def dispatch_request(self):
        return render_template(self.template_name)

class ListView(MethodView):

    def get(self):
        accounts = User.objects.all()
        return render_template('accounts/list.html', accounts=accounts)

class AccountProfileView(MethodView):

    @login_required
    def get(self):
        profile_form = model_form(User, exclude=['email', 'password', 'created_at', 'last_updated', 'is_active', 'no_of_agents'])(request.form)
        change_password_form = ChangePasswordForm(request.form)
        return render_template('accounts/profile.html', profile_form=profile_form, change_password_form=change_password_form)

    @login_required
    def post(self):
        form = model_form(User, exclude=['email', 'password', 'created_at', 'last_updated', 'is_active', 'no_of_agents'])(request.form)
        if form.validate():
            f = request.files['profile_image']
            if f:
                import hashlib
                import os.path
                filename = secure_filename(f.filename)
                extension = os.path.splitext(filename)[1]
                h = hashlib.new("ripemd160")
                h.update(filename)
                key = h.hexdigest() + "" + extension
                
                s3_object = SUPPORT_GENIE_S3.put_object(Key=key, ACL='public-read', Body=f.read())
                current_user.image_url = "https://{0}.s3.amazonaws.com/{1}".format("support-genie-portal", key)

            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.save()

            return redirect(url_for('accounts.profile'))
        else:
            flash_errors(form)
            return render_template('accounts/profile.html', profile_form=form)

class ChangePasswordView(MethodView):

    @login_required
    def post(self):
        form = ChangePasswordForm(request.form)
        if form.validate():
            verify = SupportGenie().agent_verify(agentEmail=current_user.email, password=form.password.data)
            if verify['result'] == 'success':
                result = SupportGenie().agent_change_password(agentEmail=current_user.email, password=form.new_password.data)
                if result['result'] == 'success':
                    flash('Password changed.')
                else:
                    flash(result['reason'])
            else:
                flash('Wrong password')

            return redirect(url_for('accounts.profile'))

        else:
            flash_errors(form)
            return render_template('accounts/profile.html', change_password_form=form)

class RegisterView(MethodView):
    def get_context(self):
        context = {
            "form": ExtendedRegisterForm(request.form)
        }
        return context

    def get(self):
        context = self.get_context()
        form = context.get('form')
        return render_template('accounts/register.html', register_user_form=form)

    def post(self):
        context = self.get_context()
        form = context.get('form')
        print form

        if form.validate():
            try:
                user = User()
                form.populate_obj(user)
                user.set_password(form.password.data)            
                user.active = True
                user.save()

                return redirect(url_for('pages.home'))

            except NotUniqueError:
                flash('User aready exists')

        else:
            flash_errors(form)

        return render_template('accounts/register.html', register_user_form=form)

class RegisterErrorView(MethodView):

    def get(self):
        return render_template('accounts/register-error.html')

class LoginView(MethodView):

    def get_context(self):
        form = LoginForm(request.form)
        context = {"login_user_form": form}
        return context

    def get(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('pages.home'))
        context = self.get_context()
        form = context.get('login_user_form')
        return render_template('home.html', login_user_form=form)

    def post(self):
        context = self.get_context()
        form = context.get('login_user_form')

        if form.validate():
            try:
                user = User.objects.get(username=form.username.data)
                login_user(user)
                flash("Logged in user")
            except DoesNotExist:
                flash("User does not exist.")

            if current_user.is_admin:
                return redirect(url_for('bets.index'))
            else:
                return redirect(url_for('bets.daily-bets'))
        else:
            flash_errors(form)

        return render_template('home.html', **context)

class LoginErrorView(MethodView):

    def get(self):
        return render_template('accounts/login-error.html')

class LogoutView(MethodView):

    @login_required
    def get(self):
        logout_user()
        return redirect(url_for('pages.home'))

class ForgotPasswordView(MethodView):

    def get_context(self):
        form = ForgotPasswordForm()
        context = {"form": form}
        return context

    def get(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('accounts.home'))
        context = self.get_context()
        form = context.get('form')
        return render_template('accounts/forgot-password.html', form=form)

    def post(self):
        context = self.get_context()
        form = context.get('form')

        if form.validate():
            try:
                user = User.objects.get(email=form.email.data)
                flash('User exists')
            except DoesNotExist:
                flash('User does not exist')

        else:
            flash_errors(form)

        return render_template('home.html', **context)

class AccountSettingsView(MethodView):

    def get_context(self):
        context = {
            'company': Company.objects(users__in=[current_user.id])
        }
        return context

    @login_required
    def get(self):
        context = self.get_context()
        return render_template('accounts/settings.html', **context)
