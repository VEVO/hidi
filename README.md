# HiDi: Pipelines for Embeddings

HiDi is a library for high-dimensional embedding generation for collaborative
filtering applications.

## How Do I Use It?

This will get you started.

```python
from hidi import inout, clean, matrix, pipeline


# CSV file with link_id and item_id columns
in_files = ['hidi/examples/data/user-item.csv']

# File to write output data to
outfile = 'embeddings.csv'

transforms = [
    inout.ReadTransform(in_files),      # Read data from disk
    clean.DedupeTransform(),            # Dedupe it
    matrix.SparseTransform(),           # Make a sparse user*item matrix
    matrix.SimilarityTransform(),       # To item*item similarity matrix
    matrix.SVDTransform(),              # Perform SVD dimensionality reduction
    matrix.ItemsMatrixToDFTransform(),  # Make a DataFrame with an index
    inout.WriteTransform(outfile)       # Write results to csv
]

pipeline = pipeline.Pipeline(transforms)
pipeline.run()
```

## Setup

### Requirements

HiDi is tested against CPython 2.7, 3.4, 3.5, and 3.6. It may work with
different version of CPython.

### Installation

To install HiDi, simply run

```sh
$ pip install hidi
```

## Run the Tests

```
$ pip install tox
$ tox
```
