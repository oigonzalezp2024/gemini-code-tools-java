package com.mycompany.app;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.io.IOException; 
import java.nio.file.Files; 
import java.nio.file.Paths; 
import java.nio.file.StandardOpenOption; 

/**
 * Implementación de la Capa de Base de Datos.
 * Maneja la conexión real con JDBC (MySQL).
 */
public class Database {
    private String databaseUrl;
    private String username;
    private String password;
    private String dbName;
    private String host;
    private Connection connection = null;
    private boolean isConfigured = false;
    private static final String SQL_LOG_PATH = "sql_output/executed_commands.sql";

    public void config(String dbName, String user, String pass, String host) {
        this.dbName = dbName;
        this.host = host;
        this.username = user;
        this.password = pass;
        this.databaseUrl = "jdbc:mysql://" + host + ":3306/" + dbName + "?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC";
        this.isConfigured = true;
        System.out.println("\n[DB] Configuración de la base de datos MySQL (JDBC REAL) completada. DB: " + dbName);

        try {
            Files.createDirectories(Paths.get("sql_output"));
            Files.write(Paths.get(SQL_LOG_PATH), ("-- Archivo de log SQL generado el " + new java.util.Date() + " --\n\n").getBytes(), StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            System.out.println("[FILE] Archivo de log SQL inicializado en: " + SQL_LOG_PATH);
        } catch (IOException e) {
            System.err.println("[ERROR] No se pudo inicializar la carpeta/archivo de log SQL: " + e.getMessage());
        }
    }

    /**
     * Intenta conectarse al servidor y crear la base de datos si no existe.
     */
    public boolean createDatabaseIfNotExist() {
        if (!isConfigured) {
            System.err.println("[CRÍTICO] Error: Intento de crear DB sin configuración previa.");
            return false;
        }
        
        String serverUrl = "jdbc:mysql://" + host + ":3306/?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC";
        String createDBSQL = "CREATE DATABASE IF NOT EXISTS " + dbName + ";";

        try (Connection serverConnection = DriverManager.getConnection(serverUrl, username, password)) {
            System.out.println("\n[DB] Conexión exitosa al servidor MySQL para la creación de DB.");

            logSqlToFile(createDBSQL);
            
            try (java.sql.Statement statement = serverConnection.createStatement()) {
                statement.execute(createDBSQL);
                System.out.println("[DB] ¡Ejecución REAL de CREATE DATABASE completada con éxito!");
                return true;
            } catch (SQLException e) {
                 System.err.println("[ERROR] Fallo en la ejecución de CREATE DATABASE. Detalle: " + e.getMessage());
                 return false;
            }
        } catch (SQLException e) {
            System.err.println("-------------------------------------------------------------------------------------------------------------------");
            System.err.println("[CRÍTICO] ERROR DE CONEXIÓN AL SERVIDOR MySQL para la creación de la DB.");
            System.err.println("Asegúrese de que el servidor esté activo y el usuario tenga permisos.");
            System.err.println("Mensaje de Error JDBC: " + e.getMessage());
            System.err.println("-------------------------------------------------------------------------------------------------------------------");
            return false;
        }
    }

    /**
     * Intenta establecer la conexión JDBC real a la base de datos configurada.
     */
    public Connection getConnection() throws SQLException {
        if (!isConfigured) {
            throw new IllegalStateException("La base de datos no ha sido configurada.");
        }
        
        if (connection == null || connection.isClosed()) {
            System.out.println("[DB] Intentando establecer conexión JDBC a la DB: " + dbName + "...");
            connection = DriverManager.getConnection(databaseUrl, username, password);
            System.out.println("[DB] ¡Conexión exitosa! Objeto Connection obtenido.");
        }
        return connection;
    }

    /**
     * Método auxiliar para guardar el SQL
     */
    private void logSqlToFile(String sql) {
        try {
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
