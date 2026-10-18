CREATE SCHEMA FDE_VIEWS;
-- only works in microsoft terminal tools
GO 


-- create the semantic view
CREATE VIEW FDE_VIEWS.VW_ACTIVATE_FLEET AS
SELECT 
    TS_UTC AS [Timestamp],
    V_LAT AS [Latitude],
    V_LON AS [Longitude],
    CAST(IOT_TEMP_VAL_C AS FLOAT) AS [Current_Temperature_C],
    CGO_COND_CD AS [Cargo_Condition_Code],
    RISK_CLS_TXT AS [Risk_Classification],
    DELAY_PROB_DEC AS [Delay_Probability],
    PRT_CNG_LVL AS [Port_Congestion_Level],
    RT_RSK_IDX AS [Route_Risk_Index]
FROM dbo.TBL_SC_FLEET_HIST_RAW;
GO

-- create a read only role for the ai agent
CREATE LOGIN USER_FDE_RO WITH PASSWORD = 'AgentPassword123';
CREATE USER USER_FDE_RO FOR LOGIN USER_FDE_RO;
GO

-- grant access to only the view and deny anothing else
GRANT SELECT ON FDE_VIEWS.VW_ACTIVATE_FLEET TO USER_FDE_RO;
DENY SELECT ON dbo.TBL_SC_FLEET_HIST_RAW TO USR_FDE_RO;
DENY INSERT, UPDATE, DELETE, ALTER ON SCHEMA::dbo TO USR_FDE_RO;
GO


