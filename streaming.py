import json
import requests
import re

with open('cred.json') as cred_f:
	cred = json.load(cred_f)
acc = cred['access_token']
head = {'Authorization':'Bearer '+acc}

uri_local = 'https://twingyeo.kr/api/v1/streaming/public/local'
#uri_user = 'https://twingyeo.kr/api/v1/streaming/user'
r_local = requests.get(uri_local,headers=head,stream=True)
print('socket connected.')
#r_user = requests.get(uri_user,headers=head,stream=True)
for l in r_local.iter_lines():
    dec = l.decode('utf-8')
    try:
        newdec = re.sub('data: ','',dec)
        print('@'+str(json.loads(newdec)['account']['display_name']))
        content = json.loads(newdec)['content']
        content = re.sub('</p><p>','\n',content)
        content = re.sub('(<.?p>|<.?a.*?>|<.?span.*?>)','',content)
        content = re.sub('&lt;','<',content)
        content = re.sub('&gt;','>',content)
        content = re.sub('&apos;','\'',content)
        print(content)
    except:
        pass

