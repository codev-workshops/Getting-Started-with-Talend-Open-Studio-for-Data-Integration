package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class StringHandlingTest {

    @Test void alpha() {
        assertTrue(StringHandling.ALPHA("abcdef"));
        assertFalse(StringHandling.ALPHA("zyxwvu"));
    }

    @Test void isAlpha() {
        assertTrue(StringHandling.IS_ALPHA("abc"));
        assertFalse(StringHandling.IS_ALPHA("abc123"));
    }

    @Test void change() {
        assertEquals("hello guy!", StringHandling.CHANGE("hello world!", "world", "guy"));
        assertNull(StringHandling.CHANGE(null, "a", "b"));
    }

    @Test void count() {
        assertEquals(2, StringHandling.COUNT("hello hello world", "hello"));
        assertEquals(0, StringHandling.COUNT(null, "a"));
    }

    @Test void downcase() { assertEquals("hello", StringHandling.DOWNCASE("HELLO")); }

    @Test void upcase() { assertEquals("HELLO", StringHandling.UPCASE("hello")); }

    @Test void dquote() { assertEquals("\"hello\"", StringHandling.DQUOTE("hello")); }

    @Test void ereplace() {
        assertEquals("hello guy!", StringHandling.EREPLACE("hello world!", "world", "guy"));
    }

    @Test void index() {
        assertEquals(6, StringHandling.INDEX("hello world!", "world"));
        assertEquals(-1, StringHandling.INDEX(null, "a"));
    }

    @Test void left() { assertEquals("hello", StringHandling.LEFT("hello world!", 5)); }

    @Test void right() { assertEquals("world!", StringHandling.RIGHT("hello world!", 6)); }

    @Test void len() {
        assertEquals(12, StringHandling.LEN("hello world!"));
        assertEquals(-1, StringHandling.LEN(null));
    }

    @Test void space() { assertEquals("   ", StringHandling.SPACE(3)); }

    @Test void squote() { assertEquals("'hello'", StringHandling.SQUOTE("hello")); }

    @Test void str() { assertEquals("aaa", StringHandling.STR('a', 3)); }

    @Test void trim() { assertEquals("hello", StringHandling.TRIM("  hello  ")); }

    @Test void btrim() { assertEquals("  hello", StringHandling.BTRIM("  hello  ")); }

    @Test void ftrim() { assertEquals("hello  ", StringHandling.FTRIM("  hello  ")); }
}
