import boto3

TABLE_FIELDS_CARRY_OVER = {
    'Name',
    'Owner',
    'LastAccessTime',
    'LastAnalyzedTime',
    'Retention',
    'ViewOriginalText',
    'ViewExpandedText',
    'Parameters',
    'TableType',
    'TargetTable',
}


class GlueDescriptionUpdater:
    def __init__(self, logger, region_name) -> None:
        self.glue = boto3.client('glue', region_name=region_name)
        self.logger = logger

    def update_descriptions(self, database, table_name, table_description, column_description_mapping):
        try:
            table = self.glue.get_table(DatabaseName=database, Name=table_name)['Table']

            storage_descriptor = table['StorageDescriptor']
            storage_descriptor['Columns'] = self._get_updated_columns(storage_descriptor['Columns'], column_description_mapping)

            updated_table = {
                **{key: value for key, value in table.items() if key in TABLE_FIELDS_CARRY_OVER},
                'Description': table_description,
                'StorageDescriptor': storage_descriptor,
                'PartitionKeys': self._get_updated_columns(table['PartitionKeys'], column_description_mapping)
            }

            self.glue.update_table(DatabaseName=database, TableInput=updated_table)
        except Exception as error:
            error_message = "Failed updating the descriptions for table '{}', error '{}', continuing...".format(
                table_name, error
            )
            self.logger.error(error_message)

    def _get_updated_columns(self, columns, mapping):
        return [
            {
                **column, 'Comment': mapping.get(column['Name'], "")
            } for column in columns
        ]
