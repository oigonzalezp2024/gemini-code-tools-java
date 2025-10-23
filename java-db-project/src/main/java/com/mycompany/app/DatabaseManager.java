// ===== Archivo: src\main\java\com\mycompany\app\DatabaseManager.java (CORRECCIÓN) =====
package com.mycompany.app;

import java.util.List;

// --- Imports de clases del mismo paquete (NECESARIO) ---
import com.mycompany.app.Database;
import com.mycompany.app.Controller;
import com.mycompany.app.Perfil;

/**
 * Clase principal que ejecuta el flujo completo.
 */
public class DatabaseManager {
    
    public static void main(String[] args) {
        // En un proyecto Maven/IDE, el archivo data.json debe estar en la raíz
        final String filePath = "data.json"; 

        // Parámetros de conexión REALES
        final String HOSTNAME = "localhost";
        final String USER = "root";
        final String PASSWORD = ""; 
        // Nombre de la base de datos en snake_case
        final String DBNAME = "java_project_db"; 

        System.out.println("--- INICIO DEL FLUJO DE GESTIÓN DE BASE DE DATOS (CONEXIÓN REAL JDBC) ---");
        
        // Simulación de inyección de dependencias
        Database database = new Database();
        Controller controller = new Controller(database);
        
        // 1. Lectura del archivo JSON
        List<Perfil> perfilesArray = controller.readFile(filePath);

        // 2. Configuración e intento de conexión real
        boolean connected = controller.databaseConfig(DBNAME, HOSTNAME, USER, PASSWORD);
        
        if (connected && !perfilesArray.isEmpty()) {
            // 3. Creación de la tabla (ejecución REAL de SQL)
            controller.databaseCreate("mysql", perfilesArray);
            
            // 4. Inserción de datos (ejecución REAL de SQL)
            controller.databaseInsert("mysql", perfilesArray);
        } else if (connected) {
            System.out.println("[INFO] No se encontraron perfiles para insertar.");
        }

        // 5. Cierre de la conexión
        controller.databaseClose();

        System.out.println("--- FIN DEL FLUJO ---");
    }
}
