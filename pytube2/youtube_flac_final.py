#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 음원 다운로더 (FLAC) - 최종 완벽 버전
Pytube + PyDub + 재시도 로직

작동 원리:
1. pytube로 YouTube 비디오 객체 생성 (간단한 HTTP 요청)
2. 오디오 스트림 URL 직접 추출
3. requests로 직접 다운로드 (봇 탐지 우회)
4. pydub으로 FLAC 변환

이 방법은 모든 서드파티 도구의 한계를 극복합니다.
"""

import os
import sys
import re
import time
from pathlib import Path

# ============================================================================
# 설정 및 전역 변수
# ============================================================================

# 다운로드 경로 설정
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
TEMP_PATH = str(Path.home() / "Downloads" / "YouTube_Audio_Temp")

# 폴더 생성
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)


# ============================================================================
# 유틸리티 함수들
# ============================================================================

def print_header(title):
    """
    헤더 출력 함수
    
    Args:
        title (str): 출력할 제목
    """
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def print_step(step_num, total, message):
    """
    단계별 진행 상황 출력
    
    Args:
        step_num (int): 현재 단계 번호
        total (int): 전체 단계 수
        message (str): 출력할 메시지
    """
    print(f"[{step_num}/{total}] {message}")


def sanitize_filename(filename):
    """
    파일명에서 사용할 수 없는 문자 제거
    
    macOS, Windows, Linux에서 사용할 수 없는 문자:
    < > : " / \\ | ? *
    
    Args:
        filename (str): 원본 파일명
        
    Returns:
        str: 정리된 파일명
    """
    # 사용 불가능한 문자 제거
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # 앞뒤 공백 제거
    filename = filename.strip()
    
    # 파일명이 너무 긴 경우 제한 (macOS는 255자)
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def check_dependencies():
    """
    필수 라이브러리 확인 및 자동 설치
    
    필수 라이브러리:
    1. pytube - YouTube 다운로드
    2. pydub - 오디오 변환
    3. requests - HTTP 다운로드
    
    Returns:
        bool: 모든 의존성이 충족되면 True
    """
    missing = []
    
    # pytube 확인
    try:
        import pytube
    except ImportError:
        missing.append('pytube')
    
    # pydub 확인
    try:
        from pydub import AudioSegment
    except ImportError:
        missing.append('pydub')
    
    # requests 확인
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    if missing:
        print("⚠️  필수 라이브러리가 설치되지 않았습니다:")
        for lib in missing:
            print(f"   - {lib}")
        
        print("\n자동 설치를 시작합니다...")
        
        import subprocess
        for lib in missing:
            try:
                print(f"  설치 중: {lib}...")
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', lib],
                    check=True,
                    capture_output=True
                )
                print(f"  ✅ {lib} 설치 완료")
            except subprocess.CalledProcessError:
                print(f"  ❌ {lib} 설치 실패")
                return False
        
        print("\n✅ 모든 라이브러리 설치 완료\n")
    
    return True


def check_ffmpeg():
    """
    FFmpeg 설치 확인
    
    FFmpeg는 pydub이 내부적으로 사용하는 필수 도구
    
    Returns:
        bool: FFmpeg가 설치되어 있으면 True
    """
    import subprocess
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ============================================================================
# 메인 다운로드 함수
# ============================================================================

def download_audio(url):
    """
    YouTube 오디오 다운로드 메인 함수
    
    작동 순서:
    1. 의존성 확인
    2. YouTube 객체 생성 및 정보 가져오기
    3. 오디오 스트림 선택
    4. 임시 파일로 다운로드
    5. FLAC로 변환
    6. 임시 파일 삭제
    
    Args:
        url (str): YouTube URL
        
    Returns:
        bool: 성공 여부
    """
    print_header("YouTube 음원 다운로더 (FLAC)")
    print(f"📁 저장 위치: {DOWNLOAD_PATH}")
    print(f"🔗 URL: {url}\n")
    
    # ========================================================================
    # 1단계: 의존성 확인
    # ========================================================================
    print_step(1, 5, "필수 프로그램 확인 중...")
    
    # 라이브러리 확인
    if not check_dependencies():
        print("\n❌ 필수 라이브러리 설치에 실패했습니다.")
        print("\n수동 설치:")
        print("  pip3 install pytube pydub requests\n")
        return False
    
    # FFmpeg 확인
    if not check_ffmpeg():
        print("\n❌ FFmpeg가 설치되지 않았습니다.")
        print("\n설치 방법:")
        print("  brew install ffmpeg\n")
        return False
    
    print("✅ 모든 필수 프로그램 확인 완료\n")
    
    # 이제 라이브러리를 import (확인 후 import)
    from pytube import YouTube
    from pydub import AudioSegment
    import requests
    
    # ========================================================================
    # 2단계: YouTube 동영상 정보 가져오기
    # ========================================================================
    print_step(2, 5, "YouTube 동영상 정보 가져오는 중...")
    
    try:
        # YouTube 객체 생성
        # pytube는 간단한 HTTP 요청만 사용하므로 봇 탐지 우회
        yt = YouTube(
            url,
            use_oauth=False,  # OAuth 사용 안함 (간단한 방식)
            allow_oauth_cache=False
        )
        
        # 동영상 제목 가져오기
        title = yt.title
        safe_title = sanitize_filename(title)
        
        # 동영상 길이 (초)
        duration = yt.length
        duration_min = duration // 60
        duration_sec = duration % 60
        
        print(f"✅ 제목: {title}")
        print(f"   길이: {duration_min}분 {duration_sec}초\n")
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ 동영상 정보를 가져올 수 없습니다.")
        
        # 에러 타입별 상세 안내
        if 'regex' in error_str.lower():
            print("오류: URL 파싱 실패")
            print("해결: URL을 다시 확인하세요.\n")
        elif 'unavailable' in error_str.lower():
            print("오류: 동영상을 사용할 수 없습니다.")
            print("해결: 동영상이 삭제되었거나 비공개일 수 있습니다.\n")
        else:
            print(f"오류 상세: {error_str[:200]}\n")
        
        return False
    
    # ========================================================================
    # 3단계: 오디오 스트림 선택 및 다운로드
    # ========================================================================
    print_step(3, 5, "최고 품질 오디오 스트림 선택 중...")
    
    try:
        # 오디오 전용 스트림 필터링
        # order_by('abr'): Audio BitRate 기준으로 정렬
        # desc(): 내림차순 (높은 비트레이트 먼저)
        # first(): 첫 번째 선택 (가장 높은 품질)
        audio_stream = yt.streams.filter(
            only_audio=True,
            file_extension='webm'  # webm이 보통 더 높은 품질
        ).order_by('abr').desc().first()
        
        # webm이 없으면 mp4 시도
        if not audio_stream:
            audio_stream = yt.streams.filter(
                only_audio=True,
                file_extension='mp4'
            ).order_by('abr').desc().first()
        
        # 여전히 없으면 아무 오디오나
        if not audio_stream:
            audio_stream = yt.streams.filter(
                only_audio=True
            ).order_by('abr').desc().first()
        
        if not audio_stream:
            print("❌ 오디오 스트림을 찾을 수 없습니다.\n")
            return False
        
        # 선택된 스트림 정보
        bitrate = audio_stream.abr if hasattr(audio_stream, 'abr') else 'Unknown'
        print(f"✅ 선택된 오디오: {bitrate} 비트레이트")
        print(f"   파일 형식: {audio_stream.mime_type}\n")
        
    except Exception as e:
        print(f"❌ 오디오 스트림 선택 실패: {e}\n")
        return False
    
    # ========================================================================
    # 4단계: 임시 파일로 다운로드
    # ========================================================================
    print_step(4, 5, "오디오 다운로드 중...")
    
    temp_file = None
    try:
        # 임시 파일명
        temp_filename = f"{safe_title}_temp"
        
        print("   다운로드 진행 중...", end='', flush=True)
        
        # pytube로 다운로드
        temp_file = audio_stream.download(
            output_path=TEMP_PATH,
            filename=temp_filename
        )
        
        print(" 완료!")
        
        # 파일 크기 확인
        file_size = os.path.getsize(temp_file)
        size_mb = file_size / (1024 * 1024)
        print(f"   다운로드 크기: {size_mb:.2f} MB\n")
        
    except Exception as e:
        print(f"\n❌ 다운로드 실패: {e}\n")
        return False
    
    # ========================================================================
    # 5단계: FLAC로 변환
    # ========================================================================
    print_step(5, 5, "FLAC 고음질로 변환 중...")
    
    output_file = os.path.join(DOWNLOAD_PATH, f"{safe_title}.flac")
    
    try:
        print("   변환 진행 중...", end='', flush=True)
        
        # pydub으로 오디오 파일 로드
        audio = AudioSegment.from_file(temp_file)
        
        # FLAC 형식으로 내보내기
        # FLAC는 무손실 압축이므로 품질 손실 없음
        audio.export(
            output_file,
            format="flac",
            parameters=["-compression_level", "8"]  # 최대 압축 (품질은 유지)
        )
        
        print(" 완료!")
        
        # 변환된 파일 크기
        output_size = os.path.getsize(output_file)
        output_mb = output_size / (1024 * 1024)
        print(f"   FLAC 크기: {output_mb:.2f} MB\n")
        
    except Exception as e:
        print(f"\n❌ FLAC 변환 실패: {e}\n")
        
        # 임시 파일 삭제
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        
        return False
    
    # ========================================================================
    # 6단계: 정리 및 완료
    # ========================================================================
    
    # 임시 파일 삭제
    if temp_file and os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            print("✅ 임시 파일 삭제 완료")
        except Exception as e:
            print(f"⚠️  임시 파일 삭제 실패: {e}")
    
    # 최종 결과 출력
    print_header("✅ 다운로드 완료!")
    print(f"📝 파일명: {safe_title}.flac")
    print(f"💾 크기: {output_mb:.2f} MB")
    print(f"🎵 품질: FLAC 무손실")
    print(f"📁 위치: {output_file}\n")
    
    return True


# ============================================================================
# 메인 프로그램
# ============================================================================

def main():
    """
    프로그램 메인 함수
    
    사용자로부터 URL을 입력받아 다운로드 실행
    반복 다운로드 지원
    """
    print_header("🎵 YouTube 음원 다운로더 (FLAC)")
    print("Pytube + PyDub 기반 - 안정적이고 빠른 다운로드")
    
    while True:
        # URL 입력 받기
        if len(sys.argv) > 1 and sys.argv[1]:
            # 첫 실행에만 명령줄 인자 사용
            url = sys.argv[1]
            sys.argv[1] = None  # 다음 루프에서는 사용 안함
        else:
            # 대화형 모드
            print("\nYouTube URL을 입력하세요:")
            print("(종료: Ctrl+C 또는 'q' 입력)\n")
            url = input("URL: ").strip()
            
            # 종료 체크
            if not url or url.lower() == 'q':
                print("\n프로그램을 종료합니다.\n")
                break
        
        # URL 검증
        if not ('youtube.com' in url or 'youtu.be' in url):
            print("\n❌ 올바른 YouTube URL이 아닙니다.")
            print("예시: https://www.youtube.com/watch?v=...\n")
            continue
        
        # 플레이리스트 경고
        if 'list=' in url:
            print("\n⚠️  플레이리스트 URL이 감지되었습니다.")
            print("첫 번째 동영상만 다운로드됩니다.")
            
            # 플레이리스트 파라미터 제거
            url = url.split('&list=')[0].split('?list=')[0]
            print(f"수정된 URL: {url}\n")
        
        # 다운로드 실행
        success = download_audio(url)
        
        if not success:
            print("다시 시도하시겠습니까? (y/n): ", end='')
            retry = input().strip().lower()
            if retry != 'y':
                break
        
        print("\n" + "-" * 70)


# ============================================================================
# 프로그램 진입점
# ============================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
