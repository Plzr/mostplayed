import requests
import json
import hashlib  # used to generate the key for the insert
import base64


def req_auth():
    # request authorization
    auth_code = base64.b64encode('2b9b835a9d2d45eab79778233e9142e4:6783d4b5790a4f5aaa94b863c30fc215')
    headers = {'Authorization': 'Basic ' + auth_code}
    auth_url = 'https://accounts.spotify.com/api/token'
    body = {'grant_type': 'client_credentials'}

    r = requests.post(auth_url, data=body, headers=headers)
    r_json = json.loads(r.text)
    return r_json['access_token']


# gets a list of the good records that are on Spotify
def get_records():
    query = db_select('''SELECT x.spotify_url,x.date,x.id,x.all_artists,x.title,sum(num) as total FROM
                (SELECT releases.*,COUNT(listens.release_id) * 5 as num
                FROM soundshe.releases_all releases
                INNER JOIN soundshe.listens
                ON listens.release_id=releases.id
                #WHERE year(releases.date)='2017'
                GROUP BY releases.id
                UNION ALL
                SELECT releases.*,COUNT(ce.release_id) * 10 as num
                FROM soundshe.releases_all releases
                INNER JOIN soundshe.charts_extended ce
                ON ce.release_id=releases.id
                #WHERE year(releases.date)='2017'
                WHERE ce.url!='Ghost'
                GROUP BY releases.id
                UNION ALL
                SELECT releases.*,COUNT(buys.release_id) * 15 as num
                FROM soundshe.releases_all releases
                INNER JOIN soundshe.buys
                ON buys.release_id=releases.id
                #WHERE year(releases.date)='2017'
                GROUP BY releases.id
                ) as x
                WHERE x.spotify_url!=''
                AND datediff(now(),x.date) < 30
                AND x.genre IN ('House','Techno','Disco','Bass')
                GROUP by x.id
                ORDER BY total DESC
                LIMIT 0,10''', ())

    get_data = query.fetchall()
    for row in get_data:
        print(row[0], row[3], row[4])

        # add_done = add_tracks(access_token,num_tracks,time_range,user_id,owner_id,playlist_id,now)


access_token = get_access_token(code)
print(access_token)

# x = get_records()
# print(x)
