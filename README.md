# proc_manual
x86 / x64 Processor Manual for Binary Ninja

Python script (proc_manual.py) assumes Windows OS and 32-bit Firefox

* Install intel_toc.txt to "C:\opcodes\intel_toc.txt"
* Install intel.pdf to "C:\opcodes\intel.pdf"
* Make sure PDF preview is turned on in Firefox under Options->Applications->PDF
* Right-click a line of disassembly in Binary Ninja to look up the opcode definition in the Intel processor manual

Contact me if you know the Python method of detecting the processor architecture from the current analysis database in Binary Ninja.
The current version of this plugin is only relevant to Intel x86 / x64 and should be disabled for other processor families.
