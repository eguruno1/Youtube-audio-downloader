#!/usr/bin/env python3
"""
YouTube 음원 다운로더 (FLAC) - 명령줄 버전
가장 단순하고 안정적인 방식
"""

import os
import sys
from pathlib import Path
import subprocess

# 다운로드 경로
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def download_audio(url):
    """
    yt-dlp 명령줄 직접 실행
    Python 래핑 없이 직접 실행이 가장 안정적
    """
    print("\n" + "=" * 70)
    print("YouTube 음원 다운로더 (FLAC)")
    print("=" * 70)
    print(f"\n📁 저장 위치: {DOWNLOAD_PATH}")
    print(f"🔗 URL: {url}\n")
    
    # yt-dlp 명령어 구성
    command = [
        'yt-dlp',
        '--extract-audio',                    # 오디오만 추출
        '--audio-format', 'flac',             # FLAC 형식
        '--audio-quality', '0',               # 최고 품질
        '--output', f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',  # 저장 경로
        '--no-playlist',                      # 플레이리스트 무시
        '--progress',                         # 진행률 표시
        '--cookies-from-browser', 'chrome',   # Chrome 쿠키 사용
        url
    ]
    
    print("🚀 다운로드 시작...\n")
    
    try:
        # yt-dlp 실행
        result = subprocess.run(command, check=True, text=True, capture_output=False)
        
        print("\n" + "=" * 70)
        print("✅ 다운로드 완료!")
        print(f"📁 저장 위치: {DOWNLOAD_PATH}")
        print("=" * 70 + "\n")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print("❌ 오류 발생")
        print("=" * 70)
        print("\n💡 해결 방법:")
        print("1. Chrome에서 YouTube에 로그인하세요")
        print("2. YouTube 동영상을 재생해보세요")
        print("3. 다시 시도하세요")
        print("\n또는 Safari 사용:")
        print(f"   yt-dlp --cookies-from-browser safari {url}")
        print()
        return False
        
    except FileNotFoundError:
        print("\n" + "=" * 70)
        print("❌ yt-dlp가 설치되지 않았습니다")
        print("=" * 70)
        print("\n📦 설치 방법:")
        print("   pip3 install yt-dlp")
        print()
        return False


def main():
    """메인 함수"""
    print("\n" + "=" * 70)
    print("🎵 YouTube 음원 다운로더 (FLAC)")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 URL 전달받음
        url = sys.argv[1]
    else:
        # 대화형 모드
        print("\nYouTube URL을 입력하세요:")
        print("(종료하려면 Ctrl+C 또는 빈 줄 입력)\n")
        url = input("URL: ").strip()
        
        if not url:
            print("종료합니다.")
            return
    
    # URL 검증
    if not ('youtube.com' in url or 'youtu.be' in url):
        print("\n❌ 올바른 YouTube URL이 아닙니다.")
        print("예시: https://www.youtube.com/watch?v=...")
        return
    
    # 플레이리스트 경고
    if 'list=' in url:
        print("\n⚠️  플레이리스트 URL이 감지되었습니다.")
        print("첫 번째 동영상만 다운로드됩니다.")
        response = input("계속하시겠습니까? (y/n): ").strip().lower()
        if response != 'y':
            print("취소되었습니다.")
            return
    
    # 다운로드 실행
    success = download_audio(url)
    
    # 추가 다운로드 여부
    if success:
        print("다른 동영상을 다운로드하시겠습니까?")
        print("프로그램을 다시 실행하세요:")
        print(f"   python3 {sys.argv[0]}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.\n")
        sys.exit(0)
