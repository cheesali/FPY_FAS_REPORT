from LOGIC.query_config import query_execute_decorator


#SELECT-запрос для получение всех данных
@query_execute_decorator(fetchall=True)
def get_contract_info(start_date: str, end_date: str, lotid=0) -> str:
    lot_where = ""
    if lotid != 0 and lotid != "":
        lot_where = f"WHERE LOTID = {lotid}"
    return f"""
       WITH CONTRACT AS (
        SELECT 
            COALESCE(co.PCBID, co.SNID, 'Default Value') AS 'INDEX_ID',
            co.LOTID AS 'LOTID',
            fl.LineID AS 'LINE_ID',
            co.StepID AS 'STEP_ID',
            cl.FullLOTCode AS 'TITLE',
            css.StepName AS 'STEP_NAME',
            css.Description AS 'DESCR',
            cl.StepSequence AS 'STEPS_SEQ',
            fo.Objective AS 'OBJECTIVE',
            COUNT(CASE WHEN ctr.[Result] = 'Pass' THEN 1 END) AS 'PASS',
            COUNT(CASE WHEN ctr.[Result] = 'Fail' THEN 1 END) AS 'FAIL',
            COUNT(CASE WHEN ctr.[Result] <> 'Fail' AND ctr.[Result] <> 'Pass' THEN 1 END) AS 'OTHER',
            ROUND(CAST(SUM(CASE WHEN ctr.[Result] = 'Pass' THEN 1 ELSE 0 END) AS DECIMAL(10,2)) * 100 / COUNT(co.TestResultID), 2) AS 'FPY',
            fl.LineName AS 'LINE_NAME',
            COUNT(ctr.[Result]) AS 'COUNT_RESULT',
            co.StepDate AS 'STEP_DATE'
        FROM FAS.dbo.Ct_OperLog co
        LEFT JOIN FAS.dbo.FAS_Objective fo ON fo.LOTID = co.LOTID
        LEFT JOIN FAS.dbo.Ct_TestResult ctr ON ctr.ID = co.TestResultID
        LEFT JOIN FAS.dbo.Contract_LOT cl ON cl.ID = co.LOTID
        LEFT JOIN FAS.dbo.Ct_StepScan css ON css.ID = co.StepID
        LEFT JOIN FAS.dbo.FAS_Lines fl ON fl.LineID = co.LineID
        WHERE co.LOTID > 20000 AND co.LOTID IN (SELECT coc.LOTID FROM FAS.dbo.Ct_OperLog coc WHERE coc.LOTID > 20000 AND coc.StepDate BETWEEN '{start_date}' AND '{end_date}')
        GROUP BY co.StepID, fl.LineID, cl.FullLOTCode, co.LOTID, css.StepName, css.Description, fl.LineName, StepSequence, fo.Objective, co.StepDate, co.PCBID, co.SNID  
    ), ROW_NUM_TABLE AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY co.INDEX_ID, co.STEP_ID ORDER BY co.STEP_DATE) AS 'DUBLICAT_NUM'
        FROM CONTRACT co
    ), GROUP_TABLE AS (
        SELECT LOTID, LINE_ID, STEP_ID, TITLE, STEP_NAME, DESCR, STEPS_SEQ, OBJECTIVE,
        SUM(PASS) AS 'PASS', SUM(FAIL) AS 'FAIL', SUM(OTHER) AS 'OTHER',  SUM(COUNT_RESULT) AS 'COUNT_RESULT', LINE_NAME
        FROM ROW_NUM_TABLE
        WHERE DUBLICAT_NUM = 1 AND STEP_DATE BETWEEN '2024-10-11 08:00:00.000' AND '2024-10-11 20:00:00.000'
        GROUP BY TITLE, LOTID, LINE_ID, STEP_ID,  STEP_NAME, DESCR, STEPS_SEQ, OTHER, LINE_NAME, OBJECTIVE
    )
    SELECT * FROM GROUP_TABLE
    {lot_where}
    """
    
    
