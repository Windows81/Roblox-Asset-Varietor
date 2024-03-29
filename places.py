import urllib.parse
import argparse
import requests
import base64
import typing
import json
import os

COOKIE = os.environ.get('ROBLOSECURITY')


def get_sorts(cookie=COOKIE) -> list[str]:
    return (
        s['token']
        for s in requests.get(
            'https://games.roblox.com/v1/games/sorts?gameSortsContext=GamesAllSorts&contextCountryRegionId=190',
            cookies={'.ROBLOSECURITY': cookie},
        ).json()['sorts']
    )


def sorts_page(cookie=COOKIE) -> tuple[list[str], typing.Callable[[str, int], dict[str, any]]]:
    sorts = args.sorts or get_sorts(args.cookie)

    def func(sort_n: str, row_i: int) -> dict[str, any]:
        r = requests.get(
            f'https://games.roblox.com/v1/games/list?sortToken={sort_n}&startRows={row_i}&maxRows=200',
            cookies={'.ROBLOSECURITY': cookie},
        ).json()['games']

        return {
            str(p['placeId']): {
                'name': p['name'],
                'placeId': p['placeId'],
                'creatorHasVerifiedBadge': p['creatorHasVerifiedBadge'],
                'creatorId': p['creatorId'],
                'creatorName': p['creatorName'],
                'description': p['gameDescription'],
                'isSponsored': p['isSponsored'],
                'nativeAdData': p['nativeAdData'],
                'playerCount': p['playerCount'],
                'totalDownVotes': p['totalDownVotes'],
                'totalUpVotes': p['totalUpVotes'],
                'universeId': p['universeId'],
            }
            for p in r
        }
    return sorts, func


def query_page(query: str, cookie=COOKIE) -> tuple[list[str], typing.Callable[[str, int], dict[str, any]]]:
    query = urllib.parse.quote_plus(query)
    set_c = requests.get(
        f'https://www.roblox.com/discover/?Keyword={query}',
        cookies={'.ROBLOSECURITY': cookie},
    ).headers['set-cookie']

    s_beg = set_c.index('sessionid=') + 10
    sess = set_c[s_beg:s_beg + 36]

    def func(query: str, row_i: int) -> dict[str, any]:
        query = urllib.parse.quote_plus(query)
        token = base64.b64encode(json.dumps({
            'start': row_i,
            'count': 40,
            'endOfPage': False,
        }).encode('ascii')).decode('ascii')

        # token = base64.urlsafe_b64encode(
        #    f'{{"start":{row_i},"count":40,"endOfPage":false}}'
        #    .encode('ascii')).decode('ascii')

        qs = urllib.parse.urlencode({
            'pageToken': token,
            'sessionId': sess,
            'searchQuery': query,
            'pageType': 'all',
        }, doseq=False)

        r = requests.get(
            f'https://apis.roblox.com/search-api/omni-search?{qs}',
            cookies={'.ROBLOSECURITY': cookie},
        )
        j = r.json()

        return {
            str(p['rootPlaceId']): {
                'name': p['name'],
                'placeId': p['rootPlaceId'],
                'creatorHasVerifiedBadge': p['creatorHasVerifiedBadge'],
                'creatorId': p['creatorId'],
                'creatorName': p['creatorName'],
                'description': p['description'],
                'isSponsored': p['isSponsored'],
                'nativeAdData': p['nativeAdData'],
                'playerCount': p['playerCount'],
                'totalDownVotes': p['totalDownVotes'],
                'totalUpVotes': p['totalUpVotes'],
                'universeId': p['universeId'],
            }
            for g in j['searchResults']
            for p in g['contents']
        }
    return [query], func


def list_from_calls(sorts: list[str], func: typing.Callable[[str, int], dict[str, any]], incr=200) -> dict:
    s_set = set(sorts)
    cache = {sort: {} for sort in s_set}
    row_i = 0
    while s_set:
        for sort_n in s_set.copy():
            data = func(sort_n, row_i)
            sort_t = cache[sort_n]
            old_len = len(sort_t)
            sort_t.update(data)
            new_len = len(sort_t)
            if new_len == old_len:
                s_set.remove(sort_n)
        row_i += incr
    return {i: v for t in cache.values() for i, v in t.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sorts', type=str, nargs='*')
    parser.add_argument('--query', '-q', type=str, nargs='?')
    parser.add_argument('--cookie', '-c', type=str, default=COOKIE, nargs='?')
    parser.add_argument('--filename', '-f', type=str, default='places.json', nargs='?')
    args = parser.parse_args()

    try:
        with open(args.filename, 'r') as f:
            original = json.load(f)
    except FileNotFoundError:
        original = {}

    if args.query:
        original.update(list_from_calls(*query_page(args.query, args.cookie), 40))
    else:
        original.update(list_from_calls(*sorts_page(args.cookie), 200))

    with open(args.filename, 'w') as f:
        json.dump(original, f, indent='\t')
