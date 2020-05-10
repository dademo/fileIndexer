from public import ConfigDef

configuration = {
    'sqliteConfigPath'      : ConfigDef(shortName="sqliteConfigPath", required=False, yamlPath="/global/sqliteDir", defaultValue=None),
    'dbConnectionString'    : ConfigDef(shortName="dbConnectionString", required=False, yamlPath="/global/dbConnectionString", defaultValue=None),
}