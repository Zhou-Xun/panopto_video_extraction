import json


def download_caption(json_path):
    with open(json_path) as json_file:
        videos = json.load(json_file)

    print(len(videos['Results']))

def main():
    download_caption("output_with_caption_url/output.json")


if __name__ == '__main__':
    main()