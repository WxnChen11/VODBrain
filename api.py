import requests
from typing import Generator
from datetime import datetime

def get(path: str, params: dict = None, headers: dict = None) -> requests.Response:
    params = {} if params is None else params
    headers = {} if headers is None else headers
    params['client_id'] = '1vzo3tk7le4gdf3d2n0aihn56w3fj4'

    response: requests.Response = requests.get(url='https://api.twitch.tv/v5/{path}'.format(path=path),
                                               params=params,
                                               headers=headers)
    if response.status_code != requests.codes.ok:
        print('\n[Error]')
        print('Twitch API returned status code {}. Please check your client ID.'.format(response.status_code))
        print('\nUrl\t{}\nParams\t{}\nHeaders\t{}\n'.format(response.url, params, headers))
    return response

def user_id(user_name):
    d = get('users', {'login':user_name}).json()
    if d['_total'] > 1:
        print('More than one user found!')
        return None
    elif d['_total'] == 0:
        print('No users found!')
        return None
    return d['users'][0]['_id']

def video_list(user_id, cursor):
    return get('channels/{}/videos'.format(user_id), {'limit': 100, 'cursor': cursor}).json()

def vods(user_id, game, date=None, length=3600):
    fragment: dict = {'_next': ''}

    while '_next' in fragment:
        fragment = video_list(user_id, fragment['_next'])
        if not fragment.get('videos', None):
            yield None
        else:
            for video in fragment['videos']:
                # if video['game'] and game in video['game'].lower() and video['length'] > length and video['viewable'] == 'public' and ((date and datetime.strptime(video['published_at'].split('T')[0], '%Y-%m-%d').date() == date) or not date):
                if video['length'] > length and video['viewable'] == 'public' and ((date and datetime.strptime(video['published_at'].split('T')[0], '%Y-%m-%d').date() == date) or not date):
                    yield video

def streamer_list(game, limit=100):
    return get('streams'.format(user_id), {'limit': limit, 'game': game}).json()['streams']