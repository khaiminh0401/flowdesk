package io.flowdesk.shared.api;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

class InfoControllerTest {
    private MockMvc http;

    @BeforeEach
    void setUp() {
        http = MockMvcBuilders.standaloneSetup(new InfoController()).build();
    }

    @Test
    void returnsTheSprintZeroContractWithoutADatabase() throws Exception {
        http.perform(get("/api/v1/info"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(content().json("""
                        {"application":"FlowDesk","stage":"sprint-0"}
                        """, org.springframework.test.json.JsonCompareMode.STRICT));
    }

    @Test
    void infoDoesNotAcceptWrites() throws Exception {
        http.perform(post("/api/v1/info")).andExpect(status().isMethodNotAllowed());
    }
}
