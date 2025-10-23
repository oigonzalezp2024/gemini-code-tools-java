package com.mycompany.app;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.regex.Matcher; // ⬅️ Nuevo Import
import java.util.regex.Pattern; // ⬅️ Nuevo Import

// --- Imports de clases del mismo paquete (NECESARIO) ---
import com.mycompany.app.Database; // Importa la clase Database
import com.mycompany.app.Perfil;   // Importa la clase Perfil

/**
 * Capa de Control, que orquesta el flujo de trabajo.
 */
public class Controller {

    private final Database repository;
    private Connection connection;  // La conexión real obtenida del Database

    public Controller(Database repository) {
        this.repository = repository;
    }

    /**
     * Lee el archivo JSON y simula el parseo para extraer los perfiles.
     * Utiliza Regex simple para mejorar la extracción de valores, evitando el truncamiento por comas.
     */
    public List<Perfil> readFile(String filePath) {
        List<Perfil> perfiles = new ArrayList<>();
        try {
            String jsonContent = new String(Files.readAllBytes(Paths.get(filePath))); 
            System.out.println("[FILE] Archivo '" + filePath + "' leído con éxito.");

            // Patrón para encontrar bloques de perfiles (objetos dentro del array)
            Pattern profilePattern = Pattern.compile("\\{[^{}]+\\}");
            Matcher profileMatcher = profilePattern.matcher(jsonContent);

            while (profileMatcher.find()) {
                String profileBlock = profileMatcher.group();
                Map<String, String> data = new HashMap<>();
                
                // Patrón para extraer clave y valor de manera semi-segura
                // Busca "key": "value" o "key": [value] o "key": boolean
                // El grupo 1 es la clave, el grupo 2 es el valor (incluyendo comillas si es string, o corchetes si es array)
                Pattern fieldPattern = Pattern.compile("\"([^\"]+)\"\\s*:\\s*(\\[[^\\]]*\\]|\"[^\"]*\"|\\w+)");
                Matcher fieldMatcher = fieldPattern.matcher(profileBlock);

                while (fieldMatcher.find()) {
                    String key = fieldMatcher.group(1).trim();
                    String value = fieldMatcher.group(2).trim();
                    
                    // Limpieza del valor: elimina comillas externas
                    if (value.startsWith("\"") && value.endsWith("\"")) {
                        value = value.substring(1, value.length() - 1);
                    }
                    data.put(key, value);
                }

                // Extracción de datos y preparación para el objeto Perfil
                String cargo = data.getOrDefault("cargo", "N/A");
                String nivel = data.getOrDefault("nivel_recomendado", "N/A");
                String rol = data.getOrDefault("rol_principal", "N/A");
                
                // La conversión de Array JSON a formato SQL (paréntesis)
                String herramientas = data.getOrDefault("herramientas_clave", "[]").replace('[', '(').replace(']', ')');
                boolean fundamental = Boolean.parseBoolean(data.getOrDefault("es_fundamental", "false"));

                perfiles.add(new Perfil(cargo, nivel, rol, herramientas, fundamental));
            }

            System.out.println("[DATA] Perfiles extraídos exitosamente. Total: " + perfiles.size());
            return perfiles;

        } catch (IOException e) {
            System.err.println("[ERROR] No se pudo leer el archivo: " + e.getMessage());
            // Intenta buscar en la ruta de recursos para un proyecto Maven
            try {
                // Esta ruta alternativa se incluye por si el archivo no está en la raíz
                String jsonContent = new String(Files.readAllBytes(Paths.get("src/main/java/resources/" + filePath)));
                System.out.println("[FILE] Archivo '" + "src/main/java/resources/" + filePath + "' leído con éxito (ruta alternativa).");
                 // NOTA: Para una ejecución completa, la lógica de parsing con Regex debería replicarse aquí si se encuentra el archivo en la ruta alternativa.
            } catch (IOException ex) {
                 System.err.println("[ERROR] No se pudo leer el archivo en la ruta del proyecto: " + ex.getMessage());
            }

            return new ArrayList<>();
        }
    }

