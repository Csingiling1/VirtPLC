package com.virtplc.repository;

import com.virtplc.model.PLC;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PLCRepository extends JpaRepository<PLC, Long> {
    Optional<PLC> findByPlcId(String plcId);

    boolean existsByPlcId(String plcId);

    List<PLC> findByFactoryId(Long factoryId);
}