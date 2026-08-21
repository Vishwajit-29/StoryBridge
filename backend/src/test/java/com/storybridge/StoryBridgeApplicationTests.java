package com.storybridge;

import com.storybridge.domain.Enums;
import com.storybridge.domain.Story;
import com.storybridge.repository.StoryRepository;
import com.storybridge.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class StoryBridgeApplicationTests {

    @Autowired
    private StoryRepository storyRepository;

    @Autowired
    private UserRepository userRepository;

    @Test
    void contextLoads() {
        assertNotNull(storyRepository);
        assertNotNull(userRepository);
    }

    @Test
    void testInitialDataSeeded() {
        // Admin user must be seeded by AuthService
        assertTrue(userRepository.existsByUsername("admin"));
        assertTrue(userRepository.existsByUsername("demo"));

        // Demo story must be seeded
        assertTrue(storyRepository.existsById("story_panchatantra_monkey_wedge"));
        Story story = storyRepository.findById("story_panchatantra_monkey_wedge").orElseThrow();
        assertEquals("The Monkey and the Wedge", story.getTitle());
        assertEquals(Enums.PublicationStatus.PUBLISHED, story.getStatus());
        assertTrue(story.isRightsVerified());
    }
}
