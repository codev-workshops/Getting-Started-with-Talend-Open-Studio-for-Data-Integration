package routines;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

/**
 * Integration test that verifies demo_db schema was loaded into MySQL.
 * Runs only when DEMO_DB_URL env var is set (CI or local with MySQL).
 */
@EnabledIfEnvironmentVariable(named = "DEMO_DB_URL", matches = ".+")
class DemoDatabaseIT {

    @Test
    void productsTableHas13Rows() throws Exception {
        String url  = System.getenv("DEMO_DB_URL");
        String user = System.getenv().getOrDefault("DEMO_DB_USER", "talend");
        String pass = System.getenv().getOrDefault("DEMO_DB_PASS", "talend");

        try (Connection conn = DriverManager.getConnection(url, user, pass);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM products")) {
            assertTrue(rs.next());
            assertEquals(13, rs.getInt(1));
        }
    }

    @Test
    void ordersTableHas7Rows() throws Exception {
        String url  = System.getenv("DEMO_DB_URL");
        String user = System.getenv().getOrDefault("DEMO_DB_USER", "talend");
        String pass = System.getenv().getOrDefault("DEMO_DB_PASS", "talend");

        try (Connection conn = DriverManager.getConnection(url, user, pass);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM orders")) {
            assertTrue(rs.next());
            assertEquals(7, rs.getInt(1));
        }
    }

    @Test
    void brandsTableHas13Rows() throws Exception {
        String url  = System.getenv("DEMO_DB_URL");
        String user = System.getenv().getOrDefault("DEMO_DB_USER", "talend");
        String pass = System.getenv().getOrDefault("DEMO_DB_PASS", "talend");

        try (Connection conn = DriverManager.getConnection(url, user, pass);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM brands")) {
            assertTrue(rs.next());
            assertEquals(13, rs.getInt(1));
        }
    }
}
