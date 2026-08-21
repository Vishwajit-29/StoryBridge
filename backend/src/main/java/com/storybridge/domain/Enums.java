package com.storybridge.domain;

public class Enums {

    public enum Role {
        USER,
        REVIEWER,
        ADMIN
    }

    public enum RightsType {
        PUBLIC_DOMAIN,
        OPEN_LICENSE,
        ORIGINAL,
        LICENSED,
        UNKNOWN,
        RESTRICTED
    }

    public enum PublicationStatus {
        DRAFT,
        PROCESSING,
        IN_REVIEW,
        PUBLISHED,
        REJECTED,
        ARCHIVED
    }

    public enum JobStage {
        IMPORTED,
        NORMALIZED,
        UNDERSTANDING_READY,
        UNDERSTORY_REVIEW,
        STORY_APPROVED,
        NARRATIVE_GENERATED,
        NARRATIVE_APPROVED,
        LOCALIZATION_GENERATED,
        LOCALIZATION_APPROVED,
        AUDIO_GENERATED,
        AUDIO_APPROVED,
        PUBLISHED,
        FAILED
    }

    public enum JobStatus {
        QUEUED,
        PROCESSING,
        COMPLETED,
        FAILED,
        CANCELLED
    }

    public enum ApprovalAction {
        APPROVED,
        REJECTED,
        REVISION_REQUESTED
    }
}
