package routines.system;

import java.util.Locale;

/**
 * Resolves a language or country code string to a {@link Locale}.
 * This is a minimal reimplementation of the Talend runtime class referenced
 * by the system routines shipped with the book.
 */
public final class LocaleProvider {

    private LocaleProvider() {}

    /**
     * Returns a {@link Locale} for the given ISO-639 language code
     * or ISO-3166 country code (case-insensitive).
     */
    public static Locale getLocale(String languageOrCountryCode) {
        if (languageOrCountryCode == null || languageOrCountryCode.isEmpty()) {
            return Locale.getDefault();
        }
        String code = languageOrCountryCode.trim();
        if (code.contains("_") || code.contains("-")) {
            return Locale.forLanguageTag(code.replace('_', '-'));
        }
        if (code.length() == 2 && code.equals(code.toUpperCase())) {
            return new Locale("", code);
        }
        return new Locale(code.toLowerCase());
    }
}
