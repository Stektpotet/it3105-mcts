
import numpy as np

if __name__ == '__main__':
    # i = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
    arr = np.array([1, 2, 0, 2], dtype=np.int32)
    if len(np.where(arr < 0)[0]) > 0:
        print(f"Bad initial configuration, bad coin values! - Overriding board definition: [1, 0, 0, 2]")
        arr = np.array([1, 0, 0, 2])