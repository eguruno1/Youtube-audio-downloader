#!/usr/bin/env python3
"""
YouTube 음원 다운로더 (FLAC) - PyTube 버전
yt-dlp의 PO Token 문제 해결
"""

from flask import Flask, request, jsonify
from pytube import YouTube
from pydub import AudioSegment
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
TEMP_PATH = str(Path.home() / "Downloads" / "YouTube_Audio_Temp")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)


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


def sanitize_filename(filename):
    """파일명에서 특수문자 제거"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.strip()


def download_task(url):
    """다운로드 실행 - PyTube 사용"""
    temp_file = None
    flac_file = None
    
    try:
        # URL 정리 (플레이리스트 제거)
        if '&list=' in url or '?list=' in url:
            url = url.split('&list=')[0].split('?list=')[0]
            log("플레이리스트 파라미터 제거됨")
        
        log(f"URL: {url}")
        set_status('downloading', '동영상 정보 가져오는 중...')
        
        # PyTube로 YouTube 객체 생성
        yt = YouTube(url)
        
        # 동영상 정보
        title = sanitize_filename(yt.title)
        log(f"제목: {title}")
        log(f"길이: {yt.length}초")
        
        # 오디오 스트림 선택 (최고 품질)
        set_status('downloading', '최고 품질 오디오 스트림 선택 중...')
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            raise Exception("오디오 스트림을 찾을 수 없습니다.")
        
        log(f"선택된 비트레이트: {audio_stream.abr}")
        
        # 임시 파일로 다운로드
        set_status('downloading', '다운로드 중...')
        temp_file = audio_stream.download(
            output_path=TEMP_PATH,
            filename=f"{title}_temp.mp4"
        )
        log(f"다운로드 완료: {temp_file}")
        
        # FLAC로 변환
        set_status('converting', 'FLAC 고음질로 변환 중...')
        flac_file = os.path.join(DOWNLOAD_PATH, f"{title}.flac")
        
        # PyDub으로 오디오 변환
        audio = AudioSegment.from_file(temp_file)
        audio.export(flac_file, format="flac")
        
        log(f"FLAC 변환 완료")
        
        # 임시 파일 삭제
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            log("임시 파일 삭제됨")
        
        set_status('complete', f'완료: {title}.flac')
        log(f"저장 위치: {flac_file}")
        
    except Exception as e:
        error = str(e)
        
        # 임시 파일 정리
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        
        # 에러 메시지 처리
        if 'unavailable' in error.lower():
            set_status('error', '동영상을 사용할 수 없습니다. URL을 확인해주세요.')
        elif 'regex' in error.lower():
            set_status('error', 'URL 형식이 올바르지 않습니다.')
        elif 'age' in error.lower():
            set_status('error', '연령 제한 동영상입니다.')
        else:
            set_status('error', f'오류: {error[:200]}')
        
        print(f"[ERROR] {error}", flush=True)


@app.route('/')
def index():
    """메인 페이지"""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube 다운로더 (PyTube)</title>
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
            max-width: 600px;
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
            margin-bottom: 30px;
            font-size: 14px;
        }}
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
        <p class="subtitle">FLAC 고음질 형식 (PyTube 엔진)</p>
        
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
                    
                    // 진행률
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
    print("YouTube 음원 다운로더 (FLAC) - PyTube 버전")
    print("=" * 70)
    print(f"\n저장 위치: {DOWNLOAD_PATH}")
    print("임시 파일: {TEMP_PATH}")
    print("\n✅ PyTube 엔진 사용 (yt-dlp PO Token 문제 해결)")
    print("\n브라우저에서 열기: http://127.0.0.1:5000")
    print("종료: Ctrl+C\n")
    print("=" * 70)
    print()
    
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
