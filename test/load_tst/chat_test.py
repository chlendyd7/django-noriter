import aiohttp
import asyncio
import time

URL = "http://127.0.0.1:8000/events/"  # URL 수정

async def fetch(session):
    async with session.get(URL) as response:
        print(f"응답 상태 코드: {response.status}")
        
        # 스트리밍 응답을 순차적으로 처리
        async for line in response.content:
            # 각 라인을 UTF-8로 디코딩하여 출력
            print(line.decode("utf-8").strip())

async def test_speed(n_requests=10):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = [fetch(session) for _ in range(n_requests)]
        await asyncio.gather(*tasks)  # 모든 요청 처리
        end_time = time.time()
        print(f"총 요청 개수: {n_requests}")
        print(f"총 소요 시간: {end_time - start_time:.2f}초")
        print(f"평균 응답 속도: {(end_time - start_time) / n_requests:.4f}초")

asyncio.run(test_speed(1000))
