# sockt/consumers.py
from collections import defaultdict
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import asyncio
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

class ChatConsumer(AsyncWebsocketConsumer):
    # 클래스 변수로 연결된 클라이언트 수 추적
    connected_clients = defaultdict(int)
    start_time = None
    # connection_data = []

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name # channel_name은 자동으로 생성
        )
        await self.accept()
        self.connected_clients[self.channel_name] += 1
        
        if self.start_time is None:
            self.start_time = datetime.now()
        # self.connection_data.append((len(self.connected_clients), datetime.now() - self.start_time))

        if self.connected_clients[self.channel_name] >= 100:
            print('총 시간', datetime.now() - self.start_time)


    async def disconnect(self, close_code):
        print(f"WebSocket 연결 종료 (코드: {close_code}, 채널: {self.channel_name})")
        # WebSocket 연결이 종료되면 방 그룹에서 사용자를 삭제
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        self.connected_clients[self.channel_name] -= max(0, self.connected_clients[self.channel_name] - 1)
