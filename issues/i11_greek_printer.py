greekLetters = {
    'ALPHA':         '\u03B1',
    'BETA':          '\u03B2',
    'GAMMA':         '\u03B3',
    'DELTA':         '\u03B4',
    'EPSILON':       '\u03B5',
    'ZETA':          '\u03B6',
    'ETA':           '\u03B7',
    'THETA':         '\u03B8',
    'IOTA':          '\u03B9',
    'KAPPA':         '\u03BA',
    'LAMDA':         '\u03BB',
    'MU':            '\u03BC',
    'NU':            '\u03BD',
    'XI':            '\u03BE',
    'OMICRON':       '\u03BF',
    'PI':            '\u03C0',
    'RHO':           '\u03C1',
    'FINAL SIGMA':   '\u03C2',
    'SIGMA':         '\u03C3',
    'TAU':           '\u03C4',
    'UPSILON':       '\u03C5',
    'PHI':           '\u03C6',
    'CHI':           '\u03C7',
    'PSI':           '\u03C8',
    'OMEGA':         '\u03C9'
    }

def main():
    while True:
        letter = input('give the name of a greek letter> ')
        if letter.lower() == 'exit':
            print('Bye')
            break
        if letter.lower() == 'all':
            print(greekLetters)
            continue
        try:
            print(greekLetters[letter.upper()])
        except:
            print('ERROR!!! Uunknkown letter')

if __name__ == '__main__':
    main()
    