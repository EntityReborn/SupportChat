from configobj import flatten_errors, ConfigObj
from validate import Validator

def validateConfig(config):
    validator = Validator()
    results = config.validate(validator, preserve_errors=True)
    errors = list()

    if results != True:
        print "\nError in config:"
        for (section_list, key, exc) in flatten_errors(config, results):
            if key is not None:
                errors.append('\t"%s" in "%s" failed validation. (%s)' % (key, ', '.join(section_list), exc))
            else:
                errors.append('\tThe following sections were missing:%s ' % ', '.join(section_list))

    return errors

def loadConfig(filename, confdir=None):
    if confdir == None:
        confdir = "."
        
    config = ConfigObj("%s/%s"%(confdir, filename),
        configspec="%s/config.spec"%confdir)

    invalid = validateConfig(config)
    if invalid:
        return False

    return config
