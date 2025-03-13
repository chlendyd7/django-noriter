import websockets
import json
from locust import User, task, between, events
import asyncio
import time
from datetime import datetime

class WebSocketUser(User):
    # 요청 간 대기 시간을 설정
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
        self.connected = False
        self.loop = None
        self.message_count = 0
        
    async def connect(self):
        if not self.connected:
            start_time = time.time()
            try:
                ws_url = 'ws://127.0.0.1:8000/ws/chat/'
                self.ws = await websockets.connect(
                    ws_url,
                    ping_interval=None,  # 자동 ping 비활성화
                    close_timeout=10,
                )
                self.connected = True
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="websocket",
                    name="connect",
                    response_time=total_time,
                    response_length=0,
                    exception=None,
                )
                return True
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="websocket",
                    name="connect",
                    response_time=total_time,
                    response_length=0,
                    exception=e,
                )
                return False

    async def send_message(self):
        if self.connected and self.ws:
            start_time = time.time()
            try:
                message = f"Test message {self.message_count} at {datetime.now().isoformat()}"
                await self.ws.send(json.dumps({'message': message}))
                response = await self.ws.recv()
                total_time = int((time.time() - start_time) * 1000)
                
                events.request.fire(
                    request_type="websocket",
                    name="message",
                    response_time=total_time,
                    response_length=len(response),
                    exception=None,
                )
                self.message_count += 1
                return True
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="websocket",
                    name="message",
                    response_time=total_time,
                    response_length=0,
                    exception=e,
                )
                self.connected = False
                return False

    async def ping(self):
        while self.connected:
            try:
                await self.ws.send(json.dumps({'ping': 'ping'}))  # ping 메시지 전송
                await asyncio.sleep(5)  # 5초마다 ping 전송
            except Exception as e:
                print(f"Ping 전송 중 에러: {str(e)}")
                self.connected = False

    async def _run(self):
        if not self.connected:
            await self.connect()
        
        if self.connected:
            asyncio.create_task(self.ping())  # ping을 비동기로 실행
            await self.send_message()
            await asyncio.sleep(1)  # 1초 대기

    @task
    def run_websocket(self):
        if not self.loop:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._run())
        except Exception as e:
            print(f"태스크 실행 중 에러: {str(e)}")

    def on_stop(self):
        if self.ws:
            self.loop.run_until_complete(self.ws.close())
        if self.loop:
            self.loop.close()
