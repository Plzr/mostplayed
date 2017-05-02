A web app that builds playlists from your most listened to tracks on Spotify.
<br /><br />
Uses some basic Python/Flask, MySQL and the Spotify API
<br /><br />
Endpoints used:
<br />
GET: https://accounts.spotify.com/en/authorize (Authorise the user)
<br />
POST: https://accounts.spotify.com/api/token (Get the authentication token)
<br />
POST: https://api.spotify.com/v1/users/{user_id}/playlists (Create a playlist)
<br />
GET: https://api.spotify.com/v1/me/top/tracks (Get the users top tracks)
<br />
PUT: https://api.spotify.com/v1/users/{{user_id}}/playlists/{{playlist_id}}/tracks (Replace tracks into a playlist)
<br />
PUT: https://api.spotify.com/v1/users/{{user_id}}/playlists/{{playlist_id}}/followers (Follow a playlist)
