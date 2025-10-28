package com.myproject.core;

/**
 * Analizador para el rol de Ingeniero DevOps (CI/CD).
 */
public class AIAnalyzerDevOps extends Especialista {

    public AIAnalyzerDevOps(String contextFilePath, String targetFilePath) throws Exception {
        super.runAnalysis(contextFilePath, targetFilePath, "Ingeniero DevOps (CI/CD)");
    }

    // ===============================================
    // 🔥 MÉTODO PRINCIPAL REQUERIDO: FIX
    // ===============================================
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: java -cp <jar> com.myproject.core.AIAnalyzerDevOps <archivo_contexto> <archivo_destino>");
            System.exit(1);
            return;
        }

        try {
            new AIAnalyzerDevOps(args[0], args[1]); 
        } catch (Exception e) {
            System.err.println("❌ ERROR: Falló la ejecución de AIAnalyzerDevOps.");
            e.printStackTrace();
            System.exit(1);
        }
    }
}