package com.storybridge.repository;

import com.storybridge.domain.BookmarkEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookmarkRepository extends JpaRepository<BookmarkEntity, String> {
    List<BookmarkEntity> findByUserId(String userId);
    Optional<BookmarkEntity> findByUserIdAndStoryId(String userId, String storyId);
    void deleteByUserIdAndStoryId(String userId, String storyId);
    boolean existsByUserIdAndStoryId(String userId, String storyId);
}
