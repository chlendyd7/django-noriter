import aiohttp
import asyncio
import time
import psutil
import os

URL = "http://127.0.0.1:8000/asyc/"  # URL 수정

def get_memory_usage():
    """현재 프로세스의 메모리 사용량을 MB 단위로 반환"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # MB 단위로 반환

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
        
        # 초기 메모리 사용량을 설정하고, 최대 메모리 사용량을 추적
        max_memory_usage = get_memory_usage()
        print(f"초기 메모리 사용량: {max_memory_usage:.2f} MB")
        
        tasks = [fetch(session) for _ in range(n_requests)]
        
        for i in range(n_requests):
            current_memory = get_memory_usage()
            max_memory_usage = max(max_memory_usage, current_memory)  # 최대 메모리 사용량 갱신
            print(f"요청 {i+1} 시작 - 현재 메모리 사용량: {current_memory:.2f} MB")
            await tasks[i]
            current_memory = get_memory_usage()
            max_memory_usage = max(max_memory_usage, current_memory)  # 최대 메모리 사용량 갱신
            print(f"요청 {i+1} 완료 - 현재 메모리 사용량: {current_memory:.2f} MB")

        end_time = time.time()
        
        print(f"최대 메모리 사용량: {max_memory_usage:.2f} MB")
        print(f"총 요청 개수: {n_requests}")
        print(f"총 소요 시간: {end_time - start_time:.2f}초")
        print(f"평균 응답 속도: {(end_time - start_time) / n_requests:.4f}초")

asyncio.run(test_speed(1000))
