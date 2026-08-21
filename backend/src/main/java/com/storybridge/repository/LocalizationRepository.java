package com.storybridge.repository;

import com.storybridge.domain.LocalizationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface LocalizationRepository extends JpaRepository<LocalizationEntity, String> {
    List<LocalizationEntity> findByStoryId(String storyId);
    Optional<LocalizationEntity> findByStoryIdAndDurationPresetAndLanguageCode(
            String storyId, String durationPreset, String languageCode);
}
