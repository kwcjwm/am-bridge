package com.example.am.form.mapper;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import com.example.am.form.dto.FormPageRow;
import com.example.am.form.dto.FormPageSearchCondition;
import com.example.am.form.dto.FormPageLookupOption;

@Mapper
public interface FormPageMapper {
    List<FormPageRow> search(FormPageSearchCondition request);
    List<FormPageLookupOption> selectTestCategoryOptions();
}
