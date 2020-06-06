from typing import Any, List

from public import ConfigDef

import jsonpointer


def getAppDataSources(configuration: ConfigDef, config: dict) -> List[dict]:
    def _normalize(value: Any):
        if isinstance(value, str):
            return {
                'path': value,
                'ignorePatterns': [],
                'followSymlinks': False,
            }
        elif isinstance(value, dict):
            base = {
                'path': '',
                'ignorePatterns': [],
                'followSymlinks': False,
            }
            if 'ignorePatterns' in value and isinstance(value['ignorePatterns'], str):
                value['ignorePatterns'] = [ value['ignorePatterns'] ]
            base.update(value)
            return base
        else:
            raise RuntimeError('Unable to parse value [%s]' % repr(value))

    configValue = jsonpointer.resolve_pointer(config, configuration.yamlPath)

    if isinstance(configValue, str):
        return [ _normalize(configValue) ]
    else:
        return list(map(lambda v: _normalize(v), configValue))

