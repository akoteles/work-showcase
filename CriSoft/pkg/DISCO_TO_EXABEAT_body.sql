CREATE OR REPLACE PACKAGE BODY SOURCE_B.SOURCE_A_TO_DATA_WAREHOUSE
AS
   gv_location       VARCHAR2 (100);
   gv_procedure      VARCHAR2 (100);

    PROCEDURE LOAD_DW_TRANS_B_P_RO
    AS
    BEGIN
         gv_procedure := '[SOURCE_B].SOURCE_A_TO_DATA_WAREHOUSE.LOAD_DW_TRANS_B_P_RO';
         gv_location  := null;

         source_b.prc_log (gv_procedure, gv_location,'Proccesing START');

         source_b.prc_log (gv_procedure, gv_location,'Truncate table: [SOURCE_B].DW_TRANS_B_P_RO');

         EXECUTE IMMEDIATE 'TRUNCATE TABLE SOURCE_B.DW_TRANS_B_P_RO';

         source_b.prc_log (gv_procedure, gv_location,'Insert START: [SOURCE_B].DW_TRANS_B_P_RO');

         INSERT /*+ append */
              INTO  SOURCE_B.DW_TRANS_B_P_RO
           SELECT PointCode,
                  UniDirectional,
                  InstallationDate,
                  RemovalDate,
                  LimitedPower,
                  ProfiledAvailablePower,
                  ProfiledLimitedPower,
                  TitularProductionPower,
                  AvailablePower,
                  ContractualPower,
                  PowerAllowance,
                  WithdrawalDirection,
                  InsertionDirection,
                  ObisProfileID,
                  TechMeasuresMngt,
                  ProfiledManufacturer,
                  PowerReductionPercentage,
                  SupplyStatus,
                  Seasonal,
                  TimeTreatmentType,
                  IdMeter,
                  SerialNumber,
                  Manufacturer,
                  Model,
                  IdReactiveMeter,
                  ReactiveSerialNumber,
                  ReactiveManufacter,
                  ReactiveModel,
                  IdPowerMeter,
                  PowerSerialNumber,
                  PowerManufacter,
                  PowerModel,
                  EnergyConstant,
                  PowerConstant,
                  ReactiveEnergyConstant,
                  LoadCurvesInternalConstant,
                  LoadCurvesConstant,
                  RegisterInternalConstant,
                  RegisterConstant,
                  ActiveEnergyNumberOfDigit,
                  PowerNumberOfDigit,
                  ReactiveEnergyNumberOfDigit,
                  MeasurementPointType,
                  SupplyVoltage,
                  UnbundlingMigrationDate,
                  ForfaitSupply,
                  TariffType,
                  StreetLightPoint,
                  District,
                  PowerMeasurementType,
                  GeographicalRangeShortDescr,
                  GeographicalRangeDescription,
                  GeographicalRangeCode,
                  SunshineBandShortDescription,
                  SunshineBandDescription,
                  ProductionPlantType,
                  MarketType,
                  OrganizationUnitCode,
                  Parity,
                  IntakeProfile,
                  WithdrawalProfile,
                  SupplyVoltageLevel,
                  DistributionCompanyCode,
                  MeterType,
                  CustomerPoint,
                  NeuronID,
                  CurrentConstant,
                  PowerConstant1,
                  EnergyConstant1,
                  VoltageConstant,
                  CurrentAdapterRatio1,
                  CurrentAdapterRatio2,
                  VoltageAdapterRatio1,
                  VoltageAdapterRatio2,
                  NetworkPointCode,
                  GridTelemetry,
                  ConnectionCode,
                  OrganizationUnitDescription,
                  DistributionCompany,
                  GeographicalAreaDescription,
                  CodeUpSapr,
                  PodM1,
                  IdConfigFasce,
                  SupportDailyClosure,
                  Commissioned,
                  ReadingRoute,
                  Losses,
                  FlagErc,
                  FlagConventional,
                  Regime,
                  OmepaCode,
                  ClientType,
                  VATNumberDistributionCompany,
                  VATNumberTrader,
                  ContractCode,
                  CFTCode,
                  DirectionCode,
                  ZoneCode,
                  UoCode,
                  CustomerDenomination,
                  StartDate,
                  EndDate,
                  ExtractionDate,
                  TimeZone
             FROM (WITH one_to_one
                        AS (SELECT /*+ parallel(8) result_cache */
                                  g.id AS group_id,
                                   g.group_link,
                                   c.id AS meter_id,
                                   c.installation_date,
                                   cf.id AS supply_contract_id,
                                   cf.contract_nr,
                                   cf.contract_date,
                                   cf.hierarchy_unit_code,
                                   cf.approved_power,
                                   cf.valid_from,
                                   cf.valid_to,
                                   t1.id AS third_party_id_distrib,
                                   t1.name AS name_distrib,
                                   t1.county AS county_distrib,
                                   t1.locality AS locality_distrib,
                                   t2.id AS third_party_id_client,
                                   t2.name AS name_client,
                                   t2.county AS county_client,
                                   t2.locality AS locality_client,
                                   pcg.consumption_profile_code
                              FROM SOURCE_B.SUPPLY_CONTRACTS cf
                                   INNER JOIN SOURCE_B.CONSUMPTION_POINTS lc
                                      ON cf.id = lc.SUPPLY_CONTRACT_ID
                                   INNER JOIN SOURCE_B.MEASUREMENT_GROUPS G
                                      ON cf.id = g.SUPPLY_CONTRACT_ID
                                   INNER JOIN SOURCE_B.METERS C ON g.id = c.measurement_group_id
                                   INNER JOIN SOURCE_B.THIRD_PARTIES t1 ON cf.third_party_id = t1.id
                                   INNER JOIN SOURCE_B.THIRD_PARTIES t2 ON lc.third_party_id = t2.id
                                   FULL OUTER JOIN SOURCE_B.CONSUMPTION_PROFILES_GROUPS pcg
                                      ON g.group_link = pcg.group_link)
                   SELECT DISTINCT /*+ Parallel(16) */
                          o1.group_id,
                          o1.supply_contract_id,
                          o1.contract_nr,
                          o1.contract_date,
                          o1.hierarchy_unit_code,
                          o1.third_party_id_distrib,
                          o1.name_distrib,
                          o1.county_distrib,
                          o1.locality_distrib,
                          o1.third_party_id_client,
                          o1.county_client,
                          o1.locality_client,
                          cer.connection_permit_type_code,
                          cer.description,
                          '********************************' AS delimiter,
                          o1.group_link AS PointCode,
                          CASE WHEN cer.phase_type LIKE '%MONO%' THEN 1 ELSE 0 END
                             AS UniDirectional,
                          o1.installation_date AS InstallationDate,
                          CASE
                             WHEN dcc.retired_meter_id > 0 THEN dcc.retirement_date
                             ELSE NULL
                          END
                             AS RemovalDate,
                          CASE WHEN cer.absorbed_power > 100 THEN 1 ELSE 0 END
                             AS LimitedPower,
                          cer.absorbed_power AS ProfiledAvailablePower,
                          cer.evacuation_power AS ProfiledLimitedPower,
                          cer.production_power AS TitularProductionPower,
                          cer.power AS AvailablePower,
                          o1.approved_power AS ContractualPower,
                          NULL AS PowerAllowance,
                          NULL AS WithdrawalDirection,
                          NULL AS InsertionDirection,
                          o1.consumption_profile_code AS ObisProfileID,
                          NULL AS TechMeasuresMngt,
                          NULL AS ProfiledManufacturer,
                          NULL AS PowerReductionPercentage,
                          NULL AS SupplyStatus,
                          NULL AS Seasonal,
                          NULL AS TimeTreatmentType,
                          o1.meter_id AS IdMeter,
                          dcc.serial_number AS SerialNumber,
                          dcc.brand AS Manufacturer,
                          dcc.description AS Model,
                          NULL AS IdReactiveMeter,
                          NULL AS ReactiveSerialNumber,
                          NULL AS ReactiveManufacter,
                          NULL AS ReactiveModel,
                          NULL AS IdPowerMeter,
                          NULL AS PowerSerialNumber,
                          NULL AS PowerManufacter,
                          NULL AS PowerModel,
                          NULL AS EnergyConstant,
                          dcc.power_constant AS PowerConstant,
                          NULL AS ReactiveEnergyConstant,
                          NULL AS LoadCurvesInternalConstant,
                          NULL AS LoadCurvesConstant,
                          NULL AS RegisterInternalConstant,
                          NULL AS RegisterConstant,
                          NULL AS ActiveEnergyNumberOfDigit,
                          NULL AS ReactiveEnergyNumberOfDigit,
                          NULL AS PowerNumberOfDigit,
                          NULL AS MeasurementPointType,
                          NULL AS SupplyVoltage,
                          NULL AS UnbundlingMigrationDate,
                          NULL AS ForfaitSupply,
                          NULL AS TariffType,
                          NULL AS StreetLightPoint,
                          NULL AS District,
                          NULL AS PowerMeasurementType,
                          NULL AS GeographicalRangeShortDescr,
                          NULL AS GeographicalRangeDescription,
                          NULL AS GeographicalRangeCode,
                          NULL AS SunshineBandShortDescription,
                          NULL AS SunshineBandDescription,
                          NULL AS ProductionPlantType,
                          NULL AS MarketType,
                          NULL AS OrganizationUnitCode,
                          NULL AS Parity,
                          NULL AS IntakeProfile,
                          NULL AS WithdrawalProfile,
                          cer.voltage_level AS SupplyVoltageLevel,
                          NULL AS DistributionCompanyCode,
                          NULL AS MeterType,
                          NULL AS CustomerPoint,
                          NULL AS NeuronID,
                          NULL AS CurrentConstant,
                          NULL AS EnergyConstant1,
                          NULL AS PowerConstant1,
                          NULL AS VoltageConstant,
                          NULL AS CurrentAdapterRatio1,
                          NULL AS CurrentAdapterRatio2,
                          NULL AS VoltageAdapterRatio1,
                          NULL AS VoltageAdapterRatio2,
                          NULL AS NetworkPointCode,
                          NULL AS GridTelemetry,
                          NULL AS ConnectionCode,
                          NULL AS OrganizationUnitDescription,
                          NULL AS DistributionCompany,
                          NULL AS NumericalCode,
                          NULL AS GeographicalAreaDescription,
                          NULL AS CodeUpSapr,
                          NULL AS PodM1,
                          NULL AS IdConfigFasce,
                          NULL AS SupportDailyClosure,
                          NULL AS Commissioned,
                          NULL AS ReadingRoute,
                          NULL AS Losses,
                          NULL AS FlagErc,
                          NULL AS FlagConventional,
                          NULL AS Regime,
                          NULL AS OmepaCode,
                          NULL AS ClientType,
                          NULL AS VATNumberDistributionCompany,
                          NULL AS VATNumberTrader,
                          o1.contract_nr AS ContractCode,
                          NULL AS CFTCode,
                          NULL AS DirectionCode,
                          NULL AS ZoneCode,
                          NULL AS UoCode,
                          o1.name_client AS CustomerDenomination,
                          o1.valid_from AS StartDate,
                          o1.valid_to AS EndDate,
                          SYSDATE AS ExtractionDate,
                          'UTC ' || SESSIONTIMEZONE AS TimeZone
                     FROM one_to_one o1
                          LEFT OUTER JOIN
                          (SELECT c.measurement_group_id,
                                  c.id AS meter_id,
                                  NVL (cc.retired_meter_id, 0) retired_meter_id,
                                  NVL (cc.retirement_date, NULL) retirement_date,
                                  c.serial_number,
                                  c.brand,
                                  tc.description,
                                  tc.notes,
                                  tc.constant AS power_constant
                             FROM SOURCE_B.METERS c
                                  INNER JOIN SOURCE_B.METER_TYPES tc
                                     ON c.meter_type_code = tc.code
                                  LEFT OUTER JOIN
                                  (SELECT cc.meter_id AS retired_meter_id, dcc.retirement_date
                                     FROM SOURCE_B.RETIRED_METERS cc
                                          INNER JOIN SOURCE_B.RETIREMENT_DOCUMENTS dcc
                                             ON cc.retirement_doc_id = dcc.id
                                    WHERE dcc.validated = 'D') cc
                                     ON c.id = cc.retired_meter_id) dcc
                             ON o1.meter_id = dcc.meter_id
                          LEFT OUTER JOIN
                          (SELECT DISTINCT
                                  gm.id,
                                  gm.group_link,
                                  cer.absorbed_power,
                                  CASE
                                     WHEN cer.phase_type LIKE 'M%' THEN 'MONOPHASE'
                                     WHEN cer.phase_type LIKE 'T%' THEN 'TRIPHASE'
                                     ELSE NULL
                                  END
                                     AS phase_type,
                                  CASE
                                     WHEN cer.voltage_level_code = 'IT' THEN 'AA'
                                     WHEN cer.voltage_level_code = 'MT' THEN 'MT'
                                     WHEN cer.voltage_level_code = 'JT' THEN 'BT'
                                     WHEN cer.voltage_level_code = 'HT' THEN 'HT'
                                     ELSE cer.voltage_level_code
                                  END
                                     AS voltage_level,
                                  cer.evacuation_power,
                                  ar.connection_permit_type_code,
                                  ar.description,
                                  ar.power,
                                  ar.production_power
                             FROM SOURCE_B.MEASUREMENT_GROUPS gm,
                                  SOURCE_B.CONNECTION_CERTIFICATES cer
                                  LEFT OUTER JOIN
                                  (SELECT DISTINCT TO_CHAR (ar.permit_nr) permit_nr,
                                                   ar.id,
                                                   ar.connection_permit_type_code,
                                                   tar.description,
                                                   ar.power,
                                                   ar.production_power
                                     FROM CONNECTION_PERMITS ar
                                          INNER JOIN CONNECTION_PERMIT_TYPES tar
                                             ON ar.connection_permit_type_code = tar.code) ar
                                     ON TO_CHAR (cer.permit_ref_nr) = ar.permit_nr
                            WHERE     gm.group_link = cer.group_link
                                  AND cer.finalized = 'D'
                                  AND cer.cancelled = 'N') cer
                             ON (    cer.id = o1.group_id
                                 AND cer.group_link = o1.group_link));

              source_b.prc_log (gv_procedure, gv_location,'No of rows: '|| SQL%ROWCOUNT);

              COMMIT;

              source_b.prc_log (gv_procedure, gv_location,'Gather stats for: [SOURCE_B].DW_TRANS_B_P_RO');

              dbms_stats.gather_table_stats( ownname => 'SOURCE_B',
                                                 tabname => 'DW_TRANS_B_P_RO' );

              source_b.prc_log (gv_procedure, gv_location,'Proccesing STOP');

    EXCEPTION
       WHEN OTHERS
       THEN
          source_b.prc_log (gv_procedure, gv_location, SQLERRM, 'Y');

    END LOAD_DW_TRANS_B_P_RO;

END SOURCE_A_TO_DATA_WAREHOUSE;
/