package com.storybridge.repository;

import com.storybridge.domain.ApprovalRecordEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ApprovalRecordRepository extends JpaRepository<ApprovalRecordEntity, String> {
    List<ApprovalRecordEntity> findByStoryIdOrderByCreatedAtDesc(String storyId);
}