#SELECT-запрос для получение ошибок
@query_execute_decorator(fetchall=True)
def get_errors_info(start_date: str, end_date: str, lotid=0) -> list:
    lot_where = ""
    if lotid != 0 and lotid != "":
        lot_where = f"WHERE LOTID = {lotid}"
    return f"""
    WITH NON_CONTR AS(
    SELECT 
        COUNT(fec.Description) AS 'COUNT_FAIL',
        fec.Description AS 'FAIL_DESCR',
        fec.ErrorCode AS 'ERROR_CODE',
        co.LOTID as 'LOTID',
        co.StepID 'STEP_ID',
        fl.LineName AS 'LINE_NAME',
        fl.LineID AS 'LINE_ID'
    FROM FAS.dbo.Ct_OperLog co
    LEFT JOIN FAS.dbo.Ct_TestResult ctr ON ctr.ID = co.TestResultID
    LEFT JOIN FAS.dbo.FAS_ErrorCode fec ON fec.ErrorCodeID = co.ErrorCodeID
    LEFT JOIN FAS.dbo.FAS_Lines fl ON fl.LineID = co.LineID
    WHERE co.LOTID > 20000  AND co.StepDate BETWEEN '{start_date}' AND '{end_date}' AND ctr.[Result] = 'Fail'
    AND fec.ErrorCodeID NOT IN (155, 649)
    GROUP BY co.LOTID, co.StepID, fec.Description, fec.ErrorCode, fl.LineName, fl.LineID), 
    CONTR AS(
    SELECT 
        COUNT(css.Description) AS 'COUNT_FAIL',
        css.Description AS 'FAIL_DESCR',
        fec.ErrorCode AS 'ERROR_CODE',
        fgl.LOTID AS 'LOTID',
        co.StepID AS 'STEP_ID',
        fl.LineName AS 'LINE_NAME',
        fl.LineID AS 'LINE_ID'
    FROM FAS.dbo.Ct_OperLog co
    LEFT JOIN FAS.dbo.Ct_TestResult ctr ON ctr.ID = co.TestResultID
    LEFT JOIN FAS.dbo.Contract_LOT cl ON cl.ID = co.LOTID
    LEFT JOIN FAS.dbo.Ct_StepScan css ON css.ID = co.StepID
    LEFT JOIN FAS.dbo.FAS_Lines fl ON fl.LineID = co.LineID
    LEFT JOIN FAS.dbo.FAS_GS_LOTs fgl ON fgl.LOTID = co.LOTID
    LEFT JOIN FAS.dbo.FAS_ErrorCode fec ON fec.ErrorCodeID = co.ErrorCodeID
    WHERE co.LOTID < 20000 AND co.StepDate BETWEEN '{start_date}' AND '{end_date}' AND ctr.[Result] = 'Fail'
    AND fec.ErrorCodeID NOT IN (155, 649) 
    GROUP BY co.LOTID, co.StepID, css.Description, fl.LineName, fec.ErrorCode, fl.LineID,  fgl.LOTID
    )
    SELECT * FROM NON_CONTR
    UNION
    SELECT * FROM CONTR
     {lot_where}
    ORDER BY LOTID
    """


