"""
YouTube 음원 다운로더 (FLAC 고음질) - 웹 버전
- 브라우저 기반 GUI (Flask 사용)
- macOS 호환성 문제 해결
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import threading
import time

# Flask 앱 생성
app = Flask(__name__)

# 전역 변수로 다운로드 상태 관리
download_status = {
    'status': 'ready',  # ready, downloading, converting, complete, error
    'message': 'YouTube URL을 입력하고 다운로드 버튼을 클릭하세요.',
    'progress': 0,
    'filename': '',
    'filepath': ''
}

# 기본 다운로드 경로
DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YouTube_Audio")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# HTML 템플릿 (파일로 분리하지 않고 하나의 파일에 포함)
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
            
            // 버튼 비활성화
            document.getElementById('download-btn').disabled = true;
            document.getElementById('progress-container').style.display = 'block';
            
            // 로그 초기화
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
                    updateStatus(data.status, data.message);
                    
                    // 로그 업데이트
                    const logElement = document.getElementById('log-content');
                    if (data.message) {
                        logElement.textContent += data.message + '\\n';
                        logElement.scrollTop = logElement.scrollHeight;
                    }
                    
                    // 완료 또는 에러 시 체크 중지
                    if (data.status === 'complete' || data.status === 'error') {
                        clearInterval(statusCheckInterval);
                        document.getElementById('download-btn').disabled = false;
                        
                        if (data.status === 'complete') {
                            document.getElementById('log-content').textContent += 
                                '\\n✓ 다운로드 완료!\\n파일명: ' + data.filename + '\\n';
                        }
                    }
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
    global download_status
    
    if d['status'] == 'downloading':
        download_status['status'] = 'downloading'
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        download_status['message'] = f"다운로드 중... {percent} (속도: {speed})"
        
    elif d['status'] == 'finished':
        download_status['status'] = 'converting'
        download_status['message'] = "다운로드 완료. FLAC 변환 중..."


def download_audio(url):
    """
    실제 다운로드 실행 함수 (백그라운드 스레드)
    Args:
        url: YouTube URL
    """
    global download_status
    
    try:
        download_status['status'] = 'downloading'
        download_status['message'] = '다운로드 준비 중...'
        
        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        # 다운로드 실행
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            
            download_status['message'] = f"제목: {video_title}"
            time.sleep(0.5)
            
            # 실제 다운로드
            ydl.download([url])
        
        # 완료 상태 업데이트
        download_status['status'] = 'complete'
        download_status['message'] = '✓ 다운로드 완료!'
        download_status['filename'] = f"{video_title}.flac"
        download_status['filepath'] = os.path.join(DOWNLOAD_PATH, f"{video_title}.flac")
        
    except Exception as e:
        download_status['status'] = 'error'
        download_status['message'] = f'오류 발생: {str(e)}'


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
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL이 필요합니다.'})
    
    # 다운로드 상태 초기화
    download_status = {
        'status': 'downloading',
        'message': '다운로드 시작...',
        'progress': 0,
        'filename': '',
        'filepath': ''
    }
    
    # 백그라운드 스레드에서 다운로드 실행
    thread = threading.Thread(target=download_audio, args=(url,), daemon=True)
    thread.start()
    
    return jsonify({'status': 'started', 'message': '다운로드가 시작되었습니다.'})


@app.route('/status')
def status():
    """다운로드 상태 확인 API"""
    return jsonify(download_status)


@app.route('/favicon.ico')
def favicon():
    """favicon 요청 처리 (404 오류 방지)"""
    return '', 204  # No Content


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
    
    # 브라우저 자동 실행
    import webbrowser
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    
    # Flask 서버 실행
    app.run(debug=False, port=5000)


if __name__ == "__main__":
    main()