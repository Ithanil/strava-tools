import requests
import webbrowser
import sys
from urllib.parse import urlencode, urlparse, parse_qs

# --- CONFIGURATION ---
# You can hardcode these if you want to skip the first prompts
CLIENT_ID = ''
CLIENT_SECRET = ''

def main():
    print("--- Strava OAuth Authorization Helper ---")

    # 1. Get Credentials
    c_id = CLIENT_ID if CLIENT_ID else input("Enter your Client ID: ").strip()
    c_secret = CLIENT_SECRET if CLIENT_SECRET else input("Enter your Client Secret: ").strip()

    if not c_id or not c_secret:
        print("Error: Client ID and Secret are required.")
        sys.exit(1)

    # 2. Define Scopes
    print("\n--- Scope Configuration ---")
    default_scopes = "read_all,profile:read_all,activity:read_all"

    print(f"  [Default] Read-Only:       {default_scopes}")
    print(f"  Suggested for an update script:  read_all,profile:read_all,activity:read_all,activity:write")

    user_scopes = input(f"\nEnter scopes (comma separated) [Press Enter for Default]: ").strip()

    # Use user input, or fallback to default if empty
    scopes = user_scopes if user_scopes else default_scopes

    print(f"-> Using scopes: {scopes}")

    redirect_uri = "http://localhost/exchange_token"

    # 3. Generate Authorization URL
    params = {
        'client_id': c_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'approval_prompt': 'force',
        'scope': scopes
    }

    auth_url = f"https://www.strava.com/oauth/authorize?{urlencode(params)}"

    print(f"\n1. I will now open a browser window to: {auth_url}")
    print("2. Please click 'Authorize'.")
    print("3. You will be redirected to a page that looks like an error (localhost).")
    print("4. COPY the entire URL from your browser address bar and paste it below.\n")

    input("Press Enter to open browser...")
    webbrowser.open(auth_url)

    # 4. Input Redirect URL
    redirected_url = input("\nPaste the full redirected URL here: ").strip()

    # 5. Extract Code
    try:
        parsed_url = urlparse(redirected_url)
        query_params = parse_qs(parsed_url.query)

        if 'code' not in query_params:
            print("Error: Could not find 'code' in the URL. Did you click Authorize?")
            sys.exit(1)

        code = query_params['code'][0]
    except Exception as e:
        print(f"Error parsing URL: {e}")
        sys.exit(1)

    print(f"Authorization Code found: {code}")

    # 6. Exchange Code for Token
    print("Exchanging code for Access Token...")
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': c_id,
        'client_secret': c_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)

    if response.status_code != 200:
        print(f"Error exchanging token: {response.text}")
        sys.exit(1)

    data = response.json()

    # 7. Output Credentials
    print("\n" + "="*40)
    print("SUCCESS! HERE ARE YOUR CREDENTIALS")
    print("="*40)
    print(f"Access Token:  {data.get('access_token')}")
    print(f"Refresh Token: {data.get('refresh_token')}")
    print(f"Expires At:    {data.get('expires_at')}")
    print(f"Scopes:        {scopes}")
    print("="*40)

if __name__ == "__main__":
    main()
