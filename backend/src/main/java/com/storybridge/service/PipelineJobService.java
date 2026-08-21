package com.storybridge.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.storybridge.domain.*;
import com.storybridge.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class PipelineJobService {

    private final PipelineJobRepository jobRepository;
    private final StoryRepository storyRepository;
    private final SourceRepository sourceRepository;
    private final StoryGraphRepository storyGraphRepository;
    private final NarrativeRepository narrativeRepository;
    private final LocalizationRepository localizationRepository;
    private final AudioRepository audioRepository;
    private final StorageService storageService;
    private final AsyncPipelineExecutor asyncPipelineExecutor;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public List<PipelineJobEntity> getAllJobs() {
        return jobRepository.findAllByOrderByCreatedAtDesc();
    }

    public Optional<PipelineJobEntity> getJob(String jobId) {
        return jobRepository.findById(jobId);
    }

    @Transactional
    public PipelineJobEntity triggerPipeline(
            String storyId,
            String sourceTextOrPath,
            String sourceFormat,
            String originalFileName,
            List<String> durationPresets,
            List<String> languages
    ) {
        Story story = storyRepository.findById(storyId)
                .orElseThrow(() -> new IllegalArgumentException("Story not found: " + storyId));

        String jobId = "job_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);

        PipelineJobEntity job = PipelineJobEntity.builder()
                .id(jobId)
                .storyId(storyId)
                .stage(Enums.JobStage.IMPORTED)
                .status(Enums.JobStatus.QUEUED)
                .progressPercentage(10)
                .currentStep("Job Queued")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        jobRepository.save(job);

        // Update story status
        story.setStatus(Enums.PublicationStatus.PROCESSING);
        storyRepository.save(story);

        // Save Source record
        Source source = Source.builder()
                .storyId(storyId)
                .sourceFormat(sourceFormat != null ? sourceFormat : "markdown")
                .originalFileName(originalFileName != null ? originalFileName : "source.txt")
                .rawTextContent(sourceTextOrPath != null ? sourceTextOrPath : "")
                .createdAt(LocalDateTime.now())
                .build();
        sourceRepository.save(source);

        // Dispatch truly async execution
        asyncPipelineExecutor.executeAsync(
                jobId,
                storyId,
                story.getTitle(),
                story.getOriginalAuthor(),
                sourceTextOrPath,
                durationPresets,
                languages,
                () -> syncStoryArtifacts(storyId)
        );

        return job;
    }

    @Transactional
    public void syncStoryArtifacts(String storyId) {
        try {
            Path basePath = storageService.getArtifactBasePath();
            Path storyBase = basePath.resolve(storyId);

            if (!Files.exists(storyBase)) {
                // Look for alternative matching directory
                try (DirectoryStream<Path> stream = Files.newDirectoryStream(basePath)) {
                    for (Path dir : stream) {
                        if (Files.isDirectory(dir) && !dir.getFileName().toString().equals("story_panchatantra_monkey_wedge")) {
                            if (dir.getFileName().toString().contains(storyId) || storyId.contains(dir.getFileName().toString()) || Files.exists(dir.resolve("understanding"))) {
                                storyBase = dir;
                                log.info("Matched artifact directory for {}: {}", storyId, dir.getFileName());
                                break;
                            }
                        }
                    }
                }
            }

            if (!Files.exists(storyBase)) {
                log.warn("Artifact path does not exist for story {}: {}", storyId, storyBase.toAbsolutePath());
                return;
            }

            // 1. Sync StoryGraph
            Path graphFile = storyBase.resolve("understanding").resolve("story_graph.json");
            if (Files.exists(graphFile)) {
                Path qaFile = storyBase.resolve("understanding").resolve("qa.json");
                recordStoryGraph(storyId, Files.readString(graphFile), Files.exists(qaFile) ? Files.readString(qaFile) : null);
            }

            // 2. Sync Narratives
            Path narrativeDir = storyBase.resolve("narrative");
            if (Files.exists(narrativeDir)) {
                for (String preset : List.of("quick", "standard", "complete")) {
                    Path nFile = narrativeDir.resolve(preset + ".json");
                    Path bpFile = narrativeDir.resolve("blueprint_" + preset + ".json");
                    if (Files.exists(nFile)) {
                        recordNarrative(
                                storyId,
                                preset,
                                preset.equals("quick") ? 5 : (preset.equals("standard") ? 15 : 45),
                                1000,
                                Files.exists(bpFile) ? Files.readString(bpFile) : null,
                                Files.readString(nFile)
                        );
                    }
                }
            }

            // 3. Sync Localizations
            Path locDir = storyBase.resolve("localization");
            if (Files.exists(locDir)) {
                for (String lang : List.of("hi", "mr", "ta", "te", "bn", "en")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path scriptFile = locDir.resolve(lang).resolve(preset).resolve("script.json");
                        Path qaFile = locDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(scriptFile)) {
                            String langName = lang.equals("hi") ? "Hindi (हिंदी)" : (lang.equals("mr") ? "Marathi (मराठी)" : "English");
                            recordLocalization(
                                    storyId,
                                    preset,
                                    lang,
                                    langName,
                                    Files.readString(scriptFile),
                                    Files.exists(qaFile) ? Files.readString(qaFile) : null
                            );
                        }
                    }
                }
            }

            // 4. Sync Audio Assets
            Path audioDir = storyBase.resolve("audio");
            if (Files.exists(audioDir)) {
                for (String lang : List.of("hi", "mr", "ta", "te", "bn", "en")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path assetFile = audioDir.resolve(lang).resolve(preset).resolve("asset_metadata.json");
                        Path qaFile = audioDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(assetFile)) {
                            recordAudioAsset(
                                    storyId,
                                    preset,
                                    lang,
                                    "default",
                                    120.0,
                                    Files.readString(assetFile),
                                    Files.exists(qaFile) ? Files.readString(qaFile) : null
                            );
                        }
                    }
                }
            }
            log.info("Successfully synced all artifacts for story {}", storyId);
        } catch (Exception e) {
            log.error("Failed to sync artifacts for story {}: {}", storyId, e.getMessage(), e);
        }
    }

    @Transactional
    public void recordStoryGraph(String storyId, String graphJson, String qaReportJson) {
        if (!storyGraphRepository.existsByStoryId(storyId)) {
            StoryGraphEntity entity = StoryGraphEntity.builder()
                    .storyId(storyId)
                    .version(1)
                    .graphDataJson(graphJson)
                    .qaReportJson(qaReportJson)
                    .approved(true)
                    .approvedAt(LocalDateTime.now())
                    .createdAt(LocalDateTime.now())
                    .build();
            storyGraphRepository.save(entity);
        }
    }

    @Transactional
    public void recordNarrative(String storyId, String durationPreset, int targetDurationMinutes, int wordCount, String blueprintJson, String narrativeJson) {
        Optional<NarrativeEntity> existing = narrativeRepository.findByStoryIdAndDurationPreset(storyId, durationPreset);
        if (existing.isEmpty()) {
            NarrativeEntity entity = NarrativeEntity.builder()
                    .storyId(storyId)
                    .durationPreset(durationPreset)
                    .targetDurationMinutes(targetDurationMinutes)
                    .wordCount(wordCount)
                    .blueprintJson(blueprintJson)
                    .narrativeJson(narrativeJson)
                    .approved(true)
                    .approvedAt(LocalDateTime.now())
                    .createdAt(LocalDateTime.now())
                    .build();
            narrativeRepository.save(entity);
        }
    }

    @Transactional
    public void recordLocalization(String storyId, String durationPreset, String languageCode, String languageName, String scriptJson, String qaReportJson) {
        Optional<LocalizationEntity> existing = localizationRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
        if (existing.isEmpty()) {
            LocalizationEntity entity = LocalizationEntity.builder()
                    .storyId(storyId)
                    .durationPreset(durationPreset)
                    .languageCode(languageCode)
                    .languageName(languageName)
                    .scriptJson(scriptJson)
                    .qaReportJson(qaReportJson)
                    .approved(true)
                    .approvedAt(LocalDateTime.now())
                    .createdAt(LocalDateTime.now())
                    .build();
            localizationRepository.save(entity);
        }
    }

    @Transactional
    public void recordAudioAsset(String storyId, String durationPreset, String languageCode, String voiceId, double totalDurationSec, String chaptersJson, String qaReportJson) {
        Optional<AudioEntity> existing = audioRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
        if (existing.isEmpty()) {
            AudioEntity entity = AudioEntity.builder()
                    .storyId(storyId)
                    .durationPreset(durationPreset)
                    .languageCode(languageCode)
                    .voiceId(voiceId)
                    .totalDurationSeconds(totalDurationSec)
                    .chaptersJson(chaptersJson)
                    .qaReportJson(qaReportJson)
                    .approved(true)
                    .approvedAt(LocalDateTime.now())
                    .createdAt(LocalDateTime.now())
                    .build();
            audioRepository.save(entity);
        }
    }
}
