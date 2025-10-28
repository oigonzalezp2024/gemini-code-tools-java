package com.myproject.core;

/**
 * Analizador para el rol de Ingeniero de Calidad (QA).
 */
public class AIAnalyzerQA extends Especialista {

    public AIAnalyzerQA(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Ingeniero de Calidad (QA)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerQA <archivo_contexto> <archivo_destino>");
            System.exit(1);
            return;
        }

        try {
            new AIAnalyzerQA(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerQA.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}