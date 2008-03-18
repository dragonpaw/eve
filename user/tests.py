'''
>>> from django.test.client import Client
>>> from django.contrib.auth.models import User
>>> from eve.user.models import Account, Character

>>> from eve.ccp.models import Corporation, Alliance
>>> Corporation(id=827230560).save()
>>> ed = Alliance()
>>> ed.id=494403294
>>> ed.name='Ethereal Dawn'
>>> ed.ticker='ED'
>>> ed.member_count = 500
>>> ed.executor_id = 827230560
>>> ed.save()

>>> c = Client()
>>> r = c.post('/user/create/', {'username':'ash',
...                              'email':'ash@dragonpaw.org',
...                              'eve_user_id':563133,
...                              'eve_api_key':'9saKOlZUwMd2b8sGg2DKrrE6y2rqFBfDt870ZDCGoG1baQk1vz3pZiGfnI1TQm0s',
...                              'password':'testing', 
...                              'password2':'testing'})

# The post should make the account and get us a page that says a refresh is next.
>>> r.status_code
302
>>> ash = User.objects.get(username='ash')
>>> profile = ash.get_profile()
>>> Account.objects.filter(user=profile).count()
1L

# The response should point us to the refresh warning page. Get it. 
>>> r['location']
'http://testserver/user/account/563133/refreshing/'
>>> r = c.get('/user/account/563133/refreshing/')
>>> r.status_code
200
>>> r.template[0].name
'user_account_refresh_pending.html'

# Now we should actually be ready to run the refresh. 
>>> r = c.get('/user/account/563133/refresh/')
[1] /account/Characters.xml.aspx...
>>> r.status_code
200
>>> r.template[0].name
'user_account_refreshed.html'

#Now we should be looking at the character page.
>>> r = c.get('/user/')
>>> r.status_code
200
>>> r.template[0].name
'user_main.html'

>>> Character.objects.filter(account__user=profile).count()
2L
'''