package com.example.realestate.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "apartments", indexes = {
    @Index(name = "idx_complex_no", columnList = "complexNo", unique = true)
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Apartment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String complexNo;

    private String complexName;
    private String cortarNo;
    private String realEstateTypeCode;
    private String realEstateTypeName;

    private String city;
    private String gu;
    private String dong;
    private String cortarAddress;

    private String detailAddress;
    private Double latitude;
    private Double longitude;

    private Integer totalHouseholdCount;
    private Integer totalBuildingCount;
    private Integer highFloor;
    private Integer lowFloor;
    private String useApproveYmd;

    private Integer dealCount;
    private Integer leaseCount;
    private Integer rentCount;
    private Integer shortTermRentCount;
}
