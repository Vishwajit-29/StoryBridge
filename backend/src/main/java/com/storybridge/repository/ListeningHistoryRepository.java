package com.storybridge.repository;

import com.storybridge.domain.ListeningHistoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ListeningHistoryRepository extends JpaRepository<ListeningHistoryEntity, String> {
    List<ListeningHistoryEntity> findByUserIdOrderByLastListenedAtDesc(String userId);
    Optional<ListeningHistoryEntity> findByUserIdAndStoryIdAndLanguageCodeAndDurationPreset(
            String userId, String storyId, String languageCode, String durationPreset);
}
