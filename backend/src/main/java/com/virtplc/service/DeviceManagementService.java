package com.virtplc.service;

import com.virtplc.model.Device;
import com.virtplc.model.DeviceMapping;
import com.virtplc.repository.DeviceMappingRepository;
import com.virtplc.repository.DeviceRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * Service for managing device configurations and mappings.
 * Provides CRUD operations for devices and their data mappings.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DeviceManagementService {

    private final DeviceRepository deviceRepository;
    private final DeviceMappingRepository deviceMappingRepository;
    private final GenericDeviceMappingService mappingService;

    /**
     * Create a new device.
     */
    @Transactional
    public Device createDevice(Device device) {
        if (deviceRepository.existsByDeviceId(device.getDeviceId())) {
            throw new IllegalArgumentException("Device with ID " + device.getDeviceId() + " already exists");
        }

        Device savedDevice = deviceRepository.save(device);
        log.info("Created new device: {}", savedDevice.getDeviceId());

        // Clear mapping cache to ensure new device is recognized
        mappingService.clearMappingCache();

        return savedDevice;
    }

    /**
     * Update an existing device.
     */
    @Transactional
    public Device updateDevice(Long deviceId, Device updatedDevice) {
        Device existingDevice = deviceRepository.findById(deviceId)
                .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        // Check if deviceId is being changed and if it's already taken
        if (!existingDevice.getDeviceId().equals(updatedDevice.getDeviceId()) &&
                deviceRepository.existsByDeviceId(updatedDevice.getDeviceId())) {
            throw new IllegalArgumentException("Device ID " + updatedDevice.getDeviceId() + " already exists");
        }

        existingDevice.setDeviceId(updatedDevice.getDeviceId());
        existingDevice.setDeviceName(updatedDevice.getDeviceName());
        existingDevice.setDeviceType(updatedDevice.getDeviceType());
        existingDevice.setManufacturerId(updatedDevice.getManufacturerId());
        existingDevice.setFactoryId(updatedDevice.getFactoryId());
        existingDevice.setPlcId(updatedDevice.getPlcId());
        existingDevice.setDescription(updatedDevice.getDescription());
        existingDevice.setIsActive(updatedDevice.getIsActive());
        existingDevice.setDataTimeoutSeconds(updatedDevice.getDataTimeoutSeconds());

        Device savedDevice = deviceRepository.save(existingDevice);
        log.info("Updated device: {}", savedDevice.getDeviceId());

        // Clear mapping cache
        mappingService.clearMappingCache();

        return savedDevice;
    }

    /**
     * Delete a device and its mappings.
     */
    @Transactional
    public void deleteDevice(Long deviceId) {
        Device device = deviceRepository.findById(deviceId)
                .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        // Delete mappings first
        List<DeviceMapping> mappings = deviceMappingRepository.findByDeviceAndIsActiveTrue(device);
        deviceMappingRepository.deleteAll(mappings);

        // Delete device
        deviceRepository.delete(device);
        log.info("Deleted device: {}", device.getDeviceId());

        // Clear mapping cache
        mappingService.clearMappingCache();
    }

    /**
     * Get all devices.
     */
    @Transactional(readOnly = true)
    public List<Device> getAllDevices() {
        return deviceRepository.findAll();
    }

    /**
     * Get active devices.
     */
    @Transactional(readOnly = true)
    public List<Device> getActiveDevices() {
        return deviceRepository.findByIsActiveTrue();
    }

    /**
     * Get device by ID.
     */
    @Transactional(readOnly = true)
    public Optional<Device> getDeviceById(Long id) {
        return deviceRepository.findById(id);
    }

    /**
     * Get device by device ID.
     */
    @Transactional(readOnly = true)
    public Optional<Device> getDeviceByDeviceId(String deviceId) {
        return deviceRepository.findByDeviceId(deviceId);
    }

    /**
     * Create a device mapping.
     */
    @Transactional
    public DeviceMapping createDeviceMapping(DeviceMapping mapping) {
        DeviceMapping savedMapping = deviceMappingRepository.save(mapping);
        log.info("Created mapping for device {}: field {}", mapping.getDevice().getDeviceId(), mapping.getFieldName());

        // Clear mapping cache
        mappingService.clearMappingCache();

        return savedMapping;
    }

    /**
     * Update a device mapping.
     */
    @Transactional
    public DeviceMapping updateDeviceMapping(Long mappingId, DeviceMapping updatedMapping) {
        DeviceMapping existingMapping = deviceMappingRepository.findById(mappingId)
                .orElseThrow(() -> new IllegalArgumentException("Device mapping not found: " + mappingId));

        existingMapping.setFieldName(updatedMapping.getFieldName());
        existingMapping.setFieldType(updatedMapping.getFieldType());
        existingMapping.setValuePath(updatedMapping.getValuePath());
        existingMapping.setStatusPath(updatedMapping.getStatusPath());
        existingMapping.setUnit(updatedMapping.getUnit());
        existingMapping.setMultiplier(updatedMapping.getMultiplier());
        existingMapping.setOffset(updatedMapping.getOffset());
        existingMapping.setIsActive(updatedMapping.getIsActive());

        DeviceMapping savedMapping = deviceMappingRepository.save(existingMapping);
        log.info("Updated mapping for device {}: field {}", existingMapping.getDevice().getDeviceId(),
                savedMapping.getFieldName());

        // Clear mapping cache
        mappingService.clearMappingCache();

        return savedMapping;
    }

    /**
     * Delete a device mapping.
     */
    @Transactional
    public void deleteDeviceMapping(Long mappingId) {
        DeviceMapping mapping = deviceMappingRepository.findById(mappingId)
                .orElseThrow(() -> new IllegalArgumentException("Device mapping not found: " + mappingId));

        deviceMappingRepository.delete(mapping);
        log.info("Deleted mapping for device {}: field {}", mapping.getDevice().getDeviceId(), mapping.getFieldName());

        // Clear mapping cache
        mappingService.clearMappingCache();
    }

    /**
     * Get mappings for a device.
     */
    @Transactional(readOnly = true)
    public List<DeviceMapping> getDeviceMappings(Long deviceId) {
        Device device = deviceRepository.findById(deviceId)
                .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        return deviceMappingRepository.findByDeviceAndIsActiveTrue(device);
    }

    /**
     * Get all active device mappings.
     */
    @Transactional(readOnly = true)
    public List<DeviceMapping> getAllActiveMappings() {
        return deviceMappingRepository.findAllActiveMappings();
    }
}