package egovframework.rte.cmmn.ria.support;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

import javax.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.ModelAttribute;

import sun.security.jca.GetInstance;

import com.tobesoft.platform.PlatformRequest;
import com.tobesoft.platform.data.Dataset;
import com.tobesoft.platform.data.DatasetList;
import com.tobesoft.platform.data.VariableList;

import egovframework.example.sample.service.SampleDefaultVO;
import egovframework.example.sample.service.SampleVO;

public class MiAdaptorVoImpl extends MiAdaptor {

	public Object converte4In(PlatformRequest platformRequest, HttpServletRequest request) {
		
		Object vo = null;
		
		try
		{
			DatasetList list = platformRequest.getDatasetList();
			//VariableList vl = platformRequest.getVariableList();
			//String voClass = vl.getValueAsString("voClass");
			Dataset ds_voInfo = list.get("ds_voInfo");
			String voClass = ds_voInfo.getColumnAsString(0,"voClass");
			
			Dataset ds = list.get("ds_input");
			System.out.println("voClass ==> ["+voClass+"]");
			
			Class<?> cls = Class.forName(voClass);
			vo = cls.newInstance();
						
			//Field[] field = cls.getDeclaredFields();
			
			for ( int i = 0; i < ds.getColumnCount();  i ++ )
			{
				String memberName = ds.getColumnId(i);
				String strparam = ds.getColumnAsString(0, i);
				
				String methodeName = "set" + memberName.substring(0, 1).toUpperCase() + memberName.substring(1, memberName.length());
				System.out.println("methodeName ===>"+methodeName);
				System.out.println("strparam ===>"+strparam);
				Method m = cls.getMethod(methodeName, new String().getClass());
				m.invoke(vo, strparam);
			}
			
			return vo;
			
		} catch ( Exception e)
		{
			e.printStackTrace();
		}
		
		//request.setAttribute("SampleDefaultVO", vo);
		
		return vo;
	}

	public Class getModelName() {

		return (new Object()).getClass();
	}
}