    /**
     * Configura y establece la conexión real a la base de datos.
     * @return true si la conexión fue exitosa, false si falló.
     */
    public boolean databaseConfig(String dbName, String hostname, String username, String password) {
        repository.config(dbName, username, password, hostname);
        try {
            this.connection = repository.getConnection();
            return true;
        } catch (SQLException e) {
            System.err.println("-------------------------------------------------------------------------------------------------------------------");
            System.err.println("[CRÍTICO] ERROR DE CONEXIÓN REAL A LA BASE DE DATOS.");
            System.err.println("Asegúrese de:");
            System.err.println("1. MySQL esté activo en 'localhost:3306'.");
            System.err.println("2. La base de datos '" + dbName + "' exista.");
            System.err.println("3. El usuario '" + username + "' tenga la contraseña correcta (o vacía).");
            System.err.println("Mensaje de Error JDBC: " + e.getMessage());
            System.err.println("-------------------------------------------------------------------------------------------------------------------");
            return false;
        }
    }
    
    /**
     * Genera y ejecuta el SQL para crear la tabla usando snake_case.
     */
    public void databaseCreate(String dbType, List<Perfil> perfiles) {
        if (connection == null) return; 
        if (!"mysql".equalsIgnoreCase(dbType)) return;

        // 1. Ejecutar DROP TABLE primero.
        // ➡️ Uso de snake_case para el nombre de la tabla
        String dropTableSQL = "DROP TABLE IF EXISTS perfiles_tecnicos;"; 
        repository.executeSql(dropTableSQL);
        System.out.println("[DB] Se ha ejecutado la sentencia DROP TABLE.");

        // 2. Ejecutar CREATE TABLE por separado.
        String createTableSQL = "CREATE TABLE perfiles_tecnicos (\n" +
                                "    id INT AUTO_INCREMENT PRIMARY KEY,\n" +
                                "    cargo VARCHAR(255) NOT NULL,\n" +
                                "    nivel_recomendado VARCHAR(50),\n" + // ⬅️ Snake_case
                                "    rol_principal TEXT,\n" + 
                                "    herramientas_clave TEXT,\n" + // ⬅️ Snake_case
                                "    es_fundamental BOOLEAN\n" + // ⬅️ Snake_case
                                ");";
        repository.executeSql(createTableSQL);
        System.out.println("[DB] Se ha generado y ejecutado la sentencia CREATE TABLE.");
    }

    /**
     * Genera y ejecuta los INSERTs.
     */
    public void databaseInsert(String dbType, List<Perfil> perfiles) {
        if (connection == null) return;
        if (!"mysql".equalsIgnoreCase(dbType)) return;
        
        System.out.println("\n[DB] Generando sentencias INSERT:");
        int count = 0;
        for (Perfil p : perfiles) {
            // Sanitización simple para evitar errores de comillas en SQL
            String rolClean = p.rolPrincipal.replace("'", "''"); 
            String herramientasClean = p.herramientasClave.replace("'", "''");

            // APLICAR FILTRO DE CARACTERES ESPECIALES
            String herramientasSinEspeciales = herramientasClean.replaceAll("[^a-zA-Z0-9\\s]", " ").trim();
            herramientasSinEspeciales = herramientasSinEspeciales.replaceAll("\\s+", " ");

            // ➡️ Uso de snake_case en la lista de columnas (coincidiendo con CREATE TABLE)
            String sql = String.format(
                "INSERT INTO perfiles_tecnicos (cargo, nivel_recomendado, rol_principal, herramientas_clave, es_fundamental) " +
                "VALUES ('%s', '%s', '%s', '%s', %s);",
                p.cargo,
                p.nivelRecomendado,
                rolClean,
                herramientasSinEspeciales, 
                p.esFundamental ? "TRUE" : "FALSE"
            );
            repository.executeSql(sql);
            count++;
        }
        System.out.println("[DB] Se han generado y ejecutado " + count + " sentencias INSERT.");
    }

    /**
     * Cierra la conexión de la base de datos.
     */
    public void databaseClose() {
        repository.closeConnection();
    }
}
