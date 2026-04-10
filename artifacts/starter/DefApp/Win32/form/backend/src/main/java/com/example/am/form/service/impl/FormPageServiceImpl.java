package com.example.am.form.service.impl;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.am.form.dto.FormPageRow;
import com.example.am.form.dto.FormPageSearchCondition;
import com.example.am.form.dto.FormPageLookupOption;
import com.example.am.form.mapper.FormPageMapper;
import com.example.am.form.service.FormPageService;

@Service
public class FormPageServiceImpl implements FormPageService {

    private final FormPageMapper mapper;

    public FormPageServiceImpl(FormPageMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public List<FormPageRow> search(FormPageSearchCondition request) {
        // Legacy controller/service/dao chain: EgovSampleController.selectScoreList -> EgovSampleServiceImpl.ScoreChk -> SampleDAO.ScoreChk
        // SQL hint: select A.stuno as stuno,B.STUNAME as stuname, To_char(round(avg(score),0)) as avgscore, To_char(Rank() over(order by avg(score) DESC)) as rank, To_char(DENSE_RANK() OVER(order by avg(score) DESC,(select score from sco...
        // Table candidates: score_jew, student_jew
        return mapper.search(request);
    }

    @Override
    public List<FormPageLookupOption> getTestCategoryOptions() {
        // Legacy SQL map: sampleDAO.testNameList
        return mapper.selectTestCategoryOptions();
    }
}
