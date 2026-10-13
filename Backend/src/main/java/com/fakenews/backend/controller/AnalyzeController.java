package com.fakenews.backend.controller;

import com.fakenews.backend.dto.AnalyzeRequest;
import com.fakenews.backend.service.AIService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class AnalyzeController {

    private final AIService aiService;

    public AnalyzeController(AIService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/analyze")
    public String analyze(@RequestBody AnalyzeRequest request) {

        return aiService.analyzeNews(request);
    }
}