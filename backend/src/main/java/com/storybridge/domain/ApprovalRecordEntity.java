package com.storybridge.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "approval_records")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ApprovalRecordEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(name = "story_id", nullable = false)
    private String storyId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Enums.JobStage stage;

    private String artifactId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Enums.ApprovalAction action;

    private String reviewerUsername;
    private String notes;

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
