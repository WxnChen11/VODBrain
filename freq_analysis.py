import os
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import sys
from downloader import download
import subprocess
from datetime import datetime
from get_vod_chat import get_list_from_file
from analyze_thumbnail import analyze_thumbnail_from_file_and_delete
from generate_thumbnail import generate_thumb_from_file

# output_folder_root = '/Volumes/Expansion\ Drive/jugchug/clips/'
output_folder_root = './clips/'

POGCHAMP_WORDS = get_list_from_file('pogchamp_words.txt')
CHAMP_WORDS = get_list_from_file('champ_words.txt')

CONSECUTIVE_FREQ_CONSTANT = 1

def analyze(filename, interval_sec=15):

    begin_cur_timeframe = 0
    freq_l = []
    cur_count = 0

    f = open(filename, "r")
    for line in f:
        t = line.split()[0]
        h,m,s = map(int, t[1:-1].split(':'))

        true_t = h*3600+m*60+s

        if true_t > begin_cur_timeframe + interval_sec:
            freq_l.append(cur_count)
            cur_count = 0
            begin_cur_timeframe += interval_sec
            while true_t > begin_cur_timeframe + interval_sec:
                begin_cur_timeframe += interval_sec
                freq_l.append(0)
            cur_count = 1
        else:
            cur_count += 1    

    x = np.arange(0, len(freq_l)*interval_sec, interval_sec)
    plt.plot(x, freq_l)
    plt.title(filename)
    plt.ylabel('chat frequency')
    plt.xlabel('time')

    if not os.path.isdir('freq/' + filename.split('/')[1]):
        os.mkdir('freq/' + filename.split('/')[1])

    new_dir = filename.replace('chats', 'freq')
    new_dir = new_dir.replace('.log', '.png')
    print(new_dir)
    plt.savefig(new_dir)
    plt.show()

    return freq_l

