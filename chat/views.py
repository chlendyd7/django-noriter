import json
import time
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from queue import Queue
from memory_profiler import profile

connected_clients = {}
test_time = None

def event_stream(request):
    session_id = request.session.session_key  # 세션 ID를 가져옵니다.

    while True:
        if session_id not in connected_clients:
            break
        time.sleep(5)
        yield f"data: {json.dumps({'timestamp': str(now()), 'message': 'ping'})}\n\n"

# @profile
# @csrf_exempt
def sse_connect(request):
    global test_time
    if not request.session.session_key:
        request.session.create()  # 세션이 없으면 새로 생성

    response = StreamingHttpResponse(event_stream(request), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    # response['Connection'] = 'keep-alive'
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
def send_message(request):
    """새로운 메시지를 모든 클라이언트에게 전송"""
    if request.method == 'POST':
        session_id = request.POST.get("session_id", None)
        message = request.POST.get("message", "")

        for session_id, response in connected_clients.items():
            print(f'{session_id}에게 {message} 전송')
            response.write(f"data: {{'message': '{message}'}}\n\n")
    
    return HttpResponse(status=204)

