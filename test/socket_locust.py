import asyncio
import websockets
import time

# 테스트할 WebSocket 서버 URL
url = "ws://localhost:8000/ws/chat/test/"

# 클라이언트 수
total_clients = 100

# 연결된 클라이언트 수
connected_clients = 0

# WebSocket 연결을 처리할 코루틴 함수
async def connect_to_websocket(client_id):
    global connected_clients
    try:
        async with websockets.connect(url) as websocket:
            connected_clients += 1
            await websocket.send(f"Hello from client {client_id}")
            print(f"Client {client_id} 연결됨. 현재 연결 수: {connected_clients}")
            
            # 서버에서 메시지를 기다림
            response = await websocket.recv()  # 서버로부터 응답 수신
            print(f"Client {client_id} 수신: {response}")  # 수신한 메시지 출력
            await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"Client {client_id} 연결 오류: {e}")

# 여러 클라이언트 연결을 동시에 처리
async def main():
    tasks = []
    for i in range(total_clients):
        tasks.append(connect_to_websocket(i + 1))  # 각 클라이언트에 대해 connect 함수 호출
    
    await asyncio.gather(*tasks)
    print(f"모든 클라이언트 연결 완료")

# 테스트 시작
start_time = time.time()  # 전체 테스트 시작 시간
asyncio.run(main())
end_time = time.time()  # 전체 테스트 종료 시간

# 소요 시간 출력
print(f"전체 테스트 소요 시간: {end_time - start_time:.2f}초")
