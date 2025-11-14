package com.virtplc.api;

import com.virtplc.model.TelemetryData;
import com.virtplc.service.TelemetryIngestionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * REST API for data ingestion from collectors.
 */
@RestController
@RequiredArgsConstructor
public class DataIngestionController {

    private final TelemetryIngestionService telemetryIngestionService;

    @PostMapping("/api/data/ingest")
    public ResponseEntity<Void> ingestData(@RequestBody List<TelemetryData> data) {
        data.forEach(telemetryIngestionService::ingestTelemetry);
        return ResponseEntity.ok().build();
    }
}