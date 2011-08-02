from configobj import flatten_errors, ConfigObj
from validate import Validator

errors = list()

def validateConfig(config):
    validator = Validator()
    haserrors = config.validate(validator, preserve_errors=True)
    
    if haserrors is True:
        for (section_list, key, exc) in flatten_errors(config, haserrors):
            if key is not None:
                errors.append('\t"%s" in "%s" failed validation. (%s)' % (key, ', '.join(section_list), exc))
            else:
                errors.append('\tThe following sections were missing:%s ' % ', '.join(section_list))

    return errors

def loadConfig(filename, path="."):
    config = ConfigObj("%s/%s"%(path, filename),
        configspec="%s/config.spec"%path)

    invalid = validateConfig(config)
    if invalid:
        return False

    return config
