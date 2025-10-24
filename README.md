# 🛠️ Gemini Code Tools Java

Este es un proyecto multi-módulo de Maven diseñado para demostrar la integración de diversas utilidades en un entorno Java: herramientas de análisis de código basadas en la API de Google Gemini y un módulo de gestión de base de datos (CRUD) con conexión **JDBC real a MySQL**.

La ejecución centralizada se logra mediante el módulo `launcher-app`, que genera un único **Fat JAR** con todas las dependencias.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente:

1.  **JDK (Java Development Kit)**: Versión 17 o superior.
2.  **Apache Maven**: Versión 3.6 o superior.
3.  **Servidor MySQL**: Instancia local activa (en `localhost:3306`).
4.  **Base de Datos MySQL**: No es necesario crearla manualmente; el programa intentará crear `java_project_db` si no existe.
5.  **Archivo de Datos**: El archivo `data.json` debe estar ubicado en la raíz del proyecto.
6.  **Clave API de Gemini** (Solo para el módulo de análisis de código): Configurada como variable de entorno.

### Configuración de la API de Gemini

Para usar las funcionalidades de análisis de código, la clave API debe estar disponible en el sistema:

```bash
# Ejemplo en Windows (PowerShell)
$env:GEMINI_API_KEY="TU_CLAVE_AQUI"

# Ejemplo en Linux/macOS
export GEMINI_API_KEY="TU_CLAVE_AQUI"
````

-----

## ⚙️ Configuración y Compilación

Ejecuta el siguiente comando en la raíz del proyecto para limpiar, compilar e instalar todos los módulos en el repositorio local de Maven. Esto generará el Fat JAR final en el directorio `launcher-app/target/`.

```bash
mvn clean install
```

-----

## 💻 Modos de Ejecución del Software

El proyecto ofrece varios modos principales de ejecución, dirigidos por el Fat JAR unificado (`ourcrud-java-all-1.0-SNAPSHOT.jar`) o invocando clases específicas.

### 1\. 💾 Gestión de Base de Datos (Modo Centralizado)

Este modo ejecuta la clase principal `DatabaseManager`, que se encarga de leer `data.json`, conectar con MySQL, crear la base de datos y la tabla `perfiles_tecnicos` si no existen, y luego insertar los datos, resolviendo automáticamente las dependencias del driver JDBC.

**Clase Principal:** `com.mycompany.app.DatabaseManager`

```bash
# Ejecutar desde la raíz del proyecto (la ruta del JAR es relativa)
java -jar ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar
```

**Resultado:**
El programa intentará conectar a `jdbc:mysql://localhost:3306/java_project_db` con el usuario `root` y contraseña vacía. Si es exitoso, generará y ejecutará las sentencias `DROP TABLE`, `CREATE TABLE` e `INSERT` para los perfiles de `data.json`, registrando todas las operaciones en el archivo `sql_output/executed_commands.sql`.

#### Sentencias SQL Generadas

El archivo `sql_output/executed_commands.sql` contendrá las siguientes sentencias (el contenido exacto del `INSERT` depende de la data en `data.json`):

```sql
-- Archivo de log SQL generado el [Fecha y Hora] --

CREATE DATABASE IF NOT EXISTS java_project_db;

DROP TABLE IF EXISTS perfiles_tecnicos;

CREATE TABLE perfiles_tecnicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cargo VARCHAR(255) NOT NULL,
    nivel_recomendado VARCHAR(50),
    rol_principal TEXT,
    herramientas_clave TEXT,
    es_fundamental BOOLEAN
);

INSERT INTO perfiles_tecnicos (cargo, nivel_recomendado, rol_principal, herramientas_clave, es_fundamental) VALUES ('Desarrollador Java Backend', 'Senior/Mid/Junior', 'Escribir la lógica de negocio, desarrollar y mantener APIs REST/microservicios, manejar la seguridad y la integración con la base de datos.', 'Java versiones recientes Spring Boot Spring Framework Spring Data JPA Hibernate Spring Security JUnit Mockito', TRUE);

INSERT INTO perfiles_tecnicos (cargo, nivel_recomendado, rol_principal, herramientas_clave, es_fundamental) VALUES ('Ingeniero/Administrador de Bases de Datos (DBA)', 'Mid/Senior', 'Diseño, implementación y optimización del esquema de la base de datos (SQL/NoSQL). Asegurar el rendimiento y la integridad de los datos.', 'SQL PostgreSQL MySQL Oracle NoSQL MongoDB Cassandra Optimizaci n de Queries', TRUE);

-- ... Más sentencias INSERT, una por cada perfil.
```

