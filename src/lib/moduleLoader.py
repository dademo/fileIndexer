import importlib

def loadModule(moduleName: str, moduleType: type):

    modulePath = moduleName[:moduleName.rfind('.')]
    moduleClassName = moduleName[moduleName.rfind('.')+1:]
    err = None
    
    # Importing module
    try:
        importedModule = importlib.import_module(modulePath)
    except ImportError as ex:
        err = ex

    if err:
        raise RuntimeError("Can't import the module (%s)" % repr(err))

    if not moduleClassName in dir(importedModule):
        raise ImportError('Module [%s] not found [%s]' % (moduleClassName, moduleName))

    _module = getattr(importedModule, moduleClassName)

    if not issubclass(_module, moduleType):
        raise RuntimeError('Class [%s] is not a subclass of [%s]' % (moduleName, moduleType))

    return _module()

