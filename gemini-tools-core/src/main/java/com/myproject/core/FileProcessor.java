package com.myproject.core;

import java.io.*;
import java.nio.file.*;
import java.util.stream.Collectors;

/**
 * FileProcessor: compacta la estructura de un proyecto en un solo archivo de texto.
 */
public class FileProcessor {

    public void compactProject(String projectPath, String outputFilePath) throws IOException {
        Path root = Paths.get(projectPath);
        String result = Files.walk(root)
                .filter(Files::isRegularFile)
                .filter(path -> !path.toString().contains("target"))
                .filter(path -> !path.toString().contains(".git"))
                .filter(path -> !path.toString().contains("node_modules"))
                .filter(
                    path -> path.toString().endsWith(".java") || 
                        path.toString().endsWith(".xml") || 
                        path.toString().endsWith(".md") || 
                        path.toString().endsWith(".json") ||
                        path.toString().endsWith(".php") ||
                        path.toString().endsWith(".py") ||
                        path.toString().endsWith(".txt") ||
                        path.toString().endsWith(".csv")
                ).map(
                    path -> {
                        try {
                            Path relativePath = root.relativize(path);
                            return "\n// ===== Archivo: " + relativePath.toString() + " =====\n"
                                    + Files.readString(path);
                        } catch (IOException e) {
                            System.err.println("Error al leer el archivo " + path.toString() + ": " + e.getMessage());
                            return "";
                        }
                })
                .collect(Collectors.joining("\n"));

        Files.writeString(Paths.get(outputFilePath), result);
        System.out.println("✅ Proyecto compactado en: " + outputFilePath);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.out.println("Uso: java -cp target/ourcrud-java-1.0-SNAPSHOT-jar-with-dependencies.jar com.myproject.core.FileProcessor <ruta_proyecto> <salida.txt>");
            return;
        }

        FileProcessor processor = new FileProcessor();
        processor.compactProject(args[0], args[1]);
    }
}
