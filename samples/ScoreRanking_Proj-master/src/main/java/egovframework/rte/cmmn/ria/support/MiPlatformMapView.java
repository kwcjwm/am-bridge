package egovframework.rte.cmmn.ria.support;

import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.web.servlet.view.AbstractView;

import com.tobesoft.platform.PlatformConstants;
import com.tobesoft.platform.PlatformResponse;
import com.tobesoft.platform.data.ColumnInfo;
import com.tobesoft.platform.data.Dataset;
import com.tobesoft.platform.data.DatasetList;
import com.tobesoft.platform.data.PlatformData;
import com.tobesoft.platform.data.VariableList;

public class MiPlatformMapView extends AbstractView {

	protected Log log = LogFactory.getLog(this.getClass());

	protected VariableList miVariableList = new VariableList();
	protected DatasetList miDatasetList = new DatasetList();

	@SuppressWarnings("unchecked")
	@Override
	protected void renderMergedOutputModel(Map model, HttpServletRequest request, HttpServletResponse response)
	        throws Exception {
		System.out.println("MiPlatformMapView #######################");
		PlatformData platformData = new PlatformData(miVariableList, miDatasetList);

		if ((String) model.get("MiResultCode") != null) {
			this.setMiResultMessage((String) model.get("MiResultCode"), (String) model.get("MiResultMsg"));
		} else {
			this.setMiResultMessage("0", "sucess~~");
		}
System.out.println("render MergedOutputModel #######################");

		List list = (List) model.get("MiDTO");

		if (list != null) {
			Iterator<Map> iterator = list.iterator();
			Iterator<Map> dataIterator = list.iterator();

			Dataset dataset = new Dataset("ds_output");

			while (iterator.hasNext()) {
				// Header 세팅
				Map<String, Object> record = iterator.next();
				Iterator<String> si = record.keySet().iterator();

				while (si.hasNext()) {
					String key = si.next();
					dataset.addColumn(key, ColumnInfo.COLUMN_TYPE_STRING, (short) 255);
				}
			}

			while (dataIterator.hasNext()) {
				Map<String, Object> record = dataIterator.next();

				// Value 세팅
				int row = dataset.appendRow();
				Iterator<String> si2 = record.keySet().iterator();
				while (si2.hasNext()) {
					String key = si2.next();
					String value = (String) record.get(key);

					System.out.println("key = " + key + " , value = " + value);
					dataset.setColumn(row, key, value);
				}
				miDatasetList.add(dataset);

			}
		}

		try {

			new PlatformResponse(response, PlatformConstants.CHARSET_UTF8).sendData(platformData);

		} catch (IOException ex) {
			if (log.isErrorEnabled()) {
				log.error("Exception occurred while writing xml to MiPlatform Stream.", ex);
			}

			throw new Exception();
		}

	}

	public void setMiResultMessage(String code, String Msg) {
		miVariableList.add("ErrorCode", code);
		miVariableList.add("ErrorMsg", Msg);
	}

}
