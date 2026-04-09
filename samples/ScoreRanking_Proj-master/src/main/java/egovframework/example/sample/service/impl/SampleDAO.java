
package egovframework.example.sample.service.impl;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import egovframework.example.sample.service.SampleDefaultVO;
import egovframework.example.sample.service.SampleVO;
import egovframework.rte.psl.dataaccess.EgovAbstractDAO;



@Repository("sampleDAO")
public class SampleDAO extends EgovAbstractDAO {
	
	/*국어 만점자 */
	public List<?> korscholar(Map<String,String> hashmap) throws Exception {
		return list("sampleDAO.korscholar", hashmap);
	}
	/*수학 만점자 */
	public List<?> mathscholar(Map<String,String> hashmap) throws Exception {
		return list("sampleDAO.mathscholar", hashmap);
	}
	/*영어 만점자*/
	public List<?> engscholar(Map<String,String> hashmap) throws Exception {
		return list("sampleDAO.engscholar", hashmap);
	}
	/**
	 *  2019 성적조회 코드
	 */
	public List<?> ScoreChk(Map<String,String> hashmap) throws Exception {
		return list("sampleDAO.ScoreChk", hashmap);
	}
	
	public List<?> testNameList(SampleDefaultVO searchVO) throws Exception {
		return list("sampleDAO.testNameList", searchVO);
	}
	
	public List<?> subteacher(Map<String,String> hashmap) throws Exception {
		return list("sampleDAO.subteacher", hashmap);
	}


}
