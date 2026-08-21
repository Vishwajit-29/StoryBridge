package com.storybridge.repository;

import com.storybridge.domain.NarrativeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface NarrativeRepository extends JpaRepository<NarrativeEntity, String> {
    List<NarrativeEntity> findByStoryId(String storyId);
    Optional<NarrativeEntity> findByStoryIdAndDurationPreset(String storyId, String durationPreset);
}
