package io.flowdesk;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.Map;
import java.util.UUID;
import jakarta.persistence.EntityManagerFactory;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FoundationIT {
    @Container
    @ServiceConnection
    static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:17-alpine");

    @Autowired TestRestTemplate http;
    @Autowired JdbcTemplate jdbc;
    @Autowired Flyway flyway;
    @Autowired EntityManagerFactory entityManagerFactory;

    @Test
    void contextLoadsWithPostgresAndHibernateValidation() {
        assertThat(entityManagerFactory.isOpen()).isTrue();
        assertThat(entityManagerFactory.getProperties()).containsEntry("hibernate.hbm2ddl.auto", "validate");
        assertThat(jdbc.queryForObject("select version()", String.class)).startsWith("PostgreSQL 17.");
    }

    @Test
    void migrationCreatesOnlyTheExpectedFoundationTables() {
        assertThat(flyway.info().current().getVersion().getVersion()).isEqualTo("1");
        assertThat(flyway.validateWithResult().validationSuccessful).isTrue();
        assertThat(flyway.info().pending()).isEmpty();
        assertThat(jdbc.queryForList("select tablename from pg_tables where schemaname = 'public'", String.class))
                .containsExactlyInAnyOrder("app_users", "flyway_schema_history");
        assertThat(jdbc.queryForList("select column_name from information_schema.columns "
                + "where table_schema = 'public' and table_name = 'app_users' order by ordinal_position", String.class))
                .containsExactly("id", "email", "display_name", "created_at");
    }

    @Test
    @Transactional
    void migrationSupportsUserStorageWithTimestampDefault() {
        UUID id = UUID.randomUUID();
        jdbc.update("insert into app_users (id, email, display_name) values (?, ?, ?)",
                id, "foundation@example.test", "Foundation");
        var row = jdbc.queryForMap("select * from app_users where id = ?", id);
        assertThat(row).containsEntry("id", id).containsEntry("email", "foundation@example.test")
                .containsEntry("display_name", "Foundation");
        assertThat(row.get("created_at")).isNotNull();
    }

    @Test
    @Transactional
    void migrationRejectsDuplicateEmails() {
        jdbc.update("insert into app_users (id, email, display_name) values (?, ?, ?)",
                UUID.randomUUID(), "duplicate@example.test", "First");
        assertThatThrownBy(() -> jdbc.update("insert into app_users (id, email, display_name) values (?, ?, ?)",
                UUID.randomUUID(), "duplicate@example.test", "Second"))
                .isInstanceOf(DataIntegrityViolationException.class);
    }

    @Test
    @Transactional
    void migrationRejectsMissingDisplayName() {
        assertThatThrownBy(() -> jdbc.update("insert into app_users (id, email) values (?, ?)",
                UUID.randomUUID(), "missing@example.test"))
                .isInstanceOf(DataIntegrityViolationException.class);
    }

    @Test
    void healthIsUpWithMigratedPostgres() {
        var response = http.getForEntity("/actuator/health", Map.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).containsEntry("status", "UP");
        assertThat(response.getBody()).doesNotContainKey("components");
    }

    @Test
    void infoMatchesThePublicContractOverHttp() {
        var response = http.getForEntity("/api/v1/info", Map.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isEqualTo(Map.of("application", "FlowDesk", "stage", "sprint-0"));
    }
}
