import json
import time
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from queue import Queue
from memory_profiler import profile

subscribers = []

def event_stream(subscriber_queue):
    """실시간 메시지를 스트리밍하는 제너레이터"""
    try:
        while True:
            try:
                # 메시지가 올 때까지 대기
                message = subscriber_queue.get(timeout=10)  # 10초 대기 후 heartbeat 전송
            except Exception:
                message = "ping"

            yield f"data: {json.dumps({'timestamp': str(now()), 'message': message})}\n\n"
    except GeneratorExit:
        subscribers.remove(subscriber_queue)

@profile
@csrf_exempt
def sse_view(request):
    """모든 클라이언트에게 실시간으로 메시지를 스트리밍"""
    subscriber_queue = Queue()
    subscribers.append(subscriber_queue)

    response = StreamingHttpResponse(event_stream(subscriber_queue), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Nginx에서 버퍼링 방지

    print(response)
    # 클라이언트가 연결되면 subscribers 리스트에 추가
    subscribers.append(response)
    
    print(f"현재 연결된 클라이언트 수: {len(subscribers)}")
    return response

@csrf_exempt
def send_message(request):
    """새로운 메시지를 모든 클라이언트에게 전송"""
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        print(f"받은 메시지: {message}")
        for subscriber in subscribers:
            try:
                subscriber.put(message)
            except Exception as e:
                subscribers.remove(subscriber)
            
        return HttpResponse(status=204)
    return HttpResponse("POST 요청만 허용됩니다.", status=405)
