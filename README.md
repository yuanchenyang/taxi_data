Filter taxi data
----------------

Filtering is implemented based on thresholds from
[this paper](https://www.dropbox.com/s/deruyszudfqrll0/TRB15DonovanWork.pdf). These
can be modified in `filter_config.py`.

To filter a `csv` file, run:

    python filter.py <input-filename> <output-filename>

`pypy` offers a ~2x speedup:

    pypy filter.py <input-filename> <output-filename>
