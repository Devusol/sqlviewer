import mimetypes
import hashlib
import json
import os

# import requests
from requests_oauthlib import OAuth1Session


def smugmug():
    print("Hello from a function")


def oauth_requests(api_key, api_secret, access_token, token_secret):
    """
    Skip the Out-of-Band PIN if you already have API key+secret and Access token+secret
    Return authenticated OAuth session and user's root node URI.
    1) Register Consumer to recieve API Key and Secret: https://api.smugmug.com/api/developer/apply
        Name: Photobooth, Type: Application|Plug-In|Service|Toy|Other (Service?), Platform: Linux, Use: Non-Commercial
        Account Settings -> Me -> API Keys -> Photobooth (per name used above)
    2) Retrieve Access Token and Secret from Account Settings
        Account Settings -> Privacy -> Authorized Services -> Photobooth [Token] (per name used above)
    """
    session = OAuth1Session(
        api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=token_secret
    )
    root_node_uri = get_root_node(session)
    children_nodes = get_node_children(session, root_node_uri)

    print(f"root node: {root_node_uri}\nchildren: {children_nodes}")
    return session
# , root_node_uri


def oauth_without_token(client_key, client_secret):
    """
    Get access token and secret.
    Use if Access Token and Access Token Secret are unknown. Usually if you didn't make App on your own User account.
    Ref: https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html
    """
    # Obtain Request Token
    request_token_url = 'https://secure.smugmug.com/services/oauth/1.0a/getRequestToken'
    oauth = OAuth1Session(client_key, client_secret=client_secret)
    fetch_response = oauth.fetch_request_token(request_token_url, params={
                                               'oauth_callback': 'oob'})  # out-of-band, because not web app
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    # Obtain Authorization from User
    base_authorization_url = 'https://secure.smugmug.com/services/oauth/1.0a/authorize'
    authorization_url = oauth.authorization_url(base_authorization_url)
    # only good for a few minutes?
    verifier_pin = input(
        f'URL: {authorization_url}&access=Full&permissions=Modify\nEnter PIN: ')
    # Obtain Access Token
    access_token_url = 'https://secure.smugmug.com/services/oauth/1.0a/getAccessToken'
    oauth = OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier_pin
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    resource_owner_key = oauth_tokens.get('oauth_token')
    resource_owner_secret = oauth_tokens.get('oauth_token_secret')
    print(
        f"access token: {oauth_tokens}\nowner key: {resource_owner_key}\nowner secret: {resource_owner_secret}")
    return resource_owner_key, resource_owner_secret


def get_root_node(session):
    """Return URI of user's root node, given an authenticated session."""
    api_authuser = session.get(
        f'https://api.smugmug.com/api/v2!authuser', headers={'Accept': 'application/json'}).json()
    root_node_uri = api_authuser['Response']['User']['Uris']['Node']['Uri']
    print(f'[INFO] Got root node: "{root_node_uri}".')
    return root_node_uri


def get_node_children(session, node_uri):
    """Return JSON of all child nodes, given an authenticated session and parent node URI."""
    node_children = session.get(
        f'https://api.smugmug.com{node_uri}!children', headers={'Accept': 'application/json'}).json()

    # DEBUG
    print(
        f"[INFO] Total Children: {node_children['Response']['Pages']['Total']}")
    for child in node_children['Response']['Node']:
        print('[DEBUG]', json.dumps({
            'Name': child['Name'],
            'Type': child['Type'],
            'SecurityType': child['SecurityType'],
            'HasChildren': child['HasChildren'],
            'Uri': child['Uri'],
            'WebUri': child['WebUri'],
        }, indent=4))

    return node_children


# oauth_without_token("cP8LhDrDHDBPNTTNznSW8jgQpRhQmK5z", "7g35HLJ4PdhJGRLg44SkC2mSmFWfDH5z9CWSG64jTFT3cBvMJpjCNZHFhqg5d7Bs")


def upload_image(image_paths):
    # _images = image_paths.split(",")
    print(image_paths)
    session = OAuth1Session("cP8LhDrDHDBPNTTNznSW8jgQpRhQmK5z",
                            client_secret="7g35HLJ4PdhJGRLg44SkC2mSmFWfDH5z9CWSG64jTFT3cBvMJpjCNZHFhqg5d7Bs",
                            resource_owner_key="bL56zZRZnsVCBgdGD7MhvFzzH2xLJZk5",
                            resource_owner_secret="dT2HVv2PhQDvXgX9BTn7wR7tnvtVfghgZFDzVrJ32HNWC85gpVFnszQzvmw9h2jb"
                            )
    # typePNG = "image/png"
    # typeJPG = "image/jpeg"

    for image_path in image_paths:
        image_type = mimetypes.guess_type(image_path)[0]
        print(image_type)

        with open(image_path, 'rb') as image:
            image_data = image.read()
        for i in range(2):
            # Retry once. Switching between SmugMug API and Uploader API occasionally causes SmugMug to RST connection.
            try:
                r = session.post(
                    'https://upload.smugmug.com/',
                    headers={
                        'Accept': b'application/json',
                        'Content-Length': str(len(image_data)),
                        'Content-MD5': hashlib.md5(image_data).hexdigest(),
                        'Content-Type': image_type,
                        'X-Smug-AlbumUri': "/api/v2/album/3zqtgn",
                        'X-Smug-FileName': os.path.basename(image_path),
                        'X-Smug-ResponseType': 'JSON',
                        'X-Smug-Version': 'v2',
                    },
                    data=image_data,
                )
            except Exception as e:
                r = False
                print(
                    f'[WARN] Upload attempted while offline (attempt {i+1}). "{e}".')
            else:
                break

        if r and r.json()['stat'] == 'ok':
            print(f"[INFO] Upload Success: {r.json()['Image']['URL']}")
        else:
            # TODO: increase failure handling. Upload error codes aren't great.
            print(f'[WARN] Upload Failed: "{image_path}"')
        return r
