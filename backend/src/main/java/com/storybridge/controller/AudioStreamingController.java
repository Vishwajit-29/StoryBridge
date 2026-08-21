package com.storybridge.controller;

import com.storybridge.service.StorageService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@RestController
@RequestMapping("/api/audio")
@RequiredArgsConstructor
@Slf4j
public class AudioStreamingController {

    private final StorageService storageService;

    @GetMapping("/stream/{storyId}/{lang}/{preset}/{chapterFile}")
    public ResponseEntity<Resource> streamAudioChapter(
            @PathVariable String storyId,
            @PathVariable String lang,
            @PathVariable String preset,
            @PathVariable String chapterFile
    ) {
        try {
            Path basePath = storageService.getArtifactBasePath();
            Path filePath = basePath.resolve(storyId)
                    .resolve("audio")
                    .resolve(lang.toLowerCase())
                    .resolve(preset.toLowerCase())
                    .resolve(chapterFile);

            if (!Files.exists(filePath)) {
                // Try quick preset
                Path altQuick = basePath.resolve(storyId).resolve("audio").resolve(lang.toLowerCase()).resolve("quick").resolve(chapterFile);
                if (Files.exists(altQuick)) {
                    filePath = altQuick;
                } else {
                    // Try standard preset
                    Path altStandard = basePath.resolve(storyId).resolve("audio").resolve(lang.toLowerCase()).resolve("standard").resolve(chapterFile);
                    if (Files.exists(altStandard)) {
                        filePath = altStandard;
                    } else {
                        log.warn("Audio file not found at: {}", filePath.toAbsolutePath());
                        return ResponseEntity.notFound().build();
                    }
                }
            }

            byte[] audioBytes = Files.readAllBytes(filePath);
            ByteArrayResource resource = new ByteArrayResource(audioBytes);

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + chapterFile + "\"")
                    .header(HttpHeaders.CACHE_CONTROL, "public, max-age=3600")
                    .contentType(MediaType.parseMediaType("audio/mpeg"))
                    .contentLength(audioBytes.length)
                    .body(resource);
        } catch (IOException e) {
            log.error("Failed to read audio file: {}", e.getMessage());
            return ResponseEntity.internalServerError().build();
        }
    }
}
