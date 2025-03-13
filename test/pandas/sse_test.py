import pandas as pd
import matplotlib.pyplot as plt
import time

test_start_time = None

def collect_data_and_visualize():
    global test_start_time
    
    data = {
        "connected_clients": len(connected_clients),
        "elapsed_time": time.time() - test_time if test_time else 0
    }
    
    # Pandas DataFrame에 기록
    df = pd.DataFrame([data])
    
    df.plot(x='elapsed_time', y='connected_clients', kind='line', title='Connected Clients Over Time')
    plt.xlabel('Elapsed Time (seconds)')
    plt.ylabel('Connected Clients')
    plt.show()

def track_performance(func):
    def wrapper(request, *args, **kwargs):
        global test_time

        if test_time is None:
            test_time = time.time()  # 테스트 시작 시간 설정

        response = func(request, *args, **kwargs)

        if len(connected_clients) >= 100:  # 클라이언트가 100명 이상일 때
            collect_data_and_visualize()

        return response
    return wrapper