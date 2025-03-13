#WHAT_IS_AsyncHttpConsumer = 'https://chlendyd7.notion.site/AsyncHttpConsumer-1b4933ef8740804e977ec6bc3b2f7d38?pvs=4'


import json
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from django.http.response import StreamingHttpResponse
import weakref
from channels.generic.http import AsyncHttpConsumer
import asyncio

connected_clients = {}
test_time = None

class SSEConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        session_id = self.scope["session"].session_key
        if not session_id:
            self.scope["session"].create()
            session_id = self.scope["session"].session_key

        # 클라이언트가 연결되었을 때 연결 리스트에 추가
        connected_clients.add(session_id)
        
        headers = [
            (b"Content-Type", b"text/event-stream"),
            (b"Cache-Control", b"no-cache"),
            (b"Connection", b"keep-alive"),
        ]
        await self.send_headers(headers=headers)

        try:
            while True:
                # 클라이언트에 데이터를 보내기 전에 ping 메시지 전송
                await asyncio.sleep(10)  # 10초마다 ping을 보내는 타이밍
                ping_message = "data: ping\n\n"
                await self.send_body(ping_message.encode("utf-8"), more_body=True)

                # 성능 테스트 - 연결된 클라이언트 수 체크
                print(f"현재 연결된 클라이언트 수: {len(connected_clients)}")

                # 성능 테스트 시작 시간 체크
                if test_time is None:
                    test_time = time.time()  # 테스트 시작 시간 설정

                if len(connected_clients) >= 100:
                    elapsed_time = time.time() - test_time  # 경과 시간 계산
                    print(f'{elapsed_time} 초 걸림')

        except Exception as e:
            print(f"연결 오류: {e}")
        finally:
            # 클라이언트 연결이 끊어지면 연결 리스트에서 제거
            connected_clients.remove(session_id)
            print(f"{session_id} 연결 끊어짐. 현재 연결 수: {len(connected_clients)}")

    async def receive(self, text_data):
        pass

    async def send(self, text_data):
        pass

    async def send_response(self, data):
        # send 메서드를 오버라이드하여 메시지를 전송하는 방식 수정
        message = json.dumps(data)
        await self.send({
            "type": "http.response.body",
            "body": message.encode("utf-8"),
            "status": 200,
        })
