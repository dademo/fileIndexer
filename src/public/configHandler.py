from __future__ import annotations

from typing import Any, List
import os
import logging

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
        :appPath: The application path, used to be retrieved by :meth:`getAppPath`.
    '''

    def __init__(self, configPath: str, appPath = None):

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
    def load(configPath: str):
        return ConfigHandler(configPath)

    def get(self, jsonPointer: str, raiseException: bool = True) -> Any:
        '''
            Get a configuration using a json path (with module :module:`jsonpointer`, see :ref:`6901`).
            ex: my/configuration/path

            :param jsonPointer: The wanted config path.
            :param raiseException: If an exception should be raised if a configuration key have not been found.
                                   If true and an exception have been raised, will return None

            :returns: The configuration at designed path if found.
            :raises jsonpointer.JsonPointerException: A configuration have not been found or an invalid syntax.
        '''
        
        if raiseException:
            return jsonpointer.resolve_pointer(self._config, jsonPointer)
        else:
            # Handling exception
            try:
                return jsonpointer.resolve_pointer(self._config, jsonPointer)
            except jsonpointer.JsonPointerException:
                return None

    def getFileHandleModules(self) -> List[FileHandleModule]:
        return self._fileHandleModules

    def getFileSystemModules(self) -> List[FileSystemModule]:
        return self._fileSystemModules

    def getAppPath(self) -> str:
        return self._appPath