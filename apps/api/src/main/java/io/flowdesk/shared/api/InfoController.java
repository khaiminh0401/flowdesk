package io.flowdesk.shared.api;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class InfoController {
    @GetMapping("/info")
    public InfoResponse info() {
        return new InfoResponse("FlowDesk", "sprint-0");
    }
}
