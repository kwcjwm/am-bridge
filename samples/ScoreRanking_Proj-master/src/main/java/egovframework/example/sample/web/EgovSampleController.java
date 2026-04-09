/*
 * Copyright 2008-2009 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package egovframework.example.sample.web;

import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

import egovframework.example.sample.service.EgovSampleService;
import egovframework.example.sample.service.SampleDefaultVO;
import egovframework.rte.cmmn.ria.support.UdDTO;
import egovframework.rte.fdl.property.EgovPropertyService;



@Controller
public class EgovSampleController {

	@Resource(name = "sampleService")
	private EgovSampleService sampleService;

	/** EgovPropertyService */
	@Resource(name = "propertiesService")
	protected EgovPropertyService propertiesService;

	
	/*국어 만점자 */
	@RequestMapping(value = "/miplatform/korscholar.do")
	public ModelAndView korscholar(UdDTO midto) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			Map<String, String> hashmap=midto.getVariableList();
			List<?> sampleList = sampleService.korscholar(hashmap);
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}
	
	
	/*수학 만점자 */
	@RequestMapping(value = "/miplatform/mathscholar.do")
	public ModelAndView mathscholar(UdDTO midto) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			Map<String, String> hashmap=midto.getVariableList();
			List<?> sampleList = sampleService.mathscholar(hashmap);
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}
	
	/*영어 만점자*/
	@RequestMapping(value = "/miplatform/engscholar.do")
	public ModelAndView engscholar(UdDTO midto) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			Map<String, String> hashmap=midto.getVariableList();
			List<?> sampleList = sampleService.engscholar(hashmap);
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}
	
	/**
	 * 2019년 과목별 담당교수 조회 코드
	 */
	@RequestMapping(value = "/miplatform/subteacher.do")
	public ModelAndView subteacher(UdDTO midto) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			Map<String, String> hashmap=midto.getVariableList();
			List<?> sampleList = sampleService.subteacher(hashmap);
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}
	
	
	/**
	 * 2019년 성적조회 코드 
	 */
	
	@RequestMapping(value = "/miplatform/testScoreChk.do")
	public ModelAndView selectScoreList(UdDTO midto) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			Map<String, String> hashmap=midto.getVariableList();
			List<?> sampleList = sampleService.ScoreChk(hashmap);
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}
	
	//시험 종류 불러오는 코드( 콤보박스 연동)
	@RequestMapping(value = "/miplatform/testNameList.do")
	public ModelAndView selectTestList(@ModelAttribute("searchVO") SampleDefaultVO udDtoVO) throws Exception {

		ModelAndView mav = new ModelAndView("miplatformViewByMap");

		try {
			List sampleList = sampleService.testNameList(udDtoVO);
			
			System.out.println("프로젝트 List 레코드 카운드는 ==========> " + sampleList.size());

			mav.addObject("MiResultCode", "0");
			mav.addObject("MiResultMsg", "success");
			mav.addObject("MiDTO", sampleList);

		} catch (Exception e) {
			e.printStackTrace();
			mav.addObject("MiResultCode", "-1");
			mav.addObject("MiResultMsg", e.toString());
		}
		return mav;
	}

}
