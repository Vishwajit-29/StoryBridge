package com.storybridge.repository;

import com.storybridge.domain.PipelineJobEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PipelineJobRepository extends JpaRepository<PipelineJobEntity, String> {
    List<PipelineJobEntity> findByStoryIdOrderByCreatedAtDesc(String storyId);
    List<PipelineJobEntity> findAllByOrderByCreatedAtDesc();
}
