package com.myproject.core;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Clase base abstracta para todos los roles especialistas (DBA, QA, Backend, etc.).
 * Contiene la lógica común de lectura de contexto y escritura del archivo de guía.
 */
public abstract class Especialista {

    /**
     * Lógica principal de análisis y generación de la guía o corrección.
     * @param contextFilePath Ruta al archivo de contexto (contexto.txt).
     * @param targetFilePath Ruta al archivo donde se escribirá la guía o el código corregido.
     * @param role Nombre del rol para el mensaje de salida y la guía.
     */
    protected void runAnalysis(String contextFilePath, String targetFilePath, String role) throws Exception {
        System.out.println("Iniciando análisis real de IA para el rol: " + role);
        System.out.println("Ruta del contexto: " + contextFilePath);
        System.out.println("Ruta de destino (Input): " + targetFilePath);

        // --- 1. Leer el contexto del proyecto ---
        String context;
        try {
            context = new String(Files.readAllBytes(Paths.get(contextFilePath)));
        } catch (IOException e) {
            throw new Exception("Error al leer el archivo de contexto en: " + contextFilePath, e);
        }

        // --- 2. Lógica de la IA (IMPLEMENTACIÓN REAL DE LA LLAMADA A GEMINI) ---
        AIAnalyzer analyzer = new AIAnalyzer();
        String resultContent;
        Path targetPath = Paths.get(targetFilePath);
        String fileName = targetPath.getFileName().toString();
        
        // Verificar si se está corrigiendo un archivo de código (.java) o generando una guía.
        if (fileName.toLowerCase().endsWith(".java")) {
            // Caso 1: Corrección de un archivo de código
            Path originalFilePath = targetPath;
            String fileToFix = new String(Files.readAllBytes(originalFilePath));
            
            System.out.println("⚙️  Analizando y corrigiendo el código como " + role + "...");
            // Usar AIAnalyzer para obtener el código corregido.
            // La respuesta de la API será el código completo corregido.
            resultContent = analyzer.analyze(context, fileToFix);
            
            // 3. Determinar la ruta final para el código corregido
            // Aplica la convención de sufijo (-corregido.java)
            int lastDot = fileName.lastIndexOf('.');
            String baseName = fileName.substring(0, lastDot);
            String ext = fileName.substring(lastDot);
            targetPath = targetPath.getParent().resolve(baseName + "-corregido" + ext);

        } else {
            // Caso 2: Generación de Guía/Reporte (.md, .txt, etc.)
            
            // Crear un prompt detallado para que Gemini actúe como el rol y genere el informe.
            String taskPrompt = String.format(
                "Como un %s, analiza el contexto del proyecto proporcionado. Tu objetivo es generar una guía de aprendizaje o un informe detallado en **formato Markdown** para este proyecto de Spring Boot. El informe debe enfocarse en las mejores prácticas, las responsabilidades clave y las recomendaciones específicas de tu rol. Tu respuesta debe ser **SOLAMENTE** el contenido del informe/guía, sin explicaciones adicionales fuera del reporte. Usa el contexto para hacer recomendaciones específicas al proyecto.",
                role
            );
            
            System.out.println("⚙️  Generando guía de aprendizaje de IA para el rol: " + role + "...");
            // Se usa el contexto del proyecto y el prompt de la tarea como el "archivo a corregir" 
            // para enviar la instrucción completa a Gemini.
            resultContent = analyzer.analyze(context, taskPrompt); 
            
            // targetPath ya es el original (e.g., guide_dba.md)
        }
        
        // --- 4. Escribir el archivo ---
        try {
            // Escribir el contenido real (código corregido o guía de IA generada)
            Files.write(targetPath, resultContent.getBytes("UTF-8"));
            System.out.println("✅ El contenido real (código corregido o guía de IA) fue escrito exitosamente en: " + targetPath.toString());
        } catch (IOException e) {
            throw new Exception("Error al escribir el archivo de destino en: " + targetPath.toString(), e);
        }
    }
}
