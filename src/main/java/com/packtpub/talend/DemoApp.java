package com.packtpub.talend;

import routines.*;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

/**
 * Quick smoke-test that the Talend system routines compile and the
 * demo_db MySQL schema is reachable.
 */
public class DemoApp {

    public static void main(String[] args) throws Exception {
        System.out.println("=== Talend System Routines Demo ===\n");

        // DataOperation
        System.out.println("DTX(255)       = " + DataOperation.DTX(255));
        System.out.println("XTD(\"ff\")      = " + DataOperation.XTD("ff"));

        // Mathematical
        System.out.println("SQRT(144)      = " + Mathematical.SQRT(144));
        System.out.println("ABS(-42)       = " + Mathematical.ABS(-42));

        // StringHandling
        System.out.println("UPCASE(\"hello\")= " + StringHandling.UPCASE("hello"));
        System.out.println("LEFT(\"hello world\",5) = " + StringHandling.LEFT("hello world", 5));

        // TalendDate
        System.out.println("Today          = " + TalendDate.getDate("yyyy-MM-dd"));

        // TalendDataGenerator
        System.out.println("Random name    = " + TalendDataGenerator.getFirstName()
                + " " + TalendDataGenerator.getLastName());

        // Database connectivity
        String url  = System.getProperty("demo.db.url",  "jdbc:mysql://localhost:3306/demo_db");
        String user = System.getProperty("demo.db.user", "talend");
        String pass = System.getProperty("demo.db.pass", "talend");

        System.out.println("\n=== Database Query (demo_db.products) ===\n");
        try (Connection conn = DriverManager.getConnection(url, user, pass);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(
                     "SELECT product_id, product_name, price FROM products ORDER BY product_id")) {
            System.out.printf("%-12s %-45s %s%n", "PRODUCT_ID", "PRODUCT_NAME", "PRICE");
            System.out.println("-".repeat(70));
            while (rs.next()) {
                System.out.printf("%-12d %-45s %.2f%n",
                        rs.getInt("product_id"),
                        rs.getString("product_name"),
                        rs.getFloat("price"));
            }
        }

        System.out.println("\nDone.");
    }
}
