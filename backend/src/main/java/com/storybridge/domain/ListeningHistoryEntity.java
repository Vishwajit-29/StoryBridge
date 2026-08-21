package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "listening_history", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"user_id", "story_id", "language_code", "duration_preset"})
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ListeningHistoryEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "story_id", nullable = false)
    private String storyId;

    private String languageCode;
    private String durationPreset;
    private int currentChapterIndex;
    private double progressSeconds;

    @Builder.Default
    private boolean completed = false;

    @Column(name = "last_listened_at", nullable = false)
    @Builder.Default
    private LocalDateTime lastListenedAt = LocalDateTime.now();

    @PrePersist
    public void prePersist() {
        if (lastListenedAt == null) {
            lastListenedAt = LocalDateTime.now();
        }
    }
}
