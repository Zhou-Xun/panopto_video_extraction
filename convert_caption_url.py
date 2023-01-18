import json
import re
from urllib import request


def download_caption(json_path):
    with open(json_path) as json_file:
        videos = json.load(json_file)

    for video in videos['Results']:
        print(video['Urls']['CaptionDownloadUrl'])
        request.urlretrieve(video['Urls']['CaptionDownloadUrl'], "caption/" + video['Id'] + ".txt");


def read_coursera_to_time_sentence(input_path):
    with open(input_path) as f:
        lines = f.readlines()

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


def generate_output_dictionary(sen_list, word_list, output_path):
    full_transcript = ""
    for sen in sen_list:
        full_transcript += sen + " "
    full_transcript = full_transcript.strip()

    output_dict = dict()
    output_dict['timedtext'] = word_list
    output_dict['full_transcript'] = full_transcript

    with open(output_path, 'w', encoding="utf-8") as file_obj:
        json.dump(output_dict, file_obj, indent=2)


def main():
    download_caption("output_with_caption_url/output.json")
    # time_list, sen_list = read_coursera_to_time_sentence('sample-coursera-transcript.txt')
    # time_list_second = convert_time_list_to_seconds(time_list)
    # word_list = generate_word_list(time_list_second, sen_list)
    # generate_output_dictionary(sen_list, word_list, "output_v1.json")


if __name__ == '__main__':
    main()