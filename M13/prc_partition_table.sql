CREATE OR REPLACE PROCEDURE `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  source_dataset STRING,
  source_table_name STRING,
  target_dataset STRING,
  target_table_name STRING,
  cluster_columns ARRAY<STRING>,
  partition_columns ARRAY<STRING>
)
BEGIN
  DECLARE ddl_statement STRING;
  DECLARE create_statement STRING;
  DECLARE cluster_clause STRING DEFAULT '';
  DECLARE partition_clause STRING DEFAULT '';
  DECLARE order_by_clause STRING DEFAULT '';
  DECLARE insert_query STRING;
  DECLARE source_full_name STRING;
  DECLARE target_full_name STRING;
  DECLARE snapshot_name STRING;
  DECLARE snapshot_timestamp STRING;
  DECLARE partition_col_type STRING;

  SET source_full_name = CONCAT('`', source_dataset, '.', source_table_name, '`');
  SET target_full_name = CONCAT('`', target_dataset, '.', target_table_name, '`');
  SET snapshot_timestamp = FORMAT_TIMESTAMP('%Y-%m-%dT%H_%M_%S', CURRENT_TIMESTAMP());
  SET snapshot_name = CONCAT(source_dataset, '.', source_table_name, '-', snapshot_timestamp);

  -- Step 0: Create snapshot
  SELECT CONCAT('-- Step 0: Creating snapshot ', snapshot_name);
  
  EXECUTE IMMEDIATE CONCAT(
    'CREATE SNAPSHOT TABLE `', snapshot_name, '` CLONE ', source_full_name
  );
  
  SELECT CONCAT('-- Step 0: Snapshot created successfully: ', snapshot_name);


  SELECT CONCAT('-- Step A: Fetching DDL for ', source_full_name);
  
  EXECUTE IMMEDIATE FORMAT("""
    SELECT ddl 
    FROM `%s.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = '%s'
  """, source_dataset, source_table_name) INTO ddl_statement;
  
  SELECT '-- Step A: DDL fetched successfully';

  SELECT '-- Step B: Creating target table with optimizations';
  
  SET create_statement = REGEXP_REPLACE(
    ddl_statement, 
    CONCAT('CREATE TABLE `.*?`'),
    CONCAT('CREATE TABLE ', target_full_name)
  );

  IF ARRAY_LENGTH(partition_columns) > 0 THEN
    -- Get partition column data type
    EXECUTE IMMEDIATE FORMAT("""
      SELECT data_type
      FROM `%s.INFORMATION_SCHEMA.COLUMNS`
      WHERE table_name = '%s' AND column_name = '%s'
    """, source_dataset, source_table_name, partition_columns[OFFSET(0)]) 
    INTO partition_col_type;

    -- Build partition clause based on data type
    CASE partition_col_type
      WHEN 'DATE' THEN
        SET partition_clause = CONCAT('\nPARTITION BY ', partition_columns[OFFSET(0)]);
      WHEN 'TIMESTAMP' THEN
        SET partition_clause = CONCAT('\nPARTITION BY DATE(', partition_columns[OFFSET(0)], ')');
      WHEN 'DATETIME' THEN
        SET partition_clause = CONCAT('\nPARTITION BY DATE(', partition_columns[OFFSET(0)], ')');
      WHEN 'INT64' THEN
        SET partition_clause = CONCAT('\nPARTITION BY RANGE_BUCKET(', partition_columns[OFFSET(0)], 
                                      ', GENERATE_ARRAY(0, 100000, 1000))');
      ELSE
        SELECT ERROR(CONCAT('Unsupported partition column type: ', partition_col_type));
    END CASE;
  END IF;

  IF ARRAY_LENGTH(cluster_columns) > 0 THEN
    SET cluster_clause = CONCAT('\nCLUSTER BY ', ARRAY_TO_STRING(cluster_columns, ', '));
  END IF;

  SET create_statement = REGEXP_REPLACE(create_statement, r'\s*OPTIONS\s*\([^)]*\)\s*;?\s*$', '');
  SET create_statement = REGEXP_REPLACE(create_statement, r'\s*;?\s*$', '');
  SET create_statement = CONCAT(create_statement, partition_clause, cluster_clause, ';');

  EXECUTE IMMEDIATE create_statement;
  
  SELECT CONCAT('-- Step B: Target table ', target_full_name, ' created successfully');

  SELECT '-- Step C: Copying data from source to target';

  IF ARRAY_LENGTH(cluster_columns) > 0 THEN
    SET order_by_clause = CONCAT('ORDER BY ', ARRAY_TO_STRING(cluster_columns, ', '));
  ELSEIF ARRAY_LENGTH(partition_columns) > 0 THEN
    SET order_by_clause = CONCAT('ORDER BY ', ARRAY_TO_STRING(partition_columns, ', '));
  END IF;

  SET insert_query = FORMAT("""
    INSERT INTO %s
    SELECT * FROM %s
    %s
  """, target_full_name, source_full_name, order_by_clause);

  EXECUTE IMMEDIATE insert_query;

  SELECT CONCAT('-- Step C: Data copied successfully. Process complete for ', target_full_name);

END;