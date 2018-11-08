import requests
import json
import os


def register(instance):
    client_name = 'commandline timeline'
    instance = instance
    if instance[:5] != 'https':
        instance = 'https://'+instance
    data = {'client_name': client_name,'redirect_uris': 'urn:ietf:wg:oauth:2.0:oob', 'scopes': 'read'}
    r = requests.post(instance+'/api/v1/apps', data=data)
    rdata = r.json()
    client_id = rdata['client_id']
    client_secret = rdata['client_secret']
    import webbrowser
    webbrowser.open(instance+'/oauth/authorize?client_id='+client_id +'&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=read')
    code = input('input you code from browser: ')
    print('your access_code is: '+code)
    auth_data = {'client_id': client_id, 'client_secret': client_secret, 'code': code,'grant_type': 'authorization_code', 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'}
    rauth = requests.post(instance+'/oauth/token', data=auth_data)
    access_token = rauth.json()['access_token']
    # [                                             # login:list
    #   ['instance':'instance1',                    # instances:list
    #     {                                         # user:dict
    #       'username':'user1',
    #       'cred':{                                # cred:dict
    #         'client_id':'client_id_here',
    #         'user_code':'user_code_here',
    #         'access_token':'access_token_here'
    #       }
    #     }
    #   ],
    #   ['instance':'instance2',
    #     {'username':'user2',
    #       'cred':{
    #         'client_id':'client_id_here',
    #         'user_code':'user_code_here',
    #         'access_token':'access_token_here'
    #       }
    #     }
    #   ]
    # ]
    # credential dictionary
    cred = dict()
    cred['client_id'] = client_id
    cred['client_secret'] = client_secret
    cred['access_token'] = access_token
    print(cred)
    # credential dictionary including username
    user = dict()
    # get username
    username = json.loads(requests.get(instance+'/api/v1/accounts/verify_credentials',headers={'Authorization': 'Bearer '+access_token}).content)['username']
    print('Your username is '+username)
    try:
        with open('cred.json') as f:
            login = json.load(f)
    except:
        login = []
    print(login)
    for i in login:
        if instance == i[0]['instance']:  # instance already exists
            if i[1]['username'] == username:  # check if username exists
                print('username is: ' + i[1]['username'])
                break  # same username under same instance means we already have login credential
            else:
                user['username'] = username
                user['cred'] = cred
                i.append(user)
                print(i)
                break
        else:  # instance does not exist
            user['username'] = username
            user['cred'] = cred
            instances = []
            instances.append({'instance': instance})
            instances.append(user)
            login.append(instances)
    if len(login) == 0:
        print('blank file')
        user['username'] = username
        user['cred'] = cred
        instances = []
        instances.append({'instance': instance})
        instances.append(user)
        login.append(instances)
    print('login final: '+str(login))
    # save updated credential
    with open('cred.json', 'w') as f:
        json.dump(login, f)

def retrieve(username, instance):
    import os
    global access_token
    with open('cred.json') as f:
        cred = json.load(f)
    for i in cred:
        if instance == i[0]['instance']:
            for k in i:
                try:
                    if username == k['username']:
                        access_token = k['cred']['access_token']
                        break
                except:
                    pass
    return access_token
