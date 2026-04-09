package egovframework.rte.cmmn.ria.support.interceptor;

import java.util.Locale;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.propertyeditors.LocaleEditor;
import org.springframework.web.servlet.LocaleResolver;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;
import org.springframework.web.servlet.i18n.SessionLocaleResolver;
import org.springframework.web.servlet.support.RequestContextUtils;

public class LocaleChangeInterceptor extends HandlerInterceptorAdapter {

    /**
     * Default name of the locale specification parameter: "locale".
     */
    public static final String DEFAULT_PARAM_NAME = "locale";

    private String paramName = DEFAULT_PARAM_NAME;

    /**
     * Set the name of the parameter that contains a locale specification in a
     * locale change request. Default is "locale".
     */
    public void setParamName(String paramName) {
	this.paramName = paramName;
    }

    /**
     * Return the name of the parameter that contains a locale specification in
     * a locale change request.
     */
    public String getParamName() {
	return this.paramName;
    }

    public boolean preHandle(HttpServletRequest request,
	    HttpServletResponse response, Object handler)
	    throws ServletException {

	String newLocale = request.getParameter(this.paramName);
	System.out.println("[JuddCheck] newLocale parameter = " + newLocale);
	if (newLocale != null) {
	    System.out.println("[JuddCheck] newLocale parameter = " + newLocale);
	    LocaleResolver localeResolver = RequestContextUtils.getLocaleResolver(request);
	    if( localeResolver instanceof SessionLocaleResolver)
		System.out.println("[JuddCheck] localeResolver is  SessionLocaleResolver ");
	    if (localeResolver == null) {
		throw new IllegalStateException(
			"No LocaleResolver found: not in a DispatcherServlet request?");
	    }
	    LocaleEditor localeEditor = new LocaleEditor();
	    localeEditor.setAsText(newLocale);
	    System.out.println("[JuddCheck] localeEditor = "+((Locale) localeEditor.getValue()).getDisplayCountry());
	    
	    localeResolver.setLocale(request, response, (Locale) localeEditor
		    .getValue());
	}
	// Proceed in any case.
	return true;
    }

}