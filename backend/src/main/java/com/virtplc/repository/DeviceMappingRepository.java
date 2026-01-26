package com.virtplc.repository;

import com.virtplc.model.Device;
import com.virtplc.model.DeviceMapping;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository for DeviceMapping entities.
 * Provides JPA-based data access for device mapping configurations.
 */
@Repository
public interface DeviceMappingRepository extends JpaRepository<DeviceMapping, Long> {

    List<DeviceMapping> findByDeviceAndIsActiveTrue(Device device);

    List<DeviceMapping> findByDevice_DeviceIdAndIsActiveTrue(String deviceId);

    List<DeviceMapping> findByFieldNameAndIsActiveTrue(String fieldName);

    @Query("SELECT dm FROM DeviceMapping dm WHERE dm.device.deviceId IN :deviceIds AND dm.isActive = true")
    List<DeviceMapping> findActiveMappingsByDeviceIds(@Param("deviceIds") List<String> deviceIds);

    @Query("SELECT dm FROM DeviceMapping dm WHERE dm.device.isActive = true AND dm.isActive = true")
    List<DeviceMapping> findAllActiveMappings();
}