package com.storybridge.service;

import com.storybridge.auth.AuthDTOs;
import com.storybridge.auth.JwtUtils;
import com.storybridge.domain.Enums;
import com.storybridge.domain.User;
import com.storybridge.repository.UserRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;
    private final AuthenticationManager authenticationManager;

    @PostConstruct
    public void seedInitialUsers() {
        if (!userRepository.existsByUsername("admin")) {
            User admin = User.builder()
                    .username("admin")
                    .email("admin@storybridge.ai")
                    .password(passwordEncoder.encode("admin123"))
                    .role(Enums.Role.ADMIN)
                    .build();
            userRepository.save(admin);
            log.info("Default ADMIN user created: admin / admin123");
        }

        if (!userRepository.existsByUsername("reviewer")) {
            User reviewer = User.builder()
                    .username("reviewer")
                    .email("reviewer@storybridge.ai")
                    .password(passwordEncoder.encode("reviewer123"))
                    .role(Enums.Role.REVIEWER)
                    .build();
            userRepository.save(reviewer);
            log.info("Default REVIEWER user created: reviewer / reviewer123");
        }

        if (!userRepository.existsByUsername("demo")) {
            User demo = User.builder()
                    .username("demo")
                    .email("demo@storybridge.ai")
                    .password(passwordEncoder.encode("demo123"))
                    .role(Enums.Role.USER)
                    .build();
            userRepository.save(demo);
            log.info("Default USER created: demo / demo123");
        }
    }

    public AuthDTOs.AuthResponse register(AuthDTOs.RegisterRequest req) {
        if (userRepository.existsByUsername(req.getUsername())) {
            throw new IllegalArgumentException("Username is already taken");
        }
        if (userRepository.existsByEmail(req.getEmail())) {
            throw new IllegalArgumentException("Email is already in use");
        }

        User user = User.builder()
                .username(req.getUsername())
                .email(req.getEmail())
                .password(passwordEncoder.encode(req.getPassword()))
                .role(req.getRole() != null ? req.getRole() : Enums.Role.USER)
                .build();

        userRepository.save(user);

        String token = jwtUtils.generateToken(user.getUsername(), user.getRole().name());

        return AuthDTOs.AuthResponse.builder()
                .token(token)
                .username(user.getUsername())
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }

    public AuthDTOs.AuthResponse login(AuthDTOs.LoginRequest req) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(req.getUsername(), req.getPassword())
        );

        User user = userRepository.findByUsername(req.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("Invalid username or password"));

        String token = jwtUtils.generateToken(user.getUsername(), user.getRole().name());

        return AuthDTOs.AuthResponse.builder()
                .token(token)
                .username(user.getUsername())
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }

    public AuthDTOs.UserProfileDTO getCurrentUser(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + username));

        return AuthDTOs.UserProfileDTO.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }
}
