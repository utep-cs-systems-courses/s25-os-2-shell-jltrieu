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


    if(piper.search(arg)):
        pipeIndex = argv.index('|')
        argp = argv[pipeIndex+1:]
        argv = argv[:pipeIndex]

        pr,pw = os.pipe()
        for f in (pr, pw):
            os.set_inheritable(f, True)
        print("pipe fds: pr=%d, pw=%d" % (pr, pw))
    
    rc = os.fork()
    
    if rc == 0:
        # does NOT support nested redirects; sorry!
        if(background == True):
            argv.pop()
        if redir.search(arg):
            os.close(1) # goodbye stdout ! 
            redirIndex = argv.index('>')
            os.open(argv[redirIndex+1], os.O_CREAT | os.O_WRONLY) # hello new output!
            os.set_inheritable(1, True)
            argv = argv[:redirIndex]
        if piper.search(arg):
            os.close(1) 
            os.dup2(pw, 1)
            for fd in (pr, pw):
                os.close(fd)

        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
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
        if piper.search(arg):
            rc = os.fork() # not this shit again
            
            if rc == 0:
                os.close(0)
                os.dup2(pr, 0)
                for fd in (pr, pw):
                    os.close(fd)
                    
                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, argp[0])
                    try:
                        os.execve(program, argp, os.environ)
                    except FileNotFoundError:
                        pass
            elif rc < 0: 
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)
            
            #os.write(0, os.read(pr, 9999)) # we have stdout at home 
            for fd in (pr, pw):
                os.close(fd)
        if(background == False):
            childPidCode = os.wait()
        continue
