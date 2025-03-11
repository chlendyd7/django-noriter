# Windows에서 Gunicorn 대신 Waitress 사용

## WSL을 이용한 Gunicorn 실행
Windows에서는 Gunicorn을 직접 실행할 수 없으므로 WSL을 활용하여 실행해야 함.

### WSL에서 가상환경 접속
```sh
cd /mnt/c/Users/admin/.virtualenvs/django-bank-7uCUukR1/Scripts
source activate
```

## Waitress로 실행 (Windows)
Gunicorn 대신 Waitress를 사용하여 서버 실행을 시도함. 하지만 성능 저하로 인해 정확한 테스트가 어려울 것으로 예상됨.

### 실행 중 발생한 문제 및 해결 방법
1. **AssertionError: Connection is a "hop-by-hop" header; it cannot be used by a WSGI application (see PEP 3333)**
   - 해결: 응답 헤더에서 `Connection` 제거
   ```python
   response['Connection'] = 'keep-alive'
   ```

2. **OSError: This StreamingHttpResponse instance is not writable**
   - StreamingHttpResponse 관련 문제 발생

3. **Locust 테스트 결과**
   - 성능 이슈로 인해 부하 테스트 진행이 불가능함
   - 로그: `WARNING:waitress.queue:Task queue depth is 46`

## Django 기본 서버 (runserver)로 테스트 진행
Waitress 성능 문제로 인해 Django의 기본 개발 서버(runserver)를 사용하여 테스트를 진행함.

### 테스트 결과
- **100명 동시 접속**
- **소요 시간**: 198.59초

## 결론
- Windows 환경에서는 Gunicorn을 사용할 수 없으며, Waitress는 성능 한계로 인해 적절한 테스트가 어려움.
- 정확한 성능 테스트를 위해서는 WSL에서 Gunicorn을 사용하는 것이 바람직함.

### 추후 할 것
- message 보내는 테스트도 진행 예정