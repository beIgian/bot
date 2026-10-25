"""
Standalone web server that handles Discord's OAuth2 handshake.

Flow:
  1. A user clicks the link posted by the bot's /verify command.
  2. That link points here, at /authorize, which immediately redirects
     them to Discord's own official consent screen.
  3. Discord shows the user exactly what they're approving ("add you to
     servers on your behalf") and asks them to click Authorize.
  4. Discord redirects back to /callback with a one-time code.
  5. We exchange that code for an access token scoped to guilds.join
     and store it, tied to their Discord user ID.

No password, token, or credential of the user's is ever seen or
handled by this code directly -- Discord issues a scoped token after
the user explicitly approves on Discord's own page.
"""

import requests
from flask import Flask, redirect, request, render_template_string, abort
from urllib.parse import urlencode

import db
from config import (
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
    DISCORD_API_BASE, OAUTH_SCOPES,
)

app = Flask(__name__)
db.init_db()

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Verified</title></head>
<body style="font-family: sans-serif; text-align:center; padding-top: 80px; background:#000600; color:#fff;">
  <h1>✅ You're verified</h1>
  <p>{{ username }}, you can close this tab now.</p>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body style="font-family: sans-serif; text-align:center; padding-top: 80px;">
  <h1>Something went wrong</h1>
  <p>{{ message }}</p>
</body>
</html>
"""


@app.route("/authorize")
def authorize():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": OAUTH_SCOPES,
        "prompt": "consent",
    }
    return redirect(f"https://discord.com/oauth2/authorize?{urlencode(params)}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return render_template_string(ERROR_PAGE, message="Missing authorization code."), 400

    token_resp = requests.post(
        f"{DISCORD_API_BASE}/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if token_resp.status_code != 200:
        return render_template_string(ERROR_PAGE, message="Discord rejected the authorization."), 400

    token_data = token_resp.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]

    user_resp = requests.get(
        f"{DISCORD_API_BASE}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_resp.status_code != 200:
        return render_template_string(ERROR_PAGE, message="Could not fetch your Discord profile."), 400

    user = user_resp.json()
    db.upsert_member(
        user_id=user["id"],
        username=f'{user["username"]}',
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )

    return render_template_string(SUCCESS_PAGE, username=user["username"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
