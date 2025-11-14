package com.virtplc.repository;

import com.virtplc.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);

    Optional<User> findByEmailAndCompanyDomain(String email, String companyDomain);

    long countByCompanyId(Long companyId);

    List<User> findByCompanyId(Long companyId);

    List<User> findByManufacturerId(Long manufacturerId);
}
