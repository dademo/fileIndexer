from __future__ import annotations

from typing import Any, List
import os
import logging

from public import ConfigDef
from public import ConfiguratonError

#from public import FileHandleModule, FileSystemModule

import yaml
import jsonpointer

logger = logging.getLogger('fileIndexer').getChild('public.ConfigHandler')


class ConfigHandler(object):

    '''
        An object which handle the whole application configuration.
        Enabled the user to get a configuration and to retrieve
        loaded modules (injected by the main program).

        :param configPath: The path of the configuration (we assume this path exists, instead an :class:`IOError` will be thrown).
        :type configPath: str

        :param appPath: The application path, used to be retrieved by :meth:`ConfigHandler.getAppPath`.
        :type appPath: str
    '''

    def __init__(self, configPath: str, appPath: str = None):

        logger.info('Loading configuration from file [%s]' % configPath)
        # Loading the configuration
        with open(configPath, 'r') as _configIO:
            self._config = yaml.load(_configIO, Loader=yaml.FullLoader)

        logger.info('Configuration loaded')

        self._appPath = appPath
        self._fileHandleModules = None
        self._fileSystemModules = None

        if not self._config:
            raise ConfiguratonError("Unable to load configuration at path [%s]" % configPath)

    @staticmethod
    def load(configPath: str, appPath: str = None):
        '''
            Loads the configuration from the given path and returns a configured ConfigHandler.
            Same as calling the ConfigHandler constructor.

            :param configPath: Path of the configuration to load.
            :type configPath: str
            :param appPath: The application path, used to be retrieved by :meth:`ConfigHandler.getAppPath`.
            :type appPath: str

            :returns: A configured ConfigHandler.
            :rtype: :class:`public.configHandler.ConfigHandler`
        '''
        return ConfigHandler(configPath, appPath)

    def get(self, configuration: ConfigDef) -> Any:
        '''
            Get a configuration using a json path (with module :mod:`jsonpointer`, see :rfc:`6901`).
            ex: my/configuration/path

            :param configuration: The wanted configuration.
            :type configuration: :class:`public.configDef.ConfigDef`

            :returns: The configuration at designed path if found.
            :rtype: any
            :raises jsonpointer.JsonPointerException: A configuration have not been found or an invalid syntax.
        '''
        
        if configuration.required:
            return jsonpointer.resolve_pointer(self._config, configuration.yamlPath)
        else:
            # Handling exception
            try:
                return jsonpointer.resolve_pointer(self._config, configuration.yamlPath)
            except jsonpointer.JsonPointerException:
                return configuration.defaultValue

    def getFileHandleModules(self) -> List['FileHandleModule']:
        '''
            Get all the app loaded file handle modules (injected by the main program).

            :returns: All the loaded file handle modules.
            :rtype: List[:class:`public.fileHandleModule.FileHandleModule`]
        '''
        return self._fileHandleModules

    def getFileSystemModules(self) -> List['FileSystemModule']:
        '''
            Get all the app loaded file system modules (injected by the main program).

            :returns: All the loaded file system modules.
            :rtype: List[:class:`public.fileSystemModule.FileSystemModule`]
        '''
        return self._fileSystemModules

    def getAppPath(self) -> str:
        '''
            Return the application path.

            :returns: The application path.
            :rtype: str
        '''
        return self._appPath