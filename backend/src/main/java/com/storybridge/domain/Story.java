package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "stories")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Story {

    @Id
    @Column(nullable = false, unique = true)
    private String id; // e.g. story_panchatantra_01

    @Column(nullable = false)
    private String title;

    private String originalAuthor;

    @Column(nullable = false)
    @Builder.Default
    private String originalLanguage = "en";

    private String category; // Mythology, Folklore, Classic Literature, Fables, Sci-Fi

    @Column(length = 2000)
    private String description;

    private String coverImageUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private Enums.RightsType rightsType = Enums.RightsType.PUBLIC_DOMAIN;

    @Column(nullable = false)
    @Builder.Default
    private boolean rightsVerified = false;

    private String rightsEvidence;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private Enums.PublicationStatus status = Enums.PublicationStatus.DRAFT;

    private int totalWords;

    @Column(name = "created_at", nullable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    @Builder.Default
    private LocalDateTime updatedAt = LocalDateTime.now();

    @PrePersist
    public void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        if (updatedAt == null) {
            updatedAt = LocalDateTime.now();
        }
    }
}
