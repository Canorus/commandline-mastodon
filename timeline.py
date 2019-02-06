import requests
import json
import re
import os
import shutil # for terminal window width
from datetime import datetime as dt
import pytz

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
# param['local'] = 'true'
# response = requests.get('https://twingyeo.kr/api/v1/timelines/public',headers=head,params=param)

# get home timeline
response = requests.get(instance+'/api/v1/timelines/home',headers=head,params=param)

print('data successfully received...')

#make timeline in time order
print('printing timeline...')
print('-'*shutil.get_terminal_size((80,20)).columns)
timeline = []

for res in response.json():
	timeline.insert(0,res)

def strip(t,w):
    t = re.sub('</p><p>','\n',t)
    t = re.sub('(<.?p>|<.?a.*?>|<.?span.*?>)','',t)
    t = re.sub('&lt;','<',t)
    t = re.sub('&gt;','>',t)
    t = re.sub('&apos;','\'',t)
    t = re.sub('&quot;','\'',t)
    t = re.sub('<br.*?\/?>','\n',t)
    print(t)
    print('-'*w)

def utctokst(utc_time): # in isoformat
    from datetime import datetime as dt
    import pytz
    now = str(utc_time)[:-5]
    #count length
    time_format = '%Y-%m-%dT%H:%M:%S'
    kst_format = pytz.timezone('Asia/Seoul')
    utc_format = pytz.timezone('UTC')
    time_object = dt.strptime(now, time_format)
    time_object = utc_format.localize(time_object)
    time_local = kst_format.normalize(time_object.astimezone(kst_format))
    return time_local

def cal_spacer(w, text):
    spacer1 = w - len(text) - 8
    spacer2 = w - len(text.encode('utf-8')) - 8
    spacer3 = int((spacer1 - spacer2)/2)
    return spacer2 + spacer3
    
# print timeline
w = shutil.get_terminal_size().columns
for res in timeline:
    rt = 0
    if res['reblog']:
        disp_name = res['reblog']['account']['display_name']
        user_name = res['reblog']['account']['acct']
        rt = 1
        rt_disp_name = res['account']['display_name']
        rt_user_name = res['account']['acct']
    else:
        disp_name = res['account']['display_name']
        user_name = res['account']['acct']
    #print(disp_name+'(@'+user_name+') id: '+str(res['id']))
    #created time
    now = utctokst(res['created_at']).strftime("%H:%M:%S")
    id = str(res['id'])
    name_holder = disp_name+'(@'+user_name+') '+id
    spacer = cal_spacer(w, name_holder)
    print(name_holder+' '*spacer+now)
    if rt:
        print('>>>> reblogged by '+rt_disp_name+'(@'+rt_user_name+')')
        if res['reblog']['spoiler_text']:
            print('!!변뚜주의!! '+res['reblog']['spoiler_text'])
        if res['reblog']['media_attachments']:
            for i in range(len(res['reblog']['media_attachments'])):
                print('image link: '+res['reblog']['media_attachments'][i]['url'])
    if res['spoiler_text']:
        print('!!변뚜주의!! '+res['spoiler_text'])
    if res['media_attachments']:
        for i in range(len(res['media_attachments'])):
            print('image link: '+res['media_attachments'][i]['url'])
    strip(res['content'],w)

print('timeline printed...')

print('timeline streaming initiated...')
print('-'*w)
# timeline streaming
#uri_local = instance+'/api/v1/streaming/public/local'
uri_user = instance+'/api/v1/streaming/user'
#r_local = requests.get(uri_local,headers=head,stream=True)
#print('local socket connected.')
r_user = requests.get(uri_user,headers=head,stream=True)
print('user home socket connected.')

mode = 1

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
            w = shutil.get_terminal_size().columns
            if newdec['reblog']:
                disp_name = newdec['reblog']['account']['display_name']
                user_name = newdec['reblog']['account']['acct']
                rt = 1
                rt_disp_name = newdec['account']['display_name']
                rt_user_name = newdec['account']['acct']
            else:
                disp_name = newdec['account']['display_name']
                user_name = newdec['account']['acct']
            id = str(newdec['id'])
            from_id = disp_name+'(@'+user_name+') '+id
            now = dt.now().strftime("%H:%M:%S")
            spacer = cal_spacer(w, from_id)
            print(from_id + ' '*spacer + now)
            if rt:
                print('>>>> reblogged by '+rt_disp_name+'(@'+rt_user_name+')')
            try:
                if rt:
                    print('!!변뚜주의!! '+newdec['reblog']['spoiler_text'])
                elif newdec['spoiler_text']:
                    print('!!변뚜주의!! '+newdec['spoiler_text'])
            except:
                pass
            try:
                if rt:
                    for i in range(len(newdec['reblog']['media_attachments'])):
                        print('image link: '+newdec['reblog']['media_attachments'][i]['url'])
                elif newdec['media_attachments']:
                    for i in range(len(newdec['media_attachments'])):
                        print('image link: '+newdec['media_attachments'][i]['url'])
            except:
                pass
            content = newdec['content']
            strip(content,w)
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
            strip(str(newdec['status']['content']),w)
        except:
            pass
