package com.virtplc.repository;

import com.virtplc.model.Device;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for Device entities.
 * Provides JPA-based data access for device management.
 */
@Repository
public interface DeviceRepository extends JpaRepository<Device, Long> {

    Optional<Device> findByDeviceId(String deviceId);

    List<Device> findByIsActiveTrue();

    List<Device> findByDeviceType(String deviceType);

    List<Device> findByManufacturerIdAndIsActiveTrue(String manufacturerId);

    @Query("SELECT d FROM Device d WHERE d.isActive = true AND d.deviceId IN :deviceIds")
    List<Device> findActiveDevicesByIds(@Param("deviceIds") List<String> deviceIds);

    boolean existsByDeviceId(String deviceId);
}