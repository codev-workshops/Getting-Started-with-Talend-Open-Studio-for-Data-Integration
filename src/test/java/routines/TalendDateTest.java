package routines;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import java.util.Calendar;
import java.util.Date;

class TalendDateTest {

    @Test
    void getPartOfDate() {
        Calendar cal = Calendar.getInstance();
        cal.set(2024, Calendar.MARCH, 15, 10, 30, 45);
        Date date = cal.getTime();
        assertEquals(2024, TalendDate.getPartOfDate("YEAR", date));
        assertEquals(Calendar.MARCH, TalendDate.getPartOfDate("MONTH", date));
        assertEquals(15, TalendDate.getPartOfDate("DAY_OF_MONTH", date));
    }

    @Test
    void formatDate() {
        Calendar cal = Calendar.getInstance();
        cal.set(2024, Calendar.JANUARY, 1, 0, 0, 0);
        String formatted = TalendDate.formatDate("yyyy-MM-dd", cal.getTime());
        assertEquals("2024-01-01", formatted);
    }

    @Test
    void isDate() {
        assertTrue(TalendDate.isDate("2024-01-15", "yyyy-MM-dd"));
        assertFalse(TalendDate.isDate("not-a-date", "yyyy-MM-dd"));
        assertFalse(TalendDate.isDate(null, "yyyy-MM-dd"));
    }

    @Test
    void compareDate() {
        Date d1 = TalendDate.parseDate("yyyy-MM-dd", "2024-01-01");
        Date d2 = TalendDate.parseDate("yyyy-MM-dd", "2024-06-15");
        assertEquals(-1, TalendDate.compareDate(d1, d2));
        assertEquals(1, TalendDate.compareDate(d2, d1));
        assertEquals(0, TalendDate.compareDate(d1, d1));
    }

    @Test
    void compareDateWithPattern() {
        Date d1 = TalendDate.parseDate("yyyy-MM-dd HH:mm:ss", "2024-01-15 10:00:00");
        Date d2 = TalendDate.parseDate("yyyy-MM-dd HH:mm:ss", "2024-01-15 23:00:00");
        assertEquals(0, TalendDate.compareDate(d1, d2, "yyyy-MM-dd"));
    }

    @Test
    void addDate() {
        Date d = TalendDate.parseDate("yyyy-MM-dd", "2024-01-15");
        Date result = TalendDate.addDate(d, 5, "dd");
        String formatted = TalendDate.formatDate("yyyy-MM-dd", result);
        assertEquals("2024-01-20", formatted);
    }

    @Test
    void parseDate() {
        Date d = TalendDate.parseDate("yyyy-MM-dd", "2024-03-15");
        assertNotNull(d);
        String formatted = TalendDate.formatDate("yyyy-MM-dd", d);
        assertEquals("2024-03-15", formatted);
    }

    @Test
    void getDate() {
        String today = TalendDate.getDate("yyyy-MM-dd");
        assertNotNull(today);
        assertTrue(today.matches("\\d{4}-\\d{2}-\\d{2}"));
    }

    @Test
    void formatDateLocale() {
        Date d = TalendDate.parseDate("yyyy-MM-dd", "2024-01-15");
        String result = TalendDate.formatDateLocale("yyyy-MM-dd", d, "en");
        assertEquals("2024-01-15", result);
    }

    @Test
    void formatDateLocaleUppercaseLanguageCode() {
        Date d = TalendDate.parseDate("yyyy-MM-dd", "2024-01-15");
        // Uppercase "EN" and "FR" must resolve to language locales, not country-only
        String enResult = TalendDate.formatDateLocale("yyyy-MM-dd", d, "EN");
        assertEquals("2024-01-15", enResult);
        String frResult = TalendDate.formatDateLocale("yyyy-MM-dd", d, "FR");
        assertEquals("2024-01-15", frResult);
    }
}
