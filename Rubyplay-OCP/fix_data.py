import json
import glob
import gzip
import multiprocessing
import os

from argparse import ArgumentParser


def fix_file(input_file_name: str, output_file_name: str) -> None:
    with gzip.open(input_file_name, 'rb') as input_f, \
         gzip.open(output_file_name, 'wb') as output_f:
        lines = input_f.read().decode().split('\n')
        lines = (json.dumps(eval(line)) for line in lines)
        lines = '\n'.join(lines)
        lines = lines.encode()
        output_f.write(lines)


def fix_data(input_dir: str, output_dir: str) -> None:
    def make_dest_file_name(input_file_name: str) -> str:
        return os.path.join(output_dir, os.path.basename(input_file_name))

    files = glob.glob(os.path.join(input_dir, '*.gz'))
    args = [(inp_file, make_dest_file_name(inp_file)) for inp_file in files]

    with multiprocessing.Pool() as pool:
        _ = pool.starmap(fix_file, args)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('input_dir', help='Data directory to be fixed')
    parser.add_argument('output_dir',
                        help='Data directory to dump fixed data to')

    args = parser.parse_args()

    fix_data(args.input_dir, args.output_dir)
