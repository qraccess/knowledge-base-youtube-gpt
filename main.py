from content_embedding import content_to_db
from user_query import user_query_loop
import argparse
from scrapy import download_youtube_audios, audios_to_md
from content_embedding import audio_to_db

parser = argparse.ArgumentParser(description="")


def main() -> None:
    """
    main
    """

    # 用户提问查询
    user_query_loop()


def download_audio_to_db(url: str) -> None:
    audios = download_youtube_audios(url)
    audios_to_md(audios)
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


