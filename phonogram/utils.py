def get_lines(fpath):
    with open(fpath) as mf:
        return mf.read().split("\n")
