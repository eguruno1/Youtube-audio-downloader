#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=========================================================
🎵 YouTube → YouTube Music 자동 전환 다운로더
---------------------------------------------------------
✔ 일반 YouTube 실패 시
✔ YouTube Music URL 자동 재시도
✔ audio-only HTTPS 존재 시 성공
=========================================================
"""

from yt_dlp import YoutubeDL
from pathlib import Path

SAVE_DIR = Path.home() / "Downloads" / "YouTube_Audio"
SAVE_DIR.mkdir(exist_ok=True)

def download(url):
    opts = {
        "format": "bestaudio",
        "extractaudio": True,
        "audioformat": "flac",
        "outtmpl": str(SAVE_DIR / "%(title)s.%(ext)s"),
        "noplaylist": True,
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])

def main():
    url = input("YouTube URL: ").strip()
    video_id = url.split("v=")[-1]

    try:
        print("\n▶ 일반 YouTube 시도")
        download(url)
        print("✅ 성공")
        return
    except Exception:
        print("❌ 실패 → YouTube Music 전환")

    music_url = f"https://music.youtube.com/watch?v={video_id}"

    try:
        print("\n▶ YouTube Music 시도:", music_url)
        download(music_url)
        print("✅ Music 성공")
    except Exception as e:
        print("❌ Music도 실패")
        print("원인:", e)
        print("\n👉 이 영상은 스트리밍 전용 (다운로드 불가)")

if __name__ == "__main__":
    main()
