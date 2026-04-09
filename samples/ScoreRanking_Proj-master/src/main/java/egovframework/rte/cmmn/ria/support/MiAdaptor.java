package egovframework.rte.cmmn.ria.support;

import java.io.IOException;

import javax.servlet.http.HttpServletRequest;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.tobesoft.platform.PlatformRequest;

public abstract class MiAdaptor implements UiAdaptor {

	protected Log log = LogFactory.getLog(this.getClass());

	public Object convert(HttpServletRequest request) throws Exception {

		PlatformRequest platformRequest = null;

		try {
			platformRequest = new PlatformRequest(request, PlatformRequest.CHARSET_UTF8);
			platformRequest.receiveData();
		} catch (IOException ex) {
			ex.getStackTrace();
			// throw new IOException("PlatformRequest error");
		}

		/*
		 * TODO platformRequest 에서 VariableList 와 DatasetList 를 뽑아 결정된 Map
		 * 형태(example : ModelMap) 의 객체에 담아 Request 에 다시 담고 return true 로 넘긴다.
		 */

		//CategoryVO dto = converte4In(platformRequest);
		
		//Class dto = Class.forName("egovframework.rte.fdl.sale.service.CategoryVO");
		Object dto = converte4In(platformRequest, request);

		//request.setAttribute("CategoryVO", dto);


		return dto;
	}

	public abstract Object converte4In(PlatformRequest platformRequest, HttpServletRequest request);

	//public abstract void setCurrentVO(VOInfo4Mi info);
	
	public abstract Class getModelName();
	
	
}
