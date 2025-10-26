package com.virtplc.repository;

import com.virtplc.model.SensorDataEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository for sensor data stored in TimescaleDB.
 * Provides time-series optimized queries.
 */
@Repository
public interface SensorDataRepository extends JpaRepository<SensorDataEntity, Long> {

    /**
     * Find sensor data within a timestamp range.
     */
    List<SensorDataEntity> findByTimestampBetween(LocalDateTime startTime, LocalDateTime endTime);

    /**
     * Find sensor data for a specific device within a timestamp range.
     */
    List<SensorDataEntity> findByDeviceIdAndTimestampBetween(String deviceId, LocalDateTime startTime, LocalDateTime endTime);

    /**
     * Find the latest sensor data for a device.
     */
    @Query("SELECT s FROM SensorDataEntity s WHERE s.deviceId = :deviceId ORDER BY s.timestamp DESC LIMIT 1")
    SensorDataEntity findLatestByDeviceId(@Param("deviceId") String deviceId);

    /**
     * Get average motor speeds over time range.
     */
    @Query("SELECT AVG(s.motor1Speed), AVG(s.motor2Speed) FROM SensorDataEntity s WHERE s.timestamp BETWEEN :startTime AND :endTime")
    Object[] getAverageMotorSpeeds(@Param("startTime") LocalDateTime startTime, @Param("endTime") LocalDateTime endTime);

    /**
     * Get temperature statistics over time range.
     */
    @Query("SELECT MIN(s.motor1Temp), MAX(s.motor1Temp), AVG(s.motor1Temp) FROM SensorDataEntity s WHERE s.timestamp BETWEEN :startTime AND :endTime")
    Object[] getMotor1TemperatureStats(@Param("startTime") LocalDateTime startTime, @Param("endTime") LocalDateTime endTime);
}