package egovframework.rte.cmmn.ria.support;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

public class RiaInterceptor extends HandlerInterceptorAdapter {

	private Object[] uiDto;

	public void setUiDTO(Object[] uiDto) {
		this.uiDto = uiDto;
	}

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {

		if (this.uiDto == null)
			return true;

		for (Object ud : uiDto) {
			if (ud != null)
			{
				request.setAttribute(ud.getClass().getSimpleName(), ud);
			}
			
		}

		System.out.println("handler ===============>" + handler.toString());
		return true;
	}

	@Override
	public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler,
	                       ModelAndView modelAndView) throws Exception {

	}

}
