package com.virtplc.controller;

import com.virtplc.model.Device;
import com.virtplc.model.DeviceMapping;
import com.virtplc.service.DeviceManagementService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for device management operations.
 * Provides endpoints for CRUD operations on devices and their mappings.
 */
@RestController
@RequestMapping("/api/devices")
@RequiredArgsConstructor
@Tag(name = "Device Management", description = "Endpoints for managing PLC devices and their data mappings")
public class DeviceManagementController {

    private final DeviceManagementService deviceManagementService;

    /**
     * Get all devices.
     */
    @GetMapping
    @Operation(summary = "Get all devices", description = "Retrieves a list of all registered PLC devices in the system", responses = {
            @ApiResponse(responseCode = "200", description = "Devices retrieved successfully", content = @Content(mediaType = "application/json", schema = @Schema(implementation = Device.class)))
    })
    public ResponseEntity<List<Device>> getAllDevices() {
        List<Device> devices = deviceManagementService.getAllDevices();
        return ResponseEntity.ok(devices);
    }

    /**
     * Get active devices.
     */
    @GetMapping("/active")
    @Operation(summary = "Get active devices", description = "Retrieves a list of all currently active PLC devices", responses = {
            @ApiResponse(responseCode = "200", description = "Active devices retrieved successfully", content = @Content(mediaType = "application/json", schema = @Schema(implementation = Device.class)))
    })
    public ResponseEntity<List<Device>> getActiveDevices() {
        List<Device> devices = deviceManagementService.getActiveDevices();
        return ResponseEntity.ok(devices);
    }

    /**
     * Get device by ID.
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get device by ID", description = "Retrieves a specific PLC device by its unique identifier", parameters = {
            @Parameter(name = "id", description = "Device ID", required = true, example = "1")
    }, responses = {
            @ApiResponse(responseCode = "200", description = "Device found", content = @Content(mediaType = "application/json", schema = @Schema(implementation = Device.class))),
            @ApiResponse(responseCode = "404", description = "Device not found")
    })
    public ResponseEntity<Device> getDeviceById(@PathVariable Long id) {
        return deviceManagementService.getDeviceById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get device by device ID.
     */
    @GetMapping("/by-device-id/{deviceId}")
    public ResponseEntity<Device> getDeviceByDeviceId(@PathVariable String deviceId) {
        return deviceManagementService.getDeviceByDeviceId(deviceId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Create a new device.
     */
    @PostMapping
    public ResponseEntity<Device> createDevice(@RequestBody Device device) {
        try {
            Device createdDevice = deviceManagementService.createDevice(device);
            return ResponseEntity.ok(createdDevice);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Update an existing device.
     */
    @PutMapping("/{id}")
    public ResponseEntity<Device> updateDevice(@PathVariable Long id, @RequestBody Device device) {
        try {
            Device updatedDevice = deviceManagementService.updateDevice(id, device);
            return ResponseEntity.ok(updatedDevice);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Delete a device.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDevice(@PathVariable Long id) {
        try {
            deviceManagementService.deleteDevice(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Get mappings for a device.
     */
    @GetMapping("/{deviceId}/mappings")
    public ResponseEntity<List<DeviceMapping>> getDeviceMappings(@PathVariable Long deviceId) {
        try {
            List<DeviceMapping> mappings = deviceManagementService.getDeviceMappings(deviceId);
            return ResponseEntity.ok(mappings);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Create a device mapping.
     */
    @PostMapping("/{deviceId}/mappings")
    public ResponseEntity<DeviceMapping> createDeviceMapping(@PathVariable Long deviceId,
            @RequestBody DeviceMapping mapping) {
        try {
            // Set the device
            Device device = deviceManagementService.getDeviceById(deviceId)
                    .orElseThrow(() -> new IllegalArgumentException("Device not found"));
            mapping.setDevice(device);

            DeviceMapping createdMapping = deviceManagementService.createDeviceMapping(mapping);
            return ResponseEntity.ok(createdMapping);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Update a device mapping.
     */
    @PutMapping("/mappings/{mappingId}")
    public ResponseEntity<DeviceMapping> updateDeviceMapping(@PathVariable Long mappingId,
            @RequestBody DeviceMapping mapping) {
        try {
            DeviceMapping updatedMapping = deviceManagementService.updateDeviceMapping(mappingId, mapping);
            return ResponseEntity.ok(updatedMapping);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Delete a device mapping.
     */
    @DeleteMapping("/mappings/{mappingId}")
    public ResponseEntity<Void> deleteDeviceMapping(@PathVariable Long mappingId) {
        try {
            deviceManagementService.deleteDeviceMapping(mappingId);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Get all active device mappings.
     */
    @GetMapping("/mappings/active")
    public ResponseEntity<List<DeviceMapping>> getAllActiveMappings() {
        List<DeviceMapping> mappings = deviceManagementService.getAllActiveMappings();
        return ResponseEntity.ok(mappings);
    }
}