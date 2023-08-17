from content_embedding import content_to_db
from user_query import user_query_loop
import argparse
from scrapy import download_youtube_audios, audios_to_md
from content_embedding import audio_to_db
import os

parser = argparse.ArgumentParser(description="")

cur_dir = os.path.dirname(os.path.abspath(__file__))
model_size = os.path.join(cur_dir, 'model', 'whisper', 'large-v2')
output_dir = os.path.join(cur_dir, 'output')
raw_dir = os.path.join(output_dir, 'raw')
md_dir = os.path.join(output_dir, 'md')

os.path.exists(output_dir) or os.mkdirs(output_dir)
os.path.exists(raw_dir) or os.mkdirs(raw_dir)
os.path.exists(md_dir) or os.mkdirs(md_dir)


def main() -> None:
    """
    main
    """

    # 用户提问查询
    user_query_loop()


def download_audio_to_db(url: str) -> None:
    audios = download_youtube_audios(url)
    mp3files = [item for item in os.listdir(raw_dir) if item.endswith('.mp3')]
    audios_to_md(mp3files)
    for item in audios:
        audio_to_db(item)


if __name__ == '__main__':
    parser.add_argument('--url', type=str, help='Youtube List or Video Url')
    parser.add_argument('--query', action='store_true', help='Query')

    args = parser.parse_args()

    if args.url:
        print(args.url)
        download_audio_to_db(args.url)

    if args.query:
        main()


