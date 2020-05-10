import os

from public import ConfigDef


configuration = {
    'fileHandleModulesConfiguration': ConfigDef(shortName="fileHandleModulesConfiguration", required=False, yamlPath="/global/fileHandleModules", defaultValue=[]),
    'fileSystemModulesConfiguration': ConfigDef(shortName="fileSystemModulesConfiguration", required=False, yamlPath="/global/fileSystemModules", defaultValue=[]),
    'moduleWorkersCount': ConfigDef(shortName="moduleWorkersCount", yamlPath="/global/workersCount", required=False, defaultValue=os.cpu_count()),
}