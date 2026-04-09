package egovframework.rte.cmmn.ria.support;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.tobesoft.platform.data.Dataset;
import com.tobesoft.platform.data.DatasetList;
import com.tobesoft.platform.data.VariableList;

public class UdDTO implements Serializable {

	private Map variableList;

	private Map dataSetList;

	private Map Objects;

	public void setVariableList(Map variableList) {
		this.variableList = variableList;
	}
	
	public void setDataSetList(Map dataSetList) {
		this.dataSetList = dataSetList;
	}
	
	public Map getVariableList() {
		return variableList;
	}

	public Map getDataSetList() {
		return dataSetList;
	}

	public void setObjects(Map objects) {
		Objects = objects;
	}

	public Map getObjects() {
		return Objects;
	}

	public void setVariableListToMap(VariableList vList) {
		
		variableList = new HashMap<String, String>();
		
		for ( int i = 0; i < vList.size(); i ++ )
		{
			variableList.put(vList.get(i).getId(), vList.get(i).getValue().getString());
		}
		
	}
	
	public void setDataSetListToMap(DatasetList dataSetList) {
		
		List list = new ArrayList<Object>();
		
		java.util.Map<String, String> hm = new HashMap<String, String>();
        
        Dataset ds_input = dataSetList.get("ds_input");
        // insert, update처리
        for ( int i = 0; i < ds_input.getRowCount(); i ++ )
        {
            if ( "update".equals(ds_input.getRowStatus(i)) )
            {
                hm = new HashMap<String, String>();
                for ( int j = 0; j < ds_input.getColumnCount(); j ++ )
                {
                    hm.put(ds_input.getColumnId(j), ds_input.getColumnAsString(i, j));
                }
                
            } else if ( "insert".equals(ds_input.getRowStatus(i)) )
            {
                hm = new HashMap<String, String>();
                for ( int j = 0; j < ds_input.getColumnCount(); j ++ )
                {
                    hm.put(ds_input.getColumnId(j), ds_input.getColumnAsString(i, j));
                }
            }
            list.add(hm);
        }
		this.dataSetList.put("ds_input", hm);

	}

}
