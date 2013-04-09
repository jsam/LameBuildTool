import os
import sys
import json
import fnmatch
import commands

class BuildToolCore:

    @staticmethod
    def GetObjectsFromDirectory(directory='./', extension='cpp'):
        """Search for all files with extension and return list of files as dictionary
        Targets names are equivalent to relative paths where '/' is replaced by '_',
        and extension is replaced by '.o'."""    
        if directory[-1:] == '/':
            directory = directory[:-1]

        os.chdir(directory)

        matches = []
        dictionary = {}
        for root, directory_names, file_names in os.walk (directory):
            for file_name in fnmatch.filter (file_names, '*.' + extension): # It's bad, but I fucking dont care
                matches.append (os.path.join (root, file_name))
    
        for _file in matches:
            _len_extension = len (extension)
            _len_directory = len (directory)
            dictionary [_file[_len_directory + 1:].replace('/', '_')[:-_len_extension-1] + '.o'] = _file[_len_directory + 1:]
    
        return dictionary

    @staticmethod
    def GetDependencyForObjects(targets, path='', compiler_command='c++ -MM', extension='cpp'):
        """Get dependency list of targets.
        Get list from compiler_command, then try to find corresponding .c/.cpp files"""
        if path[-1:] != '/' and path != '':
            path += '/'

        dependency = {}
        for item in targets.keys():
            dependency[item] = commands.getstatusoutput ('%s %s%s' % (compiler_command, path, targets[item]))[1].split(': ')[1].split(' ')

            if dependency[item][0] == 'error':
                sys.stderr.write ('[EE] %s returned error for object %s.' % (compiler_command, item))
            else:
                dependency[item] = [_item for _item in dependency[item] if _item != '\\\n']

        return dependency

    @staticmethod
    def GetTargetFromObjects(targets, name, path='bin/'):
        """Create a list of objects (*.o files) that are used to build target"""
        target = {}
        target[name] = {'path' : path, 'objects' : targets.keys()}
        
        return target

    @staticmethod
    def GetCompilerDictionary(compiler='c++', flags=['-Wall', '-ggdb'], libs=['-lpthread']):
        return {'binary' : compiler, 'flags' : flags, 'libs' : libs}

    @staticmethod
    def CreateJSON(objects_dictionary, dependency_dictionary, target_dictionary, 
                   compiler_dictionary, objects_path='obj/', output_file=sys.stdout):
        """Serialize known generated dictionaries to JSON"""

        dictionary = {'objects_path' : objects_path, 
                      'objects' : objects_dictionary, 
                      'dependency' : dependency_dictionary,
                      'target' : target_dictionary,
                      'compiler' : compiler_dictionary}

        json_dump = json.dumps (dictionary, sort_keys = True, 
                                indent = 4, separators = (',', ': '))

        output_file.write (json_dump)
    
    @staticmethod
    def CreateDictionary(objects_dictionary, dependency_dictionary, target_dictionary, 
                            compiler_dictionary, objects_path='obj/'):
        """Returns one dictionary from all elements """
    
        return {'objects_path' : objects_path, 
                    'objects' : objects_dictionary, 
                    'dependency' : dependency_dictionary,
                    'target' : target_dictionary,
                    'compiler' : compiler_dictionary}

    @staticmethod
    def CreateMakefile(dictionary, output_file=sys.stdout):
        """Write makefile read from dictionary to output_file"""
    #target_path = dictionary['target']['path']
    #if target_path[-1:] != '/' and target_path != '':
    #    target_path += '/'
        for _target in dictionary['target']:
            if dictionary['target'][_target]['path'][-1:] != '/' and dictionary['target'][_target]['path'] != '':
                    dictionary['target'][_target]['path'] += '/'

        if dictionary['objects_path'][-1:] != '/' and dictionary['objects_path'] != '':
            dictionary['objects_path'] += '/'

    #output_file.write('TARGET = %s%s\n' % (target_path, dictionary['target']['name']))
        output_file.write('LIBS = %s\n' % (' '.join(dictionary['compiler']['libs'])))
        output_file.write('FLAGS = %s\n' % (' '.join(dictionary['compiler']['flags'])))
        output_file.write('CC = %s\n\n' % (dictionary['compiler']['binary']))
    
        for _target in dictionary['target']:
            output_file.write('%s%s: %s\n' % (dictionary['target'][_target]['path'], _target,
                                              ' '.join([dictionary['objects_path'] + _item for _item in dictionary['target'][_target]['objects']])))
            output_file.write('\t$(CC) $(LIBS) -o $@ $^\n\n')
    
        for _object in dictionary['objects']:
            output_file.write('%s%s: %s\n' % (dictionary['objects_path'], _object, ' '.join(dictionary['dependency'][_object])))
            output_file.write('\t$(CC) $(LIBS) $(FLAGS) -c -o $@ $<\n\n')
        
        output_file.write('clean:\n\trm -f %s*.o %s\n' % (dictionary['objects_path'], 
                                                          ' '.join([dictionary['target'][_target]['path'] + _target for _target in dictionary['target'].keys()])))

    @staticmethod
    def GetDictionaryFromFile(input_file=sys.stdin):
        """Function that reads json and returns dictionary. (No Shit Sherlock)"""
        dictionary = json.loads(input_file.read())
        return dictionary

