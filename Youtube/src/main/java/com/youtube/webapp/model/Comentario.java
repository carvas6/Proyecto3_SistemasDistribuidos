package com.youtube.webapp.model;

import javax.persistence.*;
import java.util.List;

@Entity
@Table(name="Comentario")
public class Comentario {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    private int usuarioId;

    @ManyToOne
    private int videoId;

    private String contenido;

    @ManyToOne
    private int comentarioPadreId;

    @OneToMany
    private List<Comentario> hilo;

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

    public String getContenido() {
        return contenido;
    }

    public void setContenido(String contenido) {
        this.contenido = contenido;
    }

    public int getComentarioPadreId() {
        return comentarioPadreId;
    }

    public void setComentarioPadreId(int comentarioPadreId) {
        this.comentarioPadreId = comentarioPadreId;
    }

    public List<Comentario> getHilo() {
        return hilo;
    }

    public void setHilo(List<Comentario> hilo) {
        this.hilo = hilo;
    }

    @Override
    public String toString() {
        return "Comentario{" +
                "id=" + id +
                ", usuarioId=" + usuarioId +
                ", videoId=" + videoId +
                ", contenido='" + contenido + '\'' +
                ", comentarioPadreId=" + comentarioPadreId +
                '}';
    }
}
