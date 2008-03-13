# $Id$
import datetime

from django import newforms as forms
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from eve.user.models import Character, Account, UserProfile

from eve.lib.formatting import make_nav

user_nav = make_nav("Characters", "/user/", '34_12', 'Your characters and accounts.')
user_create_nav = make_nav("Create Login", "/user/create/", '07_03', 
                           'Register with the widget. Tap here if it is your first time.')
account_add_nav = make_nav('Add API Key', '/user/add/', '12_02', 
                           'Add a new account/API key. (Yes, you can have ALL of your accounts on a single Widget login.)')
log_nav = make_nav('Refresh Log', '/user/api-log/', '22_42', 
                   'View API refresh log.')
lost_password_nav = make_nav('Lost Password', '/user/lost/', '04_16',
                             'Recover a lost password.')
login_nav = make_nav('Login', '/login/', '09_06', 
                     'Log yourself in for full use.')

@login_required
def main(request):
    d = {}
    d['nav'] = [ user_nav ]  
    d['characters'] = request.user.get_profile().characters.all()
    d['accounts'] = request.user.get_profile().accounts.all()
    d['inline_nav'] = [ account_add_nav, log_nav ]
    
    return render_to_response('user_main.html', d, context_instance=RequestContext(request))

@login_required
def character(request, id):
    character = get_object_or_404(Character, id=id)
    if character.user != request.user.get_profile():
        raise Http404
    
    log_nav = make_nav('Refresh Log', character.account.get_log_url(), '22_42',
                       'View API refresh log of this account.')
    
    d = {}
    d['nav'] = [ user_nav, character ]
    #d['inline_nav'] = [ log_nav ]
    d['c'] = character
    
    return render_to_response('user_character_detail.html', d, context_instance=RequestContext(request))

class ApiFormAdd(forms.Form):
    id = forms.IntegerField(label='User ID')
    api_key = forms.CharField(label='Full API Key', min_length=64, max_length=64)

class ApiFormEdit(forms.Form):
    api_key = forms.CharField(label='Full API Key', min_length=64, max_length=64)

@login_required
def account_refresh_warning(request, id):
    account = get_object_or_404(Account, id=id)
    if account.user != request.user.get_profile():
        raise Http404
    
    d = {}
    d['account'] = account
    d['nav'] = [ user_nav, account, { 'name':'Refreshing' }]
    
    
    return render_to_response('user_account_refresh_pending.html', d,
                                   context_instance=RequestContext(request))

@login_required
def account_refresh(request, id):
    d = {}
    
    account = get_object_or_404(Account, id=id)
    if account.user != request.user.get_profile():
        raise Http404
        
    d['nav'] = [user_nav, account, { 'name': 'Refresh Completed'} ]
    d['messages'] = account.refresh()
    d['account'] = account
    d['inline_nav'] = [ user_nav ]
    
    return render_to_response('user_account_refreshed.html', d,
                                   context_instance=RequestContext(request))

@login_required
def account_overview(request, id):
    account = get_object_or_404(Account, id=id)
    if account.user != request.user.get_profile():
        raise Http404

    log_nav = make_nav('Refresh Log', account.get_log_url(), '22_42',
                       'View API refresh log of this account.')
    edit_nav = make_nav('Edit', account.get_edit_url(), '09_03',
                        'Edit the API key on this account.')  

    d = {'nav': [ user_nav, account ], 
         'inline_nav' : [ log_nav, edit_nav ] }
    
    return render_to_response('generic_menu.html', d,
                                   context_instance=RequestContext(request))

@login_required
def account_log(request):

    d = {'user':request.user.get_profile(),
         'nav':[user_nav, log_nav]}

    return render_to_response('user_api_log.html', d,
                                   context_instance=RequestContext(request))


@login_required
def account_edit(request, id=None):
    d = {}
    d['id'] = id
    d['request'] = request
    
    if id:
        account = get_object_or_404(Account, id=id)
        if account.user != request.user.get_profile():
            raise Http404
        d['nav'] = [user_nav, account]
    else:
        d['nav'] = [user_nav, account_add_nav]
    
    if request.method == 'GET':
        if id:
            d['form'] = ApiFormEdit()
        else:
            d['form'] = ApiFormAdd()
        return render_to_response('user_account_edit.html', d,
                                   context_instance=RequestContext(request))

    # OK, here on out, it's a post.
    assert(request.method == 'POST')
    
    # Delete the account?
    if id and request.POST.has_key('delete') and request.POST['delete'] == "1":
        account.delete()
        return HttpResponseRedirect( user_nav['get_absolute_url'] )
    if id:
        form = ApiFormEdit(request.POST)
    else:
        form = ApiFormAdd(request.POST)
        
    if form.is_valid() == False:
        d['form'] = form
        return render_to_response('user_account_edit.html', d,
                                   context_instance=RequestContext(request))
    if not id:
        id = form.cleaned_data['id']
        account = Account(id=id)
    account.api_key = form.cleaned_data['api_key']
    account.user = request.user.get_profile()
    
    account.save()
    
    return HttpResponseRedirect( account.get_refresh_warning_url() )

