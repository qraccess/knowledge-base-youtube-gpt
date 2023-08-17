#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2023/7/13 22:35
# @Author  : Rui
# @Contact : qrcnu@163.com
# @File    : scrapy.py
from lxml import html
from urllib.parse import urljoin
import os
from moviepy.editor import AudioFileClip
from faster_whisper import WhisperModel
import yt_dlp
from urllib.parse import urlparse, parse_qs
from pytube import Playlist, YouTube
from multiprocessing import Pool, Manager
import multiprocessing


cur_dir = os.path.dirname(os.path.abspath(__file__))
model_size = os.path.join(cur_dir, 'model', 'whisper', 'large-v2')
output_dir = os.path.join(cur_dir, 'output')
raw_dir = os.path.join(output_dir, 'raw')
md_dir = os.path.join(output_dir, 'md')

os.path.exists(output_dir) or os.mkdirs(output_dir)
os.path.exists(raw_dir) or os.mkdirs(raw_dir)
os.path.exists(md_dir) or os.mkdirs(md_dir)


def download_youtube_single_audio(video_url, shared_dict):
    youtube = YouTube(video_url)
    if os.path.exists(os.path.join(raw_dir, youtube.video_id + '.mp3')):
        print(f'{youtube.video_id} already exists')
        shared_dict[youtube.video_id] = {
            'identifier': youtube.video_id,
            'title': youtube.title,
            'author': youtube.author,
            'url': youtube.watch_url,
            'md_file': os.path.join(md_dir, youtube.video_id + '.md'),
            'channel': youtube.channel_id
        }
        return
    # download the highest quality audio stream
    try:
        stream = youtube.streams.filter(only_audio=True).first()
        download_path = stream.download(output_path=raw_dir)

        # convert to mp3
        audio = AudioFileClip(download_path)
        mp3_path = download_path.replace('.mp4', '.mp3')
        audio.write_audiofile(mp3_path)

        # remove the original file
        os.remove(download_path)

        # rename the mp3 file
        new_mp3_path = os.path.join(raw_dir, youtube.video_id + '.mp3')
        os.rename(mp3_path, new_mp3_path)
        shared_dict[youtube.video_id] = {
            'identifier': youtube.video_id,
            'title': youtube.title,
            'author': youtube.author,
            'url': youtube.watch_url,
            'md_file': os.path.join(md_dir, youtube.video_id + '.md'),
            'channel': youtube.channel_id
        }
    except Exception as e:
        print(e)


def audios_to_md(audios):
    whisper_model = WhisperModel(model_size, device="auto", compute_type="auto")
    for audio in audios:
        if os.path.exists(os.path.join(md_dir, audio.split('.')[0] + '.md')):
            continue
        try:
            print('transcribing: ', audio)
            mp3file = os.path.join(raw_dir, audio)
            segments, info = whisper_model.transcribe(mp3file,
                                                    beam_size=5, vad_filter=True,
                                                    vad_parameters=dict(min_silence_duration_ms=50))
            texts = []
            for segment in segments:
                print(segment.text)
                texts.append(segment.text)
            if texts:
                with open(os.path.join(md_dir, audio.split('.')[0] + '.md'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(texts))
                print('done: ', audio)
        except Exception as e:
            print(e)
            continue


def is_youtube_video_list(url):
    parsed = urlparse(url)
    if 'youtube.com' in parsed.netloc:
        if 'list' in parse_qs(parsed.query):
            return 0  # This is a playlist
        if '/watch' in parsed.path and 'v' in parse_qs(parsed.query):
            return 1  # This is a video
    return -1  # This is neither a video nor a playlist, or it's not a YouTube link


def download_youtube_audios(url):
    urls = []
    manager = Manager()
    shared_dict = manager.dict()

    is_playlist = is_youtube_video_list(url)
    if is_playlist == 0:
        playlist = Playlist(url)
        print('Number of videos in playlist: %s' % len(playlist.video_urls))
        urls.extend(playlist.video_urls)
    elif is_playlist == 1:
        urls.append(url)
    else:
        print('Invalid YouTube link')
        return
    num_cores = multiprocessing.cpu_count()

    with Pool(processes=num_cores//2) as p:  # Adjust this number based on your system's capabilities
        # Use the pool's map method to apply download_youtube_single_audio to every URL
        p.starmap(download_youtube_single_audio, [(item, shared_dict) for item in urls])
    return list(shared_dict.values())


if __name__ == '__main__':
    # url='https://www.youtube.com/watch?v=SfaHCX0qTlQ&list=PLlHw500PGQdJJ_-ENpCy7vVfewvraQCOj'
    # download_youtube_audios(url)
    audios = [item for item in os.listdir(raw_dir) if item.endswith('.mp3')]
    audios_to_md(audios)