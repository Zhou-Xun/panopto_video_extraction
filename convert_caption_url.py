import json
import re
from urllib import request
import requests
from panopto_oauth2 import PanoptoOAuth2

server = "sph.hosted.panopto.com"
client_id = "29bd20b2-fd78-4bdd-9c40-af7a0133c139"
client_secret = "oZVXzyYlRQun/+xrxaItsdSDm1n7Np6rNqlmjHjgcyQ="


def read_coursera_to_time_sentence(input_path, video_id):
    with open(input_path) as f:
        lines = f.readlines()

    if not lines:
        print("{} has caption url but doesn't have caption".format(video_id))

    index = 1
    start, timestamp, sen, sen_list, time_list = True, False, "", [], []
    for line in lines:
        if line == "{}\n".format(index):
            if index > 1:
                sen_list.append(sen.replace("\n", " ").strip())
            index += 1
            sen = ""
            timestamp = True
        elif timestamp:
            time_list.append(line.replace("\n", ""))
            timestamp = False
        else:
            sen += line
    sen_list.append(sen.replace("\n", " ").strip())

    return time_list, sen_list


def convert_timestamp_to_sec(timestamp):
    timestamp_split = timestamp.split(":")
    timestamp_second = int(timestamp_split[0])*3600+int(timestamp_split[1])*60+float(timestamp_split[2].replace(",", "."))
    return timestamp_second


def convert_time_list_to_seconds(time_list):
    time_list_second = []
    for i in range(len(time_list)):
        start_time = time_list[i].split(" --> ")[0]
        end_time = time_list[i].split(" --> ")[1]

        start_time_sec = convert_timestamp_to_sec(start_time)
        end_time_sec = convert_timestamp_to_sec(end_time)
        time_list_second.append([start_time_sec, end_time_sec])
    return time_list_second


def generate_word_list(time_list_second, sen_list):
    word_dict, word_list = {}, []

    for i in range(len(time_list_second)):
        start_time, end_time = time_list_second[i]
        sen = sen_list[i]
        # split the sentence
        sen_split = re.sub(r'[^\w\s]', '', sen_list[0])
        sen_split = sen.split(" ")
        # sen_split: ['Hi', 'everyone', 'Welcome', 'to']
        # sen: 'Hi, everyone. Welcome to'
        # start_time, end_time: [10.29, 12.94]
        # start assigning each timestamp to each word
        ## c_index: iterate sen
        ## w_index: iterate word

        w_index, c_index = 0, 0

        while c_index < len(sen):
            if sen[c_index: (c_index + len(sen_split[w_index]))] == sen_split[w_index]:
                time_for_each_word = (end_time - start_time) / len(sen)

                word_start = round(c_index * time_for_each_word + start_time, 2)
                word_end = round(word_start + len(sen_split[w_index]) * time_for_each_word, 2)

                word_dict['word'] = sen_split[w_index]
                word_dict['start_time'] = word_start
                word_dict['end_time'] = word_end

                word_list.append(word_dict)

                word_dict = {}
                c_index += len(sen_split[w_index])
                w_index += 1
            else:
                c_index += 1
    return word_list


def generate_output_dictionary(sen_list, word_list):
    full_transcript = ""
    for sen in sen_list:
        full_transcript += sen + " "
    full_transcript = full_transcript.strip()

    output_dict = dict()
    output_dict['timedtext'] = word_list
    output_dict['full_transcript'] = full_transcript

    return output_dict


def output_json(output_dict):
    with open("output_with_caption/output.json", 'w', encoding="utf-8") as file_obj:
        json.dump(output_dict, file_obj, indent=2)


def main():
    with open("output_with_caption_url/output.json") as json_file:
        videos = json.load(json_file)

    video_list = []
    count = 1
    for i in range(len(videos['Results'])):
        video = videos['Results'][i]
        url = video['Urls']['CaptionDownloadUrl']
        if url is not None:         
            print("================={}=================".format(i))
            count += 1
            video_dict = video.copy()
            time_list, sen_list = read_coursera_to_time_sentence("caption/" + video['Id'] + ".txt", video['Id'])
            time_list_second = convert_time_list_to_seconds(time_list)
            word_list = generate_word_list(time_list_second, sen_list)
            caption_dict = generate_output_dictionary(sen_list, word_list)

            video_dict['caption'] = caption_dict
            video_list.append(video_dict)

            # Just convert one caption
            #  To convert all captions, please comment the following if statement
            if count == 2:
                break

    print("================")
    print(len(video_list))
    output_dict = {"Results": video_list}
    output_json(output_dict)


if __name__ == '__main__':
    main()