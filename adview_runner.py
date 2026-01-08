import requests
import time

BASE_URL = "https://adview.in"

def run_adview(mobile, password):
    try:
        s = requests.Session()

        # LOGIN
        r = s.post(
            f"{BASE_URL}/api/auth/login",
            json={"mobile": mobile, "password": password},
            timeout=15
        )
        if r.status_code != 200:
            return "❌ Login failed"

        token = r.json().get("token")
        if not token:
            return "❌ Token not received"

        s.headers["Authorization"] = f"Bearer {token}"

        # GET VIDEOS
        r = s.get(f"{BASE_URL}/api/videos", timeout=15)
        videos = r.json().get("videos", [])

        if not videos:
            return "⚠️ No videos available right now"

        # WATCH VIDEOS
        count = 0
        for v in videos:
            sid = s.post(
                f"{BASE_URL}/api/videos/start",
                json={"videoId": v["id"]},
                timeout=10
            ).json().get("sessionId")

            if not sid:
                continue

            time.sleep(2)

            s.post(
                f"{BASE_URL}/api/videos/complete",
                json={"sessionId": sid, "clientReportedSeconds": 2},
                timeout=10
            )
            count += 1

        return f"✅ Session Finished | Videos watched: {count}"

    except Exception as e:
        return f"❌ Error: {e}"
