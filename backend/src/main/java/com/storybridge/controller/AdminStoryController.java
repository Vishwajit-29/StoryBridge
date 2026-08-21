package com.storybridge.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.storybridge.domain.Enums;
import com.storybridge.domain.PipelineJobEntity;
import com.storybridge.domain.Story;
import com.storybridge.service.PipelineJobService;
import com.storybridge.service.StorageService;
import com.storybridge.service.StoryService;
import com.storybridge.service.WorkflowService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/admin/stories")
@RequiredArgsConstructor
@Slf4j
public class AdminStoryController {

    private final StoryService storyService;
    private final WorkflowService workflowService;
    private final PipelineJobService pipelineJobService;
    private final StorageService storageService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping
    public ResponseEntity<List<Story>> getAllStories() {
        return ResponseEntity.ok(storyService.getAllStoriesAdmin());
    }

    @Data
    public static class CreateStoryRequest {
        private String id;
        private String title;
        private String originalAuthor;
        private String originalLanguage;
        private String category;
        private String description;
        private String coverImageUrl;
        private Enums.RightsType rightsType;
        private boolean rightsVerified;
        private String rightsEvidence;
    }

    @PostMapping
    public ResponseEntity<Story> createStory(@RequestBody CreateStoryRequest req) {
        String storyId = req.getId();
        if (storyId == null || storyId.isBlank() || storyId.replaceAll("[^a-zA-Z0-9]", "").isBlank()) {
            String titleText = req.getTitle() != null ? req.getTitle() : "story";
            String slug = titleText.toLowerCase().replaceAll("[^a-z0-9]+", "_").replaceAll("^_+|_+$", "");
            if (slug.isBlank()) {
                slug = "story";
            }
            storyId = slug + "_" + UUID.randomUUID().toString().replace("-", "").substring(0, 6);
        }

        Story story = Story.builder()
                .id(storyId)
                .title(req.getTitle() != null && !req.getTitle().isBlank() ? req.getTitle() : "Untitled Story")
                .originalAuthor(req.getOriginalAuthor() != null ? req.getOriginalAuthor() : "Unknown")
                .originalLanguage(req.getOriginalLanguage() != null ? req.getOriginalLanguage() : "en")
                .category(req.getCategory() != null ? req.getCategory() : "Mythology & Folklore")
                .description(req.getDescription() != null ? req.getDescription() : "")
                .coverImageUrl(req.getCoverImageUrl())
                .rightsType(req.getRightsType() != null ? req.getRightsType() : Enums.RightsType.PUBLIC_DOMAIN)
                .rightsVerified(req.isRightsVerified())
                .rightsEvidence(req.getRightsEvidence() != null ? req.getRightsEvidence() : "Public Domain verified")
                .status(Enums.PublicationStatus.DRAFT)
                .totalWords(0)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        return ResponseEntity.ok(storyService.createOrUpdateStory(story));
    }

    @Data
    public static class VerifyRightsRequest {
        private Enums.RightsType rightsType;
        private boolean verified;
        private String evidence;
    }

    @PostMapping("/{id}/verify-rights")
    public ResponseEntity<Story> verifyRights(
            @PathVariable String id,
            @RequestBody VerifyRightsRequest req,
            Authentication auth
    ) {
        return ResponseEntity.ok(
                workflowService.verifyStoryRights(id, req.getRightsType(), req.isVerified(), req.getEvidence(), auth != null ? auth.getName() : "admin")
        );
    }

    @Data
    public static class TriggerPipelineRequest {
        private String sourceText;
        private String sourceFormat;
        private String fileName;
        private List<String> durationPresets;
        private List<String> languages;
    }

    @PostMapping("/{id}/pipeline/trigger")
    public ResponseEntity<PipelineJobEntity> triggerPipeline(
            @PathVariable String id,
            @RequestBody TriggerPipelineRequest req
    ) {
        PipelineJobEntity job = pipelineJobService.triggerPipeline(
                id,
                req.getSourceText(),
                req.getSourceFormat() != null ? req.getSourceFormat() : "markdown",
                req.getFileName() != null ? req.getFileName() : "source.txt",
                req.getDurationPresets(),
                req.getLanguages()
        );
        return ResponseEntity.ok(job);
    }

