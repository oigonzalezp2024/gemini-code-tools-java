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
CONTEXT_FILE = os.path.join(".", "contexto.txt")

# Clases de Funcionalidad Base
FILE_PROCESSOR_CLASS = "com.myproject.core.FileProcessor"
AI_ANALYZER_CLASS = "com.myproject.core.AIAnalyzer"

# Clases de Especialistas (extienden de Especialista.java)
AI_ANALYZER_DB_CLASS = "com.myproject.core.AIAnalyzerDB"
AI_ANALYZER_QA_CLASS = "com.myproject.core.AIAnalyzerQA"
AI_ANALYZER_BACKEND_CLASS = "com.myproject.core.AIAnalyzerBackend" 
AI_ANALYZER_FRONTEND_CLASS = "com.myproject.core.AIAnalyzerFrontend"
AI_ANALYZER_DEVOPS_CLASS = "com.myproject.core.AIAnalyzerDevOps"
AI_ANALYZER_GENERIC_CLASS = "com.myproject.core.AIAnalyzerGeneric"


# ====================================
# VENTANA FLOTANTE DE CONSOLA
# ====================================
class ConsoleWindow(tk.Toplevel):
    """Ventana flotante para mostrar el registro de actividad (log)."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Registro de Actividad y Resultados")
        self.geometry("800x400") # Tamaño fijo para la consola
        self.protocol("WM_DELETE_WINDOW", self.hide_window) # Ocultar en lugar de destruir
        self.visible = True
        
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, font=('Consolas', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED, background='#2e2e2e', foreground='#e0e0e0')
        
        # Configuración de tags de color
        self.output_text.tag_config('info', foreground='#e0e0e0')
        self.output_text.tag_config('error', foreground='#ff6b6b')

    def log(self, message, is_error=False):
        """Añade un mensaje al área de texto."""
        self.output_text.config(state=tk.NORMAL)
        tag = 'error' if is_error else 'info'
        
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def hide_window(self):
        """Oculta la ventana y actualiza el estado."""
        self.withdraw()
        self.visible = False

    def show_window(self):
        """Muestra la ventana y actualiza el estado."""
        self.deiconify()
        self.visible = True
        self.focus_set()


# ====================================
# APLICACIÓN PRINCIPAL (ORQUESTADOR)
# ====================================
class OrchestratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Orquestador Java/Maven (GUI)")
        self.api_process = None 
        
        # Inicializar la consola flotante antes de crear widgets, para que log_output funcione
        self.console_window = ConsoleWindow(self) 
        
        # Variables de Configuración Base
        self.project_path_var = tk.StringVar(value="./gemini-tools-core")
        self.analyzer_path_var = tk.StringVar(value="./bbdd.txt")

        # Variables de Ruta Individuales para Especialistas
        self.dba_path_var = tk.StringVar(value="./ia_consultas/guide_dba.md")
        self.qa_path_var = tk.StringVar(value="./ia_consultas/guide_qa.md")
        self.backend_path_var = tk.StringVar(value="./ia_consultas/guide_backend.md")
        self.frontend_path_var = tk.StringVar(value="./ia_consultas/guide_frontend.md")
        self.devops_path_var = tk.StringVar(value="./ia_consultas/guide_devops.md")
        self.generic_path_var = tk.StringVar(value="./ia_consultas/guide_solid.md")

        self.create_widgets()
        # Mostrar la consola al inicio (opcional, puede ser .withdraw() para empezar oculta)
        self.console_window.show_window()


    def create_widgets(self):
        # Configurar estilo
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=6)
        style.configure('TLabel', font=('Helvetica', 10), padding=3)

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ------------------------------------
        # 1. Configuración de Inputs Base
        # ------------------------------------
        input_frame = ttk.LabelFrame(main_frame, text="Configuración de Rutas Base", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        # Input 1: Path del Proyecto
        ttk.Label(input_frame, text="Ruta Base del Proyecto (Ej: ./src/main/java):").grid(row=0, column=0, sticky="w", pady=5)
        self.project_path_entry = ttk.Entry(input_frame, textvariable=self.project_path_var)
        self.project_path_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.btn_browse_project = ttk.Button(input_frame, text="Buscar Carpeta", command=self.browse_project_path, width=15)
        self.btn_browse_project.grid(row=0, column=2, sticky="e", padx=5)
        
        # Input 2: Path de Comparación / Archivo a Corregir (AIAnalyzer Original)
        ttk.Label(input_frame, text="Ruta de Salida/Archivo a Corregir (AIAnalyzer Original):").grid(row=1, column=0, sticky="w", pady=5)
        self.analyzer_path_entry = ttk.Entry(input_frame, textvariable=self.analyzer_path_var)
        self.analyzer_path_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.btn_browse_analyzer = ttk.Button(input_frame, text="Buscar Archivo", command=lambda: self.browse_file_path(self.analyzer_path_var), width=15)
        self.btn_browse_analyzer.grid(row=1, column=2, sticky="e", padx=5)

        input_frame.grid_columnconfigure(1, weight=1) 
        
        # ------------------------------------
        # 1B. Configuración de Rutas Especialistas (2 COLUMNAS)
        # ------------------------------------
        specialist_input_frame = ttk.LabelFrame(main_frame, text="Rutas de Archivo - Roles Especialistas", padding="10")
        specialist_input_frame.pack(fill=tk.X, pady=10)

        specialists_config = [
            ("DBA", self.dba_path_var), ("QA", self.qa_path_var),
            ("Backend (Spring)", self.backend_path_var), ("Frontend (UI/UX)", self.frontend_path_var),
            ("DevOps (CI/CD)", self.devops_path_var), ("Genérico (SOLID)", self.generic_path_var),
        ]
        
        num_cols = 3 
        items_per_col = (len(specialists_config) + 1) // 2
        
        for i, (name, var) in enumerate(specialists_config):
            row_index = i % items_per_col
            col_offset = (i // items_per_col) * num_cols
            
            ttk.Label(specialist_input_frame, text=f"{name}:").grid(row=row_index, column=0 + col_offset, sticky="w", pady=2, padx=(5 if col_offset else 0, 0))
            entry = ttk.Entry(specialist_input_frame, textvariable=var)
            entry.grid(row=row_index, column=1 + col_offset, sticky="ew", padx=5)
            btn = ttk.Button(specialist_input_frame, text="Buscar Archivo", command=lambda v=var: self.browse_file_path(v), width=15)
            btn.grid(row=row_index, column=2 + col_offset, sticky="e", padx=5)
        
        specialist_input_frame.grid_columnconfigure(1, weight=1)
        specialist_input_frame.grid_columnconfigure(4, weight=1)
        
        # ------------------------------------
        # 2. Botones de Funcionalidad
        # ------------------------------------
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Fila 1: Funcionalidad Base
        self.btn_build = ttk.Button(button_frame, text="0. Compilar Proyecto (Maven)", command=lambda: self.start_task(self.build_project))
        self.btn_build.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.btn_process = ttk.Button(button_frame, text="1. Procesar Archivos (FileProcessor)", command=lambda: self.start_task(self.run_file_processor))
        self.btn_process.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.btn_analyze = ttk.Button(button_frame, text="2. Analizar y Corregir (AIAnalyzer Original)", command=lambda: self.start_task(self.run_ai_analyzer))
        self.btn_analyze.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Fila 2: Roles Especialistas (Generadores de Guías)
        titulo_especialistas = "Especialistas - Generación de Guías de Aprendizaje"
        button_frame2 = ttk.LabelFrame(main_frame, text=titulo_especialistas, padding="10")
        button_frame2.pack(fill=tk.X, pady=11)

        button_row1 = ttk.Frame(button_frame2)
        button_row1.pack(fill=tk.X, pady=5)
        
        self.btn_analyze_dba = ttk.Button(button_row1, text="Ingeniero DBA", command=lambda: self.start_task(self.run_ai_analyzer_db))
        self.btn_analyze_dba.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.btn_analyze_qa = ttk.Button(button_row1, text="Ingeniero QA", command=lambda: self.start_task(self.run_ai_analyzer_qa))
        self.btn_analyze_qa.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_analyze_backend = ttk.Button(button_row1, text="Backend (Spring)", command=lambda: self.start_task(self.run_ai_analyzer_backend))
        self.btn_analyze_backend.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        button_row2 = ttk.Frame(button_frame2)
        button_row2.pack(fill=tk.X, pady=5)
        
        self.btn_analyze_frontend = ttk.Button(button_row2, text="Frontend (UI/UX)", command=lambda: self.start_task(self.run_ai_analyzer_frontend))
        self.btn_analyze_frontend.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_analyze_devops = ttk.Button(button_row2, text="DevOps (CI/CD)", command=lambda: self.start_task(self.run_ai_analyzer_devops))
        self.btn_analyze_devops.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_analyze_generic = ttk.Button(button_row2, text="Genérico (SOLID)", command=lambda: self.start_task(self.run_ai_analyzer_generic))
        self.btn_analyze_generic.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # ------------------------------------
        # 3. Control del API
        # ------------------------------------
        api_frame = ttk.LabelFrame(main_frame, text="Control del Web API", padding="10")
        api_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start_api = ttk.Button(api_frame, text="4. Iniciar Web API (java -jar)", command=self.start_api, style='TButton')
        self.btn_start_api.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_stop_api = ttk.Button(api_frame, text="Detener API", command=self.stop_api, state=tk.DISABLED, style='TButton')
        self.btn_stop_api.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.api_status_var = tk.StringVar(value="API: Detenido")
        ttk.Label(api_frame, textvariable=self.api_status_var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # ------------------------------------
        # 4. Control del Log (Botón de Ventana Flotante)
        # ------------------------------------
        log_control_frame = ttk.Frame(main_frame)
        log_control_frame.pack(fill=tk.X, pady=5)
        
        self.btn_toggle_console = ttk.Button(log_control_frame, text="Mostrar/Ocultar Consola de Log", command=self.toggle_console_window)
        self.btn_toggle_console.pack(expand=True, fill=tk.X)
        
    def toggle_console_window(self):
        """Alterna la visibilidad de la ventana de consola."""
        if self.console_window.visible:
            self.console_window.hide_window()
        else:
            self.console_window.show_window()


    def log_output(self, message, is_error=False):
        """Añade un mensaje al área de texto de la ventana flotante."""
        if self.console_window:
            # Asegurar que la consola esté visible si se recibe un mensaje
            if not self.console_window.visible:
                 self.after(0, self.console_window.show_window)
            
            # Usar self.after para encolar la acción en el hilo principal de Tkinter
            self.after(0, lambda: self.console_window.log(message, is_error))
            self.update_idletasks() # Fuerza la actualización de la GUI


    def enable_buttons(self, enable=True):
        """Controla el estado de los botones de ejecución de tareas."""
        state = tk.NORMAL if enable else tk.DISABLED
        self.btn_build.config(state=state)
        self.btn_process.config(state=state)
        self.btn_analyze.config(state=state)
        
        # Control de los 6 botones de especialistas
        self.btn_analyze_dba.config(state=state) 
        self.btn_analyze_qa.config(state=state)
        self.btn_analyze_backend.config(state=state)
        self.btn_analyze_frontend.config(state=state)
        self.btn_analyze_devops.config(state=state)
        self.btn_analyze_generic.config(state=state)


    def start_task(self, task_function):
        """Inicia una tarea en un hilo separado."""
        def task_wrapper():
            try:
                task_function()
            except Exception as e:
                self.after(0, lambda: self.log_output(f"ERROR FATAL en el hilo: {e}", is_error=True))
            finally:
                self.after(0, lambda: self.enable_buttons(True))

        self.log_output(f"\n--- Iniciando tarea: {task_function.__name__} ---", is_error=False)
        self.enable_buttons(False) 
        threading.Thread(target=task_wrapper, daemon=True).start()

    def _read_stream(self, stream, is_error):
        """Lee el stream de un proceso línea por línea y lo registra en el log."""
        # Se asegura de usar la lógica de log_output, que gestiona el acceso al hilo de Tkinter
        for line in iter(stream.readline, ''):
            if line:
                msg = line.strip()
                if msg:
                    self.log_output(msg, is_error=is_error)
        
    def run_command(self, command_parts, success_message, error_message, cwd=None):
        """
        Ejecuta un comando y registra su salida en el log en tiempo real.
        """
        self.log_output(f"Ejecutando: {' '.join(command_parts)}")

        try:
            process = subprocess.Popen(
                command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1, # Line buffering
                cwd=cwd
            )
            
            stdout_thread = threading.Thread(target=self._read_stream, args=(process.stdout, False), daemon=True)
            stderr_thread = threading.Thread(target=self._read_stream, args=(process.stderr, True), daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()

            try:
                process.wait(timeout=300)
            except subprocess.TimeoutExpired:
                process.terminate()
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                self.log_output("ERROR: El comando ha excedido el tiempo límite de 5 minutos. Proceso terminado.", is_error=True)
                return False

            stdout_thread.join()
            stderr_thread.join()

            if process.returncode != 0:
                self.log_output(f"ERROR: Comando falló con código {process.returncode}", is_error=True)
                self.log_output(error_message, is_error=True)
                return False

            self.log_output(success_message)
            return True

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
        except Exception as e:
            self.log_output(f"ERROR inesperado: {e}", is_error=True)
            return False


    # ------------------------------------
    # Funciones de Lógica de Negocio (Inputs, Build, Process)
    # ------------------------------------

    def browse_project_path(self):
        """Abre un diálogo para seleccionar la carpeta del proyecto (input para FileProcessor)."""
        directory = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Seleccionar Carpeta Raíz del Proyecto Java"
        )
        if directory:
            self.project_path_var.set(directory)

    def browse_file_path(self, path_var):
        """Abre un diálogo para seleccionar la ruta del archivo de salida/comparación (input/output para AIAnalyzer)."""
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Seleccionar Archivo a Corregir/Generar Guía",
            defaultextension=".txt",
            filetypes=(("Archivos Markdown", "*.md"), ("Archivos de Texto", "*.txt"), ("Archivos Java", "*.java"), ("Todos los archivos", "*.*"))
        )
        if filepath:
            path_var.set(filepath)


    def _get_maven_command(self):
        """Obtiene el comando 'mvn', usando MAVEN_HOME como fallback."""
        mvn_command = ["mvn"]
        if "MAVEN_HOME" in os.environ:
            maven_home = os.environ["MAVEN_HOME"]
            if sys.platform.startswith('win'):
                mvn_cmd_path = os.path.join(maven_home, "bin", "mvn.cmd")
                if os.path.exists(mvn_cmd_path):
                    return [mvn_cmd_path]
            mvn_path = os.path.join(maven_home, "bin", "mvn")
            if os.path.exists(mvn_path):
                return [mvn_path]
        return mvn_command

    def build_project(self):
        """Ejecuta 'mvn clean install'."""
        maven_cmd = self._get_maven_command()
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
            return
            
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
        """Ejecuta com.myproject.core.AIAnalyzer (modo original de corrección, usa la ruta compartida)."""
        output_path = self.analyzer_path_var.get()
        
        if not output_path:
            self.log_output("ERROR: La ruta de salida del analizador no puede estar vacía.", is_error=True)
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
                output_path_to_read = output_path
                target_lower = output_path.lower()
                
                if target_lower.endswith(".java"):
                    base_name, ext = os.path.splitext(output_path)
                    output_path_to_read = base_name + "-corregido" + ext
                
                with open(output_path_to_read, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.log_output(f"\n--- Contenido del archivo de salida ({output_path_to_read}) ---\n", is_error=False)
                self.log_output(content)
                self.log_output("\n--- Fin del contenido ---", is_error=False)

            except FileNotFoundError:
                self.log_output(f"ERROR: Archivo de salida no encontrado en {output_path_to_read}", is_error=True)
            except Exception as e:
                self.log_output(f"ERROR al leer el archivo {output_path_to_read}: {e}", is_error=True)
    
    # ------------------------------------
    # Funciones de Especialistas (Generación de Guías)
    # ------------------------------------
    
    def _execute_specialist_logic(self, class_name, role_name, target_file_path):
        """Función auxiliar para ejecutar cualquier clase Especialista (DBA, QA, Backend, etc.)."""
        
        if not target_file_path:
            self.log_output(f"ERROR: La ruta del archivo para {role_name} no puede estar vacía.", is_error=True)
            return

        # 1. Ejecutar el Especialista
        success = self.run_command(
            command_parts=[
                JAVA_CMD,
                "-cp", JAR_PATH,
                class_name,
                CONTEXT_FILE,
                target_file_path 
            ],
            success_message=f"✅ {role_name} finalizado. Guía de aprendizaje generada.",
            error_message=f"❌ Error al ejecutar {role_name}."
        )

        # 2. Leer y mostrar el contenido del archivo de salida
        if success:
            output_path = target_file_path
            target_lower = target_file_path.lower()
            
            if target_lower.endswith(".java"):
                base_name, ext = os.path.splitext(target_file_path)
                output_path = base_name + "-corregido" + ext

            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.log_output(f"\n--- Guía de {role_name} ({os.path.basename(output_path)}) ---\n", is_error=False)
                self.log_output(content)
                self.log_output("\n--- Fin de la Guía ---", is_error=False)

            except FileNotFoundError:
                self.log_output(f"ERROR: El archivo de salida esperado no se encontró: {output_path}", is_error=True)
            except Exception as e:
                self.log_output(f"ERROR al leer el archivo de salida {output_path}: {e}", is_error=True)

    # Métodos de ejecución para cada rol 
    def run_ai_analyzer_db(self):
        self._execute_specialist_logic(AI_ANALYZER_DB_CLASS, "Ingeniero DBA", self.dba_path_var.get())

    def run_ai_analyzer_qa(self):
        self._execute_specialist_logic(AI_ANALYZER_QA_CLASS, "Ingeniero QA", self.qa_path_var.get())
        
    def run_ai_analyzer_backend(self):
        self._execute_specialist_logic(AI_ANALYZER_BACKEND_CLASS, "Backend (Spring)", self.backend_path_var.get())

    def run_ai_analyzer_frontend(self):
        self._execute_specialist_logic(AI_ANALYZER_FRONTEND_CLASS, "Frontend (UI/UX)", self.frontend_path_var.get())

    def run_ai_analyzer_devops(self):
        self._execute_specialist_logic(AI_ANALYZER_DEVOPS_CLASS, "DevOps (CI/CD)", self.devops_path_var.get())

    def run_ai_analyzer_generic(self):
        self._execute_specialist_logic(AI_ANALYZER_GENERIC_CLASS, "Genérico (SOLID)", self.generic_path_var.get())

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
                bufsize=1 
            )
            self.log_output(f"Web API iniciado con PID: {self.api_process.pid}")
            self.api_status_var.set(f"API: Corriendo (PID: {self.api_process.pid})")
            self.btn_stop_api.config(state=tk.NORMAL)
            
            stdout_thread = threading.Thread(target=self._read_stream, args=(self.api_process.stdout, False), daemon=True)
            stderr_thread = threading.Thread(target=self._read_stream, args=(self.api_process.stderr, True), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            self.api_process.wait()
            return_code = self.api_process.returncode

            stdout_thread.join()
            stderr_thread.join()

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
        
        threading.Thread(target=self._api_stopper_logic, daemon=True).start()

    def _api_stopper_logic(self):
        try:
            self.api_process.terminate() 
            try:
                self.api_process.wait(timeout=10)
                self.log_output("Web API detenido exitosamente.", is_error=False)
            except subprocess.TimeoutExpired:
                 self.log_output("El API no terminó de forma suave. Matándolo forzosamente.", is_error=True)
                 self.api_process.kill()
                 self.api_process.wait()
        
        except Exception as e:
            self.log_output(f"ERROR al detener el API: {e}", is_error=True)

        finally:
            self.api_status_var.set("API: Detenido")
            self.btn_start_api.config(state=tk.NORMAL)

    def on_closing(self):
        """Se asegura de que el API se detenga al cerrar la ventana principal."""
        
        # Cerrar también la ventana flotante
        if self.console_window:
            self.console_window.destroy()
            
        if self.api_process and self.api_process.poll() is None:
            if messagebox.askyesno("Salir", "El Web API está corriendo. ¿Desea detenerlo y cerrar la aplicación?"):
                threading.Thread(target=self._stop_and_close, daemon=True).start()
            return
        self.destroy()

    def _stop_and_close(self):
        """Detiene el API y cierra la aplicación."""
        self.stop_api()
        time.sleep(1) 
        self.destroy()

if __name__ == "__main__":
    app = OrchestratorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    