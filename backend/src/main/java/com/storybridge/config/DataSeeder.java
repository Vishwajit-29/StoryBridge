package com.storybridge.config;

import com.storybridge.domain.Enums;
import com.storybridge.domain.Story;
import com.storybridge.repository.StoryRepository;
import com.storybridge.service.PipelineJobService;
import com.storybridge.service.StorageService;
import com.storybridge.service.StoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataSeeder implements CommandLineRunner {

    private final StoryRepository storyRepository;
    private final StoryService storyService;
    private final PipelineJobService pipelineJobService;
    private final StorageService storageService;

    @Override
    public void run(String... args) {
        // Ensure default story exists
        String demoStoryId = "story_panchatantra_monkey_wedge";

        if (!storyRepository.existsById(demoStoryId)) {
            Story story = Story.builder()
                    .id(demoStoryId)
                    .title("The Monkey and the Wedge")
                    .originalAuthor("Vishnu Sharma (The Panchatantra)")
                    .originalLanguage("en")
                    .category("Fables & Moral Tales")
                    .description("A classic Panchatantra fable about a curious monkey who meddles with a carpenter's wedge in a split timber log, suffering the painful consequences of unwarranted curiosity.")
                    .rightsType(Enums.RightsType.PUBLIC_DOMAIN)
                    .rightsVerified(true)
                    .rightsEvidence("Universal Public Domain ancient Sanskrit literature (CC0)")
                    .status(Enums.PublicationStatus.PUBLISHED)
                    .totalWords(450)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            storyRepository.save(story);
            log.info("Seeded initial demo story: {}", story.getTitle());
        }

        // Scan all folders in storage/artifacts and auto-sync
        try {
            Path basePath = storageService.getArtifactBasePath();
            if (Files.exists(basePath)) {
                try (DirectoryStream<Path> stream = Files.newDirectoryStream(basePath)) {
                    for (Path dir : stream) {
                        if (Files.isDirectory(dir)) {
                            String storyId = dir.getFileName().toString();
                            if (!storyRepository.existsById(storyId)) {
                                String title = storyId.replace("story_", "").replace("_", " ");
                                title = Character.toUpperCase(title.charAt(0)) + title.substring(1);
                                Story s = Story.builder()
                                        .id(storyId)
                                        .title(title)
                                        .category("Mythology & Folklore")
                                        .description("Imported from StoryBridge storage artifacts.")
                                        .rightsType(Enums.RightsType.PUBLIC_DOMAIN)
                                        .rightsVerified(true)
                                        .status(Enums.PublicationStatus.PUBLISHED)
                                        .createdAt(LocalDateTime.now())
                                        .updatedAt(LocalDateTime.now())
                                        .build();
                                storyRepository.save(s);
                                log.info("Auto-registered story from storage: {}", storyId);
                            }
                            pipelineJobService.syncStoryArtifacts(storyId);
                        }
                    }
                }
            }
        } catch (Exception e) {
            log.warn("Storage auto-sync failed: {}", e.getMessage());
        }
    }
}