def account_password_lost(request):
    d = {}
    d['nav'] = [ lost_password_nav ]
    
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST['username'])
            profile = user.get_profile()
            profile.lost_password()
            
            message = 'Email sent'
        except User.DoesNotExist:
            message = 'Unknown user'
    else:
        message = ''

    d['message'] = message
    return render_to_response('user_password_lost.html', d,
                              context_instance=RequestContext(request))

class PasswordResetForm(forms.Form):
    password = forms.CharField(label='Password', min_length=5, widget=forms.PasswordInput, 
                               help_text='NOT your eve password. Pick a new one.')
    password2 = forms.CharField(label='Password, again', min_length=5, widget=forms.PasswordInput)
    key = forms.CharField(widget=forms.HiddenInput, min_length=50, max_length=50)
    
    def clean_password2(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not match.')
           
    def clean_key(self):
        try:
            key = self.cleaned_data['key']
            profile = UserProfile.objects.get(lost_password_key=key)
            if profile.is_lost_password_expired():
                profile.lost_password()
                raise forms.ValidationError('Key has expired. New one has been sent.')
        except UserProfile.DoesNotExist:
            raise forms.ValidationError('Key is not a valid reset key.')

def account_password_found(request, key):
    d = {}
    d['nav'] = [ lost_password_nav ]
    template = 'user_password_found.html'
    
    profile = get_object_or_404(UserProfile, lost_password_key=key)
    d['profile'] = profile

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if not form.is_valid():
            d['form'] = form
            return render_to_response(template, d,
                              context_instance=RequestContext(request))
            
        user = profile.user
        password = form.cleaned_data['password']
        
        user.set_password(password)
        user.save()
        profile.lost_password_key = ''
        profile.lost_password_time = None
        profile.save()
        
        user = auth.authenticate(username=user.username, password=password)
        auth.login(request, user)
        return HttpResponseRedirect('/')
    else:
        assert(request.method == 'GET')
        d['form'] = PasswordResetForm(initial={'key':key})
        
        return render_to_response(template, d,
                                  context_instance=RequestContext(request))

class UserCreationForm(forms.Form):
    username = forms.CharField(label="Desired Username", max_length=30)
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(label='Password', min_length=5, 
                               widget=forms.PasswordInput, 
                               help_text='NOT your eve password. Pick a new one.')
    password2 = forms.CharField(label='Password, again', min_length=5, 
                                widget=forms.PasswordInput)
    eve_user_id = forms.IntegerField(label='EVE API User ID',
                                     help_text='See above for link to get this.')
    eve_api_key = forms.CharField(label='EVE API Key, FULL', 
                                  min_length=64, max_length=64)
    
    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return self.cleaned_data
           
    def clean_username(self):
        c = User.objects.filter(username=self.cleaned_data['username']).count()
        if c > 0:
            raise forms.ValidationError("That user name is already registered.")
        else:
            return self.cleaned_data['username']

    def clean_eve_user_id(self):
        c = Account.objects.filter(id=self.cleaned_data['eve_user_id']).count()
        if c > 0:
            raise forms.ValidationError("That EVE user ID is already registered to a different account.")
        else:
            return self.cleaned_data['eve_user_id']
            

def user_creation(request):
    d = {}
    
    errors = []
    d['errors'] = errors
    d['nav'] = [ user_create_nav ]  

    if request.method == 'GET':
        d['form'] = UserCreationForm()
        return render_to_response('user_account_edit.html', d,
                                   context_instance=RequestContext(request))
        
    assert(request.method == 'POST')
    form = UserCreationForm(request.POST)
    d['form'] = form
    if form.is_valid() == False:
        for field in form.fields:
            for error in form[field].errors:
                errors.append('%s: %s' % (form[field].label, error))
        return render_to_response('user_account_edit.html', d,
                                   context_instance=RequestContext(request))
        
    # OK, let's make a user.
    username = form.cleaned_data['username']
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    eve_user_id = form.cleaned_data['eve_user_id']
    eve_api_key = form.cleaned_data['eve_api_key']
    
    user = User.objects.create_user(username, email, password)
    user.save()
    
    profile = user.get_profile()
    account = Account(user=profile, api_key=eve_api_key, id=eve_user_id)
    account.save()
    
    user = auth.authenticate(username=username, password=password)
    auth.login(request, user)
    
    return HttpResponseRedirect( account.get_refresh_warning_url() )


class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label='Password', min_length=5, 
                               widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput)
    
    def clean_username(self):
        try:
            _ = User.objects.get(username=self.cleaned_data['username'])
            return self.cleaned_data['username']
        except User.DoesNotExist:
            raise forms.ValidationError('That is not your username.')
        
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        if username is None:
            raise forms.ValidationError('The username is not set.')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            self.user = user
        else:
            print "user: %s, pass: %s" % (username, password)
            raise forms.ValidationError('That is not your password.')
        return self.cleaned_data
        
def login(request):
    d = {}
    d['nav'] = [ login_nav ]
    d['inline_nav'] = [ user_create_nav, lost_password_nav ]
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            return HttpResponseRedirect(form.cleaned_data['next'])
        else:
            d['form'] = form
    else:
        d['form'] = UserLoginForm(initial={'next': '/'})
            
    return render_to_response('user_login.html', d,
                              context_instance=RequestContext(request))