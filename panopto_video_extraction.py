import sys
import argparse
import requests
import urllib3
import json

from panopto_oauth2 import PanoptoOAuth2

server = "sph.hosted.panopto.com"
client_id = "29bd20b2-fd78-4bdd-9c40-af7a0133c139"
client_secret = "oZVXzyYlRQun/+xrxaItsdSDm1n7Np6rNqlmjHjgcyQ="


def authorization(requests_session, oauth2):
    # Go through authorization
    access_token = oauth2.get_access_token_authorization_code_grant()
    # Set the token as the header of requests
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})


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


def get_child_folders(oauth2, requests_session, folder_id):
    url = 'https://{0}/Panopto/api/v1/folders/{1}/children'.format(server, folder_id)

    resp = requests_session.get(url=url)
    if inspect_response_is_unauthorized(resp):
        # Re-authorization
        authorization(requests_session, oauth2)
    data = resp.json()
    return data['Results']


def get_video_info(oauth2, requests_session, folder_id):
    url = 'https://{0}/Panopto/api/v1/folders/{1}/sessions'.format(server, folder_id)

    resp = requests_session.get(url=url)
    if inspect_response_is_unauthorized(resp):
        # Re-authorization
        authorization(requests_session, oauth2)
    data = resp.json()
    return data['Results']


def output_json(output_dict):
    with open("output.json", 'w', encoding="utf-8") as file_obj:
        json.dump(output_dict, file_obj, indent=2)


def panopto_video_extraction():
    root_folder_id = "54c36bf0-010c-45e7-949e-af810125d039"
    requests_session = requests.Session()
    requests_session.verify = False
    oauth2 = PanoptoOAuth2(server, client_id, client_secret, False)
    authorization(requests_session, oauth2)

    # using bfs to iterate each folder level and check if there is any video in that level
    folder_list = [root_folder_id]
    video_list = []

    while folder_list:
        cur_folder = folder_list.pop(0)
        child_folders_list = get_child_folders(oauth2, requests_session, cur_folder)

        # iterate child folders
        if child_folders_list:
            for child_folder in child_folders_list:
                folder_list.append(child_folder['Id'])

        # check videos in the folder
        videos = get_video_info(oauth2, requests_session, cur_folder)
        video_list += videos

    output_dict = {"Results": video_list}
    output_json(output_dict)


if __name__ == '__main__':
    panopto_video_extraction()

