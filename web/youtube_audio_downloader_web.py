"""
YouTube 음원 다운로더 (FLAC 고음질) - 웹 버전
- 브라우저 기반 GUI (Flask 사용)
- macOS 호환성 문제 해결
- 디버그 로그 추가
"""

from flask import Flask, render_template_string, request, jsonify
import yt_dlp
import os
from pathlib import Path
import threading
import time
import sys

# Flask 앱 생성
app = Flask(__name__)

# 전역 변수로 다운로드 상태 관리
download_status = {
    'status': 'ready',  # ready, downloading, converting, complete, error
    'message': 'YouTube URL을 입력하고 다운로드 버튼을 클릭하세요.',
    'progress': 0,
    'filename': '',
    'filepath': '',
    'logs': []  # 로그 메시지 배열
}

# 상태 업데이트를 위한 락 (thread-safe)
status_lock = threading.Lock()

# 기본 다운로드 경로
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def log_message(message):
    """
    로그 메시지 추가 (콘솔과 상태에 모두 기록)
    Args:
        message: 로그 메시지
    """
    print(f"[LOG] {message}", flush=True)  # 콘솔 출력
    with status_lock:
        download_status['logs'].append(message)
        download_status['message'] = message


def update_status(status, message):
    """
    다운로드 상태 업데이트 (thread-safe)
    Args:
        status: 상태 값
        message: 상태 메시지
    """
    with status_lock:
        download_status['status'] = status
        download_status['message'] = message
        download_status['logs'].append(message)
    print(f"[STATUS] {status}: {message}", flush=True)


# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube 음원 다운로더 (FLAC)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
            font-size: 14px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .status-message {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
        }
        
        .status-ready {
            background: #f0f0f0;
            color: #666;
        }
        
        .status-downloading {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .status-converting {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .status-complete {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .status-error {
            background: #ffebee;
            color: #c62828;
        }
        
        .log-container {
            margin-top: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            padding: 15px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .log-title {
            font-weight: 600;
            color: #555;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .log-content {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            color: #333;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .path-info {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 12px;
            border-radius: 4px;
            margin-top: 15px;
            font-size: 13px;
            color: #555;
        }
        
        .path-info strong {
            color: #e65100;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 YouTube 음원 다운로더</h1>
        <p class="subtitle">FLAC 고음질 형식으로 다운로드</p>
        
        <div class="input-group">
            <label for="youtube-url">YouTube URL</label>
            <input 
                type="text" 
                id="youtube-url" 
                placeholder="https://www.youtube.com/watch?v=..."
                value=""
            >
        </div>
        
        <button class="btn" id="download-btn" onclick="startDownload()">
            다운로드 시작
        </button>
        
        <div class="progress-container" id="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>
        
        <div class="status-message status-ready" id="status-message">
            YouTube URL을 입력하고 다운로드 버튼을 클릭하세요.
        </div>
        
        <div class="path-info">
            <strong>저장 위치:</strong> {{ download_path }}
        </div>
        
        <div class="log-container">
            <div class="log-title">다운로드 로그</div>
            <div class="log-content" id="log-content">대기 중...</div>
        </div>
    </div>
    
    <script>
        let statusCheckInterval;
        let lastLogLength = 0;
        
        // 다운로드 시작 함수
        function startDownload() {
            const url = document.getElementById('youtube-url').value.trim();
            
            if (!url) {
                alert('YouTube URL을 입력해주세요.');
                return;
            }
            
            if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
                alert('올바른 YouTube URL이 아닙니다.');
                return;
            }
            
            // 플레이리스트 URL 경고
            if (url.includes('list=') || url.includes('start_radio=')) {
                const confirmMsg = '플레이리스트 URL이 감지되었습니다.\\n' +
                                  '첫 번째 동영상만 다운로드됩니다.\\n\\n' +
                                  '계속하시겠습니까?';
                if (!confirm(confirmMsg)) {
                    return;
                }
            }
            
            // 버튼 비활성화
            document.getElementById('download-btn').disabled = true;
            document.getElementById('progress-container').style.display = 'block';
            
            // 로그 초기화
            lastLogLength = 0;
            document.getElementById('log-content').textContent = '다운로드 시작...\\n';
            
            // 서버에 다운로드 요청
            fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Download started:', data);
                if (data.status === 'started') {
                    // 상태 체크 시작
                    startStatusCheck();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                updateStatus('error', '다운로드 요청 실패');
                document.getElementById('download-btn').disabled = false;
            });
        }
        
        // 상태 체크 시작
        function startStatusCheck() {
            statusCheckInterval = setInterval(checkStatus, 500);  // 0.5초마다 체크
        }
        
        // 상태 체크 함수
        function checkStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    console.log('Status:', data);
                    updateStatus(data.status, data.message);
                    
                    // 로그 업데이트 (새로운 로그만 추가)
                    if (data.logs && data.logs.length > lastLogLength) {
                        const logElement = document.getElementById('log-content');
                        const newLogs = data.logs.slice(lastLogLength);
                        newLogs.forEach(log => {
                            logElement.textContent += log + '\\n';
                        });
                        logElement.scrollTop = logElement.scrollHeight;
                        lastLogLength = data.logs.length;
                    }
                    
                    // 완료 또는 에러 시 체크 중지
                    if (data.status === 'complete' || data.status === 'error') {
                        clearInterval(statusCheckInterval);
                        document.getElementById('download-btn').disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Status check error:', error);
                });
        }
        
        // 상태 업데이트 함수
        function updateStatus(status, message) {
            const statusElement = document.getElementById('status-message');
            const progressFill = document.getElementById('progress-fill');
            
            statusElement.className = 'status-message status-' + status;
            statusElement.textContent = message;
            
            // 진행률 업데이트
            if (status === 'downloading') {
                progressFill.style.width = '50%';
            } else if (status === 'converting') {
                progressFill.style.width = '80%';
            } else if (status === 'complete') {
                progressFill.style.width = '100%';
            }
        }
    </script>
</body>
</html>
"""


def progress_hook(d):
    """
    yt-dlp 다운로드 진행 상황 콜백
    Args:
        d: 다운로드 진행 정보
    """
    try:
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            message = f"다운로드 중... {percent} (속도: {speed})"
            update_status('downloading', message)
            
        elif d['status'] == 'finished':
            update_status('converting', "다운로드 완료. FLAC 변환 중...")
            
    except Exception as e:
        print(f"[ERROR] progress_hook: {e}", flush=True)


def download_audio(url):
    """
    실제 다운로드 실행 함수 (백그라운드 스레드)
    Args:
        url: YouTube URL
    """
    try:
        # 플레이리스트 URL 체크 및 정리
        if 'list=' in url or '&start_radio=' in url:
            log_message("⚠️ 플레이리스트 URL이 감지되었습니다.")
            log_message("첫 번째 동영상만 다운로드합니다.")
            # URL에서 플레이리스트 파라미터 제거
            if '&list=' in url:
                url = url.split('&list=')[0]
            elif '?list=' in url:
                url = url.split('?list=')[0]
        
        log_message("=" * 60)
        log_message(f"다운로드 URL: {url}")
        update_status('downloading', '다운로드 준비 중...')
        
        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'progress_hooks': [progress_hook],
            'quiet': False,  # 디버그를 위해 출력 활성화
            'no_warnings': False,
            
            # 플레이리스트 차단 - 단일 동영상만 다운로드
            'noplaylist': True,  # 플레이리스트 무시
            'extract_flat': False,  # 전체 정보 추출
            
            # Rate Limit 방지
            'sleep_interval': 1,  # 요청 사이 1초 대기
            'max_sleep_interval': 3,  # 최대 3초 대기
        }
        
        log_message("yt-dlp 초기화 중...")
        
        # 다운로드 실행
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log_message("동영상 정보 가져오는 중...")
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            
            log_message(f"제목: {video_title}")
            log_message("FLAC 고음질로 다운로드 시작...")
            
            # 실제 다운로드
            ydl.download([url])
        
        # 완료
        filename = f"{video_title}.flac"
        filepath = os.path.join(DOWNLOAD_PATH, filename)
        
        with status_lock:
            download_status['status'] = 'complete'
            download_status['message'] = '✓ 다운로드 완료!'
            download_status['filename'] = filename
            download_status['filepath'] = filepath
            download_status['logs'].append('=' * 60)
            download_status['logs'].append('✓ 다운로드 완료!')
            download_status['logs'].append(f'파일명: {filename}')
            download_status['logs'].append(f'저장 위치: {DOWNLOAD_PATH}')
        
        log_message(f"완료: {filename}")
        
    except Exception as e:
        error_str = str(e)
        
        # Rate Limit 에러 처리
        if 'rate-limited' in error_str.lower():
            error_message = "YouTube 접근 제한: 너무 많은 요청으로 인해 일시적으로 차단되었습니다. 1시간 후 다시 시도해주세요."
        elif 'unavailable' in error_str.lower():
            error_message = "동영상을 사용할 수 없습니다. URL을 확인하거나 다른 동영상을 시도해주세요."
        elif 'playlist' in error_str.lower():
            error_message = "플레이리스트는 지원하지 않습니다. 단일 동영상 URL을 입력해주세요."
        else:
            error_message = f"오류 발생: {error_str}"
        
        log_message(f"[ERROR] {error_message}")
        update_status('error', error_message)
        print(f"[EXCEPTION] {e}", flush=True)
        import traceback
        traceback.print_exc()


@app.route('/')
def index():
    """메인 페이지"""
    return render_template_string(HTML_TEMPLATE, download_path=DOWNLOAD_PATH)


@app.route('/download', methods=['POST'])
def download():
    """다운로드 시작 API"""
    global download_status
    
    data = request.get_json()
    url = data.get('url', '')
    
    print(f"[API] Download request: {url}", flush=True)
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL이 필요합니다.'})
    
    # 다운로드 상태 초기화
    with status_lock:
        download_status = {
            'status': 'downloading',
            'message': '다운로드 시작...',
            'progress': 0,
            'filename': '',
            'filepath': '',
            'logs': ['다운로드 요청을 받았습니다.']
        }
    
    # 백그라운드 스레드에서 다운로드 실행
    thread = threading.Thread(target=download_audio, args=(url,), daemon=True)
    thread.start()
    
    print("[API] Download thread started", flush=True)
    
    return jsonify({'status': 'started', 'message': '다운로드가 시작되었습니다.'})


@app.route('/status')
def status():
    """다운로드 상태 확인 API"""
    with status_lock:
        status_copy = download_status.copy()
    return jsonify(status_copy)


@app.route('/favicon.ico')
def favicon():
    """favicon 요청 처리 (404 오류 방지)"""
    return '', 204


def main():
    """프로그램 진입점"""
    print("=" * 60)
    print("YouTube 음원 다운로더 (FLAC) - 웹 버전")
    print("=" * 60)
    print(f"\n다운로드 저장 위치: {DOWNLOAD_PATH}\n")
    print("브라우저가 자동으로 열립니다...")
    print("또는 아래 주소를 직접 열어주세요:")
    print("\n  👉 http://127.0.0.1:5000\n")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    print("\n[DEBUG MODE] 상세 로그가 출력됩니다.\n")
    sys.stdout.flush()
    
    # 브라우저 자동 실행
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    
    # Flask 서버 실행
    app.run(debug=False, port=5000, threaded=True)


if __name__ == "__main__":
    main()