package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "sources")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Source {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(name = "story_id", nullable = false)
    private String storyId;

    @Column(nullable = false)
    private String sourceFormat;

    private String originalFileName;
    private String checksumSha256;
    private String storagePath;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String rawTextContent;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String canonicalSourceJson;

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
