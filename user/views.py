from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import newforms as forms
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from eve.util.formatting import make_nav
from eve.user.models import Character, Account
from django.contrib.auth.decorators import login_required

user_nav = make_nav("Characters", "/user/", '34_12', note='Your characters and accounts.')
user_create_nav = make_nav("Create Login", "/user/create/", '07_03', note='Register with the widget.')
account_add_nav = make_nav('Add API Key', '/user/add/', None, 'Add a new account/API key.')

@login_required
def main(request):
    d = {}
    d['nav'] = [ user_nav ]  
    d['characters'] = request.user.get_profile().characters.all()
    d['accounts'] = request.user.get_profile().accounts.all()
    d['inline_nav'] = [ account_add_nav ]
    
    return render_to_response('user_main.html', d, context_instance=RequestContext(request))

@login_required
def character(request, id):
    character = get_object_or_404(Character, id=id)
    if character.user != request.user.get_profile():
        raise Http404
    
    d = {}
    d['nav'] = [ user_nav, character ]  
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
def account(request, id=None):
    d = {}
    d['id'] = id
    d['request'] = request
    if id is not None:
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
        return render_to_response('user_account_detail.html', d,
                                   context_instance=RequestContext(request))

    # OK, here on out, it's a post.
    assert(request.method == 'POST')
    
    # Delete the account?
    if id and request.POST.has_key('delete') and request.POST['delete'] == "1":
        account.delete()
        return HttpResponseRedirect('/user/')
    if id:
        form = ApiFormEdit(request.POST)
    else:
        form = ApiFormAdd(request.POST)
        
    if form.is_valid() == False:
        d['form'] = form
        return render_to_response('user_account_detail.html', d,
                                   context_instance=RequestContext(request))
    if not id:
        id = form.cleaned_data['id']
        account = Account(id=id)
    account.api_key = form.cleaned_data['api_key']
    account.user = request.user.get_profile()
    
    account.save()
    
    return HttpResponseRedirect('%srefreshing/' % account.get_absolute_url() )

class UserCreationForm(forms.Form):
    username = forms.CharField(label="Desired Username", max_length=30)
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(label='Password', min_length=5, widget=forms.PasswordInput, 
                               help_text='NOT your eve password. Pick a new one.')
    password2 = forms.CharField(label='Password, again', min_length=5, widget=forms.PasswordInput)
    eve_user_id = forms.IntegerField(label='EVE API User ID',
                                     help_text='See above for link to get this.')
    eve_api_key = forms.CharField(label='EVE API Key, FULL', min_length=64, max_length=64)

def user_creation(request):
    d = {}
    
    errors = []
    d['errors'] = errors
    
    d['nav'] = [ user_create_nav ]  

    if request.method == 'GET':
        d['form'] = UserCreationForm()
        return render_to_response('user_account_detail.html', d,
                                   context_instance=RequestContext(request))
        
    assert(request.method == 'POST')
    form = UserCreationForm(request.POST)
    d['form'] = form
    if form.is_valid() == False:
        for field in form.fields:
            for error in form[field].errors:
                errors.append('%s: %s' % (form[field].label, error))
    else:
        if form.cleaned_data['password'] != form.cleaned_data['password2']:
            errors.append("The passwords did not match.")
    
        if Account.objects.filter(id=form.cleaned_data['eve_user_id']).count() > 0:
            errors.append("That EVE user ID is already registered to a different account.")
        
    if errors:
        return render_to_response('user_account_detail.html', d,
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
    Account(user=profile, api_key=eve_api_key, id=eve_user_id).save()
    return HttpResponseRedirect('/login/')
