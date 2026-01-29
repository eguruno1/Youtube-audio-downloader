#!/usr/bin/env python3
"""
YouTube 음원 다운로더 (FLAC) - 간소화 버전
macOS 호환
"""

from flask import Flask, request, jsonify
import yt_dlp
import os
from pathlib import Path
import threading
import sys

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
    """다운로드 실행"""
    try:
        # URL 정리 (플레이리스트 제거)
        if '&list=' in url:
            url = url.split('&list=')[0]
            log("플레이리스트 파라미터 제거됨")
        
        log(f"URL: {url}")
        set_status('downloading', '준비 중...')
        
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'}],
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            log(f"제목: {title}")
            ydl.download([url])
        
        set_status('complete', f'완료: {title}.flac')
        
    except Exception as e:
        error = str(e)
        if 'rate-limited' in error.lower():
            set_status('error', 'YouTube 제한: 1시간 후 재시도')
        else:
            set_status('error', f'오류: {error[:100]}')


@app.route('/')
def index():
    """메인 페이지"""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YouTube 다운로더</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        input {{
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        button {{
            width: 100%;
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{ background: #45a049; }}
        button:disabled {{ background: #ccc; cursor: not-allowed; }}
        .status {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            background: #e3f2fd;
        }}
        .error {{ background: #ffebee; color: #c62828; }}
        .complete {{ background: #e8f5e9; color: #2e7d32; }}
        .log {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }}
        .info {{ color: #666; font-size: 14px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 YouTube 음원 다운로더</h1>
        <p class="info">저장 위치: {DOWNLOAD_PATH}</p>
        
        <input type="text" id="url" placeholder="YouTube URL 입력...">
        <button onclick="download()">다운로드</button>
        
        <div id="status" class="status">대기 중</div>
        <div class="log" id="log">준비됨</div>
    </div>
    
    <script>
        let interval;
        
        function download() {{
            const url = document.getElementById('url').value.trim();
            if (!url) {{
                alert('URL을 입력하세요');
                return;
            }}
            
            if (url.includes('list=')) {{
                if (!confirm('플레이리스트 URL입니다. 첫 번째 영상만 다운로드됩니다.')) {{
                    return;
                }}
            }}
            
            document.querySelector('button').disabled = true;
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
    
    return jsonify({{'status': 'started'}})


@app.route('/status')
def get_status():
    """상태 확인"""
    with status_lock:
        return jsonify(status.copy())


if __name__ == '__main__':
    print("=" * 60)
    print("YouTube 음원 다운로더 (FLAC)")
    print("=" * 60)
    print(f"\\n저장 위치: {DOWNLOAD_PATH}")
    print("\\n브라우저에서 열기: http://127.0.0.1:5000")
    print("종료: Ctrl+C\\n")
    print("=" * 60)
    
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
