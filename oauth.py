"""
Example of using Discord OAuth to allow someone to
log in to your site. The scope of 'email+identify' only
lets you see their email address and basic user id.
"""
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, render_template
import os

# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = 'https://example.com/oauth_callback'
scope = ['identify', 'email', 'guilds.join']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'

app = Flask(__name__)
app.secret_key = os.urandom(24)

from flask import Flask, Response, request
from requests_oauthlib import OAuth2Session

app = Flask(__name__)

@app.route("/")
def home():
    """
    Presents the 'Login with Discord' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    response = Response('<a href="' + login_url + '">Login with Discord</a>')
    response.set_cookie('state', state)
    print("Login url: %s" % login_url)
    return response



@app.route("/login")
@app.route("/oauth_callback")
def oauth_callback():
    """
    The callback we specified in our app.
    Processes the code given to us by Discord and sends it back
    to Discord requesting a temporary access token so we can
    make requests on behalf (as if we were) the user.
    e.g. https://discordapp.com/api/users/@me
    The token is stored in a cookie, so it can
    be reused across separate web requests.
    """
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=request.cookies.get('state'), scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    response = redirect('/profile')
    response.set_cookie('discord_token', token['access_token'])
    return response


@app.route("/profile")
def profile():
    """
    Example profile page to demonstrate how to pull the user information
    once we have a valid access token after all OAuth negotiation.
    """
    try:
        access_token = request.cookies.get('discord_token')
        discord = OAuth2Session(client_id, token={'access_token': access_token})
        response = discord.get(base_discord_api_url + '/users/@me')
        return render_template('profile.html', user=response.json())

    except:
        return redirect('/')


@app.route("/join")
def join():
    """
    Example Join Guild PUT request to force a user to join a guild.
    """

    access_token = request.cookies.get('discord_token')

    if not access_token:
        # Redirect the user to the Discord authorization page to get a valid access token
        discord = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        authorization_url, state = discord.authorization_url(base_discord_api_url)
        return redirect(authorization_url)

    discord = OAuth2Session(client_id, token={'access_token': access_token})
    response = discord.put(base_discord_api_url + '/users/@me/guilds/961719866505719898', json={'access_token': access_token})

    print(response)

    return response.json()





@app.route("/logout")
def logout():
    """
    Logs the user out by clearing the cookies
    """
    response = redirect('/')
    response.set_cookie('discord_token', '', expires=0)
    return response


# Or run like this
# FLASK_APP=discord_oauth_login_server.py flask run -h 0.0.0.0 -p 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

# based on https://github.com/DevDungeon/OAuth2-Login-Python-Flask-Example