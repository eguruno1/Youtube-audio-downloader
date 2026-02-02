#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 음원 다운로더 (FLAC) - FFmpeg 직접 사용 방식
Y2mate와 유사한 방식으로 동작

작동 원리:
1. YouTube URL에서 동영상 정보 추출
2. streamlink로 직접 스트림 URL 획득
3. ffmpeg로 오디오만 추출하여 FLAC 변환
4. 모든 작업을 로컬에서 처리

이 방법은 YouTube의 봇 탐지를 우회합니다.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs


# ============================================================================
# 설정 및 전역 변수
# ============================================================================

# 다운로드 경로 설정
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


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


def print_step(step_num, message):
    """
    단계별 진행 상황 출력
    
    Args:
        step_num (int): 단계 번호
        message (str): 출력할 메시지
    """
    print(f"[{step_num}/4] {message}")


def extract_video_id(url):
    """
    YouTube URL에서 동영상 ID 추출
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: 동영상 ID 또는 None
        
    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    # watch?v= 형식
    if 'watch?v=' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('v', [None])[0]
    
    # youtu.be 짧은 URL 형식
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[-1].split('?')[0]
    
    return None


def check_dependencies():
    """
    필수 프로그램 설치 확인
    
    streamlink는 명령줄 도구와 Python 모듈 두 가지 방법으로 확인
    1. 명령줄: streamlink --version
    2. Python 모듈: python3 -m streamlink --version
    
    Returns:
        tuple: (streamlink 설치 여부, ffmpeg 설치 여부, streamlink 실행 방법)
        streamlink 실행 방법: 'command' 또는 'module'
    """
    streamlink_installed = False
    streamlink_method = None
    ffmpeg_installed = False
    
    # streamlink 확인 - 방법 1: 명령줄 도구
    try:
        result = subprocess.run(
            ['streamlink', '--version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        streamlink_installed = True
        streamlink_method = 'command'
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # streamlink 확인 - 방법 2: Python 모듈
    if not streamlink_installed:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'streamlink', '--version'],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            streamlink_installed = True
            streamlink_method = 'module'
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # ffmpeg 확인
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        ffmpeg_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return streamlink_installed, ffmpeg_installed, streamlink_method


def install_streamlink():
    """
    streamlink 자동 설치 시도
    
    Returns:
        bool: 설치 성공 여부
    """
    print("streamlink 설치 중...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'streamlink'],
            check=True
        )
        print("✅ streamlink 설치 완료\n")
        return True
    except subprocess.CalledProcessError:
        print("❌ streamlink 설치 실패\n")
        return False


# ============================================================================
# 메인 다운로드 함수
# ============================================================================

def download_audio(url):
    """
    YouTube 오디오 다운로드 메인 함수
    
    작동 순서:
    1. URL에서 동영상 ID 추출
    2. streamlink로 스트림 URL 획득 (YouTube 봇 탐지 우회)
    3. ffmpeg로 오디오 추출 및 FLAC 변환
    4. 파일 저장
    
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
    print_step(1, "필수 프로그램 확인 중...")
    
    streamlink_ok, ffmpeg_ok, streamlink_method = check_dependencies()
    
    if not ffmpeg_ok:
        print("\n❌ FFmpeg가 설치되지 않았습니다.")
        print("\n설치 방법:")
        print("  brew install ffmpeg\n")
        return False
    
    if not streamlink_ok:
        print("⚠️  streamlink가 설치되지 않았습니다.")
        if not install_streamlink():
            print("\n수동 설치:")
            print("  pip3 install streamlink\n")
            return False
        # 설치 후 다시 확인
        streamlink_ok, _, streamlink_method = check_dependencies()
        if not streamlink_ok:
            print("❌ streamlink 설치 후에도 실행할 수 없습니다.\n")
            return False
    
    print(f"✅ 모든 필수 프로그램 확인 완료 (streamlink: {streamlink_method} 방식)\n")
    
    # streamlink 명령어 구성
    # 'command' 방식: streamlink 직접 실행
    # 'module' 방식: python3 -m streamlink 실행
    if streamlink_method == 'command':
        streamlink_cmd = ['streamlink']
    else:
        streamlink_cmd = [sys.executable, '-m', 'streamlink']
    
    # ========================================================================
    # 2단계: 동영상 정보 가져오기
    # ========================================================================
    print_step(2, "동영상 정보 가져오는 중...")
    
    # streamlink로 스트림 정보 획득
    # -j 옵션: JSON 형식으로 출력
    # --stream-url: 실제 스트림 URL만 출력
    try:
        # 먼저 사용 가능한 품질 목록 확인
        result = subprocess.run(
            streamlink_cmd + ['--json', url],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # JSON 파싱하여 제목 추출
        import json
        info = json.loads(result.stdout)
        title = info.get('metadata', {}).get('title', 'Unknown')
        
        # 파일명에 사용할 수 없는 문자 제거
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        
        print(f"✅ 제목: {title}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 동영상 정보를 가져올 수 없습니다.")
        print(f"오류: {e}\n")
        return False
    except subprocess.TimeoutExpired:
        print("❌ 시간 초과: 네트워크 연결을 확인하세요.\n")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}\n")
        return False
    
    # ========================================================================
    # 3단계: 오디오 다운로드 및 변환
    # ========================================================================
    print_step(3, "오디오 다운로드 및 FLAC 변환 중...")
    
    # 출력 파일 경로
    output_file = os.path.join(DOWNLOAD_PATH, f"{safe_title}.flac")
    
    # streamlink + ffmpeg를 파이프로 연결하여 직접 변환
    # 이 방법은 중간 파일 생성 없이 바로 FLAC로 변환
    try:
        # streamlink 명령어 구성
        if streamlink_method == 'command':
            streamlink_part = f'streamlink "{url}" best -O'
        else:
            streamlink_part = f'{sys.executable} -m streamlink "{url}" best -O'
        
        # 전체 명령어: streamlink → ffmpeg 파이프
        command = f'{streamlink_part} | ffmpeg -i pipe:0 -vn -acodec flac "{output_file}" -y'
        
        print(f"실행: {streamlink_method} 방식으로 다운로드 중...\n")
        
        # shell=True로 파이프 명령 실행
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ 변환 완료\n")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 다운로드 실패")
        
        # 에러 메시지에서 유용한 정보 추출
        error_output = e.stderr if e.stderr else str(e)
        
        if 'No playable streams found' in error_output:
            print("오류: 재생 가능한 스트림을 찾을 수 없습니다.")
            print("해결책: URL을 확인하거나 다른 동영상을 시도하세요.\n")
        elif '403' in error_output or 'Forbidden' in error_output:
            print("오류: YouTube 접근이 차단되었습니다.")
            print("해결책: 몇 분 후 다시 시도하세요.\n")
        else:
            print(f"오류 상세:\n{error_output[:500]}\n")
        
        return False
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.\n")
        # 불완전한 파일 삭제
        if os.path.exists(output_file):
            os.remove(output_file)
        return False
    
    # ========================================================================
    # 4단계: 완료
    # ========================================================================
    print_step(4, "다운로드 완료!")
    
    # 파일 크기 확인
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        size_mb = file_size / (1024 * 1024)
        
        print_header("✅ 성공!")
        print(f"📝 파일명: {safe_title}.flac")
        print(f"💾 크기: {size_mb:.2f} MB")
        print(f"📁 위치: {output_file}\n")
        
        return True
    else:
        print("❌ 파일 생성 실패\n")
        return False


