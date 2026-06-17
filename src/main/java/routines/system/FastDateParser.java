package routines.system;

import java.text.FieldPosition;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * Thread-safe date formatter/parser that caches {@link SimpleDateFormat}
 * instances per pattern+locale combination. This is a minimal
 * reimplementation of the Talend runtime class referenced by the system
 * routines shipped with the book.
 */
public final class FastDateParser {

    private static final ConcurrentMap<String, FastDateParser> CACHE = new ConcurrentHashMap<>();

    private final ThreadLocal<SimpleDateFormat> formatter;

    private FastDateParser(String pattern, Locale locale) {
        this.formatter = ThreadLocal.withInitial(() -> {
            SimpleDateFormat sdf = new SimpleDateFormat(pattern, locale);
            sdf.setLenient(false);
            return sdf;
        });
    }

    public static FastDateParser getInstance(String pattern) {
        return getInstance(pattern, Locale.getDefault());
    }

    public static FastDateParser getInstance(String pattern, Locale locale) {
        String key = pattern + "|" + locale.toLanguageTag();
        return CACHE.computeIfAbsent(key, k -> new FastDateParser(pattern, locale));
    }

    public String format(Date date) {
        return formatter.get().format(date);
    }

    public String format(Date date, StringBuffer toAppendTo, FieldPosition pos) {
        return formatter.get().format(date, toAppendTo, pos).toString();
    }

    public Date parse(String source) throws ParseException {
        return formatter.get().parse(source);
    }
}
