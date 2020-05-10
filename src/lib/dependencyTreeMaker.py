from typing import Iterable, List, Any
import logging
from pprint import pformat

from public import FileHandleModule
from public import DependencyException

logger = logging.getLogger('fileIndexer').getChild('lib.dependecyTreeMaker')


def buildDependencyTree(modules: Iterable[FileHandleModule]) -> List[List[FileHandleModule]]:
    '''
        Build a dependency tree between components in order to prepare an execution plan.

        It will return a list of steps, each step being a list of modules to execute.

        Required modules are declared within the
        :meth:`public.fileHandleModule.FileHandleModule.requiredModules`. Please note
        that these names can be a class name (as given by ``__class__``) or a FQDN
        module class name.


        :param modules: List of modules loaded by the application.
        :type modules: List[:class:`public.fileHandleModule.FileHandleModule`]

        :return: A list of steps consisting in a list of
                    :class:`public.fileHandleModule.FileHandleModule` to execute.
        :rtype: List[List[:class:`public.fileHandleModule.FileHandleModule`]]
    '''

    modulesToHandle = list(modules)
    steps = []
    handledModulesStr = []

    '''
        Helpers
    '''
    # https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    def _getFQDNName(o: Any) -> str:

        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__  # Avoid reporting __builtin__
        else:
            return '%s.%s' % (module, o.__class__.__name__)


    def _isFQDNName(name: str) -> bool:
        return name.rfind('.') != -1

    def _requiredModules(module: FileHandleModule) -> List[str]:

        requiredModules = module.requiredModules()
        if isinstance(requiredModules, str) or requiredModules == None:
            requiredModules = []
        return requiredModules


    def _isModuleInHandledModulesStr(moduleName: str) -> bool:

        if _isFQDNName(moduleName):
            return moduleName in handledModulesStr
        else:
            return any(map(lambda m: m.endswith(moduleName), handledModulesStr))

    def _exception():
        return DependencyException(
            "Some modules have missing dependencies :%s\nPlease edit your configuration." % (''.join(
                map(
                    lambda m: '\n\t- [%(moduleName)s] is missing [%(requiredModules)s]\n' % {
                        'moduleName': _getFQDNName(m),
                        'requiredModules': ','.join(_requiredModules(m))
                    },
                    modulesToHandle
            )))
        )
    
    '''
        Processing
    '''

    logger.debug('Building dependency tree')

    while len(modulesToHandle) > 0:

        iterationSteps = []
        iterationNotHandledSteps = []
        iterationHandledModulesStr = []
        # If a module have been handled in this iteration, used to avoid infinite loop on missing dependencies
        handled = False

        for module in modulesToHandle:

            requiredModules = _requiredModules(module)
            # If all required modules have been executed
            if all(map(lambda requiredModule: _isModuleInHandledModulesStr(requiredModule), requiredModules)):
                iterationSteps.append(module)
                iterationHandledModulesStr.append(_getFQDNName(module))
                #modulesToHandle.remove(module)
                handled = True
            else:
                iterationNotHandledSteps.append(module)

        if not handled and len(modulesToHandle) > 0:
            raise _exception()
        else:
            steps.append(iterationSteps)
            handledModulesStr.extend(iterationHandledModulesStr)
            modulesToHandle = iterationNotHandledSteps
    
    logger.info('All dependencies OK. %d steps in execution' % len(steps))

    logger.info('Defined steps are :%s' % ''.join(['\n\t- %s' % list(map(lambda m: _getFQDNName(m), step)) for step in steps]))

    return steps
