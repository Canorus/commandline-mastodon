import requests
import json
import webbrowser
import os

client_id=''
client_secret = ''
access_token = ''

def toot():
    if os.path.exists('cred.json'):
        with open('cred.json') as cred_file:
            cred = json.load(cred_file)
        client_id = cred['client_id']
        client_secret = cred['client_secret']
        access_token = cred['access_token']
    else:
        #register application
        client_name='mastodon commandline'
        website = input('input your mastodon instance address: ')

        data = {'client_name':client_name,'redirect_uris':'urn:ietf:wg:oauth:2.0:oob','scopes':'read write follow'}
        r = requests.post('https://twingyeo.kr/api/v1/apps',data=data)
        print(r.status_code, r.reason)
        #print(r.text)
        print(r.text)

        # parsing returned json data
        rdata = r.json()
        client_id=rdata['client_id']
        client_secret = rdata['client_secret']

        # open authentication page
        webbrowser.open('https://twingyeo.kr/oauth/authorize?client_id='+client_id+'&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=read%20write%20follow')

        # input code
        code = input('input your code: ')
        print('your access_code is: '+code)

        # Retrieving access token
        auth_data = {'client_id':client_id,'client_secret':client_secret,'code':code,'grant_type':'authorization_code','redirect_uri':'urn:ietf:wg:oauth:2.0:oob'}
        rauth = requests.post('https://twingyeo.kr/oauth/token',data = auth_data)

        print(rauth.json())
        # retrieving access token
        access_token = rauth.json()['access_token']

        # build 'cred' dic
        cred = dict()
        cred['client_id'] = client_id
        cred['client_secret'] = client_secret
        cred['access_token'] = access_token
        # save this in 'cred.json' data
        with open('cred.json','w') as cred_file:
            json.dump(cred,cred_file)
    
    global status
    status = input('input your status: ')
    if status != 'quit':
        #status header
        status_h = {'Authorization':'Bearer '+access_token}
        status_cont = {'status': status}
        st = requests.post('https://twingyeo.kr/api/v1/statuses', data=status_cont, headers=status_h)
        print(st.status_code)
    else:
        print('closing commandline-mastodon, thanks for tooting!')
global status
status = ''
while status != 'quit':
    toot()