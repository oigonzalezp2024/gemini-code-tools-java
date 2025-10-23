package com.mycompany.app;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.io.IOException; // ⬅️ Nuevo Import
import java.nio.file.Files; // ⬅️ Nuevo Import
import java.nio.file.Paths; // ⬅️ Nuevo Import
import java.nio.file.StandardOpenOption; // ⬅️ Nuevo Import

/**
 * Implementación de la Capa de Base de Datos.
 * Maneja la conexión real con JDBC (MySQL).
 */
public class Database { // <-- ¡Debe ser PUBLIC!
    private String databaseUrl;
    private String username;
    private String password;
    private Connection connection = null; 
    private boolean isConfigured = false;
    // ⬅️ Nueva Constante para la ruta del archivo de log SQL
    private static final String SQL_LOG_PATH = "sql_output/executed_commands.sql";

    // Configura la conexión con los parámetros solicitados
    public void config(String dbName, String user, String pass, String host) {
        // Usando el conector 'com.mysql:mysql-connector-j' (la versión moderna)
        this.databaseUrl = "jdbc:mysql://" + host + ":3306/" + dbName + "?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC";
        this.username = user;
        this.password = pass;
        this.isConfigured = true;
        System.out.println("\n[DB] Configuración de la base de datos MySQL (JDBC REAL) completada.");
        
        // ⬅️ Inicializa el archivo de log SQL, sobrescribiendo si ya existe
        try {
            Files.createDirectories(Paths.get("sql_output"));
            Files.write(Paths.get(SQL_LOG_PATH), ("-- Archivo de log SQL generado el " + new java.util.Date() + " --\n\n").getBytes(), StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            System.out.println("[FILE] Archivo de log SQL inicializado en: " + SQL_LOG_PATH);
        } catch (IOException e) {
            System.err.println("[ERROR] No se pudo inicializar la carpeta/archivo de log SQL: " + e.getMessage());
        }
    }
    
    /**
     * Intenta establecer la conexión JDBC real.
     */
    public Connection getConnection() throws SQLException {
        if (!isConfigured) {
            throw new IllegalStateException("La base de datos no ha sido configurada.");
        }
        
        if (connection == null || connection.isClosed()) {
             System.out.println("[DB] Intentando establecer conexión JDBC...");
             connection = DriverManager.getConnection(databaseUrl, username, password);
             System.out.println("[DB] ¡Conexión exitosa! Objeto Connection obtenido.");
        }
        return connection;
    }

    // ⬅️ Nuevo método auxiliar para guardar el SQL
    private void logSqlToFile(String sql) {
        try {
            // Se añade la sentencia SQL seguida de un salto de línea
            Files.write(Paths.get(SQL_LOG_PATH), (sql + "\n\n").getBytes(), StandardOpenOption.APPEND);
            System.out.println("[FILE] Comando SQL guardado en: " + SQL_LOG_PATH);
        } catch (IOException e) {
            System.err.println("[ERROR] Fallo al escribir la sentencia SQL en el archivo: " + e.getMessage());
        }
    }

    /**
     * Ejecuta comandos SQL realmente.
     * @param sql La sentencia SQL a ejecutar.
     */
    public void executeSql(String sql) {
        System.out.println("\n[SQL] Generando comando SQL:");
        System.out.println("----------------------------------------------------------------------------------");
        System.out.println(sql);
        System.out.println("----------------------------------------------------------------------------------");
        
        // 1. Guardar el SQL en el archivo ANTES de la ejecución real
        logSqlToFile(sql);

        if (connection != null) {
            try (java.sql.Statement statement = connection.createStatement()) {
                statement.execute(sql);
                System.out.println("[DB] ¡Ejecución REAL de SQL completada con éxito!");

            } catch (SQLException e) {
                System.err.println("[ERROR] Fallo en la ejecución REAL de la sentencia SQL. Detalle: " + e.getMessage());
            }
        } else {
             System.out.println("[DB] ADVERTENCIA: Conexión no disponible, solo se imprime y guarda el SQL (no se ejecuta realmente).");
        }
    }

    /**
     * Cierra la conexión JDBC real.
     */
    public void closeConnection() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
                System.out.println("[DB] Conexión JDBC real cerrada.");
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Error al cerrar la conexión: " + e.getMessage());
        }
    }
}
