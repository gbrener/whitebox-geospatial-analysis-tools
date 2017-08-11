#!/usr/bin/env python
''' This file is intended to be a helper for running whitebox-tools plugins from a Python script.
See whitebox_example.py for an example of how to use it.
'''
from __future__ import print_function
import os
from os import path
import sys
from sys import platform
from subprocess import CalledProcessError, Popen, PIPE, STDOUT


def default_callback(value):
    ''' A simple default callback that outputs using the print function.
    '''
    print(value)


class WhiteboxTools(object):
    ''' An object for interfacing with the whitebox - tools executable.
    '''
    # exe_path = path.dirname(path.abspath(__file__))
    # wd = ""
    # verbose = True

    def __init__(self, exe_path=None):
        self.set_whitebox_dir(exe_path)
        self.wkdir = ""
        self.verbose = True
        self.cancel_op = False

    def set_whitebox_dir(self, exe_path=None):
        ''' Sets the directory to the whitebox - tools executable file.
        '''
        exe_paths = (exe_path, os.environ.get('WHITEBOX_TOOLS_BUILD', ''))
        found_it = False
        for exe_path in exe_paths:
            if not exe_path or not os.path.exists(exe_path):
                target = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'target')
                exe_path = os.path.join(target, 'release')
                if not exe_path or not os.path.exists(exe_path):
                    pass
                else:
                    found_it = True
            else:
                found_it = True
        if not found_it:
            raise ValueError('Define WHITEBOX_TOOLS_BUILD '
                             'environment variable {}'.format(exe_paths))
        self.exe_path = exe_path
        if platform == 'win32':
            exe = "whitebox_tools.exe"
        else:
            exe = 'whitebox_tools'
        self.exe_name = os.path.join(self.exe_path, exe)

    def set_working_dir(self, path_str):
        ''' Sets the working directory.
        '''
        self.wkdir = path_str

    def set_verbose_mode(self, val=True):
        ''' Sets verbose mode(i.e. whether a running tool outputs).
        '''
        self.verbose = val

    def _run_process(self, args, **kwargs):
        callback = kwargs.get('callback', default_callback)
        proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1,
                         universal_newlines=True,
                         cwd=self.exe_path)
        lines = []
        silent = kwargs.get('silent')
        ret_code = 0
        while True:
            line = proc.stdout.readline()
            sys.stdout.flush()
            if line != '':
                if not self.cancel_op and not silent:
                    callback(line.strip())
                else:
                    self.cancel_op = False
                    proc.terminate()
                    ret_code = 2
            else:
                break
            lines.append(line)
        ret_code = ret_code or proc.poll()
        return ret_code, lines

    def run_tool(self, tool_name, args, callback=default_callback):
        ''' Runs a tool and specifies tool arguments.
        Returns 0 if completes without error.
        Returns 1 if error encountered (details are sent to callback).
        Returns 2 if process is cancelled by user.
        '''
        print('args', args)
        try:
            args2 = []
            args2.append(self.exe_name)
            args2.append("--run=\"{}\"".format(tool_name))

            if self.wkdir.strip() != "":
                args2.append("--wd=\"{}\"".format(self.wkdir))

            for arg in args:
                args2.append(arg)

            # args_str = args_str[:-1]
            # a.append("--args=\"{}\"".format(args_str))

            if self.verbose:
                args2.append("-v")
            print('args2', args2)
            return self._run_process(args2, callback=callback, silent=False)[0] or 0
        except (OSError, ValueError, CalledProcessError) as err:
            callback(str(err))
            return 1

    def help(self):
        ''' Retrieve the help description for whitebox - tools.
        '''
        try:
            args = []
            args.append(self.exe_name)
            args.append("-h")
            return self._run_process(args)[1]
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def license(self):
        ''' Retrieves the license information for whitebox - tools.
        '''
        try:
            args = []
            args.append(self.exe_name)
            args.append("--license")
            return self._run_process(args)[1]
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def version(self):
        ''' Retrieves the version information for whitebox - tools.
        '''
        try:
            args = []
            args.append(self.exe_name)
            args.append("--version")

            return self._run_process(args)[1]
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def tool_help(self, tool_name, silent=False):
        ''' Retrieve the help description for a specific tool.
        '''
        try:
            args = []
            args.append(self.exe_name)
            args.append("--toolhelp={}".format(tool_name))
            return self._run_process(args, silent=silent)[1]
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def list_tools(self):
        ''' Lists all available tools in whitebox - tools.
        '''
        try:
            args = []
            args.append(self.exe_name)
            args.append("--listtools")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)
            return self._run_process(args)[1]
        except (OSError, ValueError, CalledProcessError) as err:
            return err
