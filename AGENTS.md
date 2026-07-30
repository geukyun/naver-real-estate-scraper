# AGENTS.md

이 파일은 Gemini Code Assist를 위한 프로젝트 컨텍스트와 지침을 제공하는 파일입니다.

## 프로젝트 정보
- **프로젝트 명:** naver-real-estate-scraper
- **백엔드 기술 스택:** Java / Spring Boot
- **프론트엔드 / 스크래핑 기술 스택:** Python / Playwright

## 주요 요구사항 (Core Requirements)
1. **타겟 사이트:** 네이버 부동산 홈페이지에 접속하여 데이터를 수집합니다.
2. **데이터 추출 대상:** `docs/gyeonggi_leading_districts.md` 및 `docs/seoul_districts.md` 파일을 읽어 해당 파일에 명시된 시, 군/구 지역에 속한 아파트 단지 리스트를 추출합니다.
3. **시스템 구조:** 프론트엔드(스크래핑 담당)와 백엔드(Java 기반 데이터 처리 및 API 담당)를 분리하여 개발합니다.

## 개발 가이드 및 구현 전략 (Implementation Strategy)
- **스크래핑 전략 (Playwright Interception):** 네이버 부동산 웹페이지의 복잡한 DOM을 직접 파싱하거나 UI를 클릭하는 대신, Playwright의 네트워크 가로채기(Network Interception) 기능을 활용합니다. 지역 검색 시 브라우저가 네이버 서버와 주고받는 내부 API 응답(JSON 등)을 직접 추출하여 속도와 안정성을 확보합니다.
- **지역 탐색 및 API 호출 규칙:**
  부동산 지역 선택은 "시 -> 시/군/구 -> 읍/면/동" 순으로 진행되며, 다음의 규칙을 따릅니다.
  1. **시/군/구 목록 조회:**
     - 서울시(대상: `docs/seoul_districts.md`): `https://land.naver.com/childRegionList.naver` 호출 (파라미터: `cortarNo=1100000000`, `rletTypeCd=A01`)
     - 경기도(대상: `docs/gyeonggi_leading_districts.md`): 동일 URL 호출 (파라미터: `cortarNo=4100000000`, `rletTypeCd=A01`)
     - 응답 JSON 레이아웃 예시:
       ```json
       {
         "articleCount": {},
         "city_nm": "서울시",
         "cortar_nm": "강서구",
         "cortar_no": "1150000000",
         "dvsn_nm": "강서구",
         "map_x_crdn": "126.849534",
         "map_y_crdn": "37.550985",
         "sec_nm": ""
       }
       ```
  2. **읍/면/동 목록 조회:**
     - 1번 응답에서 대상 지역의 `cortar_nm`과 일치하는 `cortar_no`를 추출합니다.
     - 추출한 `cortar_no`를 파라미터(`cortarNo`)로 하고, `rletTypeCd=A01`을 추가 파라미터로 하여 `https://land.naver.com/childRegionList.naver` URL을 재호출합니다.
  3. **최종 단지(아파트) 리스트 호출:**
     - 마지막으로 읍/면/동 단계의 `cortarNo`를 사용하여 아래와 같은 형식의 URL을 호출합니다.
     - 예시: `https://new.land.naver.com/complexes?cortarNo=5013010900&a=APT&b=A1&e=RETAIL&h=66&i=132`
- **데이터 파이프라인:** Python 스크래퍼가 데이터를 수집 및 정제한 후, 추출된 아파트 단지 정보(JSON 포맷)를 Spring Boot 백엔드 서버의 REST API 엔드포인트(예: POST `/api/apartments`)로 전송하도록 파이프라인을 구축합니다.

## 코딩 지침 (AI Assistant Guidelines)
- 기존 프로젝트의 코드 스타일과 네이밍 규칙을 준수해주세요.
- Spring Boot의 최신 권장 사항과 Best Practice를 활용해주세요.
- 간결하고 명확한 코드 작성을 지향하며, 필요한 경우 적절한 주석을 추가해주세요.
- 새로운 기능 추가 시, 기존 아키텍처(Controller, Service, Repository 등)의 계층 구조를 유지해주세요.
- 스크래핑 모듈의 경우, 대상 웹사이트의 구조 변경에 유연하게 대처할 수 있도록 모듈화하여 작성해주세요.
- 스크래핑은 동적 웹페이지 처리에 유리한 Python과 Playwright를 활용합니다.