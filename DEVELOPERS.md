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

## Releasing

To release, ensure that a pull request to the `main` branch contains a [conventional commit](https://www.conventionalcommits.org/).
For example, if the current version is `1.0.0`, then the following conventional commit message would release the patch version `1.0.1`:

```
fix: A backwards compatible bug fix
```

Similarly, the minor version `1.1.0`:

```
feat: A backwards compatible feature
```

Similarly, the major version `2.0.0`:

```
perf: A backwards incompatible change

BREAKING CHANGE: The nature of the backwards incompatible change.
```

If you've forgotten to include a conventional commit, then add an empty commit with a conventional commit message to the pull request:

```sh
git commit --allow-empty --message 'fix: Release a patch version'
```

Releasing will bump instances of the old version to the new version, commit these changes, and tag this (new) commit.
