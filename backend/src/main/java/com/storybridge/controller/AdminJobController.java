package com.storybridge.controller;

import com.storybridge.domain.PipelineJobEntity;
import com.storybridge.service.PipelineJobService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin/jobs")
@RequiredArgsConstructor
public class AdminJobController {

    private final PipelineJobService pipelineJobService;

    @GetMapping
    public ResponseEntity<List<PipelineJobEntity>> getAllJobs() {
        return ResponseEntity.ok(pipelineJobService.getAllJobs());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PipelineJobEntity> getJobById(@PathVariable String id) {
        return pipelineJobService.getJob(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
