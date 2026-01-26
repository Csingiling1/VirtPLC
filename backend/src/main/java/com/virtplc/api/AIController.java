package com.virtplc.api;

import com.virtplc.service.AIService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/ai")
public class AIController {

    @Autowired
    private AIService aiService;

    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@RequestBody Map<String, Object> request) {
        try {
            String message = (String) request.get("message");
            String context = (String) request.get("context");
            String model = (String) request.getOrDefault("model", "ollama");

            Map<String, Object> response = aiService.chat(message, context, model);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Failed to process chat request",
                    "message", e.getMessage()));
        }
    }

    @PostMapping("/analyze")
    public ResponseEntity<Map<String, Object>> analyze(@RequestBody Map<String, Object> data) {
        try {
            Map<String, Object> analysis = aiService.analyzeData(data);
            return ResponseEntity.ok(analysis);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Failed to analyze data",
                    "message", e.getMessage()));
        }
    }

    @GetMapping("/insights")
    public ResponseEntity<Map<String, Object>> getInsights(
            @RequestParam(required = false) Long start,
            @RequestParam(required = false) Long end) {
        try {
            Map<String, Object> insights = aiService.getInsights(start, end);
            return ResponseEntity.ok(insights);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Failed to get insights",
                    "message", e.getMessage()));
        }
    }
}