    @PostMapping("/{id}/upload-source")
    public ResponseEntity<Map<String, String>> uploadSource(
            @PathVariable String id,
            @RequestParam("file") MultipartFile file
    ) throws IOException {
        String filename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "source.txt";
        String storedPath = storageService.storeFile(id, "source/raw/" + filename, file);
        return ResponseEntity.ok(Map.of("storedPath", storedPath, "filename", filename));
    }

    @PostMapping("/{id}/publish")
    public ResponseEntity<Story> publishStory(@PathVariable String id, Authentication auth) {
        return ResponseEntity.ok(workflowService.publishStory(id, auth != null ? auth.getName() : "admin"));
    }

    @PostMapping("/{id}/unpublish")
    public ResponseEntity<Story> unpublishStory(
            @PathVariable String id,
            @RequestParam(defaultValue = "Admin decision") String reason,
            Authentication auth
    ) {
        return ResponseEntity.ok(workflowService.unpublishStory(id, reason, auth != null ? auth.getName() : "admin"));
    }

    @PostMapping("/{id}/sync-artifacts")
    public ResponseEntity<Map<String, Object>> syncArtifactsFromStorage(@PathVariable String id) {
        int synced = 0;
        try {
            Path storyBase = storageService.getArtifactBasePath().resolve(id);
            if (!Files.exists(storyBase)) {
                return ResponseEntity.badRequest().body(Map.of("error", "Artifact folder not found at " + storyBase.toAbsolutePath()));
            }

            // Sync StoryGraph
            Path graphFile = storyBase.resolve("understanding").resolve("story_graph.json");
            if (Files.exists(graphFile)) {
                String graphJson = Files.readString(graphFile);
                Path qaFile = storyBase.resolve("understanding").resolve("qa.json");
                String qaJson = Files.exists(qaFile) ? Files.readString(qaFile) : null;
                pipelineJobService.recordStoryGraph(id, graphJson, qaJson);
                synced++;
            }

            // Sync Narratives
            Path narrativeDir = storyBase.resolve("narrative");
            if (Files.exists(narrativeDir)) {
                for (String preset : List.of("quick", "standard", "complete")) {
                    Path nFile = narrativeDir.resolve(preset + ".json");
                    Path bpFile = narrativeDir.resolve("blueprint_" + preset + ".json");
                    if (Files.exists(nFile)) {
                        String nJson = Files.readString(nFile);
                        String bpJson = Files.exists(bpFile) ? Files.readString(bpFile) : null;
                        pipelineJobService.recordNarrative(id, preset, preset.equals("quick") ? 5 : (preset.equals("standard") ? 15 : 45), 1000, bpJson, nJson);
                        synced++;
                    }
                }
            }

            // Sync Localizations
            Path locDir = storyBase.resolve("localization");
            if (Files.exists(locDir)) {
                for (String lang : List.of("hi", "mr", "en", "ta", "te", "bn")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path scriptFile = locDir.resolve(lang).resolve(preset).resolve("script.json");
                        Path qaFile = locDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(scriptFile)) {
                            String scriptJson = Files.readString(scriptFile);
                            String qaJson = Files.exists(qaFile) ? Files.readString(qaFile) : null;
                            String langName = lang.equals("hi") ? "Hindi (हिंदी)" : (lang.equals("mr") ? "Marathi (मराठी)" : "English");
                            pipelineJobService.recordLocalization(id, preset, lang, langName, scriptJson, qaJson);
                            synced++;
                        }
                    }
                }
            }

            // Sync Audio Assets
            Path audioDir = storyBase.resolve("audio");
            if (Files.exists(audioDir)) {
                for (String lang : List.of("hi", "mr", "en", "ta", "te", "bn")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path assetFile = audioDir.resolve(lang).resolve(preset).resolve("asset_metadata.json");
                        Path qaFile = audioDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(assetFile)) {
                            String assetJson = Files.readString(assetFile);
                            String qaJson = Files.exists(qaFile) ? Files.readString(qaFile) : null;
                            pipelineJobService.recordAudioAsset(id, preset, lang, "default", 120.0, assetJson, qaJson);
                            synced++;
                        }
                    }
                }
            }

            return ResponseEntity.ok(Map.of("status", "synced", "artifactsCount", synced));
        } catch (Exception e) {
            log.error("Failed to sync artifacts for story {}: {}", id, e.getMessage());
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