class BuildToolProfile:
    """Holds dict with rules when calling BuildToolCore methods.
    Profiles can be stored in json file."""
    profile = {'extension': 'cpp', 
               'compiler' : {'binary' : 'c++', 'flags' : ['-Wall', '-ggdb'], 'libs' : ['-lpthread'] },
               'dependency_command' : 'c++ -MM',
               'bin_dir' : 'bin/',
               'obj_dir' : 'obj/',
               }

    @staticmethod
    def FromFile(profile='default', file_name='profiles.json'):
        """Loads a specific profile from file_name aka fancy name to read a simple fucking JSON file.
        Returns a new BuildToolProfile object with requested dictionary"""
        _ret = BuildToolProfile()
        _file = open(file_name, 'r')
        _ret.profile = json.loads(_file.read())[profile]
        _file.close()
        return _ret


class BuildToolProject:
    dictionary = {}
        
    @staticmethod
    def ReadFromFile(file_name):
        """Reads project configuration from file.
        file_name is a location to json dictionary dump. Guess what it does :)"""
        _return = BuildToolProject()
        _file = open(file_name, 'r')

        _return.dictionary = BuildToolCore.GetDictionaryFromFile(_file)
        _file.close()
        
        return _return
    
    @staticmethod
    def Autogenerate(name, directory='./', profile=BuildToolProfile):
        """Tries to generate blindly a project configuration. 
        It searches for cpp/c/cc or something similar (depends on BuildToolProfile) and adds it to dict as wannabe compiled *.o. 
        Dependency for every wannabe is found using compiler command (dependency_command field in profile such as 'gcc -MM')
        Returns a dict with project configuration.
        """
        _return = BuildToolProject()
        
        objects = BuildToolCore.GetObjectsFromDirectory(directory, profile.profile['extension'])
        deps = BuildToolCore.GetDependencyForObjects(objects, '', profile.profile['dependency_command'], profile.profile['extension'])
        target = BuildToolCore.GetTargetFromObjects(objects, name, profile.profile['bin_dir'])
        
        _return.dictionary = BuildToolCore.CreateDictionary(objects, deps, target, profile.profile['compiler'], profile.profile['obj_dir'])
        return _return
    
    def SaveToFile(self, file_name):
        """Dumps project configuration dictionary to json file"""
        json_dump = json.dumps (self.dictionary, sort_keys = True, 
                                indent = 4, separators = (',', ': '))
        _file = open(file_name, "w")
        _file.write(json_dump)
        _file.close()

    def MakeMakefile(self):
        """The poem of this script. Creates a lame makefile from project configuration (dict)"""
        _file = open('makefile', 'w')
        BuildToolCore.CreateMakefile(self.dictionary, _file)
        _file.close()
