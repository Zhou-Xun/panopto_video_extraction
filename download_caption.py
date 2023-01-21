import json
import re
import urllib
from urllib import request
import requests
from panopto_oauth2 import PanoptoOAuth2

server = "sph.hosted.panopto.com"
client_id = "29bd20b2-fd78-4bdd-9c40-af7a0133c139"
client_secret = "oZVXzyYlRQun/+xrxaItsdSDm1n7Np6rNqlmjHjgcyQ="


def authorization(requests_session, oauth2):
    # Go through authorization
    access_token = oauth2.get_access_token_authorization_code_grant()
    # Set the token as the header of requests
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})
    return 'Bearer ' + access_token


def inspect_response_is_unauthorized(response):
    '''
    Inspect the response of a requets' call, and return True if the response was Unauthorized.
    An exception is thrown at other error responses.
    Reference: https://stackoverflow.com/a/24519419
    '''
    if response.status_code // 100 == 2:
        # Success on 2xx response.
        return False

    if response.status_code == requests.codes.unauthorized:
        print('Unauthorized. Access token is invalid.')
        return True

    # Throw unhandled cases.
    response.raise_for_status()


def download_caption(json_path, cookie):
    with open(json_path) as json_file:
        videos = json.load(json_file)

    count = 0
    for video in videos['Results']:
        url = video['Urls']['CaptionDownloadUrl']
        if url is not None:
            opener = urllib.request.build_opener()
            opener.addheaders = [("Cookie", cookie)]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, "caption/" + video['Id'] + ".txt")
            count += 1
    print("{} videos have caption".format(count))


def main():
    # get authorization
    requests_session = requests.Session()
    requests_session.verify = False
    oauth2 = PanoptoOAuth2(server, client_id, client_secret, False)
    access_token = authorization(requests_session, oauth2)
    # get cookie
    auth_url = 'https://{0}/Panopto/api/v1/auth/legacyLogin'.format(server)
    auth_resp = requests.get(auth_url, headers={"Authorization": access_token})

    # download caption
    download_caption("output_with_caption_url/output.json", auth_resp.headers['Set-Cookie'])



if __name__ == '__main__':
    main()