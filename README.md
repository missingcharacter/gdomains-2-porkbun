# Create DNS records in porkbun from Google Domains YAML exports

## Requirements

- Python 3.10+
- Exported `.YAML` files in a folder
  - [Instructions here](https://support.google.com/domains/answer/3290350?hl=en#manage_domains)
- [Poetry](https://github.com/python-poetry/poetry)
- Porkbun API Access is enabled for the domains you want to update
  - [Getting started with the Porkbun API](https://kb.porkbun.com/article/190-getting-started-with-the-porkbun-api)

## How to install

```shell
poetry install --no-root
```

## How to use

### All flags

```shell
$ poetry run python main.py --help
Usage: main.py [OPTIONS]

Options:
  --porkbun-api-key TEXT          Porkbun API key
  --porkbun-secret-api-key TEXT   Porkbun Secret API key
  --yamls-folder TEXT             Path to folder containing YAML files
  --dry-run / --no-dry-run        Whether to make changes or not
  --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                  Set the logging output level
  --help                          Show this message and exit.
```

### With environment variables

```shell
$ env GD2P_PORKBUN_API_KEY='pk1_...' \    # pragma: allowlist secret
  GD2P_PORKBUN_SECRET_API_KEY='sk1_...' \ # pragma: allowlist secret
  poetry run python main.py \
  --log-level DEBUG \
  --yamls-folder path/to/folder/with/exported/yamls
2024-01-05 23:30:11,084 INFO (MainThread) [root] log_level was set to DEBUG
2024-01-05 23:30:11,085 DEBUG (MainThread) [__main__] dry_run=True, log_level='DEBUG'
```

### With flags

```shell
$ poetry run python main.py \
  --log-level DEBUG \
  --porkbun-api-key 'pk1_...' \
  --porkbun-secret-api-key 'sk1_...' \
  --yamls-folder path/to/folder/with/exported/yamls
2024-01-05 23:28:04,561 INFO (MainThread) [root] log_level was set to DEBUG
2024-01-05 23:28:04,561 DEBUG (MainThread) [__main__] dry_run=True, log_level='DEBUG'
```
