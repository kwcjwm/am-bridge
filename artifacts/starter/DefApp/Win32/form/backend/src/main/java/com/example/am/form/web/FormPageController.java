package com.example.am.form.web;

import java.util.List;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.am.form.dto.FormPageRow;
import com.example.am.form.dto.FormPageSearchCondition;
import com.example.am.form.service.FormPageService;

@RestController
@RequestMapping("/api/form")
public class FormPageController {

    private final FormPageService service;

    public FormPageController(FormPageService service) {
        this.service = service;
    }

    @PostMapping("/search")
    public List<FormPageRow> search(@RequestBody FormPageSearchCondition request) {
        // Legacy URL hint: http://127.0.0.1:8080/miplatform/testScoreChk.do
        return service.search(request);
    }
}
