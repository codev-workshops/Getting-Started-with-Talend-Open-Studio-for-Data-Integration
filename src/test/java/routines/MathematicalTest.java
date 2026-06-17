package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class MathematicalTest {

    @Test void abs() { assertEquals(10.0, Mathematical.ABS(-10.0)); }

    @Test void trigFunctions() {
        assertEquals(Math.cos(1.0), Mathematical.COS(1.0));
        assertEquals(Math.sin(1.0), Mathematical.SIN(1.0));
        assertEquals(Math.tan(1.0), Mathematical.TAN(1.0));
    }

    @Test void hyperbolicFunctions() {
        assertEquals(Math.cosh(1.0), Mathematical.COSH(1.0));
        assertEquals(Math.sinh(1.0), Mathematical.SINH(1.0));
        assertEquals(Math.tanh(1.0), Mathematical.TANH(1.0));
    }

    @Test void inverseTrig() {
        assertEquals(Math.acos(0.5), Mathematical.ACOS(0.5));
        assertEquals(Math.asin(0.5), Mathematical.ASIN(0.5));
        assertEquals(Math.atan(0.5), Mathematical.ATAN(0.5));
    }

    @Test void bitwiseOps() {
        assertEquals(0b1010 & 0b1100, Mathematical.BITAND(0b1010, 0b1100));
        assertEquals(0b1010 | 0b1100, Mathematical.BITOR(0b1010, 0b1100));
        assertEquals(0b1010 ^ 0b1100, Mathematical.BITXOR(0b1010, 0b1100));
        assertEquals(~10, Mathematical.BITNOT(10));
    }

    @Test void div() { assertEquals(3, Mathematical.DIV(10.0, 3.0)); }

    @Test void exp() { assertEquals(Math.exp(2.0), Mathematical.EXP(2.0)); }

    @Test void intParse() { assertEquals(42, Mathematical.INT("42")); }

    @Test void ffix() { assertEquals("3.14", Mathematical.FFIX(3.1415926, 2)); }

    @Test void fflt() { assertNotNull(Mathematical.FFLT(3.14)); }

    @Test void ln() { assertEquals(Math.log(2.0) / Math.E, Mathematical.LN(2.0), 1e-10); }

    @Test void mod() { assertEquals(1.0, Mathematical.MOD(7, 3)); }

    @Test void neg() { assertEquals(-5.0, Mathematical.NEG(5.0)); }

    @Test void num() {
        assertEquals(1, Mathematical.NUM("123"));
        assertEquals(0, Mathematical.NUM("abc"));
    }

    @Test void real() { assertEquals(3.14, Mathematical.REAL("3.14")); }

    @Test void rnd() { assertTrue(Mathematical.RND(10.0) < 10.0); }

    @Test void sadd() { assertEquals(30.0, Mathematical.SADD("10", "20")); }

    @Test void scmp() {
        assertEquals(-1, Mathematical.SCMP("10", "20"));
        assertEquals(0, Mathematical.SCMP("10", "10"));
        assertEquals(1, Mathematical.SCMP("20", "10"));
    }

    @Test void sdiv() { assertEquals(2, Mathematical.SDIV(10, 5)); }

    @Test void smul() { assertEquals(6.0, Mathematical.SMUL("2", "3")); }

    @Test void sqrt() { assertEquals(3.0, Mathematical.SQRT(9.0)); }

    @Test void ssub() { assertEquals("10.0", Mathematical.SSUB("20", "10")); }
}
