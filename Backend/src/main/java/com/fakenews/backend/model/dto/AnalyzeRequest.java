package com.fakenews.backend.dto;

public class AnalyzeRequest {

    private String text;

    public AnalyzeRequest() {
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }
}