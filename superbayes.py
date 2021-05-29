

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
    import BayseCategorizer
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
        categorizer = BayseCategorizer()
        if not myargs['i']:
            print("Usage: superbayes -b catdir -t testdir -c catout\n")
            print("   build categories out of example text documents in catdir and saves the categorizer file as catout\n\n")
            exit(0)
        categorizer.build_categorizer(myargs['i'])
        if myargs['t']:
            accuracy = categorizer.test_categorizer(myargs['t'])
            print(" tested "+accuracy+"% accurate")
        exit(0)