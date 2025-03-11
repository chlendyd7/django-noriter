# locust -f test\uvicorn_locust.py --host=http://localhost:8000
from locust import HttpUser, task, between
import json

class SSEUser(HttpUser):
    host = "http://127.0.0.1:8000"  # Django 서버의 호스트
    wait_time = between(1, 5)

    @task
    def connect_and_receive(self):
        with self.client.get("/asyc/connect/", stream=True) as response:
            if response.status_code == 200:
                print("SSE 연결 성공")
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8').strip().split("data: ")[1])
                        print(f"수신된 데이터: {data}")
            else:
                print("SSE 연결 실패")
