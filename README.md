# mostplayed
I wanted a way to keep track of my favourite tracks across multiple playlists.
sdf
Uses some basic Python/Flask, MySQL and the Spotify API
~adffs
Endpoints used:
~
GET: https://accounts.spotify.com/en/authorize (Authorise the user)
POST: https://accounts.spotify.com/api/token (Get the authentication token)
POST: https://api.spotify.com/v1/users/{user_id}/playlists (Create a playlist)
GET: https://api.spotify.com/v1/me/top/tracks (Get the users top tracks)
PUT: https://api.spotify.com/v1/users/{{user_id}}/playlists/{{playlist_id}}/tracks (Replace tracks into a playlist)
PUT: https://api.spotify.com/v1/users/{{user_id}}/playlists/{{playlist_id}}/followers (Follow a playlist)
