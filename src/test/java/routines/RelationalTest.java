package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class RelationalTest {

    @Test
    void isNull() {
        assertTrue(Relational.ISNULL(null));
        assertFalse(Relational.ISNULL("hello"));
    }

    @Test
    void not() {
        assertTrue(Relational.NOT(false));
        assertFalse(Relational.NOT(true));
    }
}
