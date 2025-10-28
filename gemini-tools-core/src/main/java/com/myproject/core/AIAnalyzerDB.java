package com.myproject.core;

/**
 * Analizador para el rol de Ingeniero de Bases de Datos (DBA).
 */
public class AIAnalyzerDB extends Especialista {

    public AIAnalyzerDB(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Ingeniero/Administrador de Bases de Datos (DBA)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerDB <archivo_contexto> <archivo_destino>");
            System.exit(1); 
            return;
        }

        try {
            new AIAnalyzerDB(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerDB.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}