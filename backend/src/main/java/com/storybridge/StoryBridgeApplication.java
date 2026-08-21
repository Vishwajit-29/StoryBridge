package com.storybridge;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class StoryBridgeApplication {

    public static void main(String[] args) {
        SpringApplication.run(StoryBridgeApplication.class, args);
    }
}
