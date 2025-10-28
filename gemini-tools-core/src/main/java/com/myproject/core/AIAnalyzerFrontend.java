package com.myproject.core;

/**
 * Analizador para el rol de Desarrollador Frontend (UI/UX).
 */
public class AIAnalyzerFrontend extends Especialista {

    public AIAnalyzerFrontend(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Desarrollador Frontend (UI/UX)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerFrontend <archivo_contexto> <archivo_destino>");
            System.exit(1);
            return;
        }

        try {
            new AIAnalyzerFrontend(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerFrontend.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}