import sys

import nx3d

if __name__ == "__main__":
    if len(sys.argv) > 1:
        nx3d.demo(**{arg: True for arg in sys.argv[1:]})
    else:
        nx3d.demo()
