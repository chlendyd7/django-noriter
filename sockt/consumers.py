# sockt/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # WebSocket 연결을 수락하기 전에 클라이언트에게 채팅방을 설정
        self.room_name = "chatroom"
        self.room_group_name = f'chat_{self.room_name}'

        # 방 그룹에 사용자를 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 연결 승인
        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket 연결이 종료되면 방 그룹에서 사용자를 삭제
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 클라이언트로부터 받은 메시지를 처리
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 방 그룹에 메시지를 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # 그룹에서 받은 메시지를 클라이언트로 전송
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
