#!/usr/bin/python
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


import os
import sys

wd = os.path.abspath(os.path.dirname(__file__))
from irpf90_t import mandir
filename = sys.argv[1].lower()+".l"
if filename not in os.listdir(mandir):
   print "%s does not exist"%(sys.argv[1])
   sys.exit(-1)

os.system("man ./"+mandir+sys.argv[1].lower()+".l")

