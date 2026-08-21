package com.storybridge.service;

import com.storybridge.domain.Enums;
import com.storybridge.repository.PipelineJobRepository;
import com.storybridge.repository.StoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
public class AsyncPipelineExecutor {

    private final AIEngineClient aiEngineClient;
    private final PipelineJobRepository jobRepository;
    private final StoryRepository storyRepository;

    public void executeAsync(
            String jobId,
            String storyId,
            String title,
            String author,
            String contentOrPath,
            List<String> presets,
            List<String> languages,
            Runnable onArtifactsReady
    ) {
        CompletableFuture.runAsync(() -> {
            try {
                updateJobStatus(jobId, Enums.JobStage.NORMALIZED, Enums.JobStatus.PROCESSING, 20, "Calling AI Engine Pipeline...");

                Map<String, Object> request = new HashMap<>();
                request.put("story_id", storyId);
                request.put("title", title != null ? title : "Untitled Story");
                request.put("author", author != null ? author : "Unknown");
                request.put("content_or_path", contentOrPath != null ? contentOrPath : "");
                request.put("duration_presets", (presets != null && !presets.isEmpty()) ? presets : List.of("quick", "standard"));
                request.put("languages", (languages != null && !languages.isEmpty()) ? languages : List.of("hi", "mr"));

                log.info("Sending pipeline request to AI Engine for story {}", storyId);
                Map<String, Object> response = aiEngineClient.triggerPipelineJob(request);
                log.info("AI Engine response for story {}: {}", storyId, response);

                String aiJobId = response != null && response.get("job_id") != null ? response.get("job_id").toString() : null;

                updateJobStatus(jobId, Enums.JobStage.UNDERSTANDING_READY, Enums.JobStatus.PROCESSING, 40, "AI Engine processing story graph and compression...");

                // Poll AI Engine job
                if (aiJobId != null) {
                    int attempts = 0;
                    boolean completed = false;
                    while (attempts < 90 && !completed) {
                        Thread.sleep(2000);
                        attempts++;
                        Map<String, Object> statusResp = aiEngineClient.getJobStatus(aiJobId);
                        String status = statusResp != null && statusResp.get("status") != null ? statusResp.get("status").toString() : "";

                        if ("COMPLETED".equalsIgnoreCase(status)) {
                            completed = true;
                        } else if ("FAILED".equalsIgnoreCase(status)) {
                            String errMsg = statusResp.get("error") != null ? statusResp.get("error").toString() : "AI Engine execution failed";
                            throw new RuntimeException("AI Engine reported failure: " + errMsg);
                        } else {
                            int pct = Math.min(85, 40 + attempts);
                            updateJobStatus(jobId, Enums.JobStage.LOCALIZATION_GENERATED, Enums.JobStatus.PROCESSING, pct, "AI Engine generating narrative & audio (" + (attempts * 2) + "s)...");
                        }
                    }
                }

                // Sync artifacts into database
                updateJobStatus(jobId, Enums.JobStage.AUDIO_GENERATED, Enums.JobStatus.PROCESSING, 90, "Registering artifacts in database...");
                if (onArtifactsReady != null) {
                    onArtifactsReady.run();
                }

                updateJobStatus(jobId, Enums.JobStage.AUDIO_GENERATED, Enums.JobStatus.COMPLETED, 100, "Pipeline Execution Completed Successfully");

                storyRepository.findById(storyId).ifPresent(story -> {
                    story.setStatus(Enums.PublicationStatus.PUBLISHED);
                    storyRepository.save(story);
                });

                log.info("Pipeline job {} for story {} completed successfully", jobId, storyId);

            } catch (Exception e) {
                log.error("Pipeline job {} failed: {}", jobId, e.getMessage());
                updateJobStatus(jobId, Enums.JobStage.FAILED, Enums.JobStatus.FAILED, 0, "Failed: " + e.getMessage());
                storyRepository.findById(storyId).ifPresent(story -> {
                    story.setStatus(Enums.PublicationStatus.DRAFT);
                    storyRepository.save(story);
                });
            }
        });
    }

    private void updateJobStatus(String jobId, Enums.JobStage stage, Enums.JobStatus status, int progress, String step) {
        jobRepository.findById(jobId).ifPresent(job -> {
            job.setStage(stage);
            job.setStatus(status);
            job.setProgressPercentage(progress);
            job.setCurrentStep(step);
            job.setUpdatedAt(LocalDateTime.now());
            jobRepository.save(job);
        });
    }
}
