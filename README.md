# YouTube 음원 다운로더 (FLAC 고음질)

## 📋 프로그램 설명
YouTube 동영상에서 오디오만 추출하여 FLAC 고음질 형식으로 다운로드하는 GUI 프로그램입니다.

## 🔧 설치 방법

### 1단계: Python 설치 확인
```bash
python3 --version
```
Python 3.12 이상이 필요합니다.

### 2단계: 필수 라이브러리 설치
```bash
pip3 install -r requirements.txt
```

또는 개별 설치:
```bash
pip3 install yt-dlp
```

### 3단계: FFmpeg 설치 (필수!)

**Windows:**
1. https://github.com/BtbN/FFmpeg-Builds/releases 접속
2. `ffmpeg-master-latest-win64-gpl.zip` 다운로드
3. 압축 해제 후 `bin` 폴더의 경로를 시스템 환경변수 PATH에 추가

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**FFmpeg 설치 확인:**
```bash
ffmpeg -version
```

## 🚀 실행 방법

```bash
python youtube_audio_downloader.py
```

## 💡 사용 방법

1. 프로그램 실행
2. YouTube URL 입력 (예: https://www.youtube.com/watch?v=...)
3. (선택사항) 다운로드 경로 변경
4. "다운로드 시작" 버튼 클릭
5. 다운로드 완료 대기

## 📁 기본 다운로드 위치
- Windows : `C:\Users\사용자명\Downloads\YouTube_Audio` 
- macOS : `/Users/사용자명/Downloads/YouTube_Audio` 
- Linux : `/home/사용자명/Downloads/YouTube_Audio` 

## 🎵 출력 형식
- 파일 형식: FLAC (Free Lossless Audio Codec)
- 음질: 무손실 압축 (원본 품질 유지)
- 파일명: 동영상 제목.flac

## ⚠️ 주의사항
1. FFmpeg가 반드시 설치되어 있어야 합니다
2. 저작권이 있는 콘텐츠는 개인적 용도로만 사용하세요
3. 인터넷 연결이 필요합니다
4. FLAC 파일은 용량이 크므로 저장 공간을 확인하세요

## 🐛 문제 해결

**"FFmpeg not found" 오류:**
- FFmpeg가 설치되지 않았거나 PATH 설정이 안 됨
- 위의 FFmpeg 설치 과정을 다시 확인하세요

**"Invalid URL" 오류:**
- YouTube URL 형식이 올바른지 확인
- 예시: https://www.youtube.com/watch?v=XXXXXXXXXXX

**다운로드가 느린 경우:**
- 인터넷 연결 상태 확인
- YouTube 서버 상태에 따라 속도가 다를 수 있음

## 📚 Java 개발자를 위한 Python 참고사항

### Java vs Python 주요 차이점:

| Java | Python |
|------|--------|
| `System.out.println()` | `print()` |
| `String name = "test"` | `name = "test"` (타입 명시 불필요) |
| `public void method() {}` | `def method():` (들여쓰기로 블록 구분) |
| `try-catch-finally` | `try-except-finally` |
| `new Object()` | `Object()` (new 키워드 없음) |
| `this.variable` | `self.variable` |
| `import package.Class` | `import module` or `from module import Class` |

### 클래스 구조 비교:

**Java:**
```java
public class Example {
    private String name;
    
    public Example(String name) {
        this.name = name;
    }
    
    public void method() {
        // code
    }
}
```

**Python:**
```python
class Example:
    def __init__(self, name):  # 생성자
        self.name = name       # self는 Java의 this
    
    def method(self):
        # code
        pass
```

## 📝 라이선스
개인 사용 목적으로 자유롭게 사용 가능합니다.
