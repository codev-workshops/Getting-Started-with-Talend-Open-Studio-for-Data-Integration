package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class DataOperationTest {

    @Test
    void charConvertsDigitToChar() {
        assertEquals('5', DataOperation.CHAR(5));
    }

    @Test
    void dtxConvertsDecimalToHex() {
        assertEquals("ff", DataOperation.DTX(255));
        assertEquals("a", DataOperation.DTX(10));
    }

    @Test
    void fixRoundsToLong() {
        assertEquals(3L, DataOperation.FIX(3.14));
        assertEquals(4L, DataOperation.FIX(3.6));
    }

    @Test
    void xtdConvertsHexToDecimal() {
        assertEquals(255, DataOperation.XTD("ff"));
        assertEquals(10, DataOperation.XTD("a"));
    }
}
