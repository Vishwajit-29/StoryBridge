package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "story_graphs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StoryGraphEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(name = "story_id", nullable = false)
    private String storyId;

    @Builder.Default
    private int version = 1;

    @Lob
    @Column(columnDefinition = "TEXT", nullable = false)
    private String graphDataJson;

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
