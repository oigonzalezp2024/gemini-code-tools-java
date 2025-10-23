package com.myproject.core;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * AIAnalyzer: Corrige y analiza archivos usando la API Gemini (v1beta).
 * * Este analizador se conecta al modelo Gemini para recibir código corregido.
 * La clave se espera en la variable de entorno "GEMINI_API_KEY".
 */
public class AIAnalyzer {

    private static final String API_URL =
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent";
    private static final int TIMEOUT_MS = 60000;

    /**
     * Escapa una cadena para su inclusión segura como valor en un payload JSON.
     * SE CORRIGEN ERRORES DE SINTAXIS EN LAS SECUENCIAS DE ESCAPE (\n, \r, \t).
     * @param value La cadena a escapar.
     * @return La cadena escapada.
     */
    private String escapeJsonString(String value) {
        if (value == null) return "";
        // Debe ir primero para no escapar los backslashes que ya son de escape
        return value.replace("\\", "\\\\") 
                        .replace("\"", "\\\"")
                        // Correcciones de sintaxis para los caracteres de control
                        .replace("\n", "\\n")
                        .replace("\r", "\\r")
                        .replace("\t", "\\t");
    }

    /**
     * Extrae el texto generado desde la respuesta JSON de la API de Gemini
     * y realiza la decodificación de las secuencias de escape JSON.
     * SE CORRIGEN ERRORES DE SINTAXIS Y SE USA EL DESESCAPE COMPLETO (Unicode y directo).
     * @param jsonResponse La respuesta JSON completa.
     * @return El texto extraído y decodificado.
     */
    private String extractTextFromGeminiResponse(String jsonResponse) {
        String searchKey = "\"text\": \"";
        int startIndex = jsonResponse.indexOf(searchKey);
        if (startIndex == -1) {
            System.err.println("Advertencia: No se encontró el campo 'text' en la respuesta.");
            return "ERROR DE RESPUESTA: " + jsonResponse;
        }

        startIndex += searchKey.length();
        int endIndex = startIndex;
        // Búsqueda simple de la comilla de cierre que no esté escapada
        while (endIndex < jsonResponse.length()) {
            char current = jsonResponse.charAt(endIndex);
            // Comprobamos que el carácter actual sea una comilla y que el anterior no sea una barra invertida (escape)
            if (current == '"' && jsonResponse.charAt(endIndex - 1) != '\\') break;
            endIndex++;
        }

        if (endIndex >= jsonResponse.length()) {
            return "ERROR DE PARSEO: Se encontró 'text', pero no la comilla de cierre.";
        }

        String extractedText = jsonResponse.substring(startIndex, endIndex);
        
        // Decodificación de secuencias de escape JSON
        return extractedText.replace("\\n", "\n") 
                            .replace("\\\"", "\"") 
                            .replace("\\r", "\r") 
                            .replace("\\t", "\t") 
                            // Decodificar los caracteres Unicode para < y > (genéricos)
                            .replace("\\u003c", "<") 
                            .replace("\\u003e", ">") 
                            // El escape de backslash debe ser el último
                            .replace("\\\\", "\\"); 
    }

    /**
     * Analiza y corrige un archivo de código usando el modelo Gemini.
     * @param context El contexto del proyecto (ej. contenido de otro archivo).
     * @param fileToFix El contenido del archivo a corregir.
     * @return El código completo corregido devuelto por el modelo.
     * @throws IOException Si ocurre un error de red o I/O.
     */
    public String analyze(String context, String fileToFix) throws IOException {
        String apiKey = System.getenv("GEMINI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalStateException("❌ La variable de entorno GEMINI_API_KEY no está configurada.");
        }

        // Construcción del prompt (usando \n para mejor legibilidad)
        String userQuery = String.format(
            "Contexto del proyecto:\n%s\n\nArchivo a corregir:\n%s",
            context, fileToFix
        );

        // La instrucción del sistema pide solo el código para asegurar que sea ejecutable
        String systemInstruction =
            "Actúa como un ingeniero de software experimentado. Analiza el contexto completo del proyecto y el archivo proporcionado para encontrar y aplicar las correcciones necesarias. Tu respuesta DEBE ser SOLAMENTE el código completo corregido, sin explicaciones ni bloques de marcado.";

        // ✅ ESTRUCTURA JSON CORREGIDA: Se usa 'systemInstruction' y 'role':'user' (crucial para la API)
        String jsonInputString = String.format(
            "{"
          + "\"systemInstruction\":{\"parts\":[{\"text\":\"%s\"}]}," 
          + "\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"%s\"}]}]" 
          + "}",
            escapeJsonString(systemInstruction),
            escapeJsonString(userQuery)
        );

        // Conexión
        URL url = new URL(API_URL + "?key=" + apiKey);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        connection.setDoOutput(true);
        connection.setConnectTimeout(TIMEOUT_MS);
        connection.setReadTimeout(TIMEOUT_MS);

        try (OutputStream os = connection.getOutputStream()) {
            byte[] input = jsonInputString.getBytes(StandardCharsets.UTF_8);
            os.write(input);
        }

        int responseCode = connection.getResponseCode();
        if (responseCode != HttpURLConnection.HTTP_OK) {
            InputStream errorStream = connection.getErrorStream();
            String errorResponse = null;
            if (errorStream != null) {
                try (BufferedReader errorBr = new BufferedReader(
                        new InputStreamReader(errorStream, StandardCharsets.UTF_8))) {
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = errorBr.readLine()) != null) sb.append(line);
                    errorResponse = sb.toString();
                }
            }
            throw new IOException(String.format(
                "❌ Error %d (%s) al llamar a la API de Gemini. Detalles: %s",
                responseCode, connection.getResponseMessage(),
                errorResponse != null ? errorResponse : "No hay detalles."
            ));
        }

        StringBuilder responseBuilder = new StringBuilder();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) responseBuilder.append(line);
        }

        return extractTextFromGeminiResponse(responseBuilder.toString());
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.out.println("Uso: java -cp <classpath> com.myproject.core.AIAnalyzer <contexto.txt> <archivo.java>");
            System.out.println("Asegúrate de configurar la variable de entorno GEMINI_API_KEY.");
            return;
        }

        // Se utilizan clases de java.nio.file para facilitar la lectura de archivos
        String context = new String(java.nio.file.Files.readAllBytes(
            java.nio.file.Paths.get(args[0])), StandardCharsets.UTF_8);
        String fileToFix = new String(java.nio.file.Files.readAllBytes(
            java.nio.file.Paths.get(args[1])), StandardCharsets.UTF_8);

        AIAnalyzer analyzer = new AIAnalyzer();
        try {
            System.out.println("⚙️  Analizando y corrigiendo el archivo. Esto puede tardar unos segundos...");
            String result = analyzer.analyze(context, fileToFix);
            java.nio.file.Path outputPath =
                java.nio.file.Paths.get(args[1].replace(".java", "-corregido.java"));
            java.nio.file.Files.writeString(outputPath, result, StandardCharsets.UTF_8);
            System.out.println("✅ Archivo corregido generado en: " + outputPath);
        } catch (IllegalStateException e) {
            System.err.println(e.getMessage());
            System.err.println("Por favor, configura la variable de entorno GEMINI_API_KEY.");
        } catch (Exception e) {
            System.err.println("❌ Error durante el proceso de análisis y corrección.");
            e.printStackTrace();
        }
    }
}
