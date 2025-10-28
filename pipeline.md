Este es el desglose detallado del **Pipeline de CI/CD (Integración Continua / Despliegue Continuo)**, especificando el **Cargo** y la **Función a Desempeñar** en cada etapa para un proyecto de **Java Spring Boot** desde cero.

---

## 1. Configuración Inicial y Prerrequisitos (Project Setup) 🏗️

| Cargo | Función a Desempeñar | Detalle de la Tarea |
| :--- | :--- | :--- |
| **Ingeniero DevOps** | **Establecer la Infraestructura Base** | Crea el repositorio de código (Git), el *pipeline* inicial en la herramienta de CI/CD (Jenkins, GitLab CI, etc.), y define el archivo `Dockerfile` base para contenerizar la aplicación Spring Boot. |
| **Ingeniero/Administrador de Bases de Datos (DBA)** | **Provisionar Servicios de Datos** | Crea y configura las instancias de la base de datos (PostgreSQL, MySQL, etc.) para los entornos de Desarrollo, Staging y Producción. Prepara los scripts de migración de esquema. |
| **Desarrollador Java Backend** | **Inicializar el Código Fuente** | Crea el proyecto base (p. ej., con Spring Initializr), define el archivo de configuración de construcción (`pom.xml` o `build.gradle`) e implementa el primer código de negocio con sus **pruebas unitarias** correspondientes. |

***

## 2. Fase de Integración Continua (CI) 🧪

El foco es verificar que el código nuevo sea funcional, seguro y esté listo para el despliegue.

| # | Etapa | Cargo | Función a Desempeñar |
| :---: | :--- | :--- | :--- |
| **1** | **Source (Fuente)** | **Desarrollador Java Backend** | **Integrar y Activar:** Envía los cambios de código al repositorio remoto (`git push`). Este evento actúa como el **desencadenador** del *pipeline*. |
| **2** | **Build (Compilación)** | **Ingeniero DevOps** (Proceso Autom.) | **Compilar el Código:** Descarga el código y usa **Maven** o **Gradle** para generar el artefacto ejecutable (`.jar` o `.war`) de Spring Boot. |
| **3** | **Unit Tests (Pruebas Unitarias)** | **Desarrollador Java Backend** | **Validar la Lógica Individual:** El *pipeline* ejecuta automáticamente todas las pruebas unitarias (con **JUnit/Mockito**) que el desarrollador escribió. **Si fallan, el *pipeline* se detiene (Quality Gate).** |
| **4** | **Code Analysis (Análisis de Calidad y Seguridad)** | **Ingeniero DevOps** (Proceso Autom.) | **Asegurar los Estándares:** Ejecuta escaneos estáticos (p. ej., con SonarQube) para detectar vulnerabilidades, fallas de seguridad de dependencias (OWASP) y problemas de estilo de código. |
| **5** | **Containerize (Contenerización)** | **Ingeniero DevOps** | **Crear Imagen Desplegable:** Toma el artefacto `.jar`, lo combina con el `Dockerfile` y crea una **imagen de Docker**. Esta imagen se etiqueta y se sube al Registro de Contenedores. |

***

## 3. Fase de Despliegue Continuo (CD) 🚀

El foco es llevar la aplicación verificada a los diferentes entornos, culminando en Producción.

| # | Etapa | Cargo | Función a Desempeñar |
| :---: | :--- | :--- | :--- |
| **6** | **Deploy to DEV (Despliegue a Desarrollo)** | **Ingeniero DevOps** | **Despliegue Rápido:** Despliega la imagen de Docker en el clúster de Desarrollo (DEV), configurando variables de entorno y conectándose a la BD de DEV. |
| **7** | **Integration Tests (Pruebas de Integración)** | **Ingeniero QA/Tester** & **Desarrollador Backend** | **Validar Conectividad de Servicios:** Ejecuta pruebas automatizadas (p. ej., con Testcontainers) para confirmar que la aplicación Spring Boot se comunica correctamente con la base de datos y otras APIs en el entorno DEV. |
| **8** | **Manual QA & Approval (Pruebas Manuales y Aprobación)** | **Ingeniero QA/Tester** | **Verificación Funcional Final:** Despliega en el entorno de Staging/QA. El QA realiza pruebas manuales, de rendimiento y de regresión, y **otorga la aprobación explícita** para avanzar a producción. |
| **9** | **DB Migration (Migración de Base de Datos)** | **DBA** (Coordinado con DevOps) | **Sincronizar el Esquema:** Ejecuta las herramientas de migración (p. ej., Flyway) para aplicar los cambios de esquema de base de datos necesarios para que la nueva versión de Spring Boot funcione. |
| **10** | **Deploy to PROD (Despliegue a Producción)** | **Ingeniero DevOps** | **Liberación Segura:** Despliega la imagen aprobada en el clúster de Producción, utilizando **estrategias sin interrupción** (*zero-downtime*) como *Blue/Green* o *Canary* para mitigar riesgos. |
| **11** | **Post-Deployment Monitoring (Monitoreo y Rollback)** | **Ingeniero DevOps** | **Mantener la Estabilidad:** Configura alertas y monitorea las métricas clave (latencia, errores HTTP 5xx, uso de recursos). Si se detectan fallos, activa un proceso de **Rollback** automático a la versión anterior estable. |