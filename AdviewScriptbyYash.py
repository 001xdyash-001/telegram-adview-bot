import time
import uuid
import requests

BASE_URL = "https://adview.in"
WAIT_SECONDS = 1


class AdViewBot:
    def __init__(self, mobile, password, stop_checker):
        self.mobile = mobile
        self.password = password
        self.stop_checker = stop_checker
        self.session = requests.Session()
        self.device_id = str(uuid.uuid4())

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "*/*",
            "Content-Type": "application/json",
        })

    # ---------- LOGIN ----------
    def login(self):
        r = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "mobile": self.mobile,
                "password": self.password
            }
        )

        if r.status_code != 200:
            raise Exception("Login failed")

        token = r.json().get("token")
        if not token:
            raise Exception("Token not received")

        self.session.headers["Authorization"] = f"Bearer {token}"

    # ---------- GET VIDEOS ----------
    def get_videos(self):
        r = self.session.get(
            f"{BASE_URL}/api/videos",
            params={"deviceId": self.device_id}
        )

        if r.status_code != 200:
            return []

        return r.json().get("videos", [])

    # ---------- START VIDEO ----------
    def start_video(self, video_id):
        r = self.session.post(
            f"{BASE_URL}/api/videos/start",
            json={
                "videoId": video_id,
                "deviceId": self.device_id
            }
        )
        return r.json().get("sessionId")

    # ---------- COMPLETE VIDEO ----------
    def complete_video(self, session_id):
        r = self.session.post(
            f"{BASE_URL}/api/videos/complete",
            json={
                "sessionId": session_id,
                "deviceId": self.device_id,
                "clientReportedSeconds": WAIT_SECONDS
            }
        )
        return r.json()

    # ---------- MAIN RUN ----------
    def run(self, progress_callback=None):
        self.login()
        videos = self.get_videos()

        if not videos:
            if progress_callback:
                progress_callback("❌ No videos found")
            return

        for index, video in enumerate(videos, start=1):

            # 🛑 cancel check
            if self.stop_checker():
                if progress_callback:
                    progress_callback("🛑 Process stopped by user")
                return

            title = video.get("title", "Video")

            if progress_callback:
                progress_callback(f"▶ [{index}/{len(videos)}] {title}")

            session_id = self.start_video(video.get("id"))
            if not session_id:
                if progress_callback:
                    progress_callback("❌ Failed to start video")
                continue

            time.sleep(WAIT_SECONDS)

            result = self.complete_video(session_id)

            if result.get("success"):
                coins = result.get("coinsEarned", 0)
                balance = result.get("newBalance", 0)

                if progress_callback:
                    progress_callback(
                        f"✅ +{coins} coins\n"
                        f"💰 Balance: {balance}"
                    )
            else:
                if progress_callback:
                    progress_callback("❌ Video failed")
