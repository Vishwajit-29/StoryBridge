package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "audio_assets")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AudioEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(name = "story_id", nullable = false)
    private String storyId;

    @Column(nullable = false)
    private String durationPreset;

    @Column(nullable = false)
    private String languageCode;

    private String voiceId;
    private double totalDurationSeconds;

    @Lob
    @Column(columnDefinition = "TEXT", nullable = false)
    private String chaptersJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String qaReportJson;

    @Column(nullable = false)
    @Builder.Default
    private boolean approved = false;

    private String approvedBy;
    private LocalDateTime approvedAt;

    @Column(name = "created_at", nullable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();

    @PrePersist
    public void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }
}
