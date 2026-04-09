//New Script File


function fnSetVoInfo(objFrm, strVoClass)
{
	objFrm.ds_voInfo.clearData();
	var row = objFrm.ds_voInfo.addrow();
	objFrm.ds_voInfo.setcolumn(row, "voClass", strVoClass);
}


function fnCmTr(objFrm, svcid, strController, strVoClass, inputDs, outputDs, params, callbackFnc)
{

	fnSetVoInfo(objFrm, strVoClass);

	//strParam = "voClass='egovframework.rte.sample.service.SampleVO'";
	
	transaction(svcid, 
				"svc::" + strController, 
				"ds_voInfo=ds_voInfo " + inputDs, 
				outputDs,
				params,
				"fnCallback");
}