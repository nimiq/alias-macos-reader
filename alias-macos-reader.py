"""
http://en.wikipedia.org/wiki/Alias_(Mac_OS)
http://sebastien.kirche.free.fr/python_stuff/MacOS-aliases.txt

A path is made of tokens.
The path:
/Users/john/Desktop
is made of 3 tokens: Users, john, Desktop

The max length of a token in Mac OS is 255 chars (ff in hex).

We can investigate the content of an alias file by opening it with a hex editor.
We will find out that:
- every char of a token is 1 byte
- every char of a token is represented with a 2 digits hex number, e.g. D is 44 in hex.
- the ALIASED PATH is made of TOKENS and each token record is made of:
    1. LENGTH: 0500 0000 (4 bytes): the first 2 bytes are the number of chars (so bytes) of the
                                    token string, e.g. 05 is the length of Users.
    2. DELIMITER: 0101 0000 (4 bytes): reveals the beginning of the token string.
    - 


"""
import sys
from bitstring import ConstBitStream


class AliasReader:

    def __init__(self, file_path):
        self.file_path = file_path

    def find_aliased_path(self):
        s = ConstBitStream(filename=self.file_path)

        # Find the delimiter of the first token record.
        start = s.find('0b00000001000000010000000000000000')[0]
        # Go back 32 bits to get the length.
        start -= 32
        s.pos = start
        # Init token list, which will be eventually transformed into string.
        tk_string = ['/']

        while True:
            # Read the length of the current token string.
            len_tk = s.read('intle:32')
            # Read the delimiter.
            delimiter = s.read('intle:32')
            # If this is not the delimiter I expect, then the aliased path is over.
            if delimiter != 257:
                break
            # Append to token list.
            for i in range(len_tk):
                tk_string.append(chr(s.read('uint:8')))
            zero_filling = 8 * (4 - (len_tk % 4))
            s.pos += zero_filling

            # Append a separator.
            tk_string.append('/')

        return ''.join(tk_string[:-1])


if __name__ == '__main__':
    try:
        alias_file_path = sys.argv[1]
    except IndexError:
        print('You must provide the path to the alias file!')
        exit(1)
    reader = AliasReader('samples/1 alias')
    print('The aliased path is:\n{}'.format(reader.find_aliased_path()))