-----

### 2\. 📝 Compactación de Código (Generación de Contexto para IA)

Utiliza la herramienta `FileProcessor` para rastrear un directorio de proyecto (o un módulo específico) y compactar el contenido de los archivos relevantes (Java, XML, JSON, etc.) en un solo archivo de texto. Este archivo sirve como **contexto de proyecto** para el analista de IA.

**Clase Principal:** `com.myproject.core.FileProcessor`

```bash
# Uso: java -cp <Fat-JAR> <Clase> <ruta_proyecto> <salida.txt>
java -cp ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar \
     com.myproject.core.FileProcessor \
     ./gemini-tools-core \
     contexto.txt
```

**Parámetros:**

  * `ruta_proyecto`: Directorio raíz a escanear (e.g., `./gemini-tools-core` para generar contexto solo de ese módulo).
  * `salida.txt`: Nombre del archivo de texto generado (e.g., `contexto.txt`).

-----

### 3\. 🤖 Análisis y Corrección de Código con IA

Utiliza la herramienta `AIAnalyzer` para enviar un archivo a la API de Gemini, utilizando un archivo de contexto previo (generado en el Modo 2) para obtener correcciones específicas de código.

**Clase Principal:** `com.myproject.core.AIAnalyzer`

```bash
# Uso: java -cp <Fat-JAR> <Clase> <contexto.txt> <archivo.java>
java -cp ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar \
     com.myproject.core.AIAnalyzer \
     contexto.txt \
     ./gemini-tools-core/src/main/java/com/myproject/core/AIAnalyzer.java
```

**Parámetros:**

  * `contexto.txt`: El archivo de contexto generado por `FileProcessor`.
  * `archivo.java`: La ruta del archivo específico que deseas que Gemini corrija (se recomienda un archivo del mismo módulo del que se generó el contexto).

**Resultado:**
Generará un nuevo archivo con el sufijo `-corregido.java` (ej. `AIAnalyzer-corregido.java`) conteniendo el código corregido por la IA.

-----

### 4\. 🖥️ Ejecución mediante Interfaz Gráfica (GUI)

El proyecto incluye un script de Python (`main.py`) que proporciona una interfaz gráfica para orquestar los pasos de compilación, procesamiento de archivos, análisis de IA y la ejecución del módulo principal de la base de datos.

Para ejecutar la GUI, asegúrate de tener Python 3 y Tkinter instalados. Navega a la raíz del proyecto y ejecuta:

```bash
python main.py
```

Desde la GUI podrás:

  * Compilar el proyecto Maven.
  * Procesar archivos para generar el contexto (Modo 2).
  * Analizar y comparar código con la IA (Modo 3).
  * Iniciar y detener el flujo de gestión de base de datos (Modo 1), que ejecutará el proceso de gestión de base de datos en segundo plano, mostrando su salida en tiempo real.

**Resultado:**
El programa intentará conectar a `jdbc:mysql://localhost:3306/java_project_db` con el usuario `root` y contraseña vacía. Si es exitoso, generará y ejecutará las sentencias `DROP TABLE`, `CREATE TABLE` e `INSERT` para los perfiles de `data.json`.

```
