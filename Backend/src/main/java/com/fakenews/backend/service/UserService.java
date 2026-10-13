package com.fakenews.backend.service;

import com.fakenews.backend.model.User;
import com.fakenews.backend.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public User registerUser(String name, String email, String password) {

        String encodedPassword = passwordEncoder.encode(password);

        User user = new User(name, email, encodedPassword);

        return userRepository.save(user);
    }
    public User loginUser(String email, String password) {

    User user = userRepository.findFirstByEmailOrderByIdDesc(email);

    if (user != null && passwordEncoder.matches(password, user.getPassword())) {
        return user;
    }

    return null;
}
}