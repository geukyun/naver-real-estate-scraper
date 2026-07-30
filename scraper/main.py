import asyncio
import json
import os
import re
import urllib.request
import urllib.parse
from playwright.async_api import async_playwright

# -----------------------------------------------------------------------------
# [설정] 백엔드 서버의 API 주소 설정
# 환경 변수 "BACKEND_API_URL"이 설정되어 있으면 그 값을 사용하고,
# 없으면 기본값으로 로컬 주소(http://localhost:8080/api/apartments)를 사용합니다.
# -----------------------------------------------------------------------------
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/api/apartments")


def parse_markdown_list(file_path):
    """
    [함수 역할]
    docs 폴더 안의 마크다운(.md) 문서 파일에서 지역 이름(시/군/구) 목록을 읽어와서 파이썬 리스트로 변환합니다.

    [매개변수]
    - file_path (str): 읽어올 마크다운 파일의 경로

    [반환값]
    - list: 추출된 지역명 문자열 리스트 (예: ['강남구', '과천시'])
    """
    # 지정한 경로에 파일이 존재하지 않는 경우 경고 메시지를 출력하고 빈 리스트를 반환합니다.
    if not os.path.exists(file_path):
        print(f"Warning: File not found - {file_path}")
        return []

    districts = []
    # UTF-8 인코딩으로 파일을 엽니다. (한글 깨짐 방지)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()  # 줄 바꿈 및 좌우 공백 제거
            
            # 정규표현식(re)을 사용해 **지역명** 형태의 텍스트(볼드체)를 찾습니다.
            # 예: "**강남구** (Gangnam-gu)" -> group(1)은 "강남구"
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                name = match.group(1).strip()
                # 괄호와 괄호 안의 영문 명칭을 제거합니다. (예: "과천시 (Gwacheon-si)" -> "과천시")
                name = re.sub(r'\s*\(.*?\)', '', name).strip()
                if name:
                    districts.append(name)
                    
    return districts


async def fetch_child_regions(context, cortar_no):
    """
    [비동기 함수 역할]
    네이버 부동산 내부 API를 호출하여 특정 지역(cortar_no) 아래에 속한 하위 지역 목록을 가져옵니다.
    예: '서울특별시' 코드 입력 -> 서울의 모든 '구(강남구, 서초구 등)' 목록 반환
    예: '강남구' 코드 입력 -> 강남구의 모든 '동(역삼동, 삼성동 등)' 목록 반환

    [매개변수]
    - context: Playwright의 BrowserContext 객체 (웹 브라우저 세션 역할)
    - cortar_no (str): 네이버 법정동 코드 (예: 서울 '1100000000')

    [반환값]
    - list: 하위 지역 정보가 담긴 딕셔너리 리스트
    """
    # 브라우저에 새로운 탭(페이지)을 생성합니다.
    page = await context.new_page()
    
    # URL 쿼리 파라미터를 생성합니다. (rletTypeCd='A01'은 아파트를 의미)
    params = urllib.parse.urlencode({'cortarNo': cortar_no, 'rletTypeCd': 'A01'})
    api_url = f"https://land.naver.com/childRegionList.naver?{params}"

    try:
        # HTTP GET 요청을 전송하여 네이버 부동산 API에서 데이터를 가져옵니다.
        response = await page.request.get(api_url, headers={
            "referer": "https://land.naver.com/",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest"
        })

        # 응답 상태가 정상(HTTP 200 OK 등)이 아니면 빈 리스트 반환
        if not response.ok:
            print(f"  -> childRegionList API failed [{response.status}] for {cortar_no}")
            return []

        # 응답 결과를 JSON(파이썬 딕셔너리 형식)으로 변환합니다.
        json_data = await response.json()
        if isinstance(json_data, dict):
            # JSON 응답 내의 "Region" 키에 담긴 하위 지역 목록을 추출합니다.
            return json_data.get("Region", [])
        return []
    except Exception as e:
        print(f"  -> Error fetching child regions for {cortar_no}: {e}")
        return []
    finally:
        # 작업이 끝나면 생성했던 브라우저 탭을 닫아 메모리를 해제합니다.
        await page.close()


