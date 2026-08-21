package com.storybridge.service;

import com.storybridge.domain.ApprovalRecordEntity;
import com.storybridge.domain.Enums;
import com.storybridge.domain.Story;
import com.storybridge.repository.ApprovalRecordRepository;
import com.storybridge.repository.StoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class WorkflowService {

    private final StoryRepository storyRepository;
    private final ApprovalRecordRepository approvalRecordRepository;

    @Transactional
    public Story verifyStoryRights(String storyId, Enums.RightsType rightsType, boolean verified, String evidence, String reviewerUsername) {
        Story story = storyRepository.findById(storyId)
                .orElseThrow(() -> new IllegalArgumentException("Story not found: " + storyId));

        story.setRightsType(rightsType);
        story.setRightsVerified(verified);
        story.setRightsEvidence(evidence);
        story.setUpdatedAt(LocalDateTime.now());

        Story saved = storyRepository.save(story);

        ApprovalRecordEntity record = ApprovalRecordEntity.builder()
                .storyId(storyId)
                .stage(Enums.JobStage.IMPORTED)
                .action(verified ? Enums.ApprovalAction.APPROVED : Enums.ApprovalAction.REJECTED)
                .reviewerUsername(reviewerUsername)
                .notes("Rights verification: " + rightsType + " (verified=" + verified + "). Evidence: " + evidence)
                .createdAt(LocalDateTime.now())
                .build();
        approvalRecordRepository.save(record);

        log.info("Rights updated for story {}: {} (verified: {})", storyId, rightsType, verified);
        return saved;
    }

    @Transactional
    public Story publishStory(String storyId, String reviewerUsername) {
        Story story = storyRepository.findById(storyId)
                .orElseThrow(() -> new IllegalArgumentException("Story not found: " + storyId));

        // Strict SRS Section 28 Rule: Rights must be verified and not UNKNOWN / RESTRICTED
        if (!story.isRightsVerified() || story.getRightsType() == Enums.RightsType.UNKNOWN || story.getRightsType() == Enums.RightsType.RESTRICTED) {
            throw new IllegalStateException("Cannot publish story: Content rights are not verified or restricted.");
        }

        story.setStatus(Enums.PublicationStatus.PUBLISHED);
        story.setUpdatedAt(LocalDateTime.now());
        Story saved = storyRepository.save(story);

        ApprovalRecordEntity record = ApprovalRecordEntity.builder()
                .storyId(storyId)
                .stage(Enums.JobStage.PUBLISHED)
                .action(Enums.ApprovalAction.APPROVED)
                .reviewerUsername(reviewerUsername)
                .notes("Story published to public catalog.")
                .createdAt(LocalDateTime.now())
                .build();
        approvalRecordRepository.save(record);

        log.info("Story {} published successfully by {}", storyId, reviewerUsername);
        return saved;
    }

    @Transactional
    public Story unpublishStory(String storyId, String reason, String reviewerUsername) {
        Story story = storyRepository.findById(storyId)
                .orElseThrow(() -> new IllegalArgumentException("Story not found: " + storyId));

        story.setStatus(Enums.PublicationStatus.ARCHIVED);
        story.setUpdatedAt(LocalDateTime.now());
        Story saved = storyRepository.save(story);

        ApprovalRecordEntity record = ApprovalRecordEntity.builder()
                .storyId(storyId)
                .stage(Enums.JobStage.PUBLISHED)
                .action(Enums.ApprovalAction.REVISION_REQUESTED)
                .reviewerUsername(reviewerUsername)
                .notes("Story unpublished: " + reason)
                .createdAt(LocalDateTime.now())
                .build();
        approvalRecordRepository.save(record);

        log.info("Story {} unpublished by {}. Reason: {}", storyId, reviewerUsername, reason);
        return saved;
    }
}
