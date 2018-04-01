from subprocess import Popen
import os 
import api
from datetime import date, datetime
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
app_cwd = dir_path+'/TwitchChatDownloader'

def get_chat(vod, name, date):
    if os.path.isfile('chats/'+str(date)+'/'+name+'/v'+vod+'.log'):
        return False
    print("calling")
    p = Popen(['python', 'app.py', '-v', str(vod), '--format', 'irc', '--output', '../chats/'+str(date)+'/'+name], cwd=app_cwd)
    p.wait()
    return True

def get_chats_for_vods(name, game, download=False, limit=5, date=None):

    user_id = api.user_id(name)
    vods = api.vods(user_id, game, date, 3600)

    c = 0
    c_d = 0
    for vod in vods:
        if vod:
            v_id = vod['_id'][1:]
            date = datetime.strptime(vod['published_at'].split('T')[0], '%Y-%m-%d').date()
            if download:
                if get_chat(v_id, name, date):
                    c_d += 1
                    if c_d >= limit:
                        c += 1
                        break
            c += 1
    print("Total Vods Queried:",c)
    print("Total Vods Downloaded:",c_d)

def get_list_from_file(filename):

    l = []
    f = open(filename, 'r') 
    for line in f: 
        l.append(line.strip())

    print(l)
    return l

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python get_vod_chat.py yyyy-mm-dd")
    else:
        y,m,d = map(int,sys.argv[1].split('-'))
        date = date(y,m,d)
        streamer_list = get_list_from_file('streamerlists/'+sys.argv[1]+'_list.txt')
        for streamer in streamer_list:
            if streamer[0] != '*':
                get_chats_for_vods(streamer, 'fortnite', True, 5, date)