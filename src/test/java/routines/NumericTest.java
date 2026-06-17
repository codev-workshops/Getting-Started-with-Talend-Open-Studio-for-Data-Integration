package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class NumericTest {

    @Test
    void sequenceIncrementsCorrectly() {
        Numeric.removeSequence("test-seq");
        assertEquals(1, Numeric.sequence("test-seq", 1, 1));
        assertEquals(2, Numeric.sequence("test-seq", 1, 1));
        assertEquals(3, Numeric.sequence("test-seq", 1, 1));
    }

    @Test
    void sequenceNegativeStep() {
        Numeric.removeSequence("neg-seq");
        assertEquals(100, Numeric.sequence("neg-seq", 100, -2));
        assertEquals(98, Numeric.sequence("neg-seq", 100, -2));
    }

    @Test
    void resetSequence() {
        Numeric.removeSequence("reset-seq");
        Numeric.sequence("reset-seq", 1, 1);
        Numeric.sequence("reset-seq", 1, 1);
        Numeric.resetSequence("reset-seq", 50);
        assertEquals(51, Numeric.sequence("reset-seq", 1, 1));
    }

    @Test
    void randomInRange() {
        for (int i = 0; i < 100; i++) {
            int val = Numeric.random(5, 10);
            assertTrue(val >= 5 && val <= 10, "Value out of range: " + val);
        }
    }

    @Test
    void convertImpliedDecimalFormat() {
        assertEquals(1.23f, Numeric.convertImpliedDecimalFormat("9V99", "123"), 0.001f);
        assertEquals(12.3f, Numeric.convertImpliedDecimalFormat("99V9", "123"), 0.001f);
    }
}
