# short testing script which fetches recent market transactions; this only prints out
# the data, it's an exercise to the reader to parse the XML and do something useful
# with the data.
import httplib, urllib

# setup the parameters we will be sending to the webserver; note that all of this
# information is gathered from the API Key page that the user should visit, and
# the characterID is gathered from /account/Characters.xml.aspx
params = urllib.urlencode( {
    'characterID': 150209812,
    'userid': 256833,
    'apikey': 'DVPtgNgmyEGk9L9RxDTJn8dCjIraiaa7efNK4VlGKAoI6Hm8uB514zy6CbFCuScC',
    } )

# connect to server, POST our request, fairly simple stuff...
headers = { "Content-type": "application/x-www-form-urlencoded" }
conn = httplib.HTTPConnection("api.eve-online.com")
conn.request("POST", "/char/WalletTransactions.xml.aspx", params, headers)

# now get response from server, print out the status code for debugging
response = conn.getresponse()
print response.status, response.reason

# now print the data; at this point you'd want to do XML parsing and do whatever
# else you want... well, after probably doing conn.close below
data = response.read()
print data

# OCD comment placement
conn.close
