

def main():
    encoding = "utf-8"
    encoding = input('give the encoding> ')
    while True:
        code = input('give a number> ')
        if code.lower() == 'exit':
            print('Bye')
            break
        try:
            print(chr(int(code)).encode("utf-8").decode(encoding) )
            # code_int = int(code)
            # print(greekLetters[letter.upper()])
        except:
            print('ERROR!!!')
            raise

if __name__ == '__main__':
    main()
    