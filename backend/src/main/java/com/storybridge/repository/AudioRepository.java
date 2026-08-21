package com.storybridge.repository;

import com.storybridge.domain.AudioEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AudioRepository extends JpaRepository<AudioEntity, String> {
    List<AudioEntity> findByStoryId(String storyId);
    Optional<AudioEntity> findByStoryIdAndDurationPresetAndLanguageCode(
            String storyId, String durationPreset, String languageCode);
}