def analyze_POGCHAMPS_and_download(filename, interval_sec=15, show_plot=False, begin_offset=2, end_offset=2, download=False, limit=10):

    def onclick(event):

        try:
            t= int(event.xdata)
        except:
            t=0
        h = int(t/3600)
        m = int((t - h*3600)/60)
        s = t-h*3600-m*60

        print(t,'is',h,':',m,':',s)

    vod_id = filename.split('/')[3][1:-4]
    url = 'https://twitch.tv/videos/'+vod_id
    streamer = filename.split('/')[2]
    date = filename.split('/')[1]
    print(streamer,':',url)

    begin_cur_timeframe = 0
    begin_cur_timeframe_champ = 0
    begin_cur_timeframe_pogchamp = 0
    freq_l = []
    freq_champ = []
    freq_pogchamp = []
    cur_count = 0
    champ_count = 0
    pogchamp_count = 0
    total_count = 0

    f = open(filename, "r")
    for line in f:
        i_1 = line.find('[')
        i_2 = line.find(']')
        t = line[i_1+1:i_2]
        day = 0
        if ',' in t:
            day = int(t.split()[0])
            t = t.split()[2]
        line = line[i_2+2:]
        h,m,s = map(int, t.split(':'))
        h += day*24

        true_t = h*3600+m*60+s

        msg = ' '.join(line.split(' ')[1:]).strip()
        msg_lower = msg.lower()
        # print(msg)
        if len(msg) > 0:
            total_count += 1

            pog = float(sum(1 for c in msg if c.isupper()))/(len(msg) - msg.count(' '))
            # champ = float(Counter(msg.split()).most_common(1)[0][1])/len(msg.split())
            champ = any(word in msg_lower for word in CHAMP_WORDS)
            pogchamp = any(word in msg_lower for word in POGCHAMP_WORDS)
            # print(pog, champ)

            # if pog > 0.7 or (champ > 0.5 and len(msg.split()) > 2):
            if pog > 0.7:
                if true_t > begin_cur_timeframe + interval_sec:
                    freq_l.append(cur_count)
                    cur_count = 0
                    begin_cur_timeframe += interval_sec
                    while true_t > begin_cur_timeframe + interval_sec:
                        begin_cur_timeframe += interval_sec
                        freq_l.append(0)
                    cur_count = 1
                else:
                    cur_count += 1    

            # if champ > 0.5 and len(msg.split()) > 2:
            if champ:
                if true_t > begin_cur_timeframe_champ + interval_sec:
                    freq_champ.append(champ_count)
                    champ_count = 0
                    begin_cur_timeframe_champ += interval_sec
                    while true_t > begin_cur_timeframe_champ + interval_sec:
                        begin_cur_timeframe_champ += interval_sec
                        freq_champ.append(0)
                    champ_count = 1
                else:
                    champ_count += 1   

            if pogchamp:
                if true_t > begin_cur_timeframe_pogchamp + interval_sec:
                    freq_pogchamp.append(pogchamp_count)
                    pogchamp_count = 0
                    begin_cur_timeframe_pogchamp += interval_sec
                    while true_t > begin_cur_timeframe_pogchamp + interval_sec:
                        begin_cur_timeframe_pogchamp += interval_sec
                        freq_pogchamp.append(0)
                    pogchamp_count = 1
                else:
                    pogchamp_count += 1   

    # avg=5*float(sum(freq_l))/len(freq_l)
    C = 5
    avg = C*max(1,float(total_count)/(max([len(freq_l), len(freq_champ), len(freq_pogchamp),float(1/interval_sec)])*interval_sec))

    freq_metric = freq_pogchamp
    
    top_mom = np.argsort(freq_metric)[::-1] #CHANGE FREQ BELOW (L168) TOO

    top_int = []
    hist = set()
    top_count = 0

    for i in top_mom:
        if i not in hist and freq_metric[i] > interval_sec:
            if top_count > limit:
                break
            t_i = i
            start=t_i
            end=t_i
            hist.add(t_i)
            while t_i >= 0:
                t_i -= 1
                if t_i in hist:
                    start = t_i
                    break
                if freq_metric[t_i] > avg/C:
                    start = t_i
                    hist.add(t_i)
                else:
                    start = t_i
                    hist.add(t_i)
                    break

            for j in range(i, len(freq_metric)-3):
                if j in hist:
                    end = j
                    break
                if freq_metric[j+1] > freq_metric[j]*CONSECUTIVE_FREQ_CONSTANT or freq_metric[j+2] > freq_metric[j]*CONSECUTIVE_FREQ_CONSTANT or freq_metric[j+3] > freq_metric[j]*CONSECUTIVE_FREQ_CONSTANT:
                    end=j
                    hist.add(j)
                else:
                    end=j
                    hist.add(j)
                    # print("FREQ===", j)
                    # print(freq_metric[j], freq_metric[j+1], freq_metric[j+2])
                    break

            for j in range(i, len(freq_metric)-3):
                if freq_metric[j] < avg/C:
                    break
                hist.add(j)

            if start != end:
                top_int.append((start,end))
                top_count += 1

    if show_plot:
        x = np.arange(0, len(freq_l)*interval_sec, interval_sec)
        x_champ = np.arange(0, len(freq_champ)*interval_sec, interval_sec)
        x_pogchamp = np.arange(0, len(freq_pogchamp)*interval_sec, interval_sec)
        fig = plt.figure()
        plt.plot(x, freq_l)
        plt.plot(x_champ, freq_champ)
        plt.plot(x_pogchamp, freq_pogchamp)
        plt.axhline(y=avg, color='r')
        plt.title('POGCHAMP ' + filename)
        plt.ylabel('chat frequency')
        plt.xlabel('time')
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

    downloads = 0

    hist = set()

    if download:
        for start, end in top_int:
            begin_t = (start-begin_offset)*interval_sec
            end_t = (end+end_offset)*interval_sec
            args = ['python2','downloader_term.py', '-u', url, '-o', output_folder_root+date+'/'+streamer+'/'+str(vod_id), '-n', str(downloads+1)+'_'+streamer, '-s', str(begin_t), '-e', str(end_t)]
            p = subprocess.Popen(args)
            p.communicate()
            fname = str(downloads+1)+'_'+streamer+'_'+str(vod_id)+'_'+str(begin_t)+'_'+str(end_t)
            thumb_name = generate_thumb_from_file(fname, cwd=output_folder_root[2:]+date+'/'+streamer+'/'+str(vod_id))
            if analyze_thumbnail_from_file_and_delete(thumb_name, output_folder_root[2:]+date+'/'+streamer+'/'+str(vod_id)):
                downloads += 1

            if downloads >= limit:
                print("LIMIT LIMIT LIMIT")
                break

    return freq_metric    

def analyze_streamer(name, interval_sec=15):
    l = os.listdir("chats/" + name)
    for f in l:
        analyze("chats/" + name + "/" + f, interval_sec)

def analyze_streamer_POGCHAMPS_and_download(name, date, interval_sec=15):
    if os.path.isdir("chats/" + str(date.date()) + '/' + name):
        l = os.listdir("chats/" + str(date.date()) + '/' + name)
        for f in l:
            if f[-4:] == '.log':
                analyze_POGCHAMPS_and_download(filename="chats/" + str(date.date()) + '/' + name + "/" + f, interval_sec=interval_sec, show_plot=False, begin_offset=1, end_offset=0, download=True, limit=10)
        
def analyze_streamer_POGCHAMPS(name, date, interval_sec=15):
    if os.path.isdir("chats/" + str(date.date()) + '/' + name):
        l = os.listdir("chats/" + str(date.date()) + '/' + name)
        for f in l:
            if f[-4:] == '.log':
                analyze_POGCHAMPS_and_download(filename="chats/" + str(date.date()) + '/' + name + "/" + f, interval_sec=interval_sec, show_plot=True, begin_offset=2, end_offset=0, download=False, limit=10)
        
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python freq_analysis.py [name] [yyyy-mm-dd] [interval]')

    else:
        y,m,d = map(int, sys.argv[2].split('-'))
        analyze_streamer_POGCHAMPS(sys.argv[1], datetime(y,m,d), int(sys.argv[3]) if len(sys.argv) > 3 else 15)


