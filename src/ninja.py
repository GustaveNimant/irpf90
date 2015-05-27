#!/usr/bin/env python
#   IRPF90 is a Fortran90 preprocessor written in Python for programming using
#   the Implicit Reference to Parameters (IRP) method.
#   Copyright (C) 2009 Anthony SCEMAMA 
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#   Anthony Scemama
#   LCPQ - IRSAMC - CNRS
#   Universite Paul Sabatier
#   118, route de Narbonne      
#   31062 Toulouse Cedex 4      
#   scemama@irsamc.ups-tlse.fr


import os,sys
import irpf90_t
from command_line import command_line
from modules import modules
irpdir = irpf90_t.irpdir
mandir = irpf90_t.mandir

FILENAME = os.path.join(irpdir,"build.ninja")

cwd = os.getcwd()

def dress(f,in_root=False):
    """
    Transfoms the filename f into $PWD/IRPF90_temp/f
    """
    if in_root:
      result = os.path.join(cwd,f)
    else:
      result = os.path.join(cwd,irpdir,f)
    return os.path.normpath(result)


def create_build_touches(list_of_other_o):
    """
    Create the build command for the irp_touches.o file.
    """
    name = "irp_touches"
    target_o          = dress("%s.irp.o"%name)
    target_F90        = dress("%s.irp.F90"%name)

    needed_modules = [ "%s.irp.module.o"%(modules[x].filename) for x in modules ]

    list_of_modules = map(dress, needed_modules) + list_of_other_o
    list_of_modules = ' '.join(list_of_modules)

    result = '\n\n'.join(
        [ 
          "build {target_o}: compile_touches {target_F90} | {list_of_modules}",
        ] )

    result = result.format(
        target_o          = target_o          ,
        target_F90        = target_F90        ,
        list_of_modules   = list_of_modules   
      )
    return result

def create_build_target(t,list_of_other_o):
    """
    Create the build command for the target module t. t is a Fmodule object.
    """
    name = t.filename

    target            = dress(name,in_root=True)
    target_o          = dress("%s.irp.o"%name)
    target_F90        = dress("%s.irp.F90"%name)
    target_module_o   = dress("%s.irp.module.o"%name)
    target_module_F90 = dress("%s.irp.module.F90"%name)

    needed_modules = [ "%s.irp.module.o"%(modules[x].filename) for x in modules \
        if modules[x].name in t.needed_modules ] + [ target_module_o ]

    list_of_o = [ target_o, target_module_o ] + list_of_other_o
    list_of_o = ' '.join(list_of_o)

    list_of_modules = map(dress, needed_modules) + list_of_other_o
    list_of_modules = ' '.join(list_of_modules)

    list_of_includes = ' '.join(map(lambda x: dress(x,in_root=True), t.includes))

    result = '\n\n'.join(
        [ "build {target}: link {list_of_o}", 
          "build {target_o}: compile_fortran {target_F90} | {list_of_modules} {list_of_includes}",
          "build {target_module_o}: compile_fortran {target_module_F90}"
        ] )

    result = result.format(
        target            = target            ,
        target_o          = target_o          ,
        target_F90        = target_F90        ,
        target_module_o   = target_module_o   ,
        target_module_F90 = target_module_F90 ,
        list_of_o         = list_of_o         ,
        list_of_modules   = list_of_modules   ,
        list_of_includes  = list_of_includes
      )
    return result


def create_build_non_target(t,list_of_other_o):
    """
    Create the build command for the non-target module t. t is a Fmodule object.
    """
    name = t.filename

    target_o          = dress("%s.irp.o"%name)
    target_F90        = dress("%s.irp.F90"%name)
    target_module_o   = dress("%s.irp.module.o"%name)
    target_module_F90 = dress("%s.irp.module.F90"%name)

    needed_modules = [ "%s.irp.module.o"%(modules[x].filename) for x in modules \
        if modules[x].name in t.needed_modules ] + [ target_module_o ]

    list_of_modules = map(dress, needed_modules)
    list_of_modules = ' '.join(list_of_modules)
    list_of_externals = ' '.join([ dress(x,in_root=True) for x in list_of_other_o ])
    list_of_includes = ' '.join(map(lambda x: dress(x,in_root=True), t.includes))

    result = '\n\n'.join(
        [ 
          "build {target_o}: compile_fortran {target_F90} | {list_of_modules} {list_of_externals}",
          "build {target_module_o}: compile_fortran {target_module_F90} | {list_of_externals} {list_of_includes}"
        ] )

    result = result.format(
        target_o          = target_o          ,
        target_F90        = target_F90        ,
        target_module_o   = target_module_o   ,
        target_module_F90 = target_module_F90 ,
        list_of_modules   = list_of_modules   ,
        list_of_externals = list_of_externals ,
        list_of_includes  = list_of_includes
      )
    return result


