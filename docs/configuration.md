# Benchmark configuration

QCEval stores downloaded benchmarks in a cache directory controlled by `QCEVAL_HOME`.

The default cache is `~/.qceval`.

## Source override

Use `QCEVAL_BENCHMARK_REPO_URL` to override the default benchmark source URL. This is useful for development or testing.

The default benchmark source URL is `https://github.com/cake-lab/qceval.git`.

To switch the benchmark source repo for development:

```env
QCEVAL_BENCHMARK_REPO_URL=https://github.com/cake-lab/qceval-internal.git
```

If you already have a local benchmark checkout, you can skip cloning entirely:

```env
QCEVAL_BENCHMARKS_SOURCE_DIR=/absolute/path/to/qceval
```

This should point to the directory that contains the `benchmarks/` folder.

## Example configuration

```env
QCEVAL_HOME=.qceval
QCEVAL_BENCHMARK_REPO_URL=https://github.com/cake-lab/qceval.git
# QCEVAL_BENCHMARKS_SOURCE_DIR=/absolute/path/to/qceval
```

You can also set these environment variables in your shell, or in a `.env` file in the repository root. See [docs/.env.example](docs/.env.example) for an example.
