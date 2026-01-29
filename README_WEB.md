# YouTube 음원 다운로더 (웹 버전) - macOS 호환

## 🎯 변경 사항
Tkinter GUI 대신 **웹 브라우저 기반 GUI**로 변경하여 macOS 호환성 문제를 해결했습니다.

## 🚀 빠른 시작

### 1단계: Flask 설치
```bash
pip3 install flask
```

또는 전체 라이브러리 설치:
```bash
pip3 install -r requirements.txt
```

### 2단계: 프로그램 실행
```bash
python3 youtube_audio_downloader_web.py
```

### 3단계: 자동으로 브라우저가 열립니다
- 자동으로 열리지 않으면 직접 접속: http://127.0.0.1:5000

## 💡 사용 방법

1. 브라우저에서 프로그램이 열림
2. YouTube URL 입력
3. "다운로드 시작" 버튼 클릭
4. 실시간 진행 상황 확인
5. 다운로드 완료!

## 📁 저장 위치
`/Users/사용자명/Downloads/YouTube_Audio`

## ✅ 장점

### Tkinter 버전 (이전)
- ❌ macOS 버전 호환성 문제
- ❌ "macOS 26 required" 오류 발생

### 웹 버전 (현재)
- ✅ 모든 macOS 버전에서 작동
- ✅ 브라우저만 있으면 실행 가능
- ✅ 깔끔한 UI
- ✅ 실시간 진행 상황 표시
- ✅ 모바일 브라우저에서도 사용 가능

## 🛠 기술 스택

- **Python 3.9+**
- **Flask**: 웹 서버 프레임워크
- **yt-dlp**: YouTube 다운로드
- **FFmpeg**: 오디오 변환

## 📝 주요 기능

1. **실시간 진행 상황**: 다운로드 속도, 진행률 표시
2. **자동 FLAC 변환**: 고음질 무손실 형식
3. **로그 표시**: 다운로드 과정 실시간 확인
4. **에러 처리**: 오류 발생 시 명확한 메시지

## 🔧 문제 해결

### 포트 5000이 사용 중인 경우
프로그램을 수정하여 다른 포트 사용:
```python
# 파일 마지막 부분에서 포트 변경
app.run(debug=False, port=8080)  # 5000 → 8080
```

### 브라우저가 자동으로 열리지 않는 경우
수동으로 접속:
```
http://127.0.0.1:5000
```

### 종료 방법
터미널에서 `Ctrl + C` 누르기

## 🆚 Tkinter vs 웹 버전 비교

| 특징 | Tkinter | 웹 버전 |
|------|---------|---------|
| macOS 호환성 | ❌ 버전 제한 | ✅ 모든 버전 |
| 설치 복잡도 | 간단 | Flask 추가 필요 |
| UI 품질 | 기본적 | 모던하고 깔끔 |
| 원격 사용 | 불가능 | 가능 (네트워크) |
| 반응성 | 좋음 | 매우 좋음 |

## 💻 Java 개발자를 위한 비교

### Flask (Python) vs Spring Boot (Java)

**Flask (Python):**
```python
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    return jsonify({'status': 'ok'})
```

**Spring Boot (Java):**
```java
@GetMapping("/")
public String index() {
    return "index";
}

@PostMapping("/download")
@ResponseBody
public Map<String, String> download(@RequestBody Map data) {
    return Map.of("status", "ok");
}
```

Flask는 Spring Boot보다 훨씬 간단하고 빠르게 시작할 수 있습니다!

## 📌 참고사항

- 프로그램 실행 중 터미널을 닫으면 웹 서버도 종료됩니다
- 여러 개의 다운로드를 동시에 실행하면 충돌할 수 있습니다 (순차적으로 진행하세요)
- FLAC 파일은 용량이 크므로 저장 공간을 확인하세요

## 🎉 완료!

이제 macOS에서 문제없이 작동합니다. 즐거운 음악 다운로드 되세요! 🎵