#SELECT-запрос для получение дубликатов
@query_execute_decorator(fetchall=True)
def get_dublicates(start_date: str, end_date: str, lotid=0) -> str:
    lot_where = ""
    if lotid != 0 and lotid != "":
        lot_where = f"WHERE gt.LOTID = {lotid}"
    return f"""
        WITH CONTRACT AS (
        SELECT 
            COALESCE(co.PCBID, co.SNID, 'Default Value') AS 'INDEX_ID',
            co.LOTID AS 'LOTID',
            fl.LineID AS 'LINE_ID',
            co.StepID AS 'STEP_ID',
            cl.FullLOTCode AS 'TITLE',
            css.StepName AS 'STEP_NAME',
            css.Description AS 'DESCR',
            cl.StepSequence AS 'STEPS_SEQ',
            
            COUNT(CASE WHEN ctr.[Result] = 'Pass' THEN 1 END) AS 'PASS',
            COUNT(CASE WHEN ctr.[Result] = 'Fail' THEN 1 END) AS 'FAIL',
            COUNT(CASE WHEN ctr.[Result] <> 'Fail' AND ctr.[Result] <> 'Pass' THEN 1 END) AS 'OTHER',
            ROUND(CAST(SUM(CASE WHEN ctr.[Result] = 'Pass' THEN 1 ELSE 0 END) AS DECIMAL(10,2)) * 100 / COUNT(co.TestResultID), 2) AS 'FPY',
            fl.LineName AS 'LINE_NAME',
            COUNT(ctr.[Result]) AS 'COUNT_RESULT',
            co.StepDate AS 'STEP_DATE'
        FROM FAS.dbo.Ct_OperLog co
        LEFT JOIN FAS.dbo.Ct_TestResult ctr ON ctr.ID = co.TestResultID
        LEFT JOIN FAS.dbo.Contract_LOT cl ON cl.ID = co.LOTID
        LEFT JOIN FAS.dbo.Ct_StepScan css ON css.ID = co.StepID
        LEFT JOIN FAS.dbo.FAS_Lines fl ON fl.LineID = co.LineID
        WHERE co.LOTID > 20000 AND co.LOTID IN (SELECT coc.LOTID FROM FAS.dbo.Ct_OperLog coc WHERE coc.LOTID > 20000 AND coc.StepDate BETWEEN '{start_date}' AND '{end_date}')
        GROUP BY co.StepID, fl.LineID, cl.FullLOTCode, co.LOTID, css.StepName, css.Description, fl.LineName, StepSequence, co.StepDate, co.PCBID, co.SNID  
    ), ROW_NUM_TABLE AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY co.INDEX_ID, co.STEP_ID ORDER BY co.STEP_DATE) AS 'DUBLICAT_NUM'
        FROM CONTRACT co
    ), GROUP_TABLE AS (
        SELECT LOTID, LINE_ID, STEP_ID, TITLE, STEP_NAME, DESCR, STEPS_SEQ,
        SUM(PASS) AS 'PASS', SUM(FAIL) AS 'FAIL', SUM(OTHER) AS 'OTHER',  SUM(COUNT_RESULT) AS COUNT, LINE_NAME
        FROM ROW_NUM_TABLE
        WHERE DUBLICAT_NUM > 1 AND STEP_DATE BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY TITLE, LOTID, LINE_ID, STEP_ID,  STEP_NAME, DESCR, STEPS_SEQ, OTHER, LINE_NAME, COUNT_RESULT
    )
    SELECT
    gt.LOTID,
    gt.STEP_ID,
    gt.LINE_ID,
    gt.PASS AS 'PASS_DUBL',
    gt.FAIL AS 'FAIL_DUBL'
    FROM GROUP_TABLE gt
    {lot_where}
    """

@query_execute_decorator(fetchall=True)
def get_customers():
    return f"""
    SELECT cс.ID AS 'CUSTOMERS_ID',
           cс.СustomerName AS 'CUSTOMER_NAME'
    FROM FAS.dbo.CT_Сustomers cс
    GROUP BY cс.ID, cс.СustomerName
    """

@query_execute_decorator(fetchall=True)
def get_lots():
    return f"""
    SELECT 
	cl.ID AS 'LOTID',
	cl.FullLOTCode AS 'FULL_LOTCODE',
	cl.СustomersID AS 'CUSTOMERS_ID'
FROM 
	FAS.dbo.Contract_LOT cl
GROUP BY cl.ID, cl.FullLOTCode, cl.СustomersID
    """
    
@query_execute_decorator(fetchall=True)
def get_emails():
    return f"""
    SELECT ee.ID, ee.Email
    FROM
    FAS.dbo.EP_Email ee
    WHERE
    ee.AccCtrl = 1
"""
@query_execute_decorator(fetchall=True)
def get_report_for_kns_yadro():
    return f"""
    SELECT
	cpt.LOTID AS 'LOTID',
	cl.FullLOTCode AS 'FULL_LOTCODE',
	fm.ModelName AS 'MODEL_NAME',
	fm.Commercial_Name AS 'ARTICLE',
	cl.LOTSize 'LOT_SIZE',
	COUNT(LOTID) 'RELEASE_BY_ORDER',
	cl.LOT_Shipped 'LOT_SHIPPED',
	CASE
		WHEN cl.LOT_Shipped IS NULL THEN COUNT(LOTID)
		ELSE COUNT(cpt.LOTID)-cl.LOT_Shipped
	END AS 'BALANCE_OF_GP'
FROM FAS.dbo.Ct_PackingTable cpt 
Left JOIN FAS.dbo.Contract_LOT cl ON cpt.LOTID = cl.ID
LEFT JOIN FAS.dbo.FAS_Models fm ON cl.ModelID = fm.ModelID
WHERE
	PackingDate>CAST('20:00 07.31.2022' AS SMALLDATETIME)
	AND СustomersID IN (43, 39)
GROUP BY
	cpt.LOTID,
	cl.FullLOTCode,
	cl.LOTSize,
	cl.LOT_Shipped,
	IsBlocked,
	fm.ModelName,
	fm.Commercial_Name
ORDER BY cpt.LOTID DESC"""

