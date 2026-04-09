package egovframework.rte.cmmn.ria.support;

import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.web.servlet.view.AbstractView;

import com.tobesoft.platform.PlatformConstants;
import com.tobesoft.platform.PlatformResponse;
import com.tobesoft.platform.data.ColumnInfo;
import com.tobesoft.platform.data.Dataset;
import com.tobesoft.platform.data.DatasetList;
import com.tobesoft.platform.data.PlatformData;
import com.tobesoft.platform.data.VariableList;

import egovframework.example.sample.service.SampleDefaultVO;

//import egovframework.rte.cmmn.SampleDefaultVO;

public class MiPlatformViewByVO extends AbstractView {

	protected Log log = LogFactory.getLog(this.getClass());
	
	protected VariableList miVariableList = new VariableList();
	protected DatasetList miDatasetList = new DatasetList();

	@SuppressWarnings("unchecked")
	@Override
	protected void renderMergedOutputModel(Map model, HttpServletRequest request, HttpServletResponse response)
	        throws Exception {
		
		PlatformData platformData = new PlatformData(miVariableList, miDatasetList);
		
		this.setMiResultMessage((String)model.get("MiResultCode"), (String)model.get("MiResultMsg"));

		Object vo = model.get("MiDTO");
		
		// 리턴할 데이타 셋이 있으면... 컨트롤러에서 mav.addObject("MiDTO", ....); 형태로 추가해주삼
		if ( vo != null )
		{
		
			Class cls = vo.getClass();
			
			Field[] field = cls.getDeclaredFields();
			
			Dataset dataset = new Dataset("ds_output");
			
			for ( int i = 0; i < field.length; i ++ )
			{
				if ( !"serialVersionUID".equals(field[i].getName()) ) 
					dataset.addColumn(field[i].getName(), ColumnInfo.COLUMN_TYPE_STRING, (short) 255);
			}
			
			int row = dataset.appendRow();
			for ( int i = 0; i < field.length; i ++ )
			{
				if ( !"serialVersionUID".equals(field[i].getName()) )
				{
					String memberName = field[i].getName();
					String methodeName = "get" + memberName.substring(0, 1).toUpperCase() + memberName.substring(1, memberName.length());  
					Method m = cls.getMethod(methodeName, null);
					String ret = (String)m.invoke(vo, null);
					
					dataset.setColumn(row, memberName, ret);
				}
			}
	
			miDatasetList.add(dataset);
		}

		try {

			new PlatformResponse(response, PlatformConstants.CHARSET_UTF8).sendData(platformData);

		} catch (IOException ex) {
			if (log.isErrorEnabled()) {
				log.error("Exception occurred while writing xml to MiPlatform Stream.", ex);
			}

			throw new Exception();
		}

	}
	
	public void setMiResultMessage(String code, String Msg)
	{
		miVariableList.add("ErrorCode", code);
		miVariableList.add("ErrorMsg", Msg);
	}

}
