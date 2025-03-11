import json
import asyncio
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from django.http.response import StreamingHttpResponse
import weakref


# uvicorn sse.asgi:application --host 0.0.0.0 --port 8000
connected_clients = {}
test_time = None

async def event_stream(request):
    session_id = request.session.session_key  # 세션 ID를 가져옵니다.

    while True:
        if session_id not in connected_clients:
            break
        await asyncio.sleep(5)
        yield f"data: {json.dumps({'timestamp': str(now()), 'message': 'ping'})}\n\n"


@csrf_exempt
async def sse_connect(request):
    global test_time
    if not request.session.session_key:
        await sync_to_async(request.session.create)()  # 세션이 없으면 새로 생성

    response = StreamingHttpResponse(event_stream(request), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response['Connection'] = 'keep-alive'
    # response["X-Accel-Buffering"] = "no"  # Nginx에서 버퍼링 방지
    if not request.session.session_key in connected_clients:
        session_id = request.session.session_key
        connected_clients[session_id] = response


    print(f'{request.session.session_key} 연결')
    print(f'{len(connected_clients)} 명 연결')
    if test_time is None:
        test_time = time.time()  # 테스트 시작 시간 설정
    if len(connected_clients) >= 100:
        elapsed_time = time.time() - test_time  # 경과 시간 계산
        print(f'{elapsed_time} 초 걸림')


    response.status_code = 200
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
