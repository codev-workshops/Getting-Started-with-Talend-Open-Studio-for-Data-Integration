package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class TalendStringTest {

    @Test
    void replaceSpecialCharForXML() {
        assertEquals("&amp;&lt;&gt;", TalendString.replaceSpecialCharForXML("&<>"));
    }

    @Test
    void checkCDATAForXML() {
        String cdata = "<![CDATA[hello]]>";
        assertEquals(cdata, TalendString.checkCDATAForXML(cdata));
        assertEquals("&amp;", TalendString.checkCDATAForXML("&"));
    }

    @Test
    void getAsciiRandomString() {
        String s = TalendString.getAsciiRandomString(10);
        assertEquals(10, s.length());
        assertTrue(s.chars().allMatch(Character::isLetterOrDigit));
    }

    @Test
    void talendTrimBoth() {
        assertEquals("hello", TalendString.talendTrim("$$hello$$", '$', 0));
    }

    @Test
    void talendTrimLeft() {
        assertEquals("hello$$", TalendString.talendTrim("$$hello$$", '$', 1));
    }

    @Test
    void talendTrimRight() {
        assertEquals("$$hello", TalendString.talendTrim("$$hello$$", '$', -1));
    }

    @Test
    void removeAccents() {
        assertEquals("Acces a la base", TalendString.removeAccents("Acc\u00e8s \u00e0 la base"));
    }
}
