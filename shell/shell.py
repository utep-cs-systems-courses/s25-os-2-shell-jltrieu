#! /usr/bin/env python3

import os, sys, re


fdOut = os.open("p0-output.txt", os.O_CREAT | os.O_WRONLY)
fdIn = os.open("shell.py", os.O_RDONLY)

print(f"fdIn={fdIn}, fdOut={fdOut}");

# note that
#  fd #0 is "standard input" (by default, attached to kbd)
#  fd #1 is "standard ouput" (by default, attached to display)
#  fd #2 is "standard error" (by default, attached to display for error output)

lineNum = 1
while 1:
    input = os.read(fdIn, 10000)  # read up to 10k bytes
    if len(input) == 0: break     # done if nothing read
    lines = re.split(b"\n", input)
    for line in lines:
        strToPrint = f"{lineNum:5d}: {line.decode()}\n"
        os.write(fdOut, strToPrint.encode()) # write to output file
        os.write(1    , strToPrint.encode()) # write to fd1 (standard output)
        lineNum += 1
        
    # we do fake input 
        
    argv = ["/bin/ls", "-l"]
    # first, fork
    # then, make the parent wait and the child execute the program
    pid = os.getpid()
    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    rc = os.fork()
    
    if rc == 0:
        os.write(1, ("I am child.  My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
        os.execve(argv[0], argv, os.environ)
    elif rc < 0: 
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    else:
        os.write(1, ("I am parent.  My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())

