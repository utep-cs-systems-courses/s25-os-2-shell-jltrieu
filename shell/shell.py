#! /usr/bin/env python3

import os, sys, re

# note that
#  fd #0 is "standard input" (by default, attached to kbd)
#  fd #1 is "standard ouput" (by default, attached to display)
#  fd #2 is "standard error" (by default, attached to display for error output)

PS1 = "$ "
redir = re.compile(">")
piper = re.compile("\\|")
backr = re.compile("&")
background = False

if 'PS1' in os.environ:
    PS1 = os.environ['PS1']

while 1:
    # replace with os.read(0, ####) ? 
    #arg = input("%s" % PS1)
    os.write(1, ("%s" % PS1).encode())
    arg = os.read(0, 1000) # read 1000 bytes at  a time?
    arg = arg.decode()

    argv = re.split(" ", arg[:-1]) # for now, we just work with the first command
    print(argv)

    # INPUT PROCESSING
    if(argv[0] == "cd"):
        os.chdir(argv[1])
        print(os.getcwd()) 
        continue
    if(argv[0] == "exit"):
        break

    pid = os.getpid()
    if(backr.search(arg)):
        background = True
    else: 
        background = False
    # boolean for backgrounds
    # if false, parent waits
    # if true, dont wait
    rc = os.fork()
    
    if rc == 0:
        # does NOT support nested redirects; sorry!
        redirIndex = ""
        if redir.search(arg):
            os.close(1) # goodbye stdout ! 
            redirIndex = argv.index('>')
            os.open(argv[redirIndex+1], os.O_CREAT | os.O_WRONLY) # hello new output!
            os.set_inheritable(1, True)
        if piper.search(arg):
            os.close(1) 
            pipeIndex = argv.index('|')
            # do something else here
            # 
        if(background == True):
            argv.pop()
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, argv[0])
            try:
                if(redirIndex):
                    argv = argv[:redirIndex]

                os.execve(program, argv, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("%s: command not found\n" % argv[0]).encode())
        sys.exit(1)                 # terminate with error
    elif rc < 0: 
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    else:
        if(background == False):
            childPidCode = os.wait()
        continue
