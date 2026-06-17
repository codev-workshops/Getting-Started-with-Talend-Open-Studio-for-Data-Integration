package routines.system;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import java.text.ParseException;
import java.util.Date;
import java.util.Locale;

class FastDateParserTest {

    @Test
    void formatAndParse() throws ParseException {
        FastDateParser parser = FastDateParser.getInstance("yyyy-MM-dd");
        Date d = parser.parse("2024-03-15");
        assertEquals("2024-03-15", parser.format(d));
    }

    @Test
    void localeAwareInstance() throws ParseException {
        FastDateParser parser = FastDateParser.getInstance("yyyy-MM-dd", Locale.US);
        Date d = parser.parse("2024-01-01");
        assertNotNull(d);
    }

    @Test
    void cachesInstances() {
        FastDateParser a = FastDateParser.getInstance("yyyy");
        FastDateParser b = FastDateParser.getInstance("yyyy");
        assertSame(a, b);
    }
}
