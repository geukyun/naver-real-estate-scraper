package com.example.realestate.repository;

import com.example.realestate.entity.Apartment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * [Apartment 데이터베이스 접근 인터페이스 (DAO/Repository)]
 *
 * Spring Data JPA의 JpaRepository를 상속받습니다.
 * JpaRepository<Apartment, Long>의 의미:
 * - Apartment: 다룰 엔티티 클래스
 * - Long: 엔티티의 기본키(@Id) 데이터 타입
 *
 * 이 인터페이스만 선언해두면, 스프링이 구현체 클래스를 자동으로 만들어주므로
 * 별도의 SQL 쿼리 작성 없이 findAll(), save(), findById(), count(), delete() 등을 바로 사용할 수 있습니다.
 */
@Repository
public interface ApartmentRepository extends JpaRepository<Apartment, Long> {

    /**
     * [쿼리 메서드 (Query Method)]
     * 메서드 이름 규칙(findBy + 필드명)에 따라 Spring Data JPA가 자동으로 SQL을 생성합니다.
     * 실행되는 SQL 예시: SELECT * FROM apartments WHERE complex_no = ?
     *
     * @param complexNo 검색할 아파트 단지 고유 번호
     * @return Optional<Apartment> 값이 존재할 수도, 없을(null) 수도 있는 객체를 안전하게 감싼 Wrapper
     */
    Optional<Apartment> findByComplexNo(String complexNo);
}
