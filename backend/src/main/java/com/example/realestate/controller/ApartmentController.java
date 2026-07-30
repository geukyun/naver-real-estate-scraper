package com.example.realestate.controller;

import com.example.realestate.entity.Apartment;
import com.example.realestate.service.ApartmentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * [아파트 정보 REST API 컨트롤러 클래스]
 *
 * 외부(파이썬 크롤러, 웹 클라이언트 등)의 HTTP 요청을 받아
 * 알맞은 비즈니스 로직(Service)을 호출하고, 처리 결과를 HTTP 응답(JSON 형식)으로 반환합니다.
 */
@Slf4j // 로깅 기능을 위한 Lombok 어노테이션
@RestController // @Controller + @ResponseBody의 조합으로, 메서드 반환값을 JSON 형식의 HTTP 응답 데이터로 자동 변환합니다.
@RequestMapping("/api/apartments") // 이 컨트롤러의 기본 URL 경로(Prefix)를 지정합니다. (예: http://localhost:8080/api/apartments)
@RequiredArgsConstructor // final로 선언된 필드의 생성자를 자동으로 작성하여 의존성을 주입받습니다.
public class ApartmentController {

    private final ApartmentService apartmentService;

    /**
     * [아파트 수집 데이터 수신 API]
     * HTTP Method: POST
     * URL Path: /api/apartments
     *
     * 파이썬 스크래퍼가 수집한 아파트 단지 목록(JSON 리스트)을 받아 DB에 저장/업데이트합니다.
     *
     * @param apartments @RequestBody를 통해 HTTP 요청 본문(JSON)이 파이썬/자바 객체 리스트로 자동 파싱되어 입력됩니다.
     * @return ResponseEntity<Map<String, Object>> HTTP 응답 상태 코드(200 OK 등)와 함께 JSON 응답 결과를 담는 객체
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> receiveApartments(@RequestBody List<Apartment> apartments) {
        log.info("Received {} apartment records from scraper.", apartments != null ? apartments.size() : 0);

        // 전달받은 데이터가 없거나 비어있는 경우 빈 성공 메시지 응답 반환
        if (apartments == null || apartments.isEmpty()) {
            Map<String, Object> response = new HashMap<>();
            response.put("status", "SUCCESS");
            response.put("savedCount", 0);
            return ResponseEntity.ok(response);
        }

        // 서비스의 saveOrUpdateAll 메서드를 호출하여 DB 저장/수정 로직 수행
        List<Apartment> saved = apartmentService.saveOrUpdateAll(apartments);

        // 클라이언트에 전달할 응답 Map 생성
        Map<String, Object> response = new HashMap<>();
        response.put("status", "SUCCESS"); // 처리 상태
        response.put("savedCount", saved.size()); // 이번에 저장/수정 처리된 아파트 수
        response.put("totalCountInDb", apartmentService.getCount()); // 현재 DB에 누적 저장된 전체 아파트 수

        return ResponseEntity.ok(response); // HTTP 200 OK와 함께 JSON 응답 반환
    }

    /**
     * [저장된 전체 아파트 목록 조회 API]
     * HTTP Method: GET
     * URL Path: /api/apartments
     *
     * @return DB에 저장된 전체 아파트 엔티티 리스트 (JSON Array 형식으로 변환됨)
     */
    @GetMapping
    public ResponseEntity<List<Apartment>> getAllApartments() {
        return ResponseEntity.ok(apartmentService.getAllApartments());
    }

    /**
     * [저장된 아파트 총 개수 조회 API]
     * HTTP Method: GET
     * URL Path: /api/apartments/count
     *
     * @return {"totalCount": 150} 형태의 JSON 응답
     */
    @GetMapping("/count")
    public ResponseEntity<Map<String, Object>> getCount() {
        Map<String, Object> response = new HashMap<>();
        response.put("totalCount", apartmentService.getCount());
        return ResponseEntity.ok(response);
    }
}
