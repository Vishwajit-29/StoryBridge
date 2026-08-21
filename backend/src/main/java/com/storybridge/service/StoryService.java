package com.storybridge.service;

import com.storybridge.domain.*;
import com.storybridge.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class StoryService {

    private final StoryRepository storyRepository;
    private final SourceRepository sourceRepository;
    private final StoryGraphRepository storyGraphRepository;
    private final NarrativeRepository narrativeRepository;
    private final LocalizationRepository localizationRepository;
    private final AudioRepository audioRepository;
    private final BookmarkRepository bookmarkRepository;
    private final ListeningHistoryRepository listeningHistoryRepository;
    private final UserRepository userRepository;
    private final StorageService storageService;

    public List<Story> getPublishedStories(String category) {
        if (category != null && !category.isBlank()) {
            return storyRepository.findByCategory(category);
        }
        return storyRepository.findByStatus(Enums.PublicationStatus.PUBLISHED);
    }

    public List<Story> searchStories(String query) {
        if (query == null || query.isBlank()) {
            return getPublishedStories(null);
        }
        return storyRepository.searchPublishedStories(query.trim());
    }

    public Optional<Story> getStoryById(String storyId) {
        return storyRepository.findById(storyId);
    }

    public List<Story> getAllStoriesAdmin() {
        return storyRepository.findAll();
    }

    @Transactional
    public Story createOrUpdateStory(Story story) {
        story.setUpdatedAt(LocalDateTime.now());
        return storyRepository.save(story);
    }

    // --- Artifact Fetching with Dynamic Storage Fallback ---

    public Optional<StoryGraphEntity> getStoryGraph(String storyId) {
        Optional<StoryGraphEntity> fromDb = storyGraphRepository.findFirstByStoryIdOrderByVersionDesc(storyId);
        if (fromDb.isPresent()) {
            return fromDb;
        }

        // Check storage filesystem
        try {
            Path graphFile = storageService.getArtifactBasePath().resolve(storyId).resolve("understanding").resolve("story_graph.json");
            if (Files.exists(graphFile)) {
                String graphJson = Files.readString(graphFile);
                Path qaFile = storageService.getArtifactBasePath().resolve(storyId).resolve("understanding").resolve("qa.json");
                String qaJson = Files.exists(qaFile) ? Files.readString(qaFile) : null;

                StoryGraphEntity entity = StoryGraphEntity.builder()
                        .storyId(storyId)
                        .version(1)
                        .graphDataJson(graphJson)
                        .qaReportJson(qaJson)
                        .approved(true)
                        .approvedAt(LocalDateTime.now())
                        .createdAt(LocalDateTime.now())
                        .build();
                return Optional.of(storyGraphRepository.save(entity));
            }
        } catch (Exception e) {
            log.warn("Could not read story graph from filesystem for {}: {}", storyId, e.getMessage());
        }

        return Optional.empty();
    }

    public List<NarrativeEntity> getNarratives(String storyId) {
        List<NarrativeEntity> list = narrativeRepository.findByStoryId(storyId);
        if (!list.isEmpty()) {
            return list;
        }

        // Check storage filesystem
        try {
            Path narrativeDir = storageService.getArtifactBasePath().resolve(storyId).resolve("narrative");
            if (Files.exists(narrativeDir)) {
                for (String preset : List.of("quick", "standard", "complete")) {
                    Path nFile = narrativeDir.resolve(preset + ".json");
                    Path bpFile = narrativeDir.resolve("blueprint_" + preset + ".json");
                    if (Files.exists(nFile)) {
                        NarrativeEntity entity = NarrativeEntity.builder()
                                .storyId(storyId)
                                .durationPreset(preset)
                                .targetDurationMinutes(preset.equals("quick") ? 5 : (preset.equals("standard") ? 15 : 45))
                                .wordCount(1000)
                                .blueprintJson(Files.exists(bpFile) ? Files.readString(bpFile) : null)
                                .narrativeJson(Files.readString(nFile))
                                .approved(true)
                                .approvedAt(LocalDateTime.now())
                                .createdAt(LocalDateTime.now())
                                .build();
                        narrativeRepository.save(entity);
                    }
                }
                return narrativeRepository.findByStoryId(storyId);
            }
        } catch (Exception e) {
            log.warn("Could not read narratives from filesystem for {}: {}", storyId, e.getMessage());
        }

        return list;
    }

    public Optional<NarrativeEntity> getNarrative(String storyId, String durationPreset) {
        Optional<NarrativeEntity> fromDb = narrativeRepository.findByStoryIdAndDurationPreset(storyId, durationPreset);
        if (fromDb.isPresent()) {
            return fromDb;
        }
        getNarratives(storyId); // Trigger filesystem sync
        return narrativeRepository.findByStoryIdAndDurationPreset(storyId, durationPreset);
    }

    public List<LocalizationEntity> getLocalizations(String storyId) {
        List<LocalizationEntity> list = localizationRepository.findByStoryId(storyId);
        if (!list.isEmpty()) {
            return list;
        }

        // Check storage filesystem
        try {
            Path locDir = storageService.getArtifactBasePath().resolve(storyId).resolve("localization");
            if (Files.exists(locDir)) {
                for (String lang : List.of("hi", "mr", "en", "ta", "te", "bn")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path scriptFile = locDir.resolve(lang).resolve(preset).resolve("script.json");
                        Path qaFile = locDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(scriptFile)) {
                            String langName = lang.equals("hi") ? "Hindi (हिंदी)" : (lang.equals("mr") ? "Marathi (मराठी)" : "English");
                            LocalizationEntity entity = LocalizationEntity.builder()
                                    .storyId(storyId)
                                    .durationPreset(preset)
                                    .languageCode(lang)
                                    .languageName(langName)
                                    .scriptJson(Files.readString(scriptFile))
                                    .qaReportJson(Files.exists(qaFile) ? Files.readString(qaFile) : null)
                                    .approved(true)
                                    .approvedAt(LocalDateTime.now())
                                    .createdAt(LocalDateTime.now())
                                    .build();
                            localizationRepository.save(entity);
                        }
                    }
                }
                return localizationRepository.findByStoryId(storyId);
            }
        } catch (Exception e) {
            log.warn("Could not read localizations from filesystem for {}: {}", storyId, e.getMessage());
        }

        return list;
    }

    public Optional<LocalizationEntity> getLocalization(String storyId, String durationPreset, String languageCode) {
        Optional<LocalizationEntity> fromDb = localizationRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
        if (fromDb.isPresent()) {
            return fromDb;
        }
        getLocalizations(storyId); // Trigger filesystem sync
        return localizationRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
    }

    public List<AudioEntity> getAudioAssets(String storyId) {
        List<AudioEntity> list = audioRepository.findByStoryId(storyId);
        if (!list.isEmpty()) {
            return list;
        }

        // Check storage filesystem
        try {
            Path audioDir = storageService.getArtifactBasePath().resolve(storyId).resolve("audio");
            if (Files.exists(audioDir)) {
                for (String lang : List.of("hi", "mr", "en", "ta", "te", "bn")) {
                    for (String preset : List.of("quick", "standard", "complete")) {
                        Path assetFile = audioDir.resolve(lang).resolve(preset).resolve("asset_metadata.json");
                        Path qaFile = audioDir.resolve(lang).resolve(preset).resolve("qa.json");
                        if (Files.exists(assetFile)) {
                            AudioEntity entity = AudioEntity.builder()
                                    .storyId(storyId)
                                    .durationPreset(preset)
                                    .languageCode(lang)
                                    .voiceId("default")
                                    .totalDurationSeconds(120.0)
                                    .chaptersJson(Files.readString(assetFile))
                                    .qaReportJson(Files.exists(qaFile) ? Files.readString(qaFile) : null)
                                    .approved(true)
                                    .approvedAt(LocalDateTime.now())
                                    .createdAt(LocalDateTime.now())
                                    .build();
                            audioRepository.save(entity);
                        }
                    }
                }
                return audioRepository.findByStoryId(storyId);
            }
        } catch (Exception e) {
            log.warn("Could not read audio assets from filesystem for {}: {}", storyId, e.getMessage());
        }

        return list;
    }

    public Optional<AudioEntity> getAudioAsset(String storyId, String durationPreset, String languageCode) {
        Optional<AudioEntity> fromDb = audioRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
        if (fromDb.isPresent()) {
            return fromDb;
        }
        getAudioAssets(storyId); // Trigger filesystem sync
        return audioRepository.findByStoryIdAndDurationPresetAndLanguageCode(storyId, durationPreset, languageCode);
    }

    // --- User History & Bookmarks ---

    @Transactional
    public void toggleBookmark(String username, String storyId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + username));

        Optional<BookmarkEntity> existing = bookmarkRepository.findByUserIdAndStoryId(user.getId(), storyId);
        if (existing.isPresent()) {
            bookmarkRepository.delete(existing.get());
        } else {
            BookmarkEntity bookmark = BookmarkEntity.builder()
                    .userId(user.getId())
                    .storyId(storyId)
                    .createdAt(LocalDateTime.now())
                    .build();
            bookmarkRepository.save(bookmark);
        }
    }

    public boolean isBookmarked(String username, String storyId) {
        return userRepository.findByUsername(username)
                .map(user -> bookmarkRepository.existsByUserIdAndStoryId(user.getId(), storyId))
                .orElse(false);
    }

    public List<Story> getUserBookmarks(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + username));
        List<BookmarkEntity> bookmarks = bookmarkRepository.findByUserId(user.getId());
        List<String> storyIds = bookmarks.stream().map(BookmarkEntity::getStoryId).toList();
        return storyRepository.findAllById(storyIds);
    }

    @Transactional
    public void recordListeningProgress(
            String username,
            String storyId,
            String languageCode,
            String durationPreset,
            int chapterIndex,
            double progressSeconds,
            boolean completed
    ) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + username));

        ListeningHistoryEntity history = listeningHistoryRepository
                .findByUserIdAndStoryIdAndLanguageCodeAndDurationPreset(user.getId(), storyId, languageCode, durationPreset)
                .orElse(ListeningHistoryEntity.builder()
                        .userId(user.getId())
                        .storyId(storyId)
                        .languageCode(languageCode)
                        .durationPreset(durationPreset)
                        .build());

        history.setCurrentChapterIndex(chapterIndex);
        history.setProgressSeconds(progressSeconds);
        history.setCompleted(completed);
        history.setLastListenedAt(LocalDateTime.now());
        listeningHistoryRepository.save(history);
    }

    public List<ListeningHistoryEntity> getUserListeningHistory(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + username));
        return listeningHistoryRepository.findByUserIdOrderByLastListenedAtDesc(user.getId());
    }
}
