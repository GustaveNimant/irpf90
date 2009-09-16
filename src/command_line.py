#!/usr/bin/python

import getopt, sys
from version import version

description = "IRPF90 Fortran preprocessor."
options = {}
options['d'] = [ 'debug'        , 'Activate debug', 0 ]
options['v'] = [ 'version'      , 'Print version of irpf90', 0 ]
options['a'] = [ 'assert'       , 'Activate assertions', 0 ]
options['h'] = [ 'help'         , 'Print this help', 0 ]
options['o'] = [ 'openmp'       , 'Activate openMP', 0 ]
options['c'] = [ 'check_cycles' , 'Check cycles in dependencies', 0 ]
options['i'] = [ 'init'         , 'Initialize current directory', 0 ]
options['D'] = [ 'define'       , 'Define variable', 1 ]
options['p'] = [ 'preprocess'   , 'Preprocess file', 1 ]

class CommandLine(object):

  def __init__(self):
    global options
    self._opts = None
    self.argv = list(sys.argv)
    self.executable_name = self.argv[0]

  def defined(self):
    if '_defined' not in self.__dict__:
      self._defined = []
      for o,a in self.opts:
        if o in [ "-D", options['D'][0] ]:
          self._defined.append(a)
    return self._defined
  defined = property(fget=defined)

  def preprocessed(self):
    if '_preprocessed' not in self.__dict__:
      self._preprocessed = []
      for o,a in self.opts:
        if o in [ "-p", options['p'][0] ]:
          self._preprocessed.append(a)
    return self._preprocessed
  preprocessed = property(fget=preprocessed)

  def usage(self):
    t = """
$EXE - $DESCR

Usage:
  $EXE [OPTION]

Options:
"""
    t = t.replace("$EXE",self.executable_name)
    t = t.replace("$DESCR",description)
    print t
    sorted = options.keys()
    sorted.sort()
    for o in sorted:
     print "  -%s , --%15s : %s"%(o,options[o][0].ljust(15),options[o][1])
     if options[o][2] == 1:
       print "                           Requires an argument"
    print ""
    print "Version : ", version
    print ""

  def opts(self):
    if self._opts is None:
      optlist = ["",[]]
      for o in options.keys():
        b = [o]+options[o]
        if b[3] == 1:
          b[0] = b[0]+":"
          b[1] = b[1]+"="
        optlist[0] += b[0]
        optlist[1] += [b[1]]
    
      try:
        self._opts, args = getopt.getopt(self.argv[1:], optlist[0], optlist[1])
      except getopt.GetoptError, err:
        # print help information and exit:
        self.usage()
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    
    return self._opts
  opts = property(fget=opts)
  
  t = """
def do_$LONG(self):
    if '_do_$LONG' not in self.__dict__:
      self._do_$LONG = False
      for o,a in self.opts:
        if o in ("-$SHORT", "--$LONG"):
          self._do_$LONG = True
          break
    return self._do_$LONG
do_$LONG = property(fget=do_$LONG)
"""
  for short in options.keys():
    long = options[short][0]
    exec t.replace("$LONG",long).replace("$SHORT",short)

  def do_run(self):
   if '_do_run' not in self.__dict__:
     self._do_run = not (self.do_version or self.do_init)
   return self._do_run
  do_run = property(fget=do_run)


command_line = CommandLine()
