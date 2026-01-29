"""
YouTube 음원 다운로더 (FLAC 고음질)
- 유튜브 동영상에서 오디오만 추출하여 FLAC 형식으로 다운로드
- GUI 기반 프로그램 (Tkinter 사용)
"""

# =========================================================
# macOS 26 버전 오인식 문제 해결용 re-exec 처리 (중요)
# =========================================================
import os
import sys

if sys.platform == "darwin" and os.environ.get("SYSTEM_VERSION_COMPAT") != "0":
    os.environ["SYSTEM_VERSION_COMPAT"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)
    
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
import yt_dlp


class YouTubeAudioDownloader:
    """유튜브 음원 다운로더 메인 클래스"""
    
    def __init__(self, root):
        """
        생성자 - GUI 초기화
        Args:
            root: Tkinter 루트 윈도우
        """
        self.root = root
        self.root.title("YouTube 음원 다운로더 (FLAC)")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 기본 다운로드 경로 설정 (사용자의 다운로드 폴더)
        self.download_path = str(Path.home() / "Downloads" / "YouTube_Audio")
        
        # 다운로드 폴더가 없으면 생성
        os.makedirs(self.download_path, exist_ok=True)
        
        # GUI 구성요소 초기화
        self.setup_ui()
        
    def setup_ui(self):
        """GUI 레이아웃 설정"""
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 타이틀 라벨
        title_label = ttk.Label(
            main_frame, 
            text="YouTube 음원 다운로더 (FLAC 고음질)",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # URL 입력 라벨
        url_label = ttk.Label(main_frame, text="YouTube URL:", font=("Arial", 10))
        url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # URL 입력 필드 (자바의 TextField와 유사)
        self.url_entry = ttk.Entry(main_frame, width=50, font=("Arial", 10))
        self.url_entry.grid(row=2, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        # 다운로드 경로 라벨
        path_label = ttk.Label(main_frame, text="다운로드 경로:", font=("Arial", 10))
        path_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # 다운로드 경로 표시 필드
        self.path_entry = ttk.Entry(main_frame, width=40, font=("Arial", 9))
        self.path_entry.insert(0, self.download_path)
        self.path_entry.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 경로 변경 버튼
        path_button = ttk.Button(
            main_frame, 
            text="경로 변경", 
            command=self.change_download_path
        )
        path_button.grid(row=4, column=2, padx=5)
        
        # 다운로드 버튼
        self.download_button = ttk.Button(
            main_frame,
            text="다운로드 시작",
            command=self.start_download,
            style="Accent.TButton"
        )
        self.download_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 프로그레스 바 (다운로드 진행 상태 표시)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=550,
            mode="indeterminate"  # 무한 로딩 모드
        )
        self.progress_bar.grid(row=6, column=0, columnspan=3, pady=10)
        
        # 상태 메시지 라벨
        self.status_label = ttk.Label(
            main_frame,
            text="YouTube URL을 입력하고 다운로드 버튼을 클릭하세요.",
            font=("Arial", 9),
            foreground="gray"
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # 로그 텍스트 영역 (다운로드 진행 상황 표시)
        log_frame = ttk.LabelFrame(main_frame, text="다운로드 로그", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바가 있는 텍스트 위젯
        self.log_text = tk.Text(log_frame, height=8, width=70, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def change_download_path(self):
        """다운로드 경로 변경 기능"""
        # 폴더 선택 다이얼로그 표시
        new_path = filedialog.askdirectory(
            title="다운로드 폴더 선택",
            initialdir=self.download_path
        )
        
        if new_path:  # 사용자가 폴더를 선택한 경우
            self.download_path = new_path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.download_path)
            self.add_log(f"다운로드 경로 변경: {self.download_path}")
    
    def add_log(self, message):
        """
        로그 텍스트 영역에 메시지 추가
        Args:
            message: 표시할 메시지
        """
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)  # 자동 스크롤
        self.root.update_idletasks()  # UI 즉시 업데이트
        
    def update_status(self, message, color="black"):
        """
        상태 라벨 업데이트
        Args:
            message: 표시할 메시지
            color: 텍스트 색상
        """
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
        
    def validate_url(self, url):
        """
        YouTube URL 유효성 검사
        Args:
            url: 검사할 URL
        Returns:
            bool: 유효하면 True, 아니면 False
        """
        # 기본적인 YouTube URL 패턴 확인
        youtube_domains = ["youtube.com", "youtu.be", "m.youtube.com"]
        return any(domain in url for domain in youtube_domains)
    
    def progress_hook(self, d):
        """
        yt-dlp 다운로드 진행 상황 콜백 함수
        Args:
            d: 다운로드 진행 정보 딕셔너리
        """
        if d['status'] == 'downloading':
            # 다운로드 중일 때 로그 업데이트
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            self.update_status(f"다운로드 중... {percent} (속도: {speed})", "blue")
            
        elif d['status'] == 'finished':
            # 다운로드 완료 후 변환 시작
            self.add_log("다운로드 완료. FLAC 형식으로 변환 중...")
            self.update_status("FLAC 변환 중...", "orange")
    
    def download_audio(self):
        """실제 다운로드 실행 함수 (별도 스레드에서 실행)"""
        
        url = self.url_entry.get().strip()
        
        # URL 유효성 검사
        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력해주세요.")
            return
        
        if not self.validate_url(url):
            messagebox.showerror("오류", "올바른 YouTube URL이 아닙니다.")
            return
        
        try:
            # 다운로드 버튼 비활성화 (중복 클릭 방지)
            self.download_button.config(state="disabled")
            
            # 프로그레스 바 시작
            self.progress_bar.start(10)
            
            self.add_log("=" * 60)
            self.add_log(f"다운로드 시작: {url}")
            self.update_status("다운로드 준비 중...", "blue")
            
            # yt-dlp 옵션 설정
            ydl_opts = {
                # 오디오만 추출
                'format': 'bestaudio/best',
                
                # 출력 파일 경로 및 이름 형식
                # %(title)s: 동영상 제목, %(ext)s: 확장자
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                
                # FLAC 형식으로 변환 (고음질)
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',  # FFmpeg를 사용한 오디오 추출
                    'preferredcodec': 'flac',      # FLAC 코덱 사용
                }],
                
                # 진행 상황 콜백 함수 등록
                'progress_hooks': [self.progress_hook],
                
                # 콘솔 출력 비활성화 (GUI에서 로그로 표시)
                'quiet': True,
                'no_warnings': True,
            }
            
            # yt-dlp로 다운로드 실행
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 동영상 정보 가져오기
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                
                self.add_log(f"제목: {video_title}")
                self.add_log("FLAC 고음질로 다운로드 중...")
                
                # 실제 다운로드 시작
                ydl.download([url])
            
            # 다운로드 완료
            self.progress_bar.stop()
            self.add_log("✓ 다운로드 완료!")
            self.add_log(f"저장 위치: {self.download_path}")
            self.update_status("다운로드 완료!", "green")
            
            # 완료 메시지 표시
            messagebox.showinfo(
                "완료",
                f"다운로드가 완료되었습니다!\n\n"
                f"파일명: {video_title}.flac\n"
                f"저장 위치: {self.download_path}"
            )
            
        except Exception as e:
            # 에러 발생 시 처리
            self.progress_bar.stop()
            error_message = f"오류 발생: {str(e)}"
            self.add_log(f"✗ {error_message}")
            self.update_status("다운로드 실패", "red")
            messagebox.showerror("오류", error_message)
            
        finally:
            # 항상 실행되는 코드 (자바의 finally와 동일)
            self.download_button.config(state="normal")  # 버튼 다시 활성화
            self.progress_bar.stop()
    
    def start_download(self):
        """
        다운로드 시작 버튼 클릭 시 호출
        별도 스레드에서 다운로드를 실행하여 GUI가 멈추지 않도록 함
        (자바의 SwingWorker와 유사한 개념)
        """
        download_thread = threading.Thread(target=self.download_audio, daemon=True)
        download_thread.start()


def main():
    """프로그램 진입점 (자바의 main 메서드와 동일)"""
    
    # Tkinter 루트 윈도우 생성
    root = tk.Tk()
    
    # 애플리케이션 인스턴스 생성
    app = YouTubeAudioDownloader(root)
    
    # GUI 이벤트 루프 시작 (윈도우가 닫힐 때까지 실행)
    root.mainloop()


# 스크립트가 직접 실행될 때만 main() 호출
# (다른 파일에서 import 될 때는 실행 안 됨)
if __name__ == "__main__":
    main()
