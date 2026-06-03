import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONReader;
import freemarker.core.TemplateClassResolver;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateExceptionHandler;

import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.Collectors;

public class FtlRunner {

    private static final Pattern VAR_RE = Pattern.compile("\\$\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}");
    private static final Pattern SUB_RE = Pattern.compile("\\[1-n\\]");
    private static final String SEGMENT_PREFIX = "#segment#";

    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("Usage: FtlRunner <templateRoot> <stylePath> <ctxJson> <outputDir>");
            System.exit(2);
        }
        Path templateRoot = Paths.get(args[0]).toAbsolutePath();
        String stylePath = args[1].replace("\\", "/");
        Path ctxJson = Paths.get(args[2]).toAbsolutePath();
        Path outputDir = Paths.get(args[3]).toAbsolutePath();

        String ctxText = new String(Files.readAllBytes(ctxJson), StandardCharsets.UTF_8);
        Map<String, Object> rootCtx = JSON.parseObject(ctxText, Map.class, JSONReader.Feature.UseBigDecimalForDoubles);
        rootCtx.put("Format", new FormatTool());

        Configuration cfg = new Configuration(Configuration.VERSION_2_3_28);
        cfg.setNumberFormat("0.#####################");
        cfg.setDirectoryForTemplateLoading(templateRoot.toFile());
        cfg.setDefaultEncoding("UTF-8");
        cfg.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
        cfg.setNewBuiltinClassResolver(TemplateClassResolver.SAFER_RESOLVER);

        Path styleRoot = templateRoot.resolve(stylePath);
        if (!Files.isDirectory(styleRoot)) {
            throw new RuntimeException("stylePath not found: " + styleRoot);
        }

        Files.createDirectories(outputDir);
        List<String> generated = new ArrayList<>();

        try (java.util.stream.Stream<Path> walk = Files.walk(styleRoot)) {
            List<Path> files = walk.filter(Files::isRegularFile).collect(Collectors.toList());
            for (Path tpl : files) {
                String relFromRoot = templateRoot.relativize(tpl).toString().replace("\\", "/");
                String relFromStyle = styleRoot.relativize(tpl).toString().replace("\\", "/");
                String outRel = expandPath(relFromStyle, rootCtx);
                Path outFile = outputDir.resolve(outRel);
                renderOne(cfg, relFromRoot, rootCtx, outFile, generated);
            }
        }

        for (String g : generated) System.out.println("WROTE " + g);
        System.out.println("DONE " + generated.size() + " files -> " + outputDir);
    }

    private static void renderOne(Configuration cfg, String tplRel, Map<String, Object> ctx, Path outFile, List<String> generated) throws Exception {
        Template t = cfg.getTemplate(tplRel, "UTF-8");
        StringWriter sw = new StringWriter();
        t.process(ctx, sw);
        String content = sw.toString();

        boolean isSegmented = SUB_RE.matcher(outFile.toString()).find();
        if (isSegmented) {
            splitAndWriteSegments(content, outFile, generated);
        } else {
            Path finalOut = adjustOutputPath(outFile);
            Files.createDirectories(finalOut.getParent());
            Files.write(finalOut, content.getBytes(StandardCharsets.UTF_8));
            generated.add(finalOut.toString());
        }
    }

    private static void splitAndWriteSegments(String content, Path outFile, List<String> generated) throws IOException {
        Path parent = adjustOutputPath(outFile).getParent();
        Files.createDirectories(parent);
        String[] lines = content.split("\\r?\\n", -1);
        Writer cur = null;
        try {
            for (String line : lines) {
                if (line.trim().length() > 0 && line.startsWith(SEGMENT_PREFIX)) {
                    if (cur != null) cur.close();
                    String segName = line.substring(SEGMENT_PREFIX.length()).trim();
                    Path curPath = parent.resolve(segName);
                    Files.createDirectories(curPath.getParent());
                    cur = Files.newBufferedWriter(curPath, StandardCharsets.UTF_8);
                    generated.add(curPath.toString());
                } else if (cur != null) {
                    cur.write(line);
                    cur.write("\r\n");
                }
            }
        } finally {
            if (cur != null) cur.close();
        }
    }

    private static Path adjustOutputPath(Path p) {
        String name = p.getFileName().toString();
        String fixed = name;
        if (name.endsWith(".javai")) fixed = name.substring(0, name.length() - 6) + ".java";
        else if (name.endsWith(".vuei")) fixed = name.substring(0, name.length() - 5) + ".vue";
        else if (name.endsWith(".tsi"))  fixed = name.substring(0, name.length() - 4) + ".ts";
        return p.resolveSibling(fixed);
    }

    private static String expandPath(String path, Map<String, Object> ctx) {
        Matcher m = VAR_RE.matcher(path);
        StringBuffer sb = new StringBuffer();
        while (m.find()) {
            String key = m.group(1);
            Object v = ctx.get(key);
            String s = (v == null) ? "" : v.toString();
            if ("bussiPackage".equals(key) || "entityPackage".equals(key) || "parentPackage".equals(key)) {
                s = s.replace('.', '/');
            }
            m.appendReplacement(sb, Matcher.quoteReplacement(s));
        }
        m.appendTail(sb);
        return sb.toString();
    }

    public static class FormatTool {
        public String humpToUnderline(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder(para);
            int offset = 0;
            if (!para.contains("_")) {
                for (int i = 0; i < para.length(); i++) {
                    if (Character.isUpperCase(para.charAt(i))) { sb.insert(i + offset, "_"); offset++; }
                }
            }
            String r = sb.toString().toLowerCase();
            return r.startsWith("_") ? r.substring(1) : r;
        }
        public String humpToShortbar(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder(para);
            int offset = 0;
            if (!para.contains("-")) {
                for (int i = 0; i < para.length(); i++) {
                    if (Character.isUpperCase(para.charAt(i))) { sb.insert(i + offset, "-"); offset++; }
                }
            }
            String r = sb.toString().toLowerCase();
            return r.startsWith("-") ? r.substring(1) : r;
        }
        public String underlineToHump(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder();
            for (String part : para.split("_")) {
                if (!para.contains("_")) sb.append(part);
                else if (sb.length() == 0) sb.append(part.toLowerCase());
                else if (part.length() > 0) { sb.append(part.substring(0,1).toUpperCase()); sb.append(part.substring(1).toLowerCase()); }
            }
            return sb.toString();
        }
    }
}
