package com.storybridge.controller;

import com.storybridge.domain.ListeningHistoryEntity;
import com.storybridge.domain.Story;
import com.storybridge.service.StoryService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/me")
@RequiredArgsConstructor
public class UserController {

    private final StoryService storyService;

    @GetMapping("/bookmarks")
    public ResponseEntity<List<Story>> getBookmarks(Authentication authentication) {
        return ResponseEntity.ok(storyService.getUserBookmarks(authentication.getName()));
    }

    @PostMapping("/bookmarks/{storyId}")
    public ResponseEntity<Map<String, Object>> toggleBookmark(
            @PathVariable String storyId,
            Authentication authentication
    ) {
        storyService.toggleBookmark(authentication.getName(), storyId);
        boolean isBookmarked = storyService.isBookmarked(authentication.getName(), storyId);
        return ResponseEntity.ok(Map.of("storyId", storyId, "bookmarked", isBookmarked));
    }

    @GetMapping("/bookmarks/{storyId}/status")
    public ResponseEntity<Map<String, Boolean>> getBookmarkStatus(
            @PathVariable String storyId,
            Authentication authentication
    ) {
        boolean status = storyService.isBookmarked(authentication.getName(), storyId);
        return ResponseEntity.ok(Map.of("bookmarked", status));
    }

    @GetMapping("/history")
    public ResponseEntity<List<ListeningHistoryEntity>> getHistory(Authentication authentication) {
        return ResponseEntity.ok(storyService.getUserListeningHistory(authentication.getName()));
    }

    @Data
    public static class ProgressUpdateRequest {
        private String storyId;
        private String languageCode;
        private String durationPreset;
        private int chapterIndex;
        private double progressSeconds;
        private boolean completed;
    }

    @PostMapping("/history")
    public ResponseEntity<Map<String, String>> updateProgress(
            @RequestBody ProgressUpdateRequest req,
            Authentication authentication
    ) {
        storyService.recordListeningProgress(
                authentication.getName(),
                req.getStoryId(),
                req.getLanguageCode(),
                req.getDurationPreset(),
                req.getChapterIndex(),
                req.getProgressSeconds(),
                req.isCompleted()
        );
        return ResponseEntity.ok(Map.of("status", "recorded"));
    }
}
