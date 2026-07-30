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

@Slf4j
@RestController
@RequestMapping("/api/apartments")
@RequiredArgsConstructor
public class ApartmentController {

    private final ApartmentService apartmentService;

    @PostMapping
    public ResponseEntity<Map<String, Object>> receiveApartments(@RequestBody List<Apartment> apartments) {
        log.info("Received {} apartment records from scraper.", apartments != null ? apartments.size() : 0);
        if (apartments == null || apartments.isEmpty()) {
            Map<String, Object> response = new HashMap<>();
            response.put("status", "SUCCESS");
            response.put("savedCount", 0);
            return ResponseEntity.ok(response);
        }

        List<Apartment> saved = apartmentService.saveOrUpdateAll(apartments);
        Map<String, Object> response = new HashMap<>();
        response.put("status", "SUCCESS");
        response.put("savedCount", saved.size());
        response.put("totalCountInDb", apartmentService.getCount());
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<List<Apartment>> getAllApartments() {
        return ResponseEntity.ok(apartmentService.getAllApartments());
    }

    @GetMapping("/count")
    public ResponseEntity<Map<String, Object>> getCount() {
        Map<String, Object> response = new HashMap<>();
        response.put("totalCount", apartmentService.getCount());
        return ResponseEntity.ok(response);
    }
}
