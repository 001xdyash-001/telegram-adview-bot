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
            "User-Agent": "Mozilla/5.0 (Android)",
            "Accept": "*/*",
            "Content-Type": "application/json",
        })

    def login(self):
        r = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"mobile": self.mobile, "password": self.password},
            timeout=15
        )

        if r.status_code != 200:
            raise Exception("Login failed")

        token = r.json().get("token")
        if not token:
            raise Exception("Token missing")

        self.session.headers["Authorization"] = f"Bearer {token}"

    def run(self, progress_callback=None):
        self.login()

        r = self.session.get(
            f"{BASE_URL}/api/videos",
            params={"deviceId": self.device_id},
            timeout=15
        )

        videos = r.json().get("videos", []) if r.status_code == 200 else []

        if not videos:
            if progress_callback:
                progress_callback("❌ No videos available")
            return

        for video in videos:
            if self.stop_checker():
                return

            session = self.session.post(
                f"{BASE_URL}/api/videos/start",
                json={"videoId": video["id"], "deviceId": self.device_id},
                timeout=15
            ).json().get("sessionId")

            if not session:
                continue

            time.sleep(WAIT_SECONDS)

            self.session.post(
                f"{BASE_URL}/api/videos/complete",
                json={
                    "sessionId": session,
                    "deviceId": self.device_id,
                    "clientReportedSeconds": WAIT_SECONDS
                },
                timeout=15
            )
