from analyze_vods import get_list_from_file
import os
from datetime import datetime
import api

def fetch_streamers():
    already_fetched = []
    streamers = []

    date = datetime.now().date()
    if os.path.isfile('streamerlists/'+str(date)+'_list.txt'):
        already_fetched = get_list_from_file('streamerlists/'+str(date)+'_list.txt')

    streamers = [ x['channel']['name'] for x in api.streamer_list('Fortnite') ]

    for s in streamers:
        if s not in already_fetched:
            already_fetched.append(s)

    with open('streamerlists/'+str(date)+'_list.txt', 'w') as f:
        for stmr in already_fetched:
            f.write("%s\n" % stmr)

    return already_fetched

if __name__ == '__main__':
    print(fetch_streamers())