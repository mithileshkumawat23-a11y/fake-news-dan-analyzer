package com.fakenews.backend.service;

import com.fakenews.backend.dto.AnalyzeRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class AIService {

    private final RestClient restClient;

    public AIService(RestClient.Builder restClientBuilder) {

        this.restClient = restClientBuilder
                .baseUrl("http://127.0.0.1:8000")
                .build();
    }

    public String analyzeNews(AnalyzeRequest request) {

        return restClient.post()
                .uri("/analyze")
                .body(request)
                .retrieve()
                .body(String.class);
    }
}