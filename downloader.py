import math
import m3u8
import os
import re
import requests
import subprocess
import sys
import webbrowser

from pprint import pprint
from random import random

CLIENT_ID = 'qlj10cyuk2moe38hzmvsbd4zzvooe1o'

def chunk_list(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def authenticate_twitch_oauth():
    """Opens a web browser to allow the user to grant the script access to their Twitch account."""

    url = ("https://api.twitch.tv/kraken/oauth2/authorize/"
           "?response_type=token&client_id={0}&redirect_uri="
           "{1}&scope=user_read+user_subscriptions").format(CLIENT_ID, REDIRECT_URL)

    print ("Attempting to open a browser to let you authenticate with Twitch")

    try:
        if not webbrowser.open_new_tab(url):
            raise webbrowser.Error
    except webbrowser.Error:
        print ("Unable to open a web browser, try accessing this URL manually instead:\n{0}".format(url))
        sys.exit(1)

def download(vod_id, start, end, output_folder='.', name=''):

    common_headers = {'Client-ID': CLIENT_ID}

    vod_id = str(vod_id)
    start = str(start)
    end = str(end)

    url = 'https://www.twitch.tv/videos/' + vod_id

    _url_re = re.compile(r"""
        http(s)?://
        (?:
            (?P<subdomain>\w+)
            \.
        )?
        twitch.tv
        /videos/
            (?P<video_id>\d+)?
    """, re.VERBOSE)

    #new API specific variables
    _chunk_re = "(.+\.ts)\?start_offset=(\d+)&end_offset=(\d+)"
    _simple_chunk_re = "(.+\.ts)"
    _vod_api_url = "https://api.twitch.tv/api/vods/{}/access_token"
    _index_api_url = "http://usher.ttvnw.net/vod/{}"

    match = _url_re.match(url).groupdict()

    channel = match.get("channel", "twitch").lower()
    subdomain = match.get("subdomain")
    video_type = match.get("video_type", "v")
    video_id = match.get("video_id")

    output_file_name = ''

    if not name:
        if end:
            output_file_name = '%s_%s_%s.mp4' % (channel, video_id, end)
        if start and end:
            output_file_name = '%s_%s_%s_%s.mp4' % (channel, video_id, start, end)
        else:
            output_file_name = '%s_%s.mp4' % (channel, video_id)
    else:
        if end:
            output_file_name = '%s_%s_%s.mp4' % (name, video_id, end)
        if start and end:
            output_file_name = '%s_%s_%s_%s.mp4' % (name, video_id, start, end)
        else:
            output_file_name = '%s_%s.mp4' % (name, video_id)

    name = output_file_name

    assert video_type == 'v'

    # Get access code
    url = _vod_api_url.format(video_id)
    r = requests.get(url, headers=common_headers)
    data = r.json()

    # Fetch vod index
    url = _index_api_url.format(video_id)
    payload = {'nauth': data['token'], 'nauthsig': data['sig'], 'allow_source': True, 'allow_spectre': False, "player": "twitchweb", "p": int(random() * 999999), "allow_audio_only": True, "type": "any"}
    r = requests.get(url, params=payload, headers=common_headers)
    m = m3u8.loads(r.content)
    index_url = m.playlists[0].uri
    index = m3u8.load(index_url)

    # Get the piece we need
    position = 0
    chunks = []
    beginning_trim = 0
    end_trim = 0

    for seg in index.segments:
        # Add duration of current segment
        position += seg.duration

        # Check if we have gotten to the start of the clip
        if position < int(start):
            continue

        if position - int(start) < seg.duration:
            beginning_trim = position - int(start)

        # Extract clip name and byte range
        p = re.match(_chunk_re, seg.absolute_uri)
        # match for playlists without byte offsets
        if not p:
            p = re.match(_simple_chunk_re, seg.absolute_uri)
            filename = p.groups()[0]
            start_byte = 0
            end_byte = 0
        else:
            filename, start_byte, end_byte = p.groups()

        chunks.append([filename, start_byte, end_byte])

        # Check if we have reached the end of clip
        if position > int(end):
            end_trim = position - int(end)
            break

    if channel == 'twitch':
        channel = chunks[0][0].split('chunked')[0].strip('/').split('/')[-1].split('_')[1]
        name = name.replace('twitch', channel)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    #download clip chunks and merge into single file
    with open(os.path.join(output_folder, 'chunks.txt'), 'w+') as cf:
        for c in chunks:
            video_url = "{}?start_offset={}&end_offset={}".format(*c)
            cf.write('%s\n' % video_url)

    print(name, beginning_trim, end_trim)

    transport_stream_file_name = name.replace('.mp4', '.ts')
    subprocess.call('wget -i %s -nv -O %s' % ('chunks.txt', transport_stream_file_name), cwd=output_folder, shell=True)
    subprocess.call('ffmpeg -i %s -bsf:a aac_adtstoasc -c copy %s' % (transport_stream_file_name, name), cwd=output_folder, shell=True)
    os.remove(os.path.join(output_folder, 'chunks.txt'))
    os.remove(os.path.join(output_folder, transport_stream_file_name))

if __name__ == '__main__':
    t = 6528
    f = 15
    l = 15
    streamer='nightblue3'
    download(vod_id=233883089, start=t-f, end=t+l, output_folder='./downloaded_mar13/'+streamer, name=streamer)
