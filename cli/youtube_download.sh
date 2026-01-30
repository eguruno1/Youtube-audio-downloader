#!/bin/bash
# YouTube 음원 다운로더 (FLAC) - 쉘 스크립트 버전
# 가장 단순하고 확실한 방법

# 다운로드 경로
DOWNLOAD_DIR="$HOME/Downloads/YouTube_Audio"
mkdir -p "$DOWNLOAD_DIR"

# 사용법 출력
if [ $# -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "🎵 YouTube 음원 다운로더 (FLAC)"
    echo "======================================================================"
    echo ""
    echo "사용법:"
    echo "  ./youtube_download.sh <YouTube_URL>"
    echo ""
    echo "예시:"
    echo "  ./youtube_download.sh https://www.youtube.com/watch?v=..."
    echo ""
    echo "======================================================================"
    echo ""
    exit 1
fi

URL="$1"

echo ""
echo "======================================================================"
echo "🎵 YouTube 음원 다운로더 (FLAC)"
echo "======================================================================"
echo ""
echo "📁 저장 위치: $DOWNLOAD_DIR"
echo "🔗 URL: $URL"
echo ""
echo "🚀 다운로드 시작..."
echo ""

# yt-dlp 실행
yt-dlp \
    --extract-audio \
    --audio-format flac \
    --audio-quality 0 \
    --output "$DOWNLOAD_DIR/%(title)s.%(ext)s" \
    --no-playlist \
    --progress \
    --cookies-from-browser chrome \
    "$URL"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ 다운로드 완료!"
    echo "📁 저장 위치: $DOWNLOAD_DIR"
    echo "======================================================================"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo "❌ 오류 발생"
    echo "======================================================================"
    echo ""
    echo "💡 해결 방법:"
    echo "1. Chrome에서 YouTube에 로그인하세요"
    echo "2. YouTube 동영상을 재생해보세요"
    echo "3. 다시 시도하세요"
    echo ""
    echo "또는 Safari 사용:"
    echo "  yt-dlp --cookies-from-browser safari \"$URL\""
    echo ""
fi
