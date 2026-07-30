package com.example.realestate.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * [Apartment 엔티티 클래스]
 * 
 * JPA(Java Persistence API)를 사용하여 데이터베이스의 'apartments' 테이블과 1:1로 매핑되는 객체입니다.
 * 수집한 아파트 단지 정보 데이터를 데이터베이스에 저장하거나 조회할 때 사용됩니다.
 */
@Entity // 이 클래스가 JPA 엔티티(DB 테이블과 매핑되는 객체)임을 나타냅니다.
@Table(name = "apartments", indexes = {
    // complexNo(단지번호) 컬럼에 유니크(Unique) 인덱스를 생성하여 조회 성능을 높이고 중복 저장을 방지합니다.
    @Index(name = "idx_complex_no", columnList = "complexNo", unique = true)
})
@Getter // Lombok: 모든 필드의 Getter 메서드를 자동으로 생성해줍니다. (예: getComplexName())
@Setter // Lombok: 모든 필드의 Setter 메서드를 자동으로 생성해줍니다. (예: setComplexName())
@NoArgsConstructor // Lombok: 파라미터가 없는 기본 생성자(Default Constructor)를 생성해줍니다.
@AllArgsConstructor // Lombok: 모든 필드를 파라미터로 받는 생성자를 생성해줍니다.
@Builder // Lombok: 빌더 패턴(Builder Pattern)을 이용해 객체를 편리하게 생성할 수 있게 해줍니다.
public class Apartment {

    /**
     * 기본키 (Primary Key, PK)
     * @Id: 이 필드가 데이터베이스 테이블의 기본키임을 나타냅니다.
     * @GeneratedValue: 데이터베이스가 기본키 값을 자동으로 1씩 증가시키며 부여합니다. (Auto Increment)
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 네이버 아파트 단지 고유 번호 (예: "10234")
     * null 값을 허용하지 않고(nullable = false), DB 수준에서 중복 방지(unique = true)합니다.
     */
    @Column(nullable = false, unique = true)
    private String complexNo;

    // 아파트 단지 기본 정보
    private String complexName;         // 아파트 단지 이름 (예: "삼성래미안")
    private String cortarNo;            // 법정동 코드 (예: "1168010100")
    private String realEstateTypeCode;  // 부동산 유형 코드 (예: "A01")
    private String realEstateTypeName;  // 부동산 유형 이름 (예: "아파트")

    // 행정 구역 주소 정보 (스크래퍼가 파싱 시 추가해준 메타데이터)
    private String city;                // 시/도 (예: "서울특별시", "경기도")
    private String gu;                  // 시/군/구 (예: "강남구", "과천시")
    private String dong;                // 읍/면/동 (예: "역삼동")
    private String cortarAddress;       // 법정동 지번 주소

    // 상세 정보 및 위치 좌표
    private String detailAddress;       // 도로명 주소 또는 상세 주소
    private Double latitude;            // 위도 (Latitude)
    private Double longitude;           // 경도 (Longitude)

    // 아파트 건물 및 세대수 정보
    private Integer totalHouseholdCount; // 총 세대수
    private Integer totalBuildingCount;  // 총 동수 (건물 개수)
    private Integer highFloor;           // 최고 층수
    private Integer lowFloor;            // 최저 층수
    private String useApproveYmd;        // 사용승인일 (준공년월일, 예: "20081224")

    // 해당 단지의 현재 매물 수 정보
    private Integer dealCount;           // 매매 매물 수
    private Integer leaseCount;          // 전세 매물 수
    private Integer rentCount;           // 월세 매물 수
    private Integer shortTermRentCount;  // 단기임대 매물 수
}
