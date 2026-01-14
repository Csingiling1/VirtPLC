package com.virtplc.api;

import com.virtplc.model.Factory;
import com.virtplc.model.User;
import com.virtplc.service.FactoryService;
import com.virtplc.service.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/factories")
@RequiredArgsConstructor
@Slf4j
public class FactoryController {

    private final FactoryService factoryService;
    private final AuthService authService;

    @GetMapping
    public ResponseEntity<?> getFactories(@RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid authorization header"));
            }

            String token = authHeader.substring(7);
            var userOpt = authService.getUserFromToken(token);

            if (userOpt.isEmpty()) {
                return ResponseEntity.status(401).body(Map.of("error", "Invalid token"));
            }

            User user = userOpt.get();
            List<Factory> factories = factoryService.getFactoriesForUser(user);

            return ResponseEntity.ok(Map.of(
                    "factories", factories.stream().map(factory -> {
                        Map<String, Object> factoryMap = new HashMap<>();
                        factoryMap.put("id", factory.getId());
                        factoryMap.put("factoryId", factory.getFactoryId());
                        factoryMap.put("name", factory.getName());
                        factoryMap.put("description", factory.getDescription() != null ? factory.getDescription() : "");
                        factoryMap.put("isActive", factory.getIsActive());

                        if (factory.getManufacturer() != null) {
                            Map<String, Object> mfgMap = new HashMap<>();
                            mfgMap.put("id", factory.getManufacturer().getId());
                            mfgMap.put("name", factory.getManufacturer().getName());
                            mfgMap.put("manufacturerId", factory.getManufacturer().getManufacturerId());
                            factoryMap.put("manufacturer", mfgMap);
                        } else {
                            factoryMap.put("manufacturer", null);
                        }

                        factoryMap.put("shape", factory.getShape());
                        factoryMap.put("width", factory.getWidth());
                        factoryMap.put("height", factory.getHeight());
                        factoryMap.put("widthMeters", factory.getWidthMeters());
                        factoryMap.put("heightMeters", factory.getHeightMeters());
                        factoryMap.put("wireframeColor", factory.getWireframeColor());

                        return factoryMap;
                    }).collect(Collectors.toList())));
        } catch (Exception e) {
            log.error("Error getting factories: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Failed to get factories",
                    "message", e.getMessage()));
        }
    }

    @GetMapping("/{factoryId}")
    public ResponseEntity<?> getFactory(@PathVariable String factoryId,
            @RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid authorization header"));
            }

            String token = authHeader.substring(7);
            var userOpt = authService.getUserFromToken(token);

            if (userOpt.isEmpty()) {
                return ResponseEntity.status(401).body(Map.of("error", "Invalid token"));
            }

            User user = userOpt.get();
            var factoryOpt = factoryService.getFactoryForUser(factoryId, user);

            if (factoryOpt.isEmpty()) {
                return ResponseEntity.status(404).body(Map.of("error", "Factory not found or access denied"));
            }

            Factory factory = factoryOpt.get();
            Map<String, Object> response = new HashMap<>();
            response.put("id", factory.getId());
            response.put("factoryId", factory.getFactoryId());
            response.put("name", factory.getName());
            response.put("description", factory.getDescription() != null ? factory.getDescription() : "");
            response.put("isActive", factory.getIsActive());

            if (factory.getManufacturer() != null) {
                Map<String, Object> mfgMap = new HashMap<>();
                mfgMap.put("id", factory.getManufacturer().getId());
                mfgMap.put("name", factory.getManufacturer().getName());
                mfgMap.put("manufacturerId", factory.getManufacturer().getManufacturerId());
                response.put("manufacturer", mfgMap);
            } else {
                response.put("manufacturer", null);
            }

            response.put("shape", factory.getShape());
            response.put("width", factory.getWidth());
            response.put("height", factory.getHeight());
            response.put("widthMeters", factory.getWidthMeters());
            response.put("heightMeters", factory.getHeightMeters());
            response.put("wireframeColor", factory.getWireframeColor());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error getting factory: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Failed to get factory",
                    "message", e.getMessage()));
        }
    }
}
