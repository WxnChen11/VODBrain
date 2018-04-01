from get_vod_chat import get_list_from_file
from freq_analysis import analyze_streamer_POGCHAMPS_and_download
from datetime import datetime
import sys

def download_all_clips(date, intv=15):

    streamer_list = get_list_from_file('streamerlists/'+str(date.date())+'_list.txt')
    for streamer in streamer_list:
        analyze_streamer_POGCHAMPS_and_download(streamer, date, intv)

def download_clips(streamer, date, intv=15):

    analyze_streamer_POGCHAMPS_and_download(streamer, date, intv)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python download_clips.py [streamer] [yyyy-mm-dd] [interval]")
    else:
        y,m,d = map(int, sys.argv[2].split('-'))
        download_clips(sys.argv[1], datetime(y,m,d), int(sys.argv[3]) if len(sys.argv) > 3 else 15)