# ============================================================================
# 메인 프로그램
# ============================================================================

def main():
    """
    프로그램 메인 함수
    
    사용자로부터 URL을 입력받아 다운로드 실행
    """
    print_header("🎵 YouTube 음원 다운로더 (FLAC)")
    
    # URL 입력 받기
    if len(sys.argv) > 1:
        # 명령줄 인자로 URL 전달받음
        url = sys.argv[1]
    else:
        # 대화형 모드
        print("YouTube URL을 입력하세요:")
        print("(종료: Ctrl+C 또는 빈 줄)\n")
        url = input("URL: ").strip()
        
        if not url:
            print("\n프로그램을 종료합니다.\n")
            return
    
    # URL 검증
    if not ('youtube.com' in url or 'youtu.be' in url):
        print("\n❌ 올바른 YouTube URL이 아닙니다.")
        print("예시: https://www.youtube.com/watch?v=...\n")
        return
    
    # 플레이리스트 경고
    if 'list=' in url:
        print("\n⚠️  플레이리스트 URL이 감지되었습니다.")
        print("첫 번째 동영상만 다운로드됩니다.\n")
        response = input("계속하시겠습니까? (y/n): ").strip().lower()
        if response != 'y':
            print("\n취소되었습니다.\n")
            return
        
        # 플레이리스트 파라미터 제거
        url = url.split('&list=')[0].split('?list=')[0]
    
    # 다운로드 실행
    success = download_audio(url)
    
    if success:
        print("\n다른 동영상을 다운로드하려면 프로그램을 다시 실행하세요:")
        print(f"  python3 {sys.argv[0]}\n")


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
        sys.exit(1)
