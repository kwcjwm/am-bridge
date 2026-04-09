package com.example.am.form.service.impl;

import java.util.Collections;
import java.util.List;
import org.springframework.stereotype.Service;
import com.example.am.form.dto.FormPageRow;
import com.example.am.form.dto.FormPageSearchCondition;
import com.example.am.form.service.FormPageService;

@Service
public class FormPageServiceImpl implements FormPageService {

    @Override
    public List<FormPageRow> search(FormPageSearchCondition request) {
        // TODO: port legacy business logic
        // Query hint: select A.stuno as stuno,B.STUNAME as stuname, To_char(round(avg(score),0)) as avgscore, To_char(Rank() over(order by avg(score) DESC)) as rank, To_char(DENSE_RANK() OVER(order by avg(score) DESC,(select score from sco...
        return Collections.emptyList();
    }
}
