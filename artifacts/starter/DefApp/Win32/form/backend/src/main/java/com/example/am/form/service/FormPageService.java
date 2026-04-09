package com.example.am.form.service;

import java.util.List;
import com.example.am.form.dto.FormPageRow;
import com.example.am.form.dto.FormPageSearchCondition;

public interface FormPageService {
    List<FormPageRow> search(FormPageSearchCondition request);
}
