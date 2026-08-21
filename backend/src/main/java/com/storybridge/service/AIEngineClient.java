package com.storybridge.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@Service
@Slf4j
public class AIEngineClient {

    private final RestClient restClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public AIEngineClient(@Value("${storybridge.ai-engine.base-url:http://localhost:8000}") String baseUrl) {
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .defaultHeader("Accept", MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader("Content-Type", MediaType.APPLICATION_JSON_VALUE)
                .build();
    }

    public Map<String, Object> checkHealth() {
        try {
            return restClient.get()
                    .uri("/api/v1/health")
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.warn("AI Engine health check failed: {}", e.getMessage());
            return Map.of("status", "unreachable", "error", e.getMessage());
        }
    }

    public Map<String, Object> triggerPipelineJob(Map<String, Object> requestBody) {
        try {
            byte[] jsonBytes = objectMapper.writeValueAsBytes(requestBody != null ? requestBody : Map.of());
            String storyId = requestBody != null && requestBody.get("story_id") != null ? requestBody.get("story_id").toString() : "";
            log.info("Dispatching pipeline trigger to AI Engine for storyId '{}': {}", storyId, new String(jsonBytes, StandardCharsets.UTF_8));
            
            return restClient.post()
                    .uri(uriBuilder -> uriBuilder
                            .path("/api/v1/pipeline/run")
                            .queryParam("story_id", storyId)
                            .build())
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(jsonBytes)
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.error("Failed to trigger pipeline job on AI Engine: {}", e.getMessage());
            throw new RuntimeException("AI Engine pipeline trigger failed: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> getJobStatus(String jobId) {
        try {
            return restClient.get()
                    .uri("/api/v1/pipeline/jobs/{jobId}", jobId)
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.warn("Failed to get job status from AI engine for {}: {}", jobId, e.getMessage());
            return Map.of("status", "UNKNOWN", "error", e.getMessage());
        }
    }
}
