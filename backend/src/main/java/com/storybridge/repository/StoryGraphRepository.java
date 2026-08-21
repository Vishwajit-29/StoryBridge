package com.storybridge.repository;

import com.storybridge.domain.StoryGraphEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StoryGraphRepository extends JpaRepository<StoryGraphEntity, String> {
    List<StoryGraphEntity> findByStoryId(String storyId);
    Optional<StoryGraphEntity> findFirstByStoryIdOrderByVersionDesc(String storyId);
    boolean existsByStoryId(String storyId);
}
