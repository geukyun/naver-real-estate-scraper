package com.example.realestate.service;

import com.example.realestate.entity.Apartment;
import com.example.realestate.repository.ApartmentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

/**
 * [아파트 데이터 비즈니스 로직 서비스 클래스]
 *
 * 컨트롤러(Controller)에서 요청을 받아 데이터베이스 처리(Repository) 작업을 담당합니다.
 * 트랜잭션 처리(@Transactional) 및 Upsert(이미 존재하는 단지는 수정, 없으면 신규 저장) 로직을 포함합니다.
 */
@Slf4j // Lombok: log.info(), log.error() 등의 로깅 기능을 자동으로 사용할 수 있게 해줍니다.
@Service // 이 클래스가 스프링의 비즈니스 로직을 처리하는 서비스 컴포넌트임을 명시합니다.
@RequiredArgsConstructor // Lombok: final이 붙은 필드를 인자로 받는 생성자를 자동 생성하여 의존성을 주입(DI)받습니다.
public class ApartmentService {

    // 데이터베이스 작업을 실행할 Repository 객체를 의존성 주입받습니다.
    private final ApartmentRepository apartmentRepository;

    /**
     * [아파트 단지 목록 일괄 저장 및 업데이트 (Upsert 로직)]
     *
     * 크롤러가 수집한 아파트 목록을 받아서:
     * 1. 이미 DB에 해당 complexNo(단지번호)가 존재하면 최신 정보로 업데이트(Update)
     * 2. DB에 존재하지 않는 새로운 단지라면 신규 저장(Insert)
     *
     * @Transactional: 이 메서드 내의 모든 DB 작업이 하나의 트랜잭션 단위로 묶입니다. 중간에 예외가 발생하면 롤백(Rollback)됩니다.
     *
     * @param apartments 크롤러에서 전달받은 아파트 엔티티 리스트
     * @return 저장/수정 완료된 아파트 엔티티 리스트
     */
    @Transactional
    public List<Apartment> saveOrUpdateAll(List<Apartment> apartments) {
        List<Apartment> savedList = new ArrayList<>();

        for (Apartment apt : apartments) {
            // 단지 번호(complexNo)가 누락된 유효하지 않은 데이터는 건너뜁니다.
            if (apt.getComplexNo() == null || apt.getComplexNo().isEmpty()) {
                continue;
            }

            // 1. 단지 번호로 기존 DB에 동일한 아파트 데이터가 존재하는지 조회합니다.
            Apartment existing = apartmentRepository.findByComplexNo(apt.getComplexNo()).orElse(null);

            if (existing != null) {
                // [기존 데이터가 있는 경우: Update]
                // 기존 객체의 속성 값들을 새로 수집한 데이터로 덮어씌웁니다. (영속성 컨텍스트에 의해 트랜잭션 종료 시 자동 반영됨)
                existing.setComplexName(apt.getComplexName());
                existing.setCortarNo(apt.getCortarNo());
                existing.setRealEstateTypeCode(apt.getRealEstateTypeCode());
                existing.setRealEstateTypeName(apt.getRealEstateTypeName());
                existing.setCity(apt.getCity());
                existing.setGu(apt.getGu());
                existing.setDong(apt.getDong());
                existing.setCortarAddress(apt.getCortarAddress());
                existing.setDetailAddress(apt.getDetailAddress());
                existing.setLatitude(apt.getLatitude());
                existing.setLongitude(apt.getLongitude());
                existing.setTotalHouseholdCount(apt.getTotalHouseholdCount());
                existing.setTotalBuildingCount(apt.getTotalBuildingCount());
                existing.setHighFloor(apt.getHighFloor());
                existing.setLowFloor(apt.getLowFloor());
                existing.setUseApproveYmd(apt.getUseApproveYmd());
                existing.setDealCount(apt.getDealCount());
                existing.setLeaseCount(apt.getLeaseCount());
                existing.setRentCount(apt.getRentCount());
                existing.setShortTermRentCount(apt.getShortTermRentCount());

                // 변경된 데이터를 DB에 저장 후 리스트에 추가
                savedList.add(apartmentRepository.save(existing));
            } else {
                // [기존 데이터가 없는 경우: Insert]
                // 신규 데이터이므로 그대로 DB에 저장 후 리스트에 추가
                savedList.add(apartmentRepository.save(apt));
            }
        }

        log.info("Successfully processed {} apartment records.", savedList.size());
        return savedList;
    }

    /**
     * [저장된 전체 아파트 목록 조회]
     * @Transactional(readOnly = true): 읽기 전용 트랜잭션 모드로 설정하여 조회 성능을 최적화합니다.
     */
    @Transactional(readOnly = true)
    public List<Apartment> getAllApartments() {
        return apartmentRepository.findAll();
    }

    /**
     * [저장된 전체 아파트 개수 조회]
     */
    @Transactional(readOnly = true)
    public long getCount() {
        return apartmentRepository.count();
    }
}
