package egovframework.rte.cmmn.ria.support;

import javax.servlet.http.HttpServletRequest;

import org.springframework.ui.Model;

public interface UiAdaptor {

	public Object convert(HttpServletRequest request) throws Exception;

	public Class getModelName();
}
