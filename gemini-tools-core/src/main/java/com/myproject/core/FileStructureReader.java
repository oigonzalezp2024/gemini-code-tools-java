package com.myproject.core;

import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Clase que recorre recursivamente un directorio y genera un archivo
 * con toda la estructura y contenido de sus archivos.
 */
public class FileStructureReader {

    public void compactProject(String sourceDir, String outputFile) throws IOException {
        List<Path> fileList = new ArrayList<>();
        Path rootPath = Paths.get(sourceDir).toAbsolutePath();

        Files.walk(rootPath)
            .filter(Files::isRegularFile)
            .forEach(fileList::add);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {
            writer.write("### Proyecto compactado: " + rootPath);
            writer.newLine();
            writer.newLine();

            for (Path file : fileList) {
                writer.write("=== Archivo: " + rootPath.relativize(file) + " ===");
                writer.newLine();
                writer.newLine();

                try {
                    List<String> lines = Files.readAllLines(file);
                    for (String line : lines) {
                        writer.write(line);
                        writer.newLine();
                    }
                } catch (IOException e) {
                    writer.write("[ERROR] No se pudo leer el archivo: " + file.toString());
                }

                writer.newLine();
                writer.write("=== FIN DE ARCHIVO ===");
                writer.newLine();
                writer.newLine();
            }
        }

        System.out.println("✅ Proyecto compactado en: " + outputFile);
    }

    // Método main para ejecución directa
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java -cp <jar> com.myproject.core.FileStructureReader <ruta_proyecto> <archivo_salida>");
            return;
        }

        String sourceDir = args[0];
        String outputFile = args[1];

        try {
            new FileStructureReader().compactProject(sourceDir, outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
