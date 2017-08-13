# x86 / x64 Processor Manual
# Copyright (c) 2017 William J. Darmofal
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from binaryninja.plugin import PluginCommand
from binaryninja.enums import InstructionTextTokenType
from binaryninja.log import log_error

import struct
import subprocess

browser = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"

intel_toc = "C:\\opcodes\\intel_toc.txt"
intel_manual = "file:///C:/opcodes/intel.pdf#page="

armv7_toc = "C:\\opcodes\\armv7_toc.txt"
armv7_manual = "file:///C:/opcodes/armv7.pdf#page="

arm_procs = ["armv4", "armv5", "armv6", "armv7"]
defined_bs = ["BFC", "BFI", "BIC", "BKPT", "BL", "BLX", "BX", "BXJ"]

def proc_manual(bv, addr):
    for block in bv.get_basic_blocks_at(addr):
        func = block.function
        arch = func.arch

        # Bring up log window
        log_error("")
        log_error("")
        
        if "x86" in repr(arch):
            toc = intel_toc
            manual = intel_manual
            print_opcode_backwards = False

        elif any(proc in repr(arch) for proc in arm_procs):
            toc = armv7_toc
            manual = armv7_manual
            print_opcode_backwards = True
            
        else:
            log_error(repr(arch))        
            log_error("Error: unsupported architecture")
            return 1
        
        addrsize = arch.address_size
        
        # Grab the instruction text
        tokens, length = arch.get_instruction_text(bv.read(addr, 16), addr)

        opcodestr = ""
        outchar = 0

        # Grab the opcode bytes       
        bytes = bv.read(addr, length).encode('hex')
        for byte in bytes:
            opcodestr += byte.upper()
            outchar += 1
            if outchar == 2:
                opcodestr += " "
                outchar = 0

        outstr = ""
        tokenstr = ""
        lookupstr = ""
        tokencount = 0
        
        # Parse and format menumonic       
        for token in tokens:
            tokenstr = repr(token)
            tokenstr = tokenstr[1:len(tokenstr)-1]            
            tokenstr = tokenstr.strip(' \t\n\r')
            
            if tokencount==0:
                lookupstr = tokenstr.upper()
            
            if tokenstr==",":
                outstr += tokenstr
            elif tokenstr==" ":
                pass
            elif tokenstr=="":
                pass
            elif tokenstr.startswith("+0x"):
                outstr += "+0x" + tokenstr[3:].upper()
            elif tokenstr.startswith("-0x"):
                outstr += "-0x" + tokenstr[3:].upper()
            elif tokenstr.startswith("0x"):
                outstr += " " + "0x" + tokenstr[2:].upper()
            else:
                outstr += " " + tokenstr.upper()
                
            tokencount += 1            
            
        # Reverse opcode bytes if necessary
        if (print_opcode_backwards):
            temp = opcodestr.split(" ")
            opcodestr = ""
            
            i = len(temp)-1
            while (i>=0):
                opcodestr += temp[i] + " "
                i -= 1
                
            opcodestr = opcodestr.lstrip()

        # Print original asm line            
        print opcodestr + "=> " + outstr[1:]

        # Normalize menumonics
        if "x86" in repr(arch):        
            if lookupstr.startswith("J") and lookupstr!="JMP":
                lookupstr = "Jcc"
            elif lookupstr=="RETN":
                lookupstr = "RET"
            elif lookupstr.startswith("SET"):
                lookupstr = "SETcc"
                
        elif "arm" in repr(arch):        
            if lookupstr.startswith("B") and not any(menumonic in lookupstr for menumonic in defined_bs):
                lookupstr = "B"

        # Perform lookup
        f = open(toc, "r")
        
        found = False
            
        for line in f:
            if line.startswith(lookupstr+","):
                found = True
                break

        f.close()
        
        if (found):
            try:
                # Extract info
                result = line.split(",")
                print result[0] + " = " + result[1]
                
                # Open Intel proc manual to page for selected opcode
                subprocess.Popen( [browser, '-url', manual+result[2] ] )
            except:
                log_error("Couldn't find info for the selected opcode!")
        else:
            log_error("No table of contents entry for this opcode!")        

# Create a plugin command so that the user can right click on an instruction and invoke the command
PluginCommand.register_for_address("Proc Manual", "Lookup asm instruction in proc manual", proc_manual)
