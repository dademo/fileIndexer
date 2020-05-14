from typing import Any

class ConfigDef(object):
    '''
        Parameter configuration definition. Give a short name and a
        configuration path to access value(s).

        Its values are :

            * shortName | configurationName
                The name of the configuration
            * yamlPath
                Path where the configuration will be found within configuration
            * defaultValue (configurational)
                Default value for this configuration
            * kwargs
                Additional values which can be later accessed

        :param shortName: Short name for the configuration (used to access
                                values using a short name).
        :type shortName: str
        :param yamlPath: Path of the configuration in the ``config.yaml`` file.
        :type yamlPath: str
        :param defaultValue: Default value for this configuration.
        :type defaultValue: str
        :param \**kwargs: Additional values.
        :type \**kwargs: Any
    '''

    @property
    def shortName(self) -> str:
        return self._shortName or ''

    @property
    def yamlPath(self) -> str:
        return self._yamlPath

    @property
    def defaultValue(self) -> Any:
        return self._defaultValue

    @property
    def required(self) -> bool:
        return self._required

    @property
    def kwargs(self) -> dict:
        return self._kwargs.copy()

    def __init__(self, shortName: str, yamlPath: str, required: bool = False, defaultValue: Any = None, onMissing: str = "Missing value for path [%s]" % yamlPath, **kwargs):

        self._shortName = shortName
        self._yamlPath = yamlPath
        self._required = required
        self._defaultValue = defaultValue
        self._kwargs = kwargs

    def __getattr__(self, name: str):
        '''
            Used to implement shortcuts (`configurationName` for example) and kwargs access.

            :param name:
            :type name: str

            :return: The expected value.
            :rtype: Any

            :raises AttributeError: Il the given key were not found
        '''
        # kwargs
        if name in self._kwargs.keys():
            return self.kwargs[name]

        # Shortcuts
        else:
            if name == 'configurationName':
                return self.shortName
            else:
                raise AttributeError('Field [%s] not found' % name)

    def __hash__(self):
        return hash((self.shortName, self.yamlPath))