def create_build_remaining(f):
    """
    Create the build command for the remaining file f. f is a file name (str).
    """
    t, extension = f.rsplit('.',1)
    t1 = dress(t,in_root=True)
    t2 = dress(t,in_root=False)
    target_i  = f
    target_o  = "%s.o"%t
    if not target_o.startswith(os.path.join(cwd,irpdir)):
      target_o = target_o.replace(cwd,os.path.join(cwd,irpdir))

    if extension.lower() in [ 'f', 'f90' ]:
      result = "build {target_o}: compile_fortran {target_i}"
    elif extension.lower() in [ 'c' ]:
      result = "build {target_o}: compile_c {target_i}"
    elif extension.lower() in [ 'cxx', 'cpp' ]:
      result = "build {target_o}: compile_cxx {target_i}"

    result = result.format(
        target_o  = target_o,
        target_i  = target_i          
      )
    return result



def create_irpf90_make(targets):
    targets = ' '.join(targets)
    result = """NINJA += -C {0}

TARGETS={1}

.PHONY: all clean veryclean

all:
	$(NINJA)

$(TARGETS): 
	$(NINJA) $(PWD)/$@

clean:
	$(NINJA) -t clean

veryclean: clean
	rm -rf IRPF90_temp/ IRPF90_man/ irpf90.make irpf90_entities dist tags

""".format(irpdir, targets)

    import makefile
    with open(makefile.IRPF90_MAKE,'w') as file:
        file.write(result)


def run():

    output = []

    # Environment variables

    try: FC = os.environ["FC"]
    except KeyError: FC="gfortran -ffree-line-length-none"

    try: CC = os.environ["CC"]
    except KeyError: CC="gcc"

    try: CXX = os.environ["CXX"]
    except KeyError: CXX="g++"

    includes = [ "-I %s "%(irpdir) ]
    for i in command_line.include_dir:
        includes.append( "-I %s%s "%(irpdir,i) )

    FC  += " "+' '.join(includes)
    CC  += " "+' '.join(includes)
    CXX += " "+' '.join(includes)
   
    try:  SRC = os.environ["SRC"].split()
    except KeyError: SRC=[]

    try:  OBJ = os.environ["OBJ"].split()
    except KeyError: OBJ=[]

    try:  LIB = os.environ["LIB"].split()
    except KeyError: LIB=[]

    try: FCFLAGS = os.environ["FCFLAGS"].split()
    except KeyError: FCFLAGS = [ "-O2" ]

    try: CFLAGS = os.environ["CFLAGS"].split()
    except KeyError: CFLAGS = [ "-O2" ]

    try: CXXFLAGS = os.environ["CXXFLAGS"].split()
    except KeyError: CXXFLAGS = [ "-O2" ]

    FCFLAGS = ' '.join(FCFLAGS)
    CFLAGS  = ' '.join(CFLAGS)
    CXXFLAGS  = ' '.join(CXXFLAGS)
    LIB = ' '.join(LIB)

    # Rules

    t = [ "rule compile_fortran" ,
          "  command = {FC} {FCFLAGS} -c $in -o $out".format(FC=FC, FCFLAGS=FCFLAGS),
          "",
          "rule compile_touches" ,
          "  command = {FC} -c $in -o $out".format(FC=FC, FCFLAGS=FCFLAGS),
          "",
          "rule compile_c" ,
          "  command = {CC} {CFLAGS} -c $in -o $out".format(CC=CC, CFLAGS=CFLAGS),
          "",
          "rule compile_cxx" ,
          "  command = {CXX} {CXXFLAGS} -c $in -o $out".format(CXX=CXX, CXXFLAGS=CXXFLAGS),
          "",
          "rule link",
          "  command = {FC} $in {LIB} -o $out".format(FC=FC, LIB=LIB) ]
   
    output = [ '\n'.join(t) ]


    # All modules : list of Fmodule objects

    l_mod = list( modules.values() )


    # Modules that are not targets

    l_non_targets = [ x for x in l_mod if not x.is_main ]




    # Common object/source files

    l_common_o = [ "irp_touches.irp.o" ] + \
      [ "{0}.irp.o".format(x.filename) for x in l_non_targets ] + \
      [ "{0}.irp.module.o".format(x.filename) for x in l_non_targets ]


    l_common_s = []

    if command_line.do_assert:
        l_common_o += [ "irp_stack.irp.o" ]
        l_common_s += [ "irp_stack.irp.F90" ]

    if command_line.do_openmp:
        l_common_o += [ "irp_locks.irp.o" ]
        l_common_s += [ "irp_locks.irp.F90" ]

    if command_line.do_profile:
        l_common_o += [ "irp_profile.irp.o", "rdtsc.o" ]
        l_common_s += [ "irp_profile.irp.F90", "rdtsc.c" ]

    l_common_o = map(dress,l_common_o) + map(lambda x: dress(x,in_root=True), OBJ)
    l_common_s = map(dress,l_common_s) + map(lambda x: dress(x,in_root=True), SRC)


    # IRP_touches
    output.append(create_build_touches(l_common_o[1:]))

    # All targets : list of Fmodule objects

    l_targets = [ x for x in l_mod if x.is_main ]


    # Create lines

    for i in l_non_targets:
        output.append (create_build_non_target(i,OBJ))

    for i in l_targets:
        output.append(create_build_target(i, l_common_o))

    # Remaining files
    for i in l_common_s:
        output.append(create_build_remaining(i))

    
    with open(FILENAME,'w') as f:
        f.write('\n\n'.join(output))
        f.write('\n')

    create_irpf90_make([ x.filename for x in l_targets ])

    return


