CREATE OR REPLACE PROCEDURE prc_load_dim_country()
BEGIN
  DECLARE current_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP();

  CREATE TEMP TABLE changed_records AS
  SELECT
    stg.country_code,
    stg.country_name,
    stg.continent,
    stg.last_update,
    dim.country_id,
    dim.scd_version_no
  FROM `dw_schema.STG_COUNTRY` stg
  LEFT JOIN `dw_schema.DIM_COUNTRY` dim
  ON stg.country_code = dim.country_code
  WHERE dim.scd_current_flag = TRUE
    AND (
      stg.country_name != dim.country_name
      OR stg.continent != dim.continent
    );

  UPDATE `dw_schema.DIM_COUNTRY`
  SET scd_end_date = current_timestamp,
      scd_current_flag = FALSE,
      etl_update_date = current_timestamp
  WHERE country_code IN (SELECT country_code FROM changed_records)
    AND scd_current_flag = TRUE;

  INSERT INTO `dw_schema.DIM_COUNTRY` (
    country_id,
    country_code,
    country_name,
    continent,
    scd_current_flag,
    scd_start_date,
    scd_end_date,
    etl_insert_date,
    etl_update_date,
    scd_version_no
  )
  SELECT
    GENERATE_UUID() AS country_id,
    stg.country_code,
    stg.country_name,
    stg.continent,
    TRUE AS scd_current_flag,
    current_timestamp AS scd_start_date,
    NULL AS scd_end_date,
    current_timestamp AS etl_insert_date,
    current_timestamp AS etl_update_date,
    IFNULL(dim.scd_version_no, 0) + 1 AS scd_version_no
  FROM `dw_schema.STG_COUNTRY` stg
  LEFT JOIN `dw_schema.DIM_COUNTRY` dim
  ON stg.country_code = dim.country_code
  WHERE dim.country_code IS NULL OR dim.scd_current_flag = FALSE
    OR (
      stg.country_name != dim.country_name
      OR stg.continent != dim.continent
    );

  INSERT INTO `dw_schema.DIM_COUNTRY` (
    country_id,
    country_code,
    country_name,
    continent,
    scd_current_flag,
    scd_start_date,
    scd_end_date,
    etl_insert_date,
    etl_update_date,
    scd_version_no
  )
  SELECT
    GENERATE_UUID() AS country_id,
    stg.country_code,
    stg.country_name,
    stg.continent,
    TRUE AS scd_current_flag,
    current_timestamp AS scd_start_date,
    NULL AS scd_end_date,
    current_timestamp AS etl_insert_date,
    current_timestamp AS etl_update_date,
    1 AS scd_version_no
  FROM `dw_schema.STG_COUNTRY` stg
  LEFT JOIN `dw_schema.DIM_COUNTRY` dim
  ON stg.country_code = dim.country_code
  WHERE dim.country_code IS NULL;

END;
