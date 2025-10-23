
# Gemini Code Tools Java

**Herramienta de Utilidad en Java para Análisis y Compactación de Proyectos con la API de Gemini**

`gemini-code-tools-java` es una utilidad de línea de comandos construida con Java 17 y Maven, diseñada para simplificar el proceso de preparar y corregir código fuente utilizando el modelo de lenguaje avanzado **Gemini 2.5 Flash**.

La herramienta tiene dos funcionalidades principales:

1.  **Compactación del Código:** Consolida el contenido de múltiples archivos (`.java`, `.xml`, `.md`) en un único archivo de texto para crear un contexto de proyecto completo.
2.  **Análisis y Corrección con IA:** Envía el contexto del proyecto y un archivo específico al modelo Gemini para recibir la versión corregida y optimizada del código.

## 🚀 Requisitos de Arranque

* **Java Development Kit (JDK):** Versión **17** o superior.
* **Apache Maven:** Versión 3.x para construir el proyecto.
* **Clave de API de Gemini:** Debe estar configurada como variable de entorno.

### Configuración de la API Key

La herramienta requiere que se configure la variable de entorno `GEMINI_API_KEY`.

**Linux/macOS:**
```bash
export GEMINI_API_KEY="TU_CLAVE_AQUI"
````

**Windows (CMD):**

```bash
set GEMINI_API_KEY=TU_CLAVE_AQUI
```

**Windows (PowerShell):**

```bash
$env:GEMINI_API_KEY="TU_CLAVE_AQUI"
```

## 🛠️ Instrucciones de Arranque

### 1\. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/gemini-code-tools-java.git
cd gemini-code-tools-java
```

### 2\. Construir el Proyecto

Este proyecto utiliza el `maven-assembly-plugin` para crear un "JAR con dependencias" (fat JAR), que es autocontenido y fácil de ejecutar.

```bash
mvn clean package
```

Una vez completado, el archivo ejecutable se encontrará en el directorio `target/`. El nombre del archivo será similar a: `target/ourcrud-java-1.0-SNAPSHOT-jar-with-dependencies.jar`.

## 💻 Instrucciones de Uso

La herramienta puede ejecutarse en dos modos: **Compactación** o **Análisis/Corrección**.

### Modo 1: Compactar un Proyecto (Crear Contexto)

La clase principal para esta acción es `com.myproject.core.FileProcessor`.

**Función:** Recorre un directorio, filtra archivos (`.java`, `.xml`, `.md`), ignora carpetas como `target` y `.git`, y junta todo en un archivo de salida para usarlo como contexto en el análisis.

```bash
# Sintaxis: java -cp <jar-con-dependencias> com.myproject.core.FileProcessor <ruta_proyecto> <salida.txt>
java -cp target/ourcrud-java-1.0-SNAPSHOT-jar-with-dependencies.jar com.myproject.core.FileProcessor ./ ./proyecto_compactado.txt
```

> **Salida:** Se generará el archivo `contexto_del_proyecto.txt`.

### Modo 2: Analizar y Corregir un Archivo con Gemini

La clase principal para esta acción es `com.myproject.core.AIAnalyzer`.

**Función:** Toma el archivo de contexto generado previamente y el código de un archivo a corregir, lo envía a Gemini, y guarda el resultado corregido.

```bash
# Compactacion para generar contexto de analisis
# java -cp <jar-con-dependencias> com.myproject.core.FileProcessor <contexto.txt> <archivo.java>
java -cp target/ourcrud-java-1.0-SNAPSHOT-jar-with-dependencies.jar com.myproject.core.FileProcessor ./ ./proyecto_compactado.txt

# Enviar a la AI el contexto y el archivo a analizar
# java -cp <jar-con-dependencias> com.myproject.core.AIAnalyzer <contexto.txt> <archivo.java>
java -cp target/ourcrud-java-1.0-SNAPSHOT-jar-with-dependencies.jar com.myproject.core.AIAnalyzer proyecto_compactado.txt src/main/java/com/myproject/core/PathSorter.java
```

> **Salida:** Generará un nuevo archivo con el sufijo `-corregido.java`. Por ejemplo, `AIAnalyzer-corregido.java`.

### 📌 Notas Importantes

  * El código utiliza la API HTTP nativa de Java (`HttpURLConnection`) para la comunicación con Gemini, lo que minimiza las dependencias externas.
  * El analizador está configurado para usar el modelo `gemini-2.5-flash` y una **instrucción de sistema estricta** que solicita **solo el código corregido** como respuesta, sin explicaciones ni bloques de marcado.
