"""
[목적]
이 파일은 Spring Boot 백엔드 서버가 아직 켜지지 않았거나 테스트 목적일 때,
스크래퍼(파이썬 크롤러)가 보낸 수집 데이터(POST /api/apartments)를 수신하고
저장 상태를 확인(GET /api/apartments)할 수 있도록 만든 '가짜(Mock) 테스트 백엔드 서버'입니다.

파이썬 내장 라이브러리인 http.server를 사용하여 별도 패키지 설치 없이 실행 가능합니다.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

# 수집된 아파트 데이터를 메모리에 임시 보관하기 위한 전역 리스트 (간이 데이터베이스 역할)
apartments_db = []


class ApartmentRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP 요청(GET, POST 등)이 들어왔을 때 이를 처리하는 요청 처리기(Handler) 클래스입니다.
    BaseHTTPRequestHandler를 상속받아 구현합니다.
    """

    def do_POST(self):
        """
        클라이언트(스크래퍼)가 HTTP POST 요청을 보냈을 때 호출되는 메서드입니다.
        예: POST /api/apartments -> 수집한 아파트 JSON 데이터를 수신하여 저장
        """
        # 요청 URL 경로가 "/api/apartments" 인지 확인합니다.
        if self.path == "/api/apartments":
            # 요청 헤더에서 데이터의 길이(Content-Length)를 가져옵니다.
            content_length = int(self.headers.get('Content-Length', 0))
            # 요청 본문(body) 데이터를 바이트 단위로 읽어옵니다.
            post_data = self.rfile.read(content_length)

            try:
                # 바이트 데이터를 UTF-8 문자열로 변환(decode)한 후 JSON 객체(파이썬 리스트/딕셔너리)로 파싱합니다.
                data = json.loads(post_data.decode('utf-8'))

                # 전달된 데이터가 리스트 형태(여러 개)인지 단일 항목(1개)인지 확인하여 처리합니다.
                if isinstance(data, list):
                    apartments_db.extend(data)  # 리스트 전체를 DB 목록에 추가
                    saved_count = len(data)
                else:
                    apartments_db.append(data)  # 단일 딕셔너리를 DB 목록에 추가
                    saved_count = 1

                print(f"[Backend Mock] Received {saved_count} records. Total in DB: {len(apartments_db)}")

                # 클라이언트에게 응답할 JSON 데이터 구성
                response_data = {
                    "status": "SUCCESS",
                    "savedCount": saved_count,
                    "totalCountInDb": len(apartments_db)
                }

                # HTTP 200 OK 응답 헤더 전송
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()

                # JSON 데이터를 바이트로 인코딩하여 클라이언트에 전송
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                # JSON 파싱 등 에러 발생 시 HTTP 400 Bad Request 응답
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode('utf-8'))
        else:
            # 존재하지 않는 경로일 경우 HTTP 404 Not Found 응답
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        """
        클라이언트가 HTTP GET 요청을 보냈을 때 호출되는 메서드입니다.
        예: GET /api/apartments -> 저장된 전체 아파트 목록 반환
        예: GET /api/apartments/count -> 저장된 아파트 총 개수 반환
        """
        if self.path == "/api/apartments":
            # 전체 아파트 목록 반환 (HTTP 200 OK)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(apartments_db, ensure_ascii=False).encode('utf-8'))

        elif self.path == "/api/apartments/count":
            # 아파트 총 개수 반환 (HTTP 200 OK)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"totalCount": len(apartments_db)}).encode('utf-8'))

        else:
            # 잘못된 주소 요청 시 HTTP 404 Not Found
            self.send_response(404)
            self.end_headers()


def run_mock_backend(port=8080):
    """
    [함수 역할]
    지정한 포트(기본 8080)로 HTTP 웹 서버를 구동하고 요청을 대기합니다.
    """
    server_address = ('', port)  # 모든 IP 인터페이스에서 접속 가능하도록 설정
    httpd = HTTPServer(server_address, ApartmentRequestHandler)
    print(f"[Backend Mock] Server running on http://localhost:{port}/api/apartments ...")
    
    try:
        # 서버를 무한 루프로 실행하며 들어오는 요청을 계속 수신합니다.
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Ctrl+C 키 입력 시 서버를 안전하게 종료합니다.
        print("[Backend Mock] Stopping server.")
        httpd.server_close()


# -----------------------------------------------------------------------------
# 스크립트 실행 시작점 (예: python mock_backend.py 8080)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 터미널 커맨드라인 인자로 포트 번호를 전달받을 수 있도록 설정 (기본값: 8080)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_mock_backend(port)
