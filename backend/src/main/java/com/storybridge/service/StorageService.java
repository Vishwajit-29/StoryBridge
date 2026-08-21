package com.storybridge.service;

import io.minio.*;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;

@Service
@Slf4j
public class StorageService {

    @Value("${storybridge.storage.type:local}")
    private String storageType;

    @Value("${storybridge.storage.local-root-path:../storage/artifacts}")
    private String localRootPath;

    @Value("${storybridge.storage.minio.endpoint:http://localhost:9000}")
    private String minioEndpoint;

    @Value("${storybridge.storage.minio.access-key:minioadmin}")
    private String minioAccessKey;

    @Value("${storybridge.storage.minio.secret-key:minioadmin}")
    private String minioSecretKey;

    @Value("${storybridge.storage.minio.bucket:storybridge-artifacts}")
    private String minioBucket;

    private MinIOStorageProvider minioClientProvider;

    @PostConstruct
    public void init() {
        Path root = getArtifactBasePath();
        try {
            Files.createDirectories(root);
            log.info("Storage initialized at local path: {}", root.toAbsolutePath());
        } catch (IOException e) {
            log.error("Could not initialize local storage folder: {}", e.getMessage());
        }

        if ("minio".equalsIgnoreCase(storageType)) {
            try {
                MinioClient client = MinioClient.builder()
                        .endpoint(minioEndpoint)
                        .credentials(minioAccessKey, minioSecretKey)
                        .build();
                boolean exists = client.bucketExists(BucketExistsArgs.builder().bucket(minioBucket).build());
                if (!exists) {
                    client.makeBucket(MakeBucketArgs.builder().bucket(minioBucket).build());
                }
                this.minioClientProvider = new MinIOStorageProvider(client, minioBucket);
                log.info("Connected to MinIO bucket: {}", minioBucket);
            } catch (Exception e) {
                log.warn("Could not connect to MinIO ({}), falling back to local filesystem storage.", e.getMessage());
            }
        }
    }

    public Path getArtifactBasePath() {
        // 1. Check parent storage/artifacts first (when running from backend/)
        Path parentStorage = Paths.get("..", "storage", "artifacts").toAbsolutePath().normalize();
        if (Files.exists(parentStorage) && hasStoryFolders(parentStorage)) {
            return parentStorage;
        }

        // 2. Check local storage/artifacts (when running from project root)
        Path curStorage = Paths.get("storage", "artifacts").toAbsolutePath().normalize();
        if (Files.exists(curStorage) && hasStoryFolders(curStorage)) {
            return curStorage;
        }

        // 3. Check configured localRootPath
        Path configured = Paths.get(localRootPath).toAbsolutePath().normalize();
        if (Files.exists(configured) && hasStoryFolders(configured)) {
            return configured;
        }

        // 4. Return any existing candidate
        List<Path> candidates = List.of(parentStorage, curStorage, configured);
        for (Path p : candidates) {
            if (Files.exists(p)) {
                return p;
            }
        }

        return parentStorage;
    }

    private boolean hasStoryFolders(Path p) {
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(p)) {
            for (Path sub : stream) {
                if (Files.isDirectory(sub) && (sub.getFileName().toString().startsWith("story_") || Files.exists(sub.resolve("understanding")))) {
                    return true;
                }
            }
        } catch (Exception ignored) {}
        return false;
    }

    public String storeFile(String storyId, String relativePath, MultipartFile file) throws IOException {
        Path targetPath = getArtifactBasePath().resolve(storyId).resolve(relativePath);
        Files.createDirectories(targetPath.getParent());
        Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
        return targetPath.toAbsolutePath().toString();
    }

    public String storeTextContent(String storyId, String relativePath, String content) throws IOException {
        Path targetPath = getArtifactBasePath().resolve(storyId).resolve(relativePath);
        Files.createDirectories(targetPath.getParent());
        Files.writeString(targetPath, content);
        return targetPath.toAbsolutePath().toString();
    }

    public byte[] readFile(String storyId, String relativePath) throws IOException {
        Path targetPath = getArtifactBasePath().resolve(storyId).resolve(relativePath);
        if (!Files.exists(targetPath)) {
            // Check direct absolute path
            targetPath = Paths.get(relativePath);
        }
        if (!Files.exists(targetPath)) {
            throw new FileNotFoundException("File not found at: " + targetPath.toAbsolutePath());
        }
        return Files.readAllBytes(targetPath);
    }

    public static class MinIOStorageProvider {
        private final MinioClient client;
        private final String bucket;

        public MinIOStorageProvider(MinioClient client, String bucket) {
            this.client = client;
            this.bucket = bucket;
        }
    }
}
