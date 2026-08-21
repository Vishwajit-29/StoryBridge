package com.storybridge.repository;

import com.storybridge.domain.Enums;
import com.storybridge.domain.Story;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StoryRepository extends JpaRepository<Story, String> {
    List<Story> findByStatus(Enums.PublicationStatus status);
    List<Story> findByCategory(String category);

    @Query("SELECT s FROM Story s WHERE s.status = 'PUBLISHED' AND (" +
           "LOWER(s.title) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.description) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.originalAuthor) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<Story> searchPublishedStories(@Param("query") String query);
}
