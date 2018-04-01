import os
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import sys
from downloader import download
import subprocess
from datetime import datetime
from get_vod_chat import get_list_from_file

# output_folder_root = '/Volumes/Expansion\ Drive/jugchug/clips/'
output_folder_root = './clips/'

POGCHAMP_WORDS = get_list_from_file('pogchamp_words.txt')

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
    freq_l = []
    freq_champ = []
    cur_count = 0
    champ_count = 0

    f = open(filename, "r")
    for line in f:
        t = line.split()[0]
        h,m,s = map(int, t[1:-1].split(':'))

        true_t = h*3600+m*60+s

        msg = ' '.join(line.split(' ')[2:]).strip()
        msg_lower = msg.lower()
        # print(msg)
        if len(msg) > 0:
            pog = float(sum(1 for c in msg if c.isupper()))/(len(msg) - msg.count(' '))
            champ = float(Counter(msg.split()).most_common(1)[0][1])/len(msg.split())
            pogchamp = ()
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

            if champ > 0.5 and len(msg.split()) > 2:
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

    if show_plot:
        x = np.arange(0, len(freq_l)*interval_sec, interval_sec)
        x_champ = np.arange(0, len(freq_champ)*interval_sec, interval_sec)
        fig = plt.figure()
        plt.plot(x, freq_l)
        plt.plot(x_champ, freq_champ)
        plt.axhline(y=5*float(sum(freq_l))/len(freq_l), color='r')
        plt.title('POGCHAMP ' + filename)
        plt.ylabel('chat frequency')
        plt.xlabel('time')
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

    avg=5*float(sum(freq_l))/len(freq_l)
    hist = set()
    top_mom = np.argsort(freq_l)[::-1]

    downloads = 0

    if download:
        for i, x in enumerate(top_mom):
            freq = freq_l[x]
            if freq > avg and freq > interval_sec:
                l = list(range(x-begin_offset, x+end_offset))
                if not any(e in hist for e in l):
                    for e in l:
                        hist.add(e)
                    t = x*interval_sec
                    begin_t = t-begin_offset*interval_sec
                    end_t = t+end_offset*interval_sec
                    args = ['python2','downloader_term.py', '-u', url, '-o', output_folder_root+date+'/'+streamer+'/'+str(vod_id), '-n', str(downloads+1)+'_'+streamer, '-s', str(begin_t), '-e', str(end_t)]
                    p = subprocess.Popen(args)
                    p.communicate()
                    downloads += 1

                    if downloads >= limit:
                        break
    return freq_l    

def analyze_streamer(name, interval_sec=15):
    l = os.listdir("chats/" + name)
    for f in l:
        analyze("chats/" + name + "/" + f, interval_sec)

def analyze_streamer_POGCHAMPS_and_download(name, date, interval_sec=15):
    if os.path.isdir("chats/" + str(date.date()) + '/' + name):
        l = os.listdir("chats/" + str(date.date()) + '/' + name)
        for f in l:
            if f[-4:] == '.log':
                analyze_POGCHAMPS_and_download(filename="chats/" + str(date.date()) + '/' + name + "/" + f, interval_sec=interval_sec, show_plot=True, begin_offset=2, end_offset=2, download=True, limit=5)
        
def analyze_streamer_POGCHAMPS(name, date, interval_sec=15):
    if os.path.isdir("chats/" + str(date.date()) + '/' + name):
        l = os.listdir("chats/" + str(date.date()) + '/' + name)
        for f in l:
            if f[-4:] == '.log':
                analyze_POGCHAMPS_and_download(filename="chats/" + str(date.date()) + '/' + name + "/" + f, interval_sec=interval_sec, show_plot=True, begin_offset=4, end_offset=1, download=False, limit=5)
        
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python freq_analysis.py [name] [yyyy-mm-dd]')

    else:
        y,m,d = map(int, sys.argv[2].split('-'))
        analyze_streamer_POGCHAMPS(sys.argv[1], datetime(y,m,d), 5)


