#!/usr/bin/env python3
"""
YouTube 음원 다운로더 (FLAC) - 최종 안정 버전
yt-dlp + 브라우저 쿠키 방식 (PO Token 문제 완전 해결)
"""

from flask import Flask, request, jsonify
import yt_dlp
import os
from pathlib import Path
import threading
import sys
import subprocess

app = Flask(__name__)

# 다운로드 상태
status = {'state': 'ready', 'message': '대기 중', 'logs': []}
status_lock = threading.Lock()

# 다운로드 경로
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def log(msg):
    """로그 추가"""
    print(f"[LOG] {msg}", flush=True)
    with status_lock:
        status['logs'].append(msg)
        status['message'] = msg


def set_status(state, msg):
    """상태 업데이트"""
    with status_lock:
        status['state'] = state
        status['message'] = msg
        status['logs'].append(msg)
    print(f"[STATUS] {state}: {msg}", flush=True)


def progress_hook(d):
    """다운로드 진행 상황"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A').strip()
        set_status('downloading', f"다운로드 중 {percent}")
    elif d['status'] == 'finished':
        set_status('converting', "FLAC 변환 중...")


def download_task(url):
    """다운로드 실행 - yt-dlp with cookies"""
    try:
        # URL 정리
        if '&list=' in url or '?list=' in url:
            url = url.split('&list=')[0].split('?list=')[0]
            log("플레이리스트 파라미터 제거됨")
        
        log(f"URL: {url}")
        set_status('downloading', '준비 중...')
        
        # yt-dlp 옵션 (브라우저 쿠키 사용 - 핵심!)
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'quiet': True,
            
            # 핵심: Chrome 브라우저 쿠키 사용
            'cookiesfrombrowser': ('chrome',),
            
            # 백업 옵션
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['dash', 'hls'],
                }
            },
        }
        
        log("yt-dlp 초기화 중 (Chrome 쿠키 사용)...")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            log("동영상 정보 가져오는 중...")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            log(f"제목: {title}")
            log("다운로드 시작...")
            ydl.download([url])
        
        set_status('complete', f'완료: {title}.flac')
        log(f"저장 위치: {DOWNLOAD_PATH}/{title}.flac")
        
    except Exception as e:
        error = str(e)
        
        # 쿠키 관련 에러 체크
        if 'cookie' in error.lower() or 'browser' in error.lower():
            set_status('error', 'Chrome 브라우저를 찾을 수 없습니다. Safari를 시도합니다...')
            # Safari로 재시도
            try_safari(url)
        elif 'rate-limited' in error.lower():
            set_status('error', 'YouTube 제한: 1시간 후 재시도')
        elif '403' in error or 'Forbidden' in error:
            set_status('error', 'YouTube 접근 거부: Chrome에서 YouTube에 로그인 후 재시도')
        elif '400' in error or 'Bad Request' in error:
            set_status('error', 'YouTube API 오류: Safari 브라우저 쿠키로 재시도 중...')
            try_safari(url)
        else:
            set_status('error', f'오류: {error[:200]}')
        
        print(f"[ERROR] {error}", flush=True)


def try_safari(url):
    """Safari 쿠키로 재시도"""
    try:
        log("Safari 브라우저 쿠키로 재시도...")
        
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'quiet': True,
            'cookiesfrombrowser': ('safari',),  # Safari 쿠키
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            log(f"제목: {title}")
            ydl.download([url])
        
        set_status('complete', f'완료: {title}.flac (Safari 쿠키 사용)')
        
    except Exception as e2:
        set_status('error', f'Safari도 실패: YouTube에 로그인 필요')
        log(f"Safari 오류: {str(e2)[:100]}")


@app.route('/')
def index():
    """메인 페이지"""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube 다운로더 (최종 안정 버전)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 650px;
            width: 100%;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .notice {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 13px;
            line-height: 1.6;
        }}
        .notice strong {{ color: #1565C0; }}
        .notice ul {{ margin: 10px 0 0 20px; }}
        .info {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #555;
        }}
        .info strong {{ color: #e65100; }}
        input {{
            width: 100%;
            padding: 12px 15px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        button {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        button:hover {{ transform: translateY(-2px); }}
        button:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}
        .progress {{
            margin: 20px 0;
            display: none;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .status {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 14px;
        }}
        .status.ready {{ background: #f0f0f0; color: #666; }}
        .status.downloading {{ background: #e3f2fd; color: #1976d2; }}
        .status.converting {{ background: #fff3e0; color: #f57c00; }}
        .status.complete {{ background: #e8f5e9; color: #2e7d32; }}
        .status.error {{ background: #ffebee; color: #c62828; }}
        .log {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            line-height: 1.6;
        }}
        .log-title {{
            font-weight: 600;
            color: #555;
            margin-bottom: 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 YouTube 음원 다운로더</h1>
        <p class="subtitle">FLAC 고음질 (브라우저 쿠키 방식)</p>
        
        <div class="notice">
            <strong>⚠️ 중요: 처음 사용 전 필수 설정</strong>
            <ul>
                <li>Chrome 또는 Safari 브라우저에서 <strong>YouTube에 로그인</strong>하세요</li>
                <li>로그인 후 아무 동영상이나 재생해보세요</li>
                <li>그 다음 이 프로그램을 사용하세요</li>
            </ul>
        </div>
        
        <div class="info">
            <strong>저장 위치:</strong> {DOWNLOAD_PATH}
        </div>
        
        <input type="text" id="url" placeholder="YouTube URL 입력 (예: https://www.youtube.com/watch?v=...)">
        <button onclick="download()">다운로드</button>
        
        <div id="progress" class="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>
        
        <div id="status" class="status ready">대기 중</div>
        
        <div>
            <div class="log-title">다운로드 로그</div>
            <div class="log" id="log">준비됨</div>
        </div>
    </div>
    
    <script>
        let interval;
        
        function download() {{
            const url = document.getElementById('url').value.trim();
            if (!url) {{
                alert('YouTube URL을 입력하세요');
                return;
            }}
            
            if (!url.includes('youtube.com') && !url.includes('youtu.be')) {{
                alert('올바른 YouTube URL이 아닙니다.');
                return;
            }}
            
            if (url.includes('list=')) {{
                if (!confirm('플레이리스트 URL입니다. 첫 번째 영상만 다운로드됩니다.\\n계속하시겠습니까?')) {{
                    return;
                }}
            }}
            
            document.querySelector('button').disabled = true;
            document.getElementById('progress').style.display = 'block';
            document.getElementById('log').textContent = '시작...\\n';
            
            fetch('/download', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{url: url}})
            }});
            
            interval = setInterval(checkStatus, 500);
        }}
        
        function checkStatus() {{
            fetch('/status')
                .then(r => r.json())
                .then(data => {{
                    const statusDiv = document.getElementById('status');
                    statusDiv.textContent = data.message;
                    statusDiv.className = 'status ' + data.state;
                    
                    const log = document.getElementById('log');
                    log.textContent = data.logs.join('\\n');
                    log.scrollTop = log.scrollHeight;
                    
                    const progressFill = document.getElementById('progress-fill');
                    if (data.state === 'downloading') {{
                        progressFill.style.width = '50%';
                    }} else if (data.state === 'converting') {{
                        progressFill.style.width = '80%';
                    }} else if (data.state === 'complete') {{
                        progressFill.style.width = '100%';
                    }}
                    
                    if (data.state === 'complete' || data.state === 'error') {{
                        clearInterval(interval);
                        document.querySelector('button').disabled = false;
                    }}
                }});
        }}
    </script>
</body>
</html>'''
    return html


@app.route('/download', methods=['POST'])
def download():
    """다운로드 시작"""
    data = request.get_json()
    url = data.get('url', '')
    
    with status_lock:
        status['state'] = 'downloading'
        status['message'] = '시작...'
        status['logs'] = ['다운로드 요청']
    
    thread = threading.Thread(target=download_task, args=(url,), daemon=True)
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/status')
def get_status():
    """상태 확인"""
    with status_lock:
        return jsonify(status.copy())


if __name__ == '__main__':
    print("=" * 70)
    print("YouTube 음원 다운로더 (FLAC) - 최종 안정 버전")
    print("=" * 70)
    print(f"\n저장 위치: {DOWNLOAD_PATH}")
    print("\n✅ yt-dlp + 브라우저 쿠키 방식 (PO Token 문제 해결)")
    print("\n⚠️  중요: 사용 전 필수 설정")
    print("   1. Chrome 또는 Safari에서 YouTube에 로그인")
    print("   2. 아무 동영상이나 재생")
    print("   3. 이 프로그램 사용")
    print("\n브라우저에서 열기: http://127.0.0.1:5000")
    print("종료: Ctrl+C\n")
    print("=" * 70)
    print()
    
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
