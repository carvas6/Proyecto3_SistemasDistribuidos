package com.youtube.webapp.model;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.List;

@Entity
@Table(name="Video")
public class Video {
    @Id
    @GeneratedValue(strategy=GenerationType.IDENTITY)
    private int id;

    @ManyToOne
    private int usuarioId;

    private float tamanyo;

    private String rutaAWS;

    private Timestamp fechaSubida;

    @OneToMany
    private List<Comentario> comentarios;

    @OneToMany
    private List<Voto> votos;

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

    public float getTamanyo() {
        return tamanyo;
    }

    public void setTamanyo(float tamanyo) {
        this.tamanyo = tamanyo;
    }

    public String getRutaAWS() {
        return rutaAWS;
    }

    public void setRutaAWS(String rutaAWS) {
        this.rutaAWS = rutaAWS;
    }

    public Timestamp getFechaSubida() {
        return fechaSubida;
    }

    public void setFechaSubida(Timestamp fechaSubida) {
        this.fechaSubida = fechaSubida;
    }

    public List<Comentario> getComentarios() {
        return comentarios;
    }

    public void setComentarios(List<Comentario> comentarios) {
        this.comentarios = comentarios;
    }

    public List<Voto> getVotos() {
        return votos;
    }

    public void setVotos(List<Voto> votos) {
        this.votos = votos;
    }

    @Override
    public String toString() {
        return "Video{" +
                "id=" + id +
                ", usuarioId=" + usuarioId +
                ", tamanyo=" + tamanyo +
                ", rutaAWS='" + rutaAWS + '\'' +
                ", fechaSubida=" + fechaSubida +
                '}';
    }
}
