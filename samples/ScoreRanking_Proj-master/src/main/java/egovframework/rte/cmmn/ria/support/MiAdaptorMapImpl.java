package egovframework.rte.cmmn.ria.support;

import javax.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.ModelAttribute;

import com.tobesoft.platform.PlatformRequest;

public class MiAdaptorMapImpl extends MiAdaptor {
	
	public Object converte4In(PlatformRequest platformRequest, HttpServletRequest request) {

		log.debug(" ============================ MiAdaptorMapImpl convert4In");
		
		UdDTO dto = new UdDTO();

		dto.setVariableListToMap(platformRequest.getVariableList());
		
		//request.setAttribute("SampleDefaultVO", dto);
		
		return dto;
	}

	public Class getModelName() {

		return (new UdDTO()).getClass();
	}
}
