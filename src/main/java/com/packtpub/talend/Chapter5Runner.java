package com.packtpub.talend;

import java.io.*;
import java.math.BigDecimal;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.*;

/**
 * Chapter 5 — Data Transformation jobs.
 *
 * Implements the ten Talend jobs from ExampleJobs/.../Chapter5/ as pure Java:
 *   1. Aggregating      (tAggregateRow)
 *   2. Denormalize       (tDenormalize)
 *   3. ExtractDelimited  (tExtractDelimitedFields)
 *   4. Filtering1        (tFilterRow — basic)
 *   5. Filtering2        (tFilterRow — with rejects)
 *   6. Filtering3        (tFilterRow — replicate + dual filter)
 *   7. FindAndReplace    (tReplace)
 *   8. Normalize         (tNormalize)
 *   9. SampleRow         (tSampleRow)
 *  10. Sorting           (tSortRow)
 */
public class Chapter5Runner {

    static final String DATA_DIR = "SampleDataFiles/Chapter5/";
    static final String OUT_DIR  = "output/Chapter5/";

    public static void main(String[] args) throws Exception {
        Files.createDirectories(Path.of(OUT_DIR));

        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   Chapter 5 — Data Transformation Jobs                  ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝\n");

        Map<String, JobResult> results = new LinkedHashMap<>();

        results.put("Aggregating",           runAggregating());
        results.put("Denormalize",           runDenormalize());
        results.put("ExtractDelimitedFields", runExtractDelimitedFields());
        results.put("Filtering1",            runFiltering1());
        results.put("Filtering2",            runFiltering2());
        results.put("Filtering3",            runFiltering3());
        results.put("FindAndReplace",        runFindAndReplace());
        results.put("Normalize",             runNormalize());
        results.put("SampleRow",             runSampleRow());
        results.put("Sorting",               runSorting());

        System.out.println("\n══════════════════════════════════════════════════════════");
        System.out.println("All Chapter 5 jobs completed.");
        System.out.println("══════════════════════════════════════════════════════════\n");

        generateHtmlReport(results);
    }

