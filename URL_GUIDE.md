# ⚠️ 중요: URL 사용 가이드

## ✅ 올바른 URL (단일 동영상)

```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
```

**예시:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
```

## ❌ 잘못된 URL (플레이리스트/라디오)

```
https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
https://www.youtube.com/watch?v=VIDEO_ID&start_radio=1
```

**이런 URL은 피하세요:**
```
❌ https://www.youtube.com/watch?v=6bO37ojnyTY&list=RD6bO37ojnyTY&start_radio=1
```

## 🔧 플레이리스트 URL을 단일 동영상 URL로 변환하는 방법

### 방법 1: URL 직접 수정
플레이리스트 URL에서 `&list=...` 부분을 삭제하세요.

**변환 전:**
```
https://www.youtube.com/watch?v=6bO37ojnyTY&list=RD6bO37ojnyTY&start_radio=1
```

**변환 후:**
```
https://www.youtube.com/watch?v=6bO37ojnyTY
```

### 방법 2: YouTube에서 직접 복사
1. YouTube에서 동영상 재생
2. 동영상 제목 아래 "공유" 버튼 클릭
3. 표시되는 짧은 URL 복사 (youtu.be/...)

## 📋 현재 발생한 오류 해결 방법

### YouTube Rate Limit 오류
```
ERROR: Video unavailable. The current session has been rate-limited by YouTube
```

**원인:**
- 너무 많은 동영상을 빠르게 다운로드하려고 시도
- 입력한 URL이 428개의 동영상이 포함된 플레이리스트였음

**해결 방법:**
1. **1시간 대기** - YouTube의 제한이 자동으로 해제됩니다
2. **단일 동영상 URL 사용** - 플레이리스트가 아닌 개별 동영상 URL 입력
3. **다른 네트워크 사용** - 가능하다면 다른 Wi-Fi나 모바일 핫스팟 사용

## 🛡️ 프로그램 개선 사항

최신 버전에서는 다음 기능이 추가되었습니다:

1. ✅ **플레이리스트 자동 차단** - `noplaylist: True` 옵션 추가
2. ✅ **URL 자동 정리** - 플레이리스트 파라미터 자동 제거
3. ✅ **Rate Limit 방지** - 요청 사이 1~3초 대기
4. ✅ **경고 메시지** - 플레이리스트 URL 입력 시 확인 메시지

## 💡 사용 팁

1. **단일 동영상만 다운로드**
   - 한 번에 하나의 동영상만 다운로드하세요
   - 여러 개가 필요하면 하나씩 순차적으로

2. **Rate Limit 피하기**
   - 연속으로 많은 동영상을 다운로드하지 마세요
   - 각 다운로드 사이에 30초~1분 정도 간격을 두세요

3. **올바른 URL 확인**
   - URL에 `&list=` 또는 `&start_radio=`가 있는지 확인
   - 있다면 해당 부분을 삭제하고 사용

## 🔍 문제가 계속되는 경우

1. **브라우저 캐시 삭제**
2. **프로그램 재시작**
3. **다른 시간대에 재시도**
4. **VPN 사용 고려** (선택사항)

## ℹ️ 추가 정보

- 이 프로그램은 **개인적 사용 목적**으로만 사용하세요
- 저작권이 있는 콘텐츠는 적법하게 사용하세요
- YouTube 이용약관을 준수하세요
