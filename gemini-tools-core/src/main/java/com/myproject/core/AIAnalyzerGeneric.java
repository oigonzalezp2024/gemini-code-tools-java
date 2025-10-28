package com.myproject.core;

/**
 * Analizador Genérico (por ejemplo, para principios SOLID).
 */
public class AIAnalyzerGeneric extends Especialista {

    public AIAnalyzerGeneric(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Analizador Genérico (SOLID)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerGeneric <archivo_contexto> <archivo_destino>");
            System.exit(1);
            return;
        }

        try {
            new AIAnalyzerGeneric(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerGeneric.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}