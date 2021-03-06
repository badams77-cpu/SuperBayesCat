

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
            argv = argv[2:]
        else:
            opts[argv[0]] = 1
            argv = argv[1:]
    return opts

if __name__ == '__main__':
    from sys import argv
    import msgpack
    from BayesCategorizer import BayesCategorizer
    myargs = getopts(argv)
    if '-h' in myargs:
        print("Usage: superbayes -b catdir -t testdir -c catout\n")
        print("   build categories out of example text documents in catdir and saves the categorizer file as catout\n\n")
        print("superbayes -i document -c catin\n")
        print("   reads the categorizer file and categorizes document as and outputs the matching category to stdout\n\n")
        print("superbayes -i document -c catin --move catoutdir\n")
        print("   reads the categorizer file, categorizes document and moves it to directory catoutdir/{category}\n\n")
        print("superbayes -i document -c catin --copy catoutdir\n")
        print("   reads the catgorizer file, categorizes document and copies it to directory catoutdir/{category}\n\n")
        print("superbayes\n")
        print("   start gui mode if available\n")
        exit(0)
    if '-b' in myargs:
        print("building")
        categorizer = BayesCategorizer()
        categorizer.build_categorizer(myargs['-b'])
        if '-c' in myargs:
            file = myargs['-c']
            catout = open(file, 'wb')
            packed = msgpack.packb(BayesCategorizer.encode(categorizer))
            print("Writing categorizer "+file)
            catout.write(packed)
            catout.close()
        if '-t' in myargs:
            accuracy = categorizer.test_categorizer(myargs['-t'])
            print(" tested "+str(accuracy)+"% accurate")
        exit(0)
    if '-t' in myargs:
        if '-c' in myargs:
            file = myargs['-c']
            catin = open(file, 'rb')
            unpack = catin.read();
            print("Read categorizer "+file)
            categorizer = BayesCategorizer.decode(msgpack.unpackb(unpack))
            catin.close()
            accuracy = categorizer.test_categorizer(myargs['-t'])
            print(" tested "+str(accuracy)+"% accurate")