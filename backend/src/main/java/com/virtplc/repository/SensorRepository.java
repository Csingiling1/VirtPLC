package com.virtplc.repository;

import com.virtplc.model.Sensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SensorRepository extends JpaRepository<Sensor, Long> {
    Optional<Sensor> findBySensorId(String sensorId);

    boolean existsBySensorId(String sensorId);

    List<Sensor> findByPlcId(Long plcId);
}