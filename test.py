import struct

import numpy as np

if __name__ == '__main__':
    p = struct.pack(">H", 255)
    print(p)