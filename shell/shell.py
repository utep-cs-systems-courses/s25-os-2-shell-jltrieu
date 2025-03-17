#! /usr/bin/env python3

import os, sys, re

# note that
#  fd #0 is "standard input" (by default, attached to kbd)
#  fd #1 is "standard ouput" (by default, attached to display)
#  fd #2 is "standard error" (by default, attached to display for error output)

while 1:
    # we do input 
    # look into env variables and PS1
    arg = input("$ ")
    argv = re.split(" ", arg) # for now, we just work with the first command
    print(argv)

    # INPUT PROCESSING
    

    # first, fork
    # then, make the parent wait and the child execute the program
    pid = os.getpid()
    rc = os.fork()
    
    if rc == 0:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            # os.write(1, ("%s/%s: trying\n" % (dir, argv[0])).encode())
            program = "%s/%s" % (dir, argv[0])
            try:
                os.execve(program, argv, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("%s: command not found\n" % argv[0]).encode())
        sys.exit(1)                 # terminate with error
    elif rc < 0: 
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    else:
        childPidCode = os.wait()
        continue

