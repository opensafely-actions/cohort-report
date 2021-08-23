# Development

## Setting up

A Python reusable action's dependencies are made available by the Python runtime.
Consequently, setting up a local development environment involves installing global production dependencies (from [the Python runtime's repo](https://github.com/opensafely-core/python-docker)) as well as local development dependencies (from this repo).

First, create and activate a new Python 3.8 virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install `pip-tools`:

```sh
pip install pip-tools
```

Update *requirements.dev.txt*, resolving global production dependencies and local development dependencies:

```sh
pip-compile --generate-hashes --output-file=requirements.dev.txt requirements.dev.in
```

Finally, synchronise the local development environment:

```sh
pip-sync requirements.dev.txt
```

For more information about dependencies and the Python runtime, see <https://docs.opensafely.org/actions-reusable/>.

## Testing

```sh
make test
```
