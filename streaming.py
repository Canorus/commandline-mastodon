import json
import requests
import re
from urllib.parse import unquote

with open('cred.json') as cred_f:
    cred = json.load(cred_f)
acc = cred['access_token']
head = {'Authorization':'Bearer '+acc}

uri = 'https://twingyeo.kr/api/v1/streaming/public/local'

r = requests.get(uri,headers=head,stream=True)
print('socket connected.')
for l in r.iter_lines():
    dec = l.decode('utf-8')
    try:
        newdec = re.sub('data: ','',dec)
        print('@'+str(json.loads(newdec)['account']['display_name']))
        print(unquote(re.sub('(<.?p>|<.?a.*?>|<.?span.*?>)','',json.loads(newdec)['content'])))
        #print('@'+json.loads(dec)['account']['display_name'])
        #print(json.loads(dec)['content'])
        #print(json.loads(dec)['data']['content'])
    except:
        pass
