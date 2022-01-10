package com.youtube.webapp.model;

import javax.persistence.Entity;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

@Entity
@Table(name="Video_Tags")
public class Video_Tags {
    @ManyToOne
    private int videoId;

    private String tag;

    public int getVideoId() {
        return videoId;
    }

    public void setVideoId(int videoId) {
        this.videoId = videoId;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    @Override
    public String toString() {
        return "Video_Tags{" +
                "videoId=" + videoId +
                ", tag='" + tag + '\'' +
                '}';
    }
}
