import asyncio
import json
import os
import re
import urllib.request
import urllib.parse
from playwright.async_api import async_playwright

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/api/apartments")


def parse_markdown_list(file_path):
    """
    마크다운 파일에서 시/군/구 지역 이름을 추출합니다.
    """
    if not os.path.exists(file_path):
        print(f"Warning: File not found - {file_path}")
        return []

    districts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # **강남구** (Gangnam-gu) 형태 또는 * **과천시 (Gwacheon-si)** 형태 파싱
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                name = match.group(1).strip()
                # 괄호 안의 영문 명칭 제거 (예: 과천시 (Gwacheon-si) -> 과천시)
                name = re.sub(r'\s*\(.*?\)', '', name).strip()
                if name:
                    districts.append(name)
    return districts


async def fetch_child_regions(context, cortar_no):
    """
    cortar_no(지역 코드)를 입력받아 하위 지역 목록(시/군/구 또는 읍/면/동)을 반환합니다.
    """
    page = await context.new_page()
    params = urllib.parse.urlencode({'cortarNo': cortar_no, 'rletTypeCd': 'A01'})
    api_url = f"https://land.naver.com/childRegionList.naver?{params}"

    try:
        response = await page.request.get(api_url, headers={
            "referer": "https://land.naver.com/",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest"
        })

        if not response.ok:
            print(f"  -> childRegionList API failed [{response.status}] for {cortar_no}")
            return []

        json_data = await response.json()
        if isinstance(json_data, dict):
            return json_data.get("Region", [])
        return []
    except Exception as e:
        print(f"  -> Error fetching child regions for {cortar_no}: {e}")
        return []
    finally:
        await page.close()


async def fetch_complexes(context, dong_cortar_no):
    """
    읍/면/동 cortarNo를 사용해 해당 동의 아파트 단지 목록을 조회합니다.
    """
    if not dong_cortar_no:
        return []

    page = await context.new_page()
    api_url = f"https://new.land.naver.com/api/regions/complexes?cortarNo={dong_cortar_no}&realEstateType=APT&tradeType="

    try:
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
            return json_data.get("complexList", [])
        return json_data if isinstance(json_data, list) else []
    except Exception as e:
        print(f"  -> Error fetching complexes for {dong_cortar_no}: {e}")
        return []
    finally:
        await page.close()


async def scrape_city(context, city_code, city_name, target_districts):
    """
    지정된 광역시/도(서울/경기 등) 내의 타겟 구/시 및 동 단지 데이터를 수집합니다.
    """
    print(f"\n[City Processing] {city_name} (Code: {city_code})")
    all_complexes = []

    # 1. 시/군/구 목록 조회
    gu_list = await fetch_child_regions(context, city_code)
    if not gu_list:
        print(f"No districts found for {city_name}.")
        return []

    for gu in gu_list:
        gu_name = gu.get("cortar_nm", gu.get("cortarNm", ""))
        gu_code = gu.get("cortar_no", gu.get("cortarNo", ""))

        if not gu_name or not gu_code:
            continue

        # 타겟 수집 대상 구/시인지 확인
        is_target = False
        for target in target_districts:
            target_parts = target.split()
            target_keyword = target_parts[-1] if target_parts else target
            if target_keyword in gu_name or gu_name in target_keyword:
                is_target = True
                break

        if not is_target:
            continue

        print(f"  └─ Fetching Dongs for district: {gu_name} ({gu_code})")

        # 2. 읍/면/동 목록 조회
        dong_list = await fetch_child_regions(context, gu_code)

        for dong in dong_list:
            dong_name = dong.get("cortar_nm", dong.get("cortarNm", ""))
            dong_code = dong.get("cortar_no", dong.get("cortarNo", ""))

            if not dong_name or not dong_code:
                continue

            # 3. 최종 단지(아파트) 목록 조회
            complexes = await fetch_complexes(context, dong_code)
            if complexes:
                print(f"      ├─ {dong_name} ({dong_code}): Found {len(complexes)} complexes")
                for c in complexes:
                    if isinstance(c, dict):
                        # 메타데이터 병합
                        c["city"] = city_name
                        c["gu"] = gu_name
                        c["dong"] = dong_name
                        all_complexes.append(c)

    return all_complexes


async def scrape_naver_real_estate(districts):
    print(f"Target districts ({len(districts)}): {districts[:5]} ...")
    all_apartments = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

        # 쿠키 및 세션 활성화를 위한 초기 접속
        page = await context.new_page()
        await page.goto("https://land.naver.com/", wait_until="domcontentloaded")
        await page.goto("https://new.land.naver.com/", wait_until="domcontentloaded")
        await page.close()

        # 1. 서울특별시 (cortarNo: 1100000000)
        seoul_complexes = await scrape_city(context, "1100000000", "서울특별시", districts)
        all_apartments.extend(seoul_complexes)

        # 2. 경기도 (cortarNo: 4100000000)
        gyeonggi_complexes = await scrape_city(context, "4100000000", "경기도", districts)
        all_apartments.extend(gyeonggi_complexes)

        await browser.close()
        return all_apartments


def send_to_backend(data):
    """
    수집한 데이터를 Spring Boot 백엔드 REST API (POST /api/apartments)로 전송합니다.
    """
    if not data:
        print("\nNo data collected to send to backend.")
        return

    print(f"\nSending {len(data)} records to Spring Boot backend ({BACKEND_API_URL}) ...")

    # Sample printing
    print("Sample record:")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))

    json_payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        BACKEND_API_URL,
        data=json_payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            print(f"Backend Response [{resp.status}]: {resp_body}")
    except Exception as e:
        print(f"Could not send data to backend (Backend server may not be running): {e}")


if __name__ == "__main__":
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    seoul_file = os.path.join(docs_dir, 'seoul_districts.md')
    gyeonggi_file = os.path.join(docs_dir, 'gyeonggi_leading_districts.md')

    target_districts = []
    target_districts.extend(parse_markdown_list(seoul_file))
    target_districts.extend(parse_markdown_list(gyeonggi_file))
    target_districts = list(set(target_districts))

    scraped_data = asyncio.run(scrape_naver_real_estate(target_districts))

    print(f"\n==========================================")
    print(f" Scraping Completed! Total complexes: {len(scraped_data)}")
    print(f"==========================================")

    send_to_backend(scraped_data)