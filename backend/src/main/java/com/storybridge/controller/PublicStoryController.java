package com.storybridge.controller;

import com.storybridge.domain.*;
import com.storybridge.service.StoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class PublicStoryController {

    private final StoryService storyService;

    @GetMapping("/stories")
    public ResponseEntity<List<Story>> getPublishedStories(@RequestParam(required = false) String category) {
        return ResponseEntity.ok(storyService.getPublishedStories(category));
    }

    @GetMapping("/stories/{id}")
    public ResponseEntity<Story> getStoryDetails(@PathVariable String id) {
        return storyService.getStoryById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/stories/{id}/graph")
    public ResponseEntity<StoryGraphEntity> getStoryGraph(@PathVariable String id) {
        return storyService.getStoryGraph(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.noContent().build());
    }

    @GetMapping("/stories/{id}/narratives")
    public ResponseEntity<List<NarrativeEntity>> getNarratives(@PathVariable String id) {
        return ResponseEntity.ok(storyService.getNarratives(id));
    }

    @GetMapping("/stories/{id}/narratives/{preset}")
    public ResponseEntity<NarrativeEntity> getNarrativeByPreset(
            @PathVariable String id,
            @PathVariable String preset
    ) {
        return storyService.getNarrative(id, preset)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.noContent().build());
    }

    @GetMapping("/stories/{id}/localizations")
    public ResponseEntity<List<LocalizationEntity>> getLocalizations(@PathVariable String id) {
        return ResponseEntity.ok(storyService.getLocalizations(id));
    }

    @GetMapping("/stories/{id}/localizations/{preset}/{lang}")
    public ResponseEntity<LocalizationEntity> getLocalization(
            @PathVariable String id,
            @PathVariable String preset,
            @PathVariable String lang
    ) {
        return storyService.getLocalization(id, preset, lang)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.noContent().build());
    }

    @GetMapping("/stories/{id}/audio")
    public ResponseEntity<List<AudioEntity>> getAudioAssets(@PathVariable String id) {
        return ResponseEntity.ok(storyService.getAudioAssets(id));
    }

    @GetMapping("/stories/{id}/audio/{preset}/{lang}")
    public ResponseEntity<AudioEntity> getAudioAsset(
            @PathVariable String id,
            @PathVariable String preset,
            @PathVariable String lang
    ) {
        return storyService.getAudioAsset(id, preset, lang)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.noContent().build());
    }

    @GetMapping("/search")
    public ResponseEntity<List<Story>> searchStories(@RequestParam(required = false, defaultValue = "") String q) {
        return ResponseEntity.ok(storyService.searchStories(q));
    }
}
