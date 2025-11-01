package com.virtplc.repository;

import com.virtplc.model.Factory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FactoryRepository extends JpaRepository<Factory, Long> {
    Optional<Factory> findByFactoryId(String factoryId);

    boolean existsByFactoryId(String factoryId);

    List<Factory> findByManufacturerId(Long manufacturerId);
}