package com.mycompany.app; // Asegúrate de usar el 'groupId' de tu pom.xml

/**
 * Modelo de datos para un Perfil Técnico.
 */
public class Perfil {
    String cargo;
    String nivelRecomendado;
    String rolPrincipal;
    String herramientasClave; 
    boolean esFundamental;

    public Perfil(String cargo, String nivelRecomendado, String rolPrincipal, String herramientasClave, boolean esFundamental) {
        this.cargo = cargo;
        this.nivelRecomendado = nivelRecomendado;
        this.rolPrincipal = rolPrincipal;
        this.herramientasClave = herramientasClave;
        this.esFundamental = esFundamental;
    }
}
