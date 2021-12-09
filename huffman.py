from os.path import dirname, basename, join, abspath as path
from time import time
from datetime import datetime as dt
import click


class Log:
    def __init__(self, path, name):
        self.path = path
        self.name = name

    def log(self, msg, name=None):
        if name is None:
            name = self.name
        now = dt.today()
        with open(self.path, 'a', encoding='utf-8') as file:
            file.write(f'{now.year}-{str(now.month).rjust(2, "0")}-{str(now.day).rjust(2, "0")} '
                       f'{str(now.hour).rjust(2, "0")}:{str(now.minute).rjust(2, "0")}:{str(now.second).rjust(2, "0")},{str(now.microsecond)[:3]}'
                       ' | '
                       f'{name}'
                       ' | '
                       f'{msg}\n')


log = Log(join(dirname(__file__), 'hfm.log'), 'hfm-py')


def huffman(data):
    units = {}  # getting element-wise info
    for c in data:
        if c in units:
            units[c] += 1
        else:
            units[c] = 1
    codes = dict.fromkeys(units.keys(), '')
    units = sorted([([u], units[u]) for u in units], key=lambda u: u[1])

    while units:  # creating Haffman table
        if len(units) > 2:
            b = int(units[0][1] + units[1][1] > units[1][1] + units[2][1])
        else:
            b = 0
        for c in units[b][0]:
            codes[c] = '0' + codes[c]
        for c in units[1 + b][0]:
            codes[c] = '1' + codes[c]
        units[2 * b] = units[b][0] + units[1 + b][0], units[b][1] + units[1 + b][1]
        if len(units) > 2:
            del units[1]
            units.sort(key=lambda u: u[1])
        else:
            del units
            break
    return codes


def shichiro_encode(table):
    table = ';'.join([f'{k};{table[k]}' for k in table]).split(';')
    bits = ''
    for i in range(len(table)):
        if i % 2:
            code = table[i]
            bitlen = bin(len(code))[2:]
            if len(bitlen) > 7:
                while len(bitlen) > 7:
                    bits += '1' + bitlen[:7]
                    bitlen = bitlen[7:]
                bits += bitlen.rjust(8, '0') + bin(len(bitlen))[2:].rjust(8, '0')
            else:
                bits += bitlen.rjust(8, '0')
            bits += code
        else:
            bits += bin(int(table[i]))[2:].rjust(8, '0')
            continue
    return bits


def shichiro_decode(byts):
    bits=''.join(byts)
    dec = []
    table = {}
    stack = ''
    i = 0
    c = 0
    while i < len(bits) and len(bits) - i >= 8:
        if c % 2 == 0:
            dec.append(bits[i:i+8])
            i += 8
            c += 1
            continue
        bitlen = ''
        if bits[i] == '0':
            bitlen = int(bits[i:i+8], 2)
            i += 8
        else:
            while bits[i] == '1':
                bitlen += bits[i+1:i+8]
                i += 8
            bitlen = int(bitlen + bits[i+8-int(bits[i+8:i+16], 2):i+8], 2)
            i += 16
        dec.append(bits[i:i+bitlen])
        i += bitlen
        c += 1
    for i in range(0, len(dec), 2):
        table[dec[i + 1]] = int(dec[i], 2)
    return table


def compress_file(filename):
    log.log(f"Loading '{filename}'...")
    with open(filename, 'rb') as file:  # get data
        data = list(map(int, file.read()))
    log.log(f'Original size: {len(data)} bytes.')
    log.log('Creating Huffman table...')
    hf = huffman(data)
    table = shichiro_encode(hf)
    log.log('Embedding Huffman table...')
    tablen = bin(len(table))[2:]  # embed the table
    bits = ''
    bitlen = bin(len(tablen))[2:]
    while len(bitlen) > 7:
        bits += '1' + bitlen[:7]
        bitlen = bitlen[7:]
    bits += bitlen.rjust(8, '0') + bin(len(bitlen))[2:].rjust(8, '0') + tablen + table
    log.log(f'Huffman table size: {len(bits)} bits.')
    log.log('Compressing...')
    for i in range(len(data)):  # encode to Haffman
        bits += hf[data[i]]
    out = []
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8].ljust(8, '0'), 2))
    out.append(len(bits) % 8)
    log.log(f'Compressed size: {len(out)} bytes.')
    log.log(f"Saving to '{filename}.hfm'...")
    with open(f'{filename}.hfm', 'wb') as file:  # save Haffman code
        file.write(bytes(out))
    log.log('SUCCESSFULLY COMPRESSED')
    print(f'"origSize":{len(data)},')
    print(f'"compSize":{len(out)},')


def decompress_file(filename):
    log.log(f"Loading '{filename}'...")
    with open(filename, 'rb') as file:  # get data
        data = [bin(byte)[2:].rjust(8, '0') for byte in file.read()]
        os = len(data)
        data[-2] = data[-2][:int(data[-1], 2)]
        del data[-1]
    log.log('Extracting Huffman table...')
    bitlen = ''  # extract the table
    i = 0
    while 1:
        if data[i][0] == '1':
            bitlen += data[i][1:]
        else:
            bitlen += data[i][int(data[i + 1], 2):]
            break
        i += 1
    del data[:i + 2]
    data = ''.join(data)
    bitlen = int(bitlen, 2)
    tablen = int(data[:bitlen], 2)
    table = shichiro_decode(data[bitlen:tablen+bitlen])
    data = data[bitlen+tablen:]
    stack = ''
    out = []
    log.log('Decompressing...')
    for c in data:  # decode Haffman
        stack += c
        if stack in table:
            out.append(int(table[stack]))
            stack = ''
    filename = filename[:-4]
    log.log(f"Saving to '{filename}'...")
    with open(f'{filename}', 'wb') as file:  # save decoded data
        file.write(bytes(out))
    log.log(f'SUCCESSFULLY DECOMPRESSED')
    print(f'"compSize":{os},')
    print(f'"origSize":{len(out)},')


@click.command(options_metavar='[-c / -d]')
@click.argument('files', nargs=-1, metavar='<file [file [...]]>')
@click.option('-c/-d', 'comp', default=True, help='Compress/decompress mode selectors.')
def CLI(files, comp):
    log.log(f'hfm {"-c" * comp}{"-d" * (not comp)} {" ".join(files)}')
    for file in files:
        print('{')
        stime = time()
        if comp:
            compress_file(path(file))
            wtime = time() - stime
            print('"status":true,')
            print(f'"time":{round(wtime, 3)},')
            print(f'"dlink":"./files/{basename(file) + ".hfm"}"')
        else:
            try:
                decompress_file(path(file))
                wtime = time() - stime
                print('"status":true,')
                print(f'"time":{round(wtime, 3)},')
                print(f'"dlink":"./files/{basename(file)[:-4]}"')
            except Exception as e:
                print(f'"status":false')
        print('}')


if __name__ == '__main__':
    CLI()
