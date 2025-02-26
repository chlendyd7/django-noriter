import json
import asyncio
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from django.http.response import StreamingHttpResponse
import weakref

# uvicorn sse.asgi:application --host 0.0.0.0 --port 8000

subscribers= weakref.WeakSet()

async def event_stream(subscriber_queue):
    """비동기 SSE 스트리밍"""
    for i in range(10):  # 10개의 메시지를 예시로 보내는 코드
        yield f"data: {json.dumps({'timestamp': str(now()), 'message': f'Message {i}'})}\n\n"
    yield "data: {\"message\": \"Connection Closing\"}\n\n"
    # try:
    #     while True:
    #         try:
    #             message = await asyncio.wait_for(subscriber_queue.get(), timeout=10)
    #         except asyncio.TimeoutError:
    #             message = "ping"  # 10초마다 ping 전송 (heartbeat)

    #         yield f"data: {json.dumps({'timestamp': str(now()), 'message': message})}\n\n"
    # except GeneratorExit:
    #     print("클라이언트 연결 종료")
    #     subscribers.discard(subscriber_queue)  # 클라이언트 연결 종료 시 제거 server'})}\n\n"

@csrf_exempt
async def sse_view(request):
    """비동기 SSE 응답"""
    try:
        loop = asyncio.get_running_loop()
        print(f"Running in Async Loop: {loop} 루프 실행중이다")
    except RuntimeError:
        print("Not running in an Async Loop")
    subscriber_queue = asyncio.Queue()
    subscribers.add(subscriber_queue)

    response = StreamingHttpResponse(
        event_stream(subscriber_queue),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Nginx에서 버퍼링 방지

    print(f"현재 연결된 클라이언트 수: {len(subscribers)}")
    return response

@csrf_exempt
async def send_message(request):
    """비동기 메시지 브로드캐스트"""
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        print(f"받은 메시지: {message}")

        # 모든 클라이언트에 메시지 비동기 전송
        for subscriber in subscribers.copy():
            try:
                await subscriber.put(message)
            except Exception:
                subscribers.discard(subscriber)  # 연결 종료된 클라이언트 제거

        return HttpResponse(status=204)
    return HttpResponse("POST 요청만 허용됩니다.", status=405)
