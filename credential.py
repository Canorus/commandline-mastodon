import requests
import json
import os

def chk_(url):
    if url[:5] != 'https':
        return 'https://' + url
    else:
        return url

def per(i):
    follow = int(i / 4)
    write = int(i % 4 / 2)
    read = int(i % 4 % 2 / 1)
    per = ''
    if read:
        per += 'read'
    if write:
        per += ' write'
    if follow:
        per += ' follow'
    return per

def register(instance, *args):
    instance = chk_(instance)
    client_name = input('Please input your client name: ')
    if args:
        p = per(args[0])
    else:
        p = per(1)
    data = {'client_name': client_name,'redirect_uris': 'urn:ietf:wg:oauth:2.0:oob', 'scopes': p}
    r = requests.post(instance+'/api/v1/apps', data=data)
    rdata = r.json()
    client_id = rdata['client_id']
    client_secret = rdata['client_secret']
    import webbrowser
    p = p.replace(' ','%20')
    webbrowser.open(instance+'/oauth/authorize?client_id='+client_id +'&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope='+p)
    code = input('input you code from browser: ')
    print('your access_code is: '+code)
    auth_data = {'client_id': client_id, 'client_secret': client_secret, 'code': code,'grant_type': 'authorization_code', 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'}
    rauth = requests.post(instance + '/oauth/token', data=auth_data)
    access_token = rauth.json()['access_token']
    username = json.loads(requests.get(instance+'/api/v1/accounts/verify_credentials',headers={'Authorization': 'Bearer '+access_token}).content)['acct']
    if args:
        user = {}
        user[username] = access_token
        login = {}
        login[instance] = user
        file_name = input('Set filename: ')
        with open(file_name+'.json', 'w') as fw:
            json.dump(login, fw)
        return 0
    try:
        with open('cred.json') as f:
            login = json.load(f)
    except:
        login = {}
    if instance in login:
        if username in login[instance]:
            pass
        else:
            login[instance][username] = access_token
    else:
        user = dict()
        user[username] = access_token
        login[instance] = user
    with open('cred.json', 'w') as f:
        json.dump(login, f)
    print('returning access_token: '+access_token)
    return access_token
    

def retrieve(username, instance):
    import os
    instance = chk_(instance)
    with open('cred.json') as f:
        cred = json.load(f)
    if instance in cred:
        if username in cred[instance]:
            return cred[instance][username]
        else:
            return register(instance)
    else:
        return register(instance)

def delcred(username, instance):
    instance = chk_(instance)
    with open('cred.json') as fr:
        cred = json.load(fr)
    try:
        cred[instance].pop(username)
        if len(cred[instance]) == 0:
            cred.pop(instance)
    except:
        print('matching user credential not found')
    with open('cred.json', 'w') as f:
        json.dump(cred,f)