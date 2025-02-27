import requests
import time
import threading
from memory_profiler import profile
import psutil
import os

def get_memory_usage():
    """현재 프로세스의 메모리 사용량을 MB 단위로 반환"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

class SSEClient(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.daemon = True

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            for line in response.iter_lines():
                if line:
                    continue
        except Exception as e:
            print(f"클라이언트 에러: {e}")

@profile
def test_sse_memory(base_url, num_clients):
    """SSE 클라이언트 연결 테스트"""
    clients = []
    initial_memory = get_memory_usage()
    print(f"초기 메모리 사용량: {initial_memory:.2f} MB")

    # 클라이언트 연결
    for i in range(num_clients):
        client = SSEClient(f"{base_url}/asyc/")
        client.start()
        clients.append(client)
        
        if (i + 1) % 10 == 0:
            time.sleep(1)  # 서버 부하 방지
            current_memory = get_memory_usage()
            print(f"클라이언트 {i+1}개 연결 후 메모리: {current_memory:.2f} MB")
            print(f"메모리 증가량: {current_memory - initial_memory:.2f} MB")

    # 테스트 메시지 전송
    time.sleep(2)
    requests.post(f"{base_url}/send-message/", json={"message": "테스트 메시지"})

    # 모니터링 시간
    time.sleep(10)
    final_memory = get_memory_usage()
    print(f"\n최종 메모리 사용량: {final_memory:.2f} MB")
    print(f"총 메모리 증가량: {final_memory - initial_memory:.2f} MB")

if __name__ == "__main__":
    # 동기식 서버 테스트
    print("=== 동기식 서버 테스트 ===")
    test_sse_memory("http://localhost:8000", 50)
    
    time.sleep(5)
    
    # 비동기식 서버 테스트
    print("\n=== 비동기식 서버 테스트 ===")
    test_sse_memory("http://localhost:8001", 50)
    