package io.flowdesk.shared.api;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class InfoController {
    @GetMapping("/info")
    public Map<String, String> info() {
        return Map.of("application", "FlowDesk", "stage", "sprint-0");
    }
}
