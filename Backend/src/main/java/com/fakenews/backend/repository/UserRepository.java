package com.fakenews.backend.repository;

import com.fakenews.backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
    User findFirstByEmailOrderByIdDesc(String email);
}