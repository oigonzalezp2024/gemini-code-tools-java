# 🛠️ ourcrud-java: Herramientas de Código y Gestión JDBC

Este es un proyecto multi-módulo de Maven diseñado para demostrar la integración de diversas utilidades en un entorno Java: herramientas de análisis de código basadas en la API de Google Gemini y un módulo de gestión de base de datos (CRUD) con conexión JDBC real a MySQL.

La ejecución centralizada se logra mediante el módulo `launcher-app`, que genera un único **Fat JAR** con todas las dependencias.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente:

1.  **JDK (Java Development Kit)**: Versión 17 o superior.
2.  **Apache Maven**: Versión 3.6 o superior.
3.  **Servidor MySQL**: Instancia local activa (en `localhost:3306`).
4.  **Base de Datos MySQL**: Debe existir una base de datos llamada `java_project_db`.
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

## ⚙️ Configuración y Compilación

Ejecuta el siguiente comando en la raíz del proyecto para limpiar, compilar e instalar todos los módulos en el repositorio local de Maven. Esto generará el Fat JAR final en el directorio `launcher-app/target/`.

```bash
mvn clean install
```

## 💻 Modos de Ejecución del Software

El proyecto ofrece tres modos principales de ejecución, dirigidos por el Fat JAR unificado (`ourcrud-java-all-1.0-SNAPSHOT.jar`) o invocando clases específicas.

### 1\. 💾 Gestión de Base de Datos (Modo Centralizado)

Este modo ejecuta la clase principal `DatabaseManager`, que se encarga de leer `data.json`, conectar con MySQL, crear la tabla `perfiles_tecnicos` y insertar los datos, resolviendo automáticamente las dependencias del driver JDBC.

**Clase Principal:** `com.mycompany.app.DatabaseManager`

```bash
# Ejecutar desde la raíz del proyecto (la ruta del JAR es relativa)
java -jar ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar
```

**Resultado:**
El programa intentará conectar a `jdbc:mysql://localhost:3306/java_project_db` con el usuario `root` y contraseña vacía. Si es exitoso, generará y ejecutará las sentencias `DROP TABLE`, `CREATE TABLE` e `INSERT` para los perfiles de `data.json`.

-----

### 2\. 📝 Compactación de Código (Generación de Contexto)

Utiliza la herramienta `FileProcessor` para rastrear un directorio de proyecto y compactar el contenido de los archivos relevantes (Java, XML, JSON, etc.) en un solo archivo de texto. Este archivo sirve como **contexto de proyecto** para el analista de IA.

**Clase Principal:** `com.myproject.core.FileProcessor`

```bash
# Uso: java -cp <Fat-JAR> <Clase> <ruta_proyecto> <salida.txt>
java -cp ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar \
     com.myproject.core.FileProcessor \
     . \
     contexto_completo.txt
```

**Parámetros:**

  * `ruta_proyecto`: Directorio raíz a escanear (e.g., `.` para el directorio actual).
  * `salida.txt`: Nombre del archivo de texto generado.

-----

### 3\. 🤖 Análisis y Corrección de Código con IA

Utiliza la herramienta `AIAnalyzer` para enviar un archivo a la API de Gemini, utilizando un archivo de contexto previo (generado en el Modo 2) para obtener correcciones específicas de código.

**Clase Principal:** `com.myproject.core.AIAnalyzer`

```bash
# Uso: java -cp <Fat-JAR> <Clase> <contexto.txt> <archivo.java>
java -cp ./launcher-app/target/ourcrud-java-all-1.0-SNAPSHOT.jar \
     com.myproject.core.AIAnalyzer \
     contexto_completo.txt \
     ./java-db-project/src/main/java/com/mycompany/app/Controller.java
```

**Parámetros:**

  * `contexto.txt`: El archivo de contexto generado por `FileProcessor`.
  * `archivo.java`: La ruta del archivo específico que deseas que Gemini corrija.

**Resultado:**
Generará un nuevo archivo con el sufijo `-corregido.java` (ej. `Controller-corregido.java`) conteniendo el código corregido por la IA.

```