import requests
import json
import re
import os

from credential import retrieve

instance = input('input your instance: ')
if instance[:5] != 'https':
    instance = 'https://'+instance
username = input('input your username: ')
access_code = retrieve(username, instance)
try:
    with open('position.json') as f:
        pos = json.load(f)
    for i in pos:
        if i[0]['instance'] == instance:
            for k in i:
                try:
                    if k['username'] == username:
                        position = k['position']
                        break
                except:
                    pass
except:
    pass
try:
    param = {'since_id':position}
except:
    param = ""
head = {'Authorization':'Bearer '+access_code}

# get local timeline
# param = {'local':'true'}
# response = requests.get('https://twingyeo.kr/api/v1/timelines/public',headers=head,params=param)
#print('data successfully received...')

timeline = 0

# get home timeline
response = requests.get(instance+'/api/v1/timelines/home',headers=head,params=param)
print('data successfully received...')

#make timeline in time order
print('printing timeline...')
print('-------------------------------')
timeline = []

for res in response.json():
	timeline.insert(0,res)

def strip(t):
    t = re.sub('</p><p>','\n',t)
    t = re.sub('(<.?p>|<.?a.*?>|<.?span.*?>)','',t)
    t = re.sub('&lt;','<',t)
    t = re.sub('&gt;','>',t)
    t = re.sub('&apos;','\'',t)
    t = re.sub('&quot;','\'',t)
    t = re.sub('<br.*?\/?>','\n',t)
    print(t)
    print('-------------------------------')

def dec(t):
    t = t.decode('utf-8')
    try:
        t = re.sub('data: ','',t)
    except:
        if t == ':thump':
            pass
        else:
            print('')
            print('-------------------------------')
    print(str(json.loads(t)['account']['display_name']+' (@'+str(json.loads(t)['account']['username'])+')'+' id: '+str(json.loads(t)['id'])))
    strip(json.loads(t)['content'])

# print timeline

for res in timeline:
    rt = 0
    if res['reblog']:
        disp_name = res['reblog']['account']['display_name']
        user_name = res['reblog']['account']['username']
        rt = 1
        rt_disp_name = res['account']['display_name']
        rt_user_name = res['account']['username']
    else:
        disp_name = res['account']['display_name']
        user_name = res['account']['username']
    print(disp_name+'(@'+user_name+') id: '+str(res['id']))
    if rt:
        print('>>>> reblogged by'+rt_disp_name+'(@'+rt_user_name+')')
    if res['spoiler_text']:
        print('!!변뚜주의!! '+res['spoiler_text'])
    if res['media_attachments']:
        print('image link: '+res['media_attachments'][0]['url'])
    strip(res['content'])

print('timeline printed...')

print('timeline streaming initiated...')
print('-------------------------------')
# timeline streaming
#uri_local = instance+'/api/v1/streaming/public/local'
uri_user = instance+'/api/v1/streaming/user'
#r_local = requests.get(uri_local,headers=head,stream=True)
#print('local socket connected.')
r_user = requests.get(uri_user,headers=head,stream=True)
print('user home socket connected.')

mode = 1

#inte = zip(r_local.iter_lines(), r_user.iter_lines())
#for user, local in inte:
#    (dec(user),dec(local))

for l in r_user.iter_lines():
    rt = 0
    dec = l.decode('utf-8')
    if dec == 'event: notification':
        mode = 0
    elif dec == 'event: update':
        mode = 1
    elif dec ==':thump':
        mode = 1
    if mode:
        try:
            newdec = json.loads(re.sub('data: ','',dec))
            if newdec['reblog']:
                disp_name = newdec['reblog']['account']['display_name']
                user_name = newdec['reblog']['account']['username']
                rt = 1
                rt_disp_name = newdec['account']['display_name']
                rt_user_name = newdec['account']['username']
            else:
                disp_name = newdec['account']['display_name']
                user_name = newdec['account']['username']
            print(disp_name+'(@'+user_name+') id: '+newdec['id'])
            if rt:
                print('>>>> reblogged by '+rt_disp_name+'(@'+rt_user_name+')')
            try:
                if newdec['spoiler_text']:
                    print('!!변뚜주의!! '+newdec['spoiler_text'])
            except:
                pass
            try:
                if newdec['media_attachments']:
                    print('image link: '+newdec['media_attachments'][0]['url'])
            except:
                pass
            content = newdec['content']
            strip(content)
            # save last status from timeline
            # maybe add user timeline / local timeline
            # [                                             # position:list
            #   ['instance':'instance1',                    # i:index number
            #     {                                         # user:dict
            #       'username':'user1',
            #       'position':'last id'
            #     }
            #   ],
            #   ['instance':'instance2',
            #     {'username':'user2',
            #       'position':'last id'
            #     }
            #   ]
            # ]
            try:
                with open('position.json') as f:
                    position = json.load(f)
            except:
                position = []
            instance_count = 0
            for i in range(len(position)):
                if position[i][0]['instance'] == instance:
                    username_count = 0
                    for k in range(len(position[i])):
                        username_count += 1
                        try:
                            if position[i][k]['username'] == username:
                                position[i][k]['position'] = str(newdec['id'])
                                break
                        except:
                            pass
                    # instance exists, username doesn't
                    #print('no username')
                    if username_count == len(position[i]):
                        position[i][k].append({"username":username, "position":str(newdec['id'])})
                    break
                instance_count += 1
            # instance doesn't exists
            if instance_count == len(position):
                #print('no instance')
                position.append([{"instance":instance},{"username":username,"position":str(newdec['id'])}])
            with open('position.json','w') as f:
                json.dump(position,f)
        except:
            pass
    else:
        try:
            newdec = json.loads(re.sub('data: ','',dec))
            action = ""
            if newdec['type'] == 'reblog':
                action = 'reblogged'
            elif newdec['type'] == 'favourite':
                action = 'favourited'
            elif newdec['type'] == 'mention':
                action = 'mentioned to'
            elif newdec['type'] == 'follow':
                print('@'+str(newdec['account']['display_name'])+' followed you')
                raise
            # check if newdec['account']['url'] is different from mine
            # then add instance address
            print('@'+str(newdec['account']['display_name'])+' '+action+' your status:')
            print('>>> ')
            strip(str(newdec['status']['content']))
        except:
            pass
