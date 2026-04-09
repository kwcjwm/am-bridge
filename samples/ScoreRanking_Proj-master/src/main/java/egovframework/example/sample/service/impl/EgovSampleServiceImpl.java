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
package egovframework.example.sample.service.impl;

import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import egovframework.example.sample.service.EgovSampleService;
import egovframework.example.sample.service.SampleDefaultVO;
import egovframework.example.sample.service.SampleVO;
import egovframework.rte.fdl.cmmn.EgovAbstractServiceImpl;
import egovframework.rte.fdl.idgnr.EgovIdGnrService;

/**
 * @Class Name : EgovSampleServiceImpl.java
 * @Description : Sample Business Implement Class
 * @Modification Information
 * @ @ 수정일 수정자 수정내용 @ --------- --------- ------------------------------- @
 *   2009.03.16 최초생성
 *
 * @author 개발프레임웍크 실행환경 개발팀
 * @since 2009. 03.16
 * @version 1.0
 * @see
 *
 * 		Copyright (C) by MOPAS All right reserved.
 */

@Service("sampleService")
public class EgovSampleServiceImpl extends EgovAbstractServiceImpl implements EgovSampleService {

	private static final Logger LOGGER = LoggerFactory.getLogger(EgovSampleServiceImpl.class);

	/** SampleDAO */
	// TODO ibatis 사용
	@Resource(name = "sampleDAO")
	private SampleDAO sampleDAO;
	
	// TODO mybatis 사용
	// @Resource(name="sampleMapper")
	// private SampleMapper sampleDAO;

	/** ID Generation */
	@Resource(name = "egovIdGnrService")
	private EgovIdGnrService egovIdGnrService;
	
	/*국어 만점자*/
	public List<?> korscholar(Map<String, String> hashmap) throws Exception {
		return sampleDAO.korscholar(hashmap);
	}
	
	/*영어 만점자*/
	public List<?> engscholar(Map<String, String> hashmap) throws Exception {
		return sampleDAO.engscholar(hashmap);
	}
	
	/*수학만점자*/
	public List<?> mathscholar(Map<String, String> hashmap) throws Exception {
		return sampleDAO.mathscholar(hashmap);
	}
	
	/** 2019 디와이정보기술 성적 조회 코드*/
	@Override
	public List<?> ScoreChk(Map<String, String> hashmap) throws Exception {
		return sampleDAO.ScoreChk(hashmap);
	}
	
	@Override
	public List<?> testNameList(SampleDefaultVO searchVO) throws Exception {
		return sampleDAO.testNameList(searchVO);
	}
	
	@Override
	public List<?> subteacher(Map<String, String> hashmap) throws Exception {
		return sampleDAO.subteacher(hashmap);
	}


}