    // ──────────────────────────────────────────────────────────
    // Job 1: Aggregating (tAggregateRow)
    // invoices.csv -> group by customer_name, SUM(invoice_value)
    // ──────────────────────────────────────────────────────────
    static JobResult runAggregating() throws IOException {
        System.out.println("▶ Job 1: Aggregating (tAggregateRow)");
        List<String> lines = readNonEmpty(DATA_DIR + "invoices.csv");
        int inputRows = lines.size();

        Map<String, BigDecimal> totals = new LinkedHashMap<>();
        for (String line : lines) {
            String[] parts = line.split(";", -1);
            String customer = parts[1].trim();
            BigDecimal value = new BigDecimal(parts[2].trim());
            totals.merge(customer, value, BigDecimal::add);
        }

        List<String> outputLines = new ArrayList<>();
        for (var entry : totals.entrySet()) {
            outputLines.add(entry.getKey() + ";" + entry.getValue());
        }

        String outFile = OUT_DIR + "customer_invoiced_total.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("Aggregating", "tAggregateRow",
                "invoices.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Group by customer_name, SUM(invoice_value)", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 2: Denormalize (tDenormalize)
    // categories-to-denormalize.csv -> merge categories per product_id
    // ──────────────────────────────────────────────────────────
    static JobResult runDenormalize() throws IOException {
        System.out.println("▶ Job 2: Denormalize (tDenormalize)");
        List<String> lines = readNonEmpty(DATA_DIR + "categories-to-denormalize.csv");
        int inputRows = lines.size();

        Map<String, List<String>> grouped = new LinkedHashMap<>();
        for (String line : lines) {
            String[] parts = line.split(";", 2);
            String productId = parts[0].trim();
            String category  = parts[1].trim();
            grouped.computeIfAbsent(productId, k -> new ArrayList<>()).add(category);
        }

        List<String> outputLines = new ArrayList<>();
        for (var entry : grouped.entrySet()) {
            outputLines.add(entry.getKey() + "|" + String.join(";", entry.getValue()));
        }

        String outFile = OUT_DIR + "denormalized-categories.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("Denormalize", "tDenormalize",
                "categories-to-denormalize.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Group rows by product_id, concat categories with ';'", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 3: ExtractDelimitedFields (tExtractDelimitedFields)
    // employees.csv -> split 'name' by ',' into first_name, last_name
    // ──────────────────────────────────────────────────────────
    static JobResult runExtractDelimitedFields() throws IOException {
        System.out.println("▶ Job 3: ExtractDelimitedFields (tExtractDelimitedFields)");
        List<String> lines = readNonEmpty(DATA_DIR + "employees.csv");
        int inputRows = lines.size();

        List<String> outputLines = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split("\\|", 2);
            String employeeId = parts[0].trim();
            String name = parts[1].trim();
            String[] nameParts = name.split(",", 2);
            String firstName = nameParts.length > 0 ? nameParts[0].trim() : "";
            String lastName  = nameParts.length > 1 ? nameParts[1].trim() : "";
            outputLines.add(employeeId + ";" + firstName + ";" + lastName);
        }

        String outFile = OUT_DIR + "extract-delimited-fields.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("ExtractDelimitedFields", "tExtractDelimitedFields",
                "employees.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Split 'name' field by ',' into first_name, last_name", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 4: Filtering1 (tFilterRow — basic)
    // currencies.csv -> keep rows where currency == "EUR"
    // ──────────────────────────────────────────────────────────
    static JobResult runFiltering1() throws IOException {
        System.out.println("▶ Job 4: Filtering1 (tFilterRow — basic)");
        List<String> lines = readNonEmpty(DATA_DIR + "currencies.csv");
        int inputRows = lines.size();

        List<String> outputLines = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split(";", -1);
            if (parts.length >= 2 && "EUR".equals(parts[1].trim())) {
                outputLines.add(parts[0].trim() + ";" + parts[1].trim());
            }
        }

        String outFile = OUT_DIR + "filtering1-currencies.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("Filtering1", "tFilterRow",
                "currencies.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Filter: currency == 'EUR'", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 5: Filtering2 (tFilterRow — with rejects)
    // currencies.csv -> EUR matches + reject file
    // ──────────────────────────────────────────────────────────
    static JobResult runFiltering2() throws IOException {
        System.out.println("▶ Job 5: Filtering2 (tFilterRow — with rejects)");
        List<String> lines = readNonEmpty(DATA_DIR + "currencies.csv");
        int inputRows = lines.size();

        List<String> matchLines  = new ArrayList<>();
        List<String> rejectLines = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split(";", -1);
            String country  = parts[0].trim();
            String currency = parts.length >= 2 ? parts[1].trim() : "";
            if ("EUR".equals(currency)) {
                matchLines.add(country + ";" + currency);
            } else {
                rejectLines.add(country + ";" + currency + ";row does not match filter");
            }
        }

        String outFile    = OUT_DIR + "filtering2-currencies.csv";
        String rejectFile = OUT_DIR + "filtering2-currency-rejects.csv";
        Files.writeString(Path.of(outFile), String.join("\n", matchLines) + "\n");
        Files.writeString(Path.of(rejectFile), String.join("\n", rejectLines) + "\n");

        printSample("  Matches (" + outFile + "):", matchLines);
        printSample("  Rejects (" + rejectFile + "):", rejectLines);
        System.out.println("  Rows in: " + inputRows + "  |  Matches: " + matchLines.size()
                + "  |  Rejects: " + rejectLines.size() + "\n");

        List<String> allOut = new ArrayList<>(matchLines);
        allOut.add("--- REJECTS ---");
        allOut.addAll(rejectLines);
        return new JobResult("Filtering2", "tFilterRow",
                "currencies.csv", outFile + " + " + rejectFile, inputRows,
                matchLines.size() + rejectLines.size(),
                allOut, "Filter currency=='EUR'; rejects to separate file", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 6: Filtering3 (tReplicate + dual tFilterRow)
    // currencies.csv -> replicate, filter EUR / not-EUR to two files
    // ──────────────────────────────────────────────────────────
    static JobResult runFiltering3() throws IOException {
        System.out.println("▶ Job 6: Filtering3 (tReplicate + dual tFilterRow)");
        List<String> lines = readNonEmpty(DATA_DIR + "currencies.csv");
        int inputRows = lines.size();

        List<String> eurLines    = new ArrayList<>();
        List<String> notEurLines = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split(";", -1);
            String country  = parts[0].trim();
            String currency = parts.length >= 2 ? parts[1].trim() : "";
            if ("EUR".equals(currency)) {
                eurLines.add(country + ";" + currency);
            } else {
                notEurLines.add(country + ";" + currency);
            }
        }

        String eurFile    = OUT_DIR + "eur-currencies.csv";
        String notEurFile = OUT_DIR + "not-eur-currencies.csv";
        Files.writeString(Path.of(eurFile), String.join("\n", eurLines) + "\n");
        Files.writeString(Path.of(notEurFile), String.join("\n", notEurLines) + "\n");

        printSample("  EUR (" + eurFile + "):", eurLines);
        printSample("  Not-EUR (" + notEurFile + "):", notEurLines);
        System.out.println("  Rows in: " + inputRows + "  |  EUR: " + eurLines.size()
                + "  |  Not-EUR: " + notEurLines.size() + "\n");

        List<String> allOut = new ArrayList<>(eurLines);
        allOut.add("--- NOT EUR ---");
        allOut.addAll(notEurLines);
        return new JobResult("Filtering3", "tReplicate + tFilterRow",
                "currencies.csv", eurFile + " + " + notEurFile, inputRows,
                eurLines.size() + notEurLines.size(),
                allOut, "Replicate stream; filter EUR and not-EUR to separate files", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 7: FindAndReplace (tReplace)
    // country-codes.csv -> replace "AR" with "ARGENTINA"
    // ──────────────────────────────────────────────────────────
    static JobResult runFindAndReplace() throws IOException {
        System.out.println("▶ Job 7: FindAndReplace (tReplace)");
        List<String> lines = readNonEmpty(DATA_DIR + "country-codes.csv");
        int inputRows = lines.size();

        List<String> outputLines = new ArrayList<>();
        for (String line : lines) {
            String code = line.trim();
            if ("AR".equalsIgnoreCase(code)) {
                outputLines.add("ARGENTINA");
            } else {
                outputLines.add(code);
            }
        }

        String outFile = OUT_DIR + "find-and-replace-output.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (tLogRow equivalent):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("FindAndReplace", "tReplace",
                "country-codes.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Replace 'AR' -> 'ARGENTINA' (whole word match)", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 8: Normalize (tNormalize)
    // categories-to-normalise.csv -> split categories by ';'
    // ──────────────────────────────────────────────────────────
    static JobResult runNormalize() throws IOException {
        System.out.println("▶ Job 8: Normalize (tNormalize)");
        List<String> lines = readNonEmpty(DATA_DIR + "categories-to-normalise.csv");
        int inputRows = lines.size();

        List<String> outputLines = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split("\\|", 2);
            String productId  = parts[0].trim();
            String categories = parts.length > 1 ? parts[1].trim() : "";
            String[] cats = categories.split(";", -1);
            for (String cat : cats) {
                outputLines.add(productId + ";" + cat.trim());
            }
        }

        String outFile = OUT_DIR + "normalized-categories.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("Normalize", "tNormalize",
                "categories-to-normalise.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Normalize 'categories' column by ';' delimiter", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 9: SampleRow (tSampleRow)
    // country-codes.csv -> rows 5..10
    // ──────────────────────────────────────────────────────────
    static JobResult runSampleRow() throws IOException {
        System.out.println("▶ Job 9: SampleRow (tSampleRow)");
        List<String> lines = readNonEmpty(DATA_DIR + "country-codes.csv");
        int inputRows = lines.size();

        List<String> outputLines = new ArrayList<>();
        for (int i = 0; i < lines.size(); i++) {
            int rowNum = i + 1;
            if (rowNum >= 5 && rowNum <= 10) {
                outputLines.add(lines.get(i).trim());
            }
        }

        String outFile = OUT_DIR + "sample-row-output.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (rows 5-10, tLogRow equivalent):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("SampleRow", "tSampleRow",
                "country-codes.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Sample rows 5..10 from input", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Job 10: Sorting (tSortRow)
    // currencies.csv -> sort by currency ASC, country DESC
    // ──────────────────────────────────────────────────────────
    static JobResult runSorting() throws IOException {
        System.out.println("▶ Job 10: Sorting (tSortRow)");
        List<String> lines = readNonEmpty(DATA_DIR + "currencies.csv");
        int inputRows = lines.size();

        List<String[]> parsed = new ArrayList<>();
        for (String line : lines) {
            String[] parts = line.split(";", -1);
            String country  = parts[0].trim();
            String currency = parts.length >= 2 ? parts[1].trim() : "";
            parsed.add(new String[]{country, currency});
        }

        parsed.sort(Comparator
                .comparing((String[] r) -> r[1])
                .thenComparing((String[] r) -> r[0], Comparator.reverseOrder()));

        List<String> outputLines = parsed.stream()
                .map(r -> r[0] + ";" + r[1])
                .collect(Collectors.toList());

        String outFile = OUT_DIR + "sorted-currencies.csv";
        Files.writeString(Path.of(outFile), String.join("\n", outputLines) + "\n");

        printSample("  Output (" + outFile + "):", outputLines);
        System.out.println("  Rows in: " + inputRows + "  |  Rows out: " + outputLines.size() + "\n");

        return new JobResult("Sorting", "tSortRow",
                "currencies.csv", outFile, inputRows, outputLines.size(),
                outputLines, "Sort by currency ASC, country DESC", true, "");
    }

    // ──────────────────────────────────────────────────────────
    // Helpers
    // ──────────────────────────────────────────────────────────

    static List<String> readNonEmpty(String path) throws IOException {
        return Files.readAllLines(Path.of(path)).stream()
                .filter(l -> !l.trim().isEmpty())
                .collect(Collectors.toList());
    }

    static void printSample(String header, List<String> lines) {
        System.out.println(header);
        int limit = Math.min(lines.size(), 8);
        for (int i = 0; i < limit; i++) {
            System.out.println("    " + lines.get(i));
        }
        if (lines.size() > limit) {
            System.out.println("    ... (" + (lines.size() - limit) + " more rows)");
        }
    }

    // ──────────────────────────────────────────────────────────
    // HTML Report
    // ──────────────────────────────────────────────────────────

    static void generateHtmlReport(Map<String, JobResult> results) throws IOException {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        long totalIn = results.values().stream().mapToLong(r -> r.inputRows).sum();
        long totalOut = results.values().stream().mapToLong(r -> r.outputRows).sum();
        long passed = results.values().stream().filter(r -> r.success).count();

        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n");
        sb.append("<meta charset=\"UTF-8\">\n");
        sb.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n");
        sb.append("<title>Chapter 5 — Data Transformation Report</title>\n");
        sb.append("<style>\n");
        sb.append("""
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
                background: #0a0e17;
                color: #e0e6f0;
                min-height: 100vh;
                padding: 2rem;
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
                padding: 2rem;
                background: linear-gradient(135deg, #0d1525 0%, #1a2740 100%);
                border: 1px solid #1e3a5f;
                border-radius: 12px;
            }
            .header h1 {
                font-size: 2rem;
                background: linear-gradient(90deg, #00e5ff, #00e676);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            .header .subtitle {
                color: #7a8ba8;
                font-size: 0.95rem;
            }
            .summary-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .card {
                background: linear-gradient(135deg, #111b2e 0%, #162035 100%);
                border: 1px solid #1e3a5f;
                border-radius: 10px;
                padding: 1.5rem;
                text-align: center;
            }
            .card .value {
                font-size: 2.2rem;
                font-weight: 700;
                background: linear-gradient(90deg, #00e5ff, #00e676);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .card .label {
                color: #7a8ba8;
                font-size: 0.85rem;
                margin-top: 0.3rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .job-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
                gap: 1.2rem;
            }
            .job-card {
                background: linear-gradient(135deg, #111b2e 0%, #162035 100%);
                border: 1px solid #1e3a5f;
                border-radius: 10px;
                overflow: hidden;
                transition: border-color 0.3s;
            }
            .job-card:hover { border-color: #00e5ff; }
            .job-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 1.2rem;
                background: rgba(0, 229, 255, 0.05);
                border-bottom: 1px solid #1e3a5f;
            }
            .job-header .job-name {
                font-weight: 600;
                font-size: 1.05rem;
                color: #00e5ff;
            }
            .job-header .component {
                font-size: 0.8rem;
                color: #00e676;
                background: rgba(0, 230, 118, 0.12);
                padding: 3px 10px;
                border-radius: 12px;
                border: 1px solid rgba(0, 230, 118, 0.3);
            }
            .job-body { padding: 1rem 1.2rem; }
            .job-body .desc {
                color: #8899b0;
                font-size: 0.9rem;
                margin-bottom: 0.8rem;
            }
            .meta-row {
                display: flex;
                gap: 1.5rem;
                margin-bottom: 0.6rem;
                font-size: 0.85rem;
            }
            .meta-row .meta-label {
                color: #5a6a80;
                min-width: 60px;
            }
            .meta-row .meta-value { color: #c0cce0; }
            .badge {
                display: inline-block;
                font-size: 0.75rem;
                padding: 2px 8px;
                border-radius: 8px;
                font-weight: 600;
            }
            .badge-pass {
                color: #00e676;
                background: rgba(0, 230, 118, 0.12);
                border: 1px solid rgba(0, 230, 118, 0.3);
            }
            .badge-fail {
                color: #ff5252;
                background: rgba(255, 82, 82, 0.12);
                border: 1px solid rgba(255, 82, 82, 0.3);
            }
            .data-preview {
                margin-top: 0.6rem;
                background: #080c14;
                border: 1px solid #1a2540;
                border-radius: 6px;
                padding: 0.6rem 0.8rem;
                max-height: 160px;
                overflow-y: auto;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 0.78rem;
                color: #8899b0;
                line-height: 1.5;
            }
            .data-preview .row-num {
                color: #3a4a60;
                display: inline-block;
                min-width: 24px;
                text-align: right;
                margin-right: 8px;
            }
            .data-preview .separator-row {
                color: #00e5ff;
                opacity: 0.5;
                font-style: italic;
            }
            .footer {
                text-align: center;
                margin-top: 2rem;
                padding: 1rem;
                color: #3a4a60;
                font-size: 0.8rem;
            }
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: #080c14; }
            ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
        """);
        sb.append("</style>\n</head>\n<body>\n");

        // Header
        sb.append("<div class=\"header\">\n");
        sb.append("  <h1>Chapter 5 — Data Transformation</h1>\n");
        sb.append("  <div class=\"subtitle\">Getting Started with Talend Open Studio for Data Integration</div>\n");
        sb.append("</div>\n");

        // Summary cards
        sb.append("<div class=\"summary-cards\">\n");
        sb.append(summaryCard(String.valueOf(results.size()), "Jobs Executed"));
        sb.append(summaryCard(String.valueOf(passed), "Passed"));
        sb.append(summaryCard(String.valueOf(totalIn), "Rows Read"));
        sb.append(summaryCard(String.valueOf(totalOut), "Rows Written"));
        sb.append(summaryCard(timestamp.split(" ")[1], "Run Time"));
        sb.append("</div>\n");

        // Job cards
        sb.append("<div class=\"job-grid\">\n");
        int jobNum = 0;
        for (var entry : results.entrySet()) {
            jobNum++;
            JobResult r = entry.getValue();

            sb.append("<div class=\"job-card\">\n");
            sb.append("  <div class=\"job-header\">\n");
            sb.append("    <span class=\"job-name\">").append(jobNum).append(". ").append(r.jobName).append("</span>\n");
            sb.append("    <span class=\"component\">").append(escapeHtml(r.component)).append("</span>\n");
            sb.append("  </div>\n");
            sb.append("  <div class=\"job-body\">\n");
            sb.append("    <div class=\"desc\">").append(escapeHtml(r.description)).append("</div>\n");

            sb.append("    <div class=\"meta-row\">");
            sb.append("<span class=\"meta-label\">Input</span>");
            sb.append("<span class=\"meta-value\">").append(escapeHtml(r.inputFile)).append("</span>");
            sb.append("</div>\n");

            sb.append("    <div class=\"meta-row\">");
            sb.append("<span class=\"meta-label\">Output</span>");
            sb.append("<span class=\"meta-value\">").append(escapeHtml(r.outputFile)).append("</span>");
            sb.append("</div>\n");

            sb.append("    <div class=\"meta-row\">");
            sb.append("<span class=\"meta-label\">Rows</span>");
            sb.append("<span class=\"meta-value\">").append(r.inputRows).append(" in &rarr; ").append(r.outputRows).append(" out</span>");
            sb.append("</div>\n");

            sb.append("    <div class=\"meta-row\">");
            sb.append("<span class=\"meta-label\">Status</span>");
            sb.append("<span class=\"badge ").append(r.success ? "badge-pass" : "badge-fail").append("\">");
            sb.append(r.success ? "PASS" : "FAIL").append("</span>");
            sb.append("</div>\n");

            // Data preview
            sb.append("    <div class=\"data-preview\">\n");
            int limit = Math.min(r.outputSample.size(), 12);
            for (int i = 0; i < limit; i++) {
                String row = r.outputSample.get(i);
                if (row.startsWith("---")) {
                    sb.append("      <div class=\"separator-row\">").append(escapeHtml(row)).append("</div>\n");
                } else {
                    sb.append("      <div><span class=\"row-num\">").append(i + 1).append("</span>")
                      .append(escapeHtml(row)).append("</div>\n");
                }
            }
            if (r.outputSample.size() > limit) {
                sb.append("      <div class=\"separator-row\">... ")
                  .append(r.outputSample.size() - limit).append(" more rows</div>\n");
            }
            sb.append("    </div>\n");

            sb.append("  </div>\n");
            sb.append("</div>\n");
        }
        sb.append("</div>\n");

        // Footer
        sb.append("<div class=\"footer\">");
        sb.append("Generated ").append(timestamp).append(" | Chapter 5 — Data Transformation | Talend Open Studio");
        sb.append("</div>\n");
        sb.append("</body>\n</html>\n");

        String reportPath = OUT_DIR + "report.html";
        Files.writeString(Path.of(reportPath), sb.toString());
        System.out.println("Report written to " + reportPath);
    }

    static String summaryCard(String value, String label) {
        return "<div class=\"card\"><div class=\"value\">" + value
                + "</div><div class=\"label\">" + label + "</div></div>\n";
    }

    static String escapeHtml(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("\"", "&quot;");
    }

    // ──────────────────────────────────────────────────────────
    // Result holder
    // ──────────────────────────────────────────────────────────

    static class JobResult {
        final String jobName;
        final String component;
        final String inputFile;
        final String outputFile;
        final int inputRows;
        final int outputRows;
        final List<String> outputSample;
        final String description;
        final boolean success;
        final String error;

        JobResult(String jobName, String component, String inputFile, String outputFile,
                  int inputRows, int outputRows, List<String> outputSample,
                  String description, boolean success, String error) {
            this.jobName = jobName;
            this.component = component;
            this.inputFile = inputFile;
            this.outputFile = outputFile;
            this.inputRows = inputRows;
            this.outputRows = outputRows;
            this.outputSample = outputSample;
            this.description = description;
            this.success = success;
            this.error = error;
        }
    }
}
