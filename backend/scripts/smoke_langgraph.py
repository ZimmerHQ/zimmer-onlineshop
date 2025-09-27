import json, sys, time, requests
BASE = "http://localhost:8001"

def post(path, body):
    r = requests.post(f"{BASE}{path}", json=body, timeout=20)
    return r.status_code, r.text

def main():
    ok = True
    s, t = post("/api/chat", {"conversation_id":"t","message":"A0001"})
    print("1) code →", s, t[:160]); ok &= (s==200)
    time.sleep(0.5)
    s, t = post("/api/chat", {"conversation_id":"t","message":"همینو میخوام"})
    print("2) confirm →", s, t[:160]); ok &= (s==200)
    print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
