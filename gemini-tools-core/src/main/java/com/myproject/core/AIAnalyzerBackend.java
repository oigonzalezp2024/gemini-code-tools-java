package com.myproject.core;

/**
 * Analizador para el rol de Desarrollador Backend (Spring).
 */
public class AIAnalyzerBackend extends Especialista {

    public AIAnalyzerBackend(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Desarrollador Backend (Spring)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerBackend <archivo_contexto> <archivo_destino>");
            System.exit(1);
            return;
        }

        try {
            new AIAnalyzerBackend(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerBackend.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}