async def fetch_complexes(context, dong_cortar_no):
    """
    [비동기 함수 역할]
    특정 읍/면/동의 법정동 코드(dong_cortar_no)를 입력받아 해당 동에 있는 아파트 단지 목록을 조회합니다.

    [매개변수]
    - context: Playwright BrowserContext 객체
    - dong_cortar_no (str): 읍/면/동 단위 법정동 코드

    [반환값]
    - list: 해당 동에 존재하는 아파트 단지(Complex) 목록
    """
    if not dong_cortar_no:
        return []

    page = await context.new_page()
    # 아파트 단지 목록을 요청하는 API 주소 (realEstateType=APT: 아파트 대상)
    api_url = f"https://new.land.naver.com/api/regions/complexes?cortarNo={dong_cortar_no}&realEstateType=APT&tradeType="

    try:
        # 네이버 부동산 신규 API 요청 (User-Agent 헤더를 설정하여 차단을 방지함)
        response = await page.request.get(api_url, headers={
            "referer": f"https://new.land.naver.com/complexes?cortarNo={dong_cortar_no}&a=APT",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })

        if not response.ok:
            print(f"  -> Complexes API failed [{response.status}] for {dong_cortar_no}")
            return []

        json_data = await response.json()
        if isinstance(json_data, dict):
            # API 응답에서 "complexList" 키 항목을 가져옵니다.
            return json_data.get("complexList", [])
        return json_data if isinstance(json_data, list) else []
    except Exception as e:
        print(f"  -> Error fetching complexes for {dong_cortar_no}: {e}")
        return []
    finally:
        await page.close()


async def scrape_city(context, city_code, city_name, target_districts):
    """
    [비동기 함수 역할]
    하나의 광역시/도(예: 서울특별시, 경기도) 전체를 순회하며,
    우리가 수집하고자 하는 타겟 시/군/구 및 동 단위의 아파트 단지 정보를 크롤링합니다.

    [매개변수]
    - context: Playwright BrowserContext 객체
    - city_code (str): 시/도 코드 (예: 서울 '1100000000')
    - city_name (str): 시/도 이름 (예: "서울특별시")
    - target_districts (list): 수집할 타겟 구/시 이름 목록 (예: ['강남구', '과천시'])

    [반환값]
    - list: 수집된 모든 아파트 단지 딕셔너리 정보 리스트
    """
    print(f"\n[City Processing] {city_name} (Code: {city_code})")
    all_complexes = []

    # 1단계: 시/도 코드 아래의 시/군/구 목록 가져오기 (예: 서울 -> 강남구, 서초구, 송파구 ...)
    gu_list = await fetch_child_regions(context, city_code)
    if not gu_list:
        print(f"No districts found for {city_name}.")
        return []

    for gu in gu_list:
        # 네이버 API 응답에 필드명이 'cortar_nm' 또는 'cortarNm'으로 올 수 있으므로 모두 처리
        gu_name = gu.get("cortar_nm", gu.get("cortarNm", ""))
        gu_code = gu.get("cortar_no", gu.get("cortarNo", ""))

        if not gu_name or not gu_code:
            continue

        # 우리가 타겟으로 삼은 관심 지역(target_districts)에 포함되는지 확인합니다.
        is_target = False
        for target in target_districts:
            target_parts = target.split()
            target_keyword = target_parts[-1] if target_parts else target
            # 키워드가 구 이름에 포함되어 있거나 서로 일치하는지 체크
            if target_keyword in gu_name or gu_name in target_keyword:
                is_target = True
                break

        # 타겟 지역이 아니면 다음 구/시로 건너뜁니다.
        if not is_target:
            continue

        print(f"  └─ Fetching Dongs for district: {gu_name} ({gu_code})")

        # 2단계: 관심 구/시 아래의 읍/면/동 목록 가져오기 (예: 강남구 -> 역삼동, 삼성동, 대치동 ...)
        dong_list = await fetch_child_regions(context, gu_code)

        for dong in dong_list:
            dong_name = dong.get("cortar_nm", dong.get("cortarNm", ""))
            dong_code = dong.get("cortar_no", dong.get("cortarNo", ""))

            if not dong_name or not dong_code:
                continue

            # 3단계: 읍/면/동 아래의 실제 아파트 단지(Complex) 목록 가져오기
            complexes = await fetch_complexes(context, dong_code)
            if complexes:
                print(f"      ├─ {dong_name} ({dong_code}): Found {len(complexes)} complexes")
                for c in complexes:
                    if isinstance(c, dict):
                        # 각 단지 데이터에 상위 메타데이터(시/도, 시/군/구, 읍/면/동 이름)를 추가해줍니다.
                        c["city"] = city_name
                        c["gu"] = gu_name
                        c["dong"] = dong_name
                        all_complexes.append(c)

    return all_complexes


