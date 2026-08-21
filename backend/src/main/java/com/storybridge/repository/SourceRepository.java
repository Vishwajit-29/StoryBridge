package com.storybridge.repository;

import com.storybridge.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SourceRepository extends JpaRepository<Source, String> {
    List<Source> findByStoryId(String storyId);
    Optional<Source> findFirstByStoryIdOrderByCreatedAtDesc(String storyId);
}
