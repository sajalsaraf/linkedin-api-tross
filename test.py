"""Test script: stops server if running, starts it, hits the API.
Usage: python3 test.py <linkedin_username>
"""
import sys
import time
import subprocess
import signal
import httpx
import json


def kill_existing():
    result = subprocess.run(
        ["pgrep", "-f", "uvicorn main:app"],
        capture_output=True, text=True
    )
    pids = result.stdout.strip().split("\n")
    for pid in pids:
        if pid:
            subprocess.run(["kill", pid], capture_output=True)
    if any(p for p in pids if p):
        time.sleep(1)
        print("Stopped existing server.")


def start_server():
    proc = subprocess.Popen(
        ["/usr/local/bin/python3", "-m", "uvicorn", "main:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait for server to be ready
    for _ in range(15):
        try:
            r = httpx.get("http://localhost:8000/health", timeout=1)
            if r.status_code == 200:
                print("Server started.")
                return proc
        except Exception:
            pass
        time.sleep(0.5)
    print("Server failed to start.")
    proc.kill()
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test.py <linkedin_username>")
        sys.exit(1)

    profile_url = sys.argv[1]
    if not profile_url.startswith("http"):
        profile_url = f"https://www.linkedin.com/in/{profile_url}"

    kill_existing()
    proc = start_server()

    try:
        print(f"Fetching profile for: {profile_url}\n")
        resp = httpx.get(
            "http://localhost:8000/profile",
            params={"url": profile_url},
            timeout=30,
        )
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text or "(empty response)"
            print(f"Error {resp.status_code}: {detail}")
    finally:
        proc.send_signal(signal.SIGTERM)
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
