package com.youtube.webapp.model;

import javax.persistence.*;

@Entity
@Table(name="Voto")
public class Voto {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    private int usuarioId;

    @ManyToOne
    private int videoId;

    private int valor;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getUsuarioId() {
        return usuarioId;
    }

    public void setUsuarioId(int usuarioId) {
        this.usuarioId = usuarioId;
    }

    public int getVideoId() {
        return videoId;
    }

    public void setVideoId(int videoId) {
        this.videoId = videoId;
    }

    public int getValor() {
        return valor;
    }

    public void setValor(int valor) {
        this.valor = valor;
    }

    @Override
    public String toString() {
        return "Voto{" +
                "id=" + id +
                ", usuarioId=" + usuarioId +
                ", videoId=" + videoId +
                ", valor=" + valor +
                '}';
    }
}
