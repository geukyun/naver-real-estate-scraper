package com.example.realestate.service;

import com.example.realestate.entity.Apartment;
import com.example.realestate.repository.ApartmentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class ApartmentService {

    private final ApartmentRepository apartmentRepository;

    @Transactional
    public List<Apartment> saveOrUpdateAll(List<Apartment> apartments) {
        List<Apartment> savedList = new ArrayList<>();
        for (Apartment apt : apartments) {
            if (apt.getComplexNo() == null || apt.getComplexNo().isEmpty()) {
                continue;
            }

            Apartment existing = apartmentRepository.findByComplexNo(apt.getComplexNo()).orElse(null);
            if (existing != null) {
                // Update properties
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
                savedList.add(apartmentRepository.save(existing));
            } else {
                savedList.add(apartmentRepository.save(apt));
            }
        }
        log.info("Successfully processed {} apartment records.", savedList.size());
        return savedList;
    }

    @Transactional(readOnly = true)
    public List<Apartment> getAllApartments() {
        return apartmentRepository.findAll();
    }

    @Transactional(readOnly = true)
    public long getCount() {
        return apartmentRepository.count();
    }
}
