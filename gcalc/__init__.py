from sys import argv

from gcalc.commandline import GCalc


def main():
    c = GCalc()
    line: str = ' '.join(argv[1:])
    stop = c.onecmd(line)
    c.postcmd(stop, line)


if __name__ == "__main__":
    main()
