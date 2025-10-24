import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
import subprocess
import threading
import sys
import os
import time

# --- Constantes del Proyecto ---
JAVA_CMD = "java"
JAR_PATH = os.path.join(".", "launcher-app", "target", "ourcrud-java-all-1.0-SNAPSHOT.jar")
FILE_PROCESSOR_CLASS = "com.myproject.core.FileProcessor"
AI_ANALYZER_CLASS = "com.myproject.core.AIAnalyzer"
CONTEXT_FILE = os.path.join(".", "contexto.txt")

class OrchestratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Orquestador Java/Maven (GUI)")
        self.geometry("950x650") # Aumentado el ancho para los nuevos botones
        self.api_process = None # Proceso para el Web API en segundo plano
        
        self.create_widgets()

    def create_widgets(self):
        # Configurar estilo para mejor apariencia
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=6)
        style.configure('TLabel', font=('Helvetica', 10), padding=3)

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ------------------------------------
        # 1. Configuración de Inputs
        # ------------------------------------
        input_frame = ttk.LabelFrame(main_frame, text="Configuración de Rutas", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        # Input 1: Path del Proyecto (para FileProcessor)
        ttk.Label(input_frame, text="Ruta Base del Proyecto (Ej: ./src/main/java):").grid(row=0, column=0, sticky="w", pady=5)
        self.project_path_var = tk.StringVar(value="./gemini-tools-core") # Valor por defecto
        self.project_path_entry = ttk.Entry(input_frame, textvariable=self.project_path_var)
        self.project_path_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.btn_browse_project = ttk.Button(input_frame, text="Buscar Carpeta", command=self.browse_project_path, width=15)
        self.btn_browse_project.grid(row=0, column=2, sticky="e", padx=5)
        
        # Input 2: Path de Comparación (para AIAnalyzer)
        ttk.Label(input_frame, text="Ruta de Salida/Comparación (AIAnalyzer):").grid(row=1, column=0, sticky="w", pady=5)
        self.analyzer_path_var = tk.StringVar(value="./ai_analysis_output.txt") # Valor por defecto
        self.analyzer_path_entry = ttk.Entry(input_frame, textvariable=self.analyzer_path_var)
        self.analyzer_path_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.btn_browse_analyzer = ttk.Button(input_frame, text="Buscar Archivo", command=self.browse_analyzer_path, width=15)
        self.btn_browse_analyzer.grid(row=1, column=2, sticky="e", padx=5)

        input_frame.grid_columnconfigure(1, weight=1) # Permite que el campo de entrada se expanda
        input_frame.grid_columnconfigure(2, weight=0) # Evita que el botón de búsqueda se expanda
        
        # ------------------------------------
        # 2. Botones de Funcionalidad
        # ------------------------------------
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Botón 1: Build (Maven Clean Install)
        self.btn_build = ttk.Button(button_frame, text="0. Compilar Proyecto (Maven)", command=lambda: self.start_task(self.build_project))
        self.btn_build.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Botón 2: FileProcessor
        self.btn_process = ttk.Button(button_frame, text="1. Procesar Archivos (FileProcessor)", command=lambda: self.start_task(self.run_file_processor))
        self.btn_process.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Botón 3: AIAnalyzer
        self.btn_analyze = ttk.Button(button_frame, text="2. Analizar y Comparar (AIAnalyzer)", command=lambda: self.start_task(self.run_ai_analyzer))
        self.btn_analyze.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # ------------------------------------
        # 3. Control del API
        # ------------------------------------
        api_frame = ttk.LabelFrame(main_frame, text="Control del Web API", padding="10")
        api_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start_api = ttk.Button(api_frame, text="3. Iniciar Web API (java -jar)", command=self.start_api, style='TButton')
        self.btn_start_api.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_stop_api = ttk.Button(api_frame, text="Detener API", command=self.stop_api, state=tk.DISABLED, style='TButton')
        self.btn_stop_api.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.api_status_var = tk.StringVar(value="API: Detenido")
        ttk.Label(api_frame, textvariable=self.api_status_var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # ------------------------------------
        # 4. Estado y Log
        # ------------------------------------
        ttk.Label(main_frame, text="Registro de Actividad y Resultados:").pack(pady=(10, 2), anchor=tk.W)
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, font=('Consolas', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED, background='#2e2e2e', foreground='#e0e0e0') # Estilo oscuro para log


    def log_output(self, message, is_error=False):
        """Añade un mensaje al área de texto."""
        self.output_text.config(state=tk.NORMAL)
        tag = 'error' if is_error else 'info'
        
        self.output_text.tag_config('info', foreground='#e0e0e0')
        self.output_text.tag_config('error', foreground='#ff6b6b')

        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.update() 

    def enable_buttons(self, enable=True):
        """Controla el estado de los botones de ejecución de tareas."""
        state = tk.NORMAL if enable else tk.DISABLED
        self.btn_build.config(state=state)
        self.btn_process.config(state=state)
        self.btn_analyze.config(state=state)

    def start_task(self, task_function):
        """Inicia una tarea en un hilo separado."""
        self.log_output(f"\n--- Iniciando tarea: {task_function.__name__} ---", is_error=False)
        self.enable_buttons(False) # Deshabilita los botones de tarea
        threading.Thread(target=task_function, daemon=True).start()

    def run_command(self, command_parts, success_message, error_message, cwd=None):
        """Ejecuta un comando y registra su salida en el log."""
        self.log_output(f"Ejecutando: {' '.join(command_parts)}")
        try:
            result = subprocess.run(
                command_parts,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300 # 5 minutos de timeout
            )
            if result.stdout:
                self.log_output("STDOUT:\n" + result.stdout.strip())
            
            self.log_output(success_message)
            return True

        except subprocess.CalledProcessError as e:
            self.log_output(f"ERROR: Comando falló con código {e.returncode}", is_error=True)
            self.log_output("STDOUT:\n" + e.stdout.strip(), is_error=True)
            self.log_output("STDERR:\n" + e.stderr.strip(), is_error=True)
            self.log_output(error_message, is_error=True)
            return False
        except FileNotFoundError:
            missing_tool = command_parts[0]
            if missing_tool.endswith('mvn') or missing_tool.endswith('mvn.cmd'):
                error_detail = "El comando 'mvn' (Maven) no fue encontrado. Asegúrate de que Maven esté instalado y configurado correctamente en la variable de entorno PATH."
            elif missing_tool == "java":
                error_detail = "El comando 'java' (Java Runtime) no fue encontrado. Asegúrate de que el JRE/JDK esté instalado y configurado correctamente en la variable de entorno PATH."
            else:
                error_detail = f"Comando '{missing_tool}' no encontrado. ¿Está instalado y en su PATH?"
                
            self.log_output(f"ERROR: {error_detail}", is_error=True)
            return False
        except subprocess.TimeoutExpired:
            self.log_output("ERROR: El comando ha excedido el tiempo límite de 5 minutos.", is_error=True)
            return False
        except Exception as e:
            self.log_output(f"ERROR inesperado: {e}", is_error=True)
            return False
        finally:
            self.enable_buttons(True)


    # ------------------------------------
    # Funciones de Lógica de Negocio
    # ------------------------------------

    def browse_project_path(self):
        """Abre un diálogo para seleccionar la carpeta del proyecto (input para FileProcessor)."""
        directory = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Seleccionar Carpeta Raíz del Proyecto Java"
        )
        if directory:
            self.project_path_var.set(directory)

    def browse_analyzer_path(self):
        """Abre un diálogo para seleccionar la ruta del archivo de salida/comparación (input/output para AIAnalyzer)."""
        filepath = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            title="Seleccionar Archivo de Salida para AIAnalyzer",
            defaultextension=".txt",
            filetypes=(("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        if filepath:
            self.analyzer_path_var.set(filepath)

    def _get_maven_command(self):
        """
        Intenta obtener el comando 'mvn'.
        Usa MAVEN_HOME como un mecanismo de fallback robusto si 'mvn' no está en PATH.
        """
        
        # 1. Intentar con el comando simple 'mvn' (esperando que esté en PATH)
        mvn_command = ["mvn"]
        
        # 2. Fallback a MAVEN_HOME si existe
        if "MAVEN_HOME" in os.environ:
            maven_home = os.environ["MAVEN_HOME"]
            
            # En Windows, el ejecutable puede ser mvn.cmd.
            if sys.platform.startswith('win'):
                mvn_cmd_path = os.path.join(maven_home, "bin", "mvn.cmd")
                if os.path.exists(mvn_cmd_path):
                    return [mvn_cmd_path]
            
            # Usar mvn (funciona en Linux/Mac y a menudo en Windows si JAVA_HOME está bien)
            mvn_path = os.path.join(maven_home, "bin", "mvn")
            if os.path.exists(mvn_path):
                return [mvn_path]

        # Si no se encuentra un path explícito, devolvemos el comando simple
        return mvn_command

    def build_project(self):
        """Ejecuta 'mvn clean install' utilizando el comando Maven resuelto."""
        maven_cmd = self._get_maven_command()
        
        # Agregamos los argumentos de Maven al comando resuelto.
        command_parts = maven_cmd + ["clean", "install"]
        
        self.run_command(
            command_parts=command_parts,
            success_message="✅ Proyecto Java/Maven compilado con éxito.",
            error_message="❌ La compilación del proyecto falló."
        )

    def run_file_processor(self):
        """Ejecuta com.myproject.core.FileProcessor."""
        project_path = self.project_path_var.get()
        
        if not project_path:
            self.log_output("ERROR: La ruta base del proyecto no puede estar vacía.", is_error=True)
            self.enable_buttons(True)
            return
            
        # El archivo de contexto se sobrescribe automáticamente
        success = self.run_command(
            command_parts=[
                JAVA_CMD,
                "-cp", JAR_PATH,
                FILE_PROCESSOR_CLASS,
                project_path,
                CONTEXT_FILE
            ],
            success_message=f"✅ FileProcessor finalizado. Contexto creado en: {CONTEXT_FILE}",
            error_message="❌ Error al ejecutar FileProcessor."
        )
        if success:
             self.log_output(f"El archivo {CONTEXT_FILE} se ha creado/sobrescrito con el contexto del proyecto.", is_error=False)


    def run_ai_analyzer(self):
        """Ejecuta com.myproject.core.AIAnalyzer y muestra el resultado."""
        output_path = self.analyzer_path_var.get()
        
        if not output_path:
            self.log_output("ERROR: La ruta de salida del analizador no puede estar vacía.", is_error=True)
            self.enable_buttons(True)
            return

        # 1. Ejecutar el AIAnalyzer
        success = self.run_command(
            command_parts=[
                JAVA_CMD,
                "-cp", JAR_PATH,
                AI_ANALYZER_CLASS,
                CONTEXT_FILE,
                output_path
            ],
            success_message=f"✅ AIAnalyzer finalizado. Resultado guardado en: {output_path}",
            error_message="❌ Error al ejecutar AIAnalyzer."
        )

        # 2. Leer y mostrar el contenido del archivo de salida
        if success:
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.log_output(f"\n--- Contenido del archivo de salida ({output_path}) ---\n", is_error=False)
                self.log_output(content)
                self.log_output("\n--- Fin del contenido ---", is_error=False)

            except FileNotFoundError:
                self.log_output(f"ERROR: Archivo de salida no encontrado en {output_path}", is_error=True)
            except Exception as e:
                self.log_output(f"ERROR al leer el archivo {output_path}: {e}", is_error=True)
        
        self.enable_buttons(True)


    # ------------------------------------
    # Control del API Web
    # ------------------------------------

    def start_api(self):
        """Inicia el Web API en un proceso separado."""
        if self.api_process and self.api_process.poll() is None:
            self.log_output("El Web API ya está corriendo.", is_error=False)
            return

        self.btn_start_api.config(state=tk.DISABLED)
        self.api_status_var.set("API: Iniciando...")
        self.log_output("\n--- Iniciando Java Web API en segundo plano ---")

        # Usamos un hilo para manejar la subejecución y evitar que la GUI se bloquee
        threading.Thread(target=self._api_starter_logic, daemon=True).start()

    def _api_starter_logic(self):
        try:
            if not os.path.exists(JAR_PATH):
                self.log_output(f"ERROR: JAR no encontrado en {JAR_PATH}. ¿Ha compilado el proyecto?", is_error=True)
                return

            self.api_process = subprocess.Popen(
                [JAVA_CMD, "-jar", JAR_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # Para lectura en tiempo real
            )
            self.log_output(f"Web API iniciado con PID: {self.api_process.pid}")
            self.api_status_var.set(f"API: Corriendo (PID: {self.api_process.pid})")
            self.btn_stop_api.config(state=tk.NORMAL)
            
            # Bucle para capturar la salida del API en tiempo real
            for line in iter(self.api_process.stdout.readline, ''):
                if not line: break
                self.log_output(f"API >> {line.strip()}")

            # Después de que el API termina, verifica el código de retorno
            self.api_process.wait()
            return_code = self.api_process.returncode

            self.log_output(f"Web API terminó con código: {return_code}", is_error=(return_code != 0))
            self.api_status_var.set("API: Detenido")
            self.btn_stop_api.config(state=tk.DISABLED)

        except Exception as e:
            self.log_output(f"ERROR al iniciar/monitorear el API: {e}", is_error=True)
            self.api_status_var.set("API: Error")
        finally:
            self.btn_start_api.config(state=tk.NORMAL)


    def stop_api(self):
        """Detiene el proceso del Web API de forma controlada."""
        if not self.api_process or self.api_process.poll() is not None:
            self.log_output("El Web API no está corriendo o ya ha terminado.", is_error=False)
            self.btn_stop_api.config(state=tk.DISABLED)
            self.api_status_var.set("API: Detenido")
            return
        
        self.log_output("\n--- Solicitando terminación del Java Web API ---", is_error=False)
        self.btn_stop_api.config(state=tk.DISABLED)
        self.api_status_var.set("API: Deteniendo...")
        
        # Usamos un hilo para el proceso de terminación para evitar el bloqueo por 'wait'
        threading.Thread(target=self._api_stopper_logic, daemon=True).start()

    def _api_stopper_logic(self):
        try:
            # 1. Terminación suave (SIGTERM)
            self.api_process.terminate() 
            self.api_process.wait(timeout=10)
            self.log_output("Web API detenido exitosamente.", is_error=False)
            
        except subprocess.TimeoutExpired:
            # 2. Terminación forzosa (SIGKILL)
            self.log_output("El API no terminó de forma suave. Matándolo forzosamente.", is_error=True)
            self.api_process.kill()
            self.api_process.wait()
        
        except Exception as e:
            self.log_output(f"ERROR al detener el API: {e}", is_error=True)

        finally:
            # Muestra cualquier salida final de error
            stdout, stderr = self.api_process.communicate()
            if stderr:
                self.log_output("API STDERR final:\n" + stderr.strip(), is_error=True)
                
            self.api_status_var.set("API: Detenido")
            self.btn_start_api.config(state=tk.NORMAL)

    def on_closing(self):
        """Se asegura de que el API se detenga al cerrar la ventana."""
        if self.api_process and self.api_process.poll() is None:
            if messagebox.askyesno("Salir", "El Web API está corriendo. ¿Desea detenerlo y cerrar la aplicación?"):
                self.stop_api()
                self.destroy()
            return
        self.destroy()

if __name__ == "__main__":
    app = OrchestratorApp()
    # Asegura la limpieza del API al cerrar la ventana
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