async def scrape_naver_real_estate(districts):
    """
    [비동기 메인 수집 함수]
    Playwright 브라우저를 실행하고, 서울 및 경기도 지역의 아파트 정보를 수집합니다.

    [매개변수]
    - districts (list): 마크다운 파일 등에서 읽어온 타겟 구/시 리스트

    [반환값]
    - list: 수집된 전체 아파트 단지 정보 리스트
    """
    print(f"Target districts ({len(districts)}): {districts[:5]} ...")
    all_apartments = []

    # async_playwright()를 사용하여 비동기 브라우저 세션을 시작합니다.
    async with async_playwright() as p:
        # 크롬(Chromium) 브라우저를 띄웁니다 (headless=True: 화면에 창을 띄우지 않는 백그라운드 모드)
        browser = await p.chromium.launch(headless=True)
        
        # 실제 사용자처럼 보이도록 User-Agent 및 헤더 정보를 설정하여 브라우저 컨텍스트 생성
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

        # 봇(Bot) 차단을 우회하고 핑/쿠키/세션을 활성화하기 위해 메인 페이지에 한 번 먼저 접속합니다.
        page = await context.new_page()
        await page.goto("https://land.naver.com/", wait_until="domcontentloaded")
        await page.goto("https://new.land.naver.com/", wait_until="domcontentloaded")
        await page.close()

        # 1. 서울특별시 (법정동 코드: 1100000000) 아파트 단지 데이터 수집
        seoul_complexes = await scrape_city(context, "1100000000", "서울특별시", districts)
        all_apartments.extend(seoul_complexes)

        # 2. 경기도 (법정동 코드: 4100000000) 아파트 단지 데이터 수집
        gyeonggi_complexes = await scrape_city(context, "4100000000", "경기도", districts)
        all_apartments.extend(gyeonggi_complexes)

        # 수집 완료 후 브라우저 종료
        await browser.close()
        return all_apartments


def send_to_backend(data):
    """
    [함수 역할]
    크롤링으로 수집한 아파트 데이터(JSON)를 Spring Boot 백엔드 서버(REST API POST /api/apartments)로 전송합니다.

    [매개변수]
    - data (list): 전송할 아파트 딕셔너리 리스트
    """
    if not data:
        print("\nNo data collected to send to backend.")
        return

    print(f"\nSending {len(data)} records to Spring Boot backend ({BACKEND_API_URL}) ...")

    # 데이터 샘플 출력 (첫 번째 항목을 보기 좋게 JSON 문자열로 출력)
    print("Sample record:")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))

    # 파이썬 리스트/딕셔너리 객체를 JSON 문자열로 변환한 후 UTF-8 바이트로 엔코딩합니다.
    json_payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    # 백엔드 API로 보낼 HTTP POST 요청 객체를 생성합니다.
    req = urllib.request.Request(
        BACKEND_API_URL,
        data=json_payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        # 백엔드로 HTTP 요청을 보내고 응답을 받습니다.
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            print(f"Backend Response [{resp.status}]: {resp_body}")
    except Exception as e:
        # 백엔드 서버가 켜져있지 않거나 오류가 발생했을 경우 에러 메시지 출력
        print(f"Could not send data to backend (Backend server may not be running): {e}")


# -----------------------------------------------------------------------------
# [스크립트 실행 시 시작점 (Main)]
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. docs 폴더 내의 서울/경기 관련 마크다운 파일 경로를 설정합니다.
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    seoul_file = os.path.join(docs_dir, 'seoul_districts.md')
    gyeonggi_file = os.path.join(docs_dir, 'gyeonggi_leading_districts.md')

    # 2. 마크다운 파일들에서 수집 대상 타겟 시/군/구 목록을 추출합니다.
    target_districts = []
    target_districts.extend(parse_markdown_list(seoul_file))
    target_districts.extend(parse_markdown_list(gyeonggi_file))
    # 중복 지역 이름 제거
    target_districts = list(set(target_districts))

    # 3. 비동기 이벤트 루프(asyncio.run)를 실행하여 크롤링을 구동합니다.
    scraped_data = asyncio.run(scrape_naver_real_estate(target_districts))

    print(f"\n==========================================")
    print(f" Scraping Completed! Total complexes: {len(scraped_data)}")
    print(f"==========================================")

    # 4. 수집 완료된 데이터를 백엔드 API로 전송합니다.
    send_to_backend(scraped_data)