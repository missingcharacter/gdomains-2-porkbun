import click
import os
import logging
import porkbun_api as pb
from ruamel.yaml import YAML
from typing import Optional


def set_log_level(log_level: Optional[str] = None) -> None:
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(format=("%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"))
    log = logging.getLogger()  # Gets the root logger
    log.setLevel(log_level.upper())
    log.info(f"log_level was set to {log_level}")


def get_yaml_files(yamls_folder: str) -> list[str]:
    return [filename for filename in os.listdir(yamls_folder) if filename.lower().endswith(".yaml")]


def get_yaml_docs(log: logging.Logger, yamls_folder: str) -> list[dict]:
    yaml = YAML(typ="safe")
    yaml_files = get_yaml_files(yamls_folder)
    docs: list[dict] = []
    for yaml_file in yaml_files:
        log.info(f"Processing {yaml_file=}")
        domain: str = yaml_file.lower().replace(".yaml", "")
        log.info(f"Working on {domain=}")
        with open(os.path.join(yamls_folder, yaml_file), "r") as f:
            data = yaml.load_all(f)
            for doc in data:
                doc["domain"] = domain
                docs.append(doc)
    return docs


def extract_records(log: logging.Logger, yamls_folder: str) -> list[dict]:
    records: list[dict] = []
    yaml_docs = get_yaml_docs(log, yamls_folder)
    for doc in yaml_docs:
        subdomain = doc["name"].replace(doc["domain"], "").replace(".", "")
        rtype = doc["type"]
        ttl = doc["ttl"]
        for record in doc["rrdatas"]:
            priority: Optional[int] = None
            content: str = record
            if rtype == "MX":
                priority, content = record.split(" ")
            records.append(
                {
                    "domain": doc["domain"],
                    "subdomain": subdomain,
                    "rtype": rtype,
                    "ttl": ttl,
                    "priority": priority,
                    "content": content,
                }
            )
    return records


def create_record(
    log: logging.Logger,
    domain: str,
    rtype: str,
    content: str,
    subdomain: str = "",
    ttl: int = 600,
    priority: Optional[int] = None,
    dry_run: bool = True,
) -> None:
    log_message: str = f"record {subdomain}.{domain} of type {rtype} with content {content}"
    if priority:
        log_message += f" and priority {priority}"
    try:
        if dry_run:
            log.info(f"Would create {log_message}")
        else:
            log.info(f"Creating {log_message}")
            pb.create(
                domain=domain,
                rtype=rtype,
                content=content,
                subdomain=subdomain,
                ttl=ttl,
                priority=priority,
            )
    except Exception as e:
        log.exception(f"Error creating {log_message}: {e}")


@click.command()
@click.option("--porkbun-api-key", help="Porkbun API key")
@click.option("--porkbun-secret-api-key", help="Porkbun Secret API key")
@click.option("--yamls-folder", help="Path to folder containing YAML files")
@click.option("--dry-run/--no-dry-run", is_flag=True, default=True, help="Whether to make changes or not")
@click.option(
    "--log-level",
    type=click.Choice(list(logging._levelToName.values()), case_sensitive=False),
    default="INFO",
    help="Set the logging output level",
)
def main(
    porkbun_api_key: str,
    porkbun_secret_api_key: str,
    yamls_folder: str,
    dry_run: bool = True,
    log_level: str = "INFO",
) -> None:
    set_log_level(log_level)
    log = logging.getLogger(__name__)
    log.debug(f"{dry_run=}, {log_level=}")
    pb.APIKEY = porkbun_api_key
    pb.SECRETAPIKEY = porkbun_secret_api_key
    ip = pb.ping()
    log.info(f"Ping response: {ip}")
    records = extract_records(log, yamls_folder)
    for record in records:
        create_record(
            log=log,
            domain=record["domain"],
            rtype=record["rtype"],
            content=record["content"],
            subdomain=record["subdomain"],
            ttl=record["ttl"],
            priority=record["priority"],
            dry_run=dry_run,
        )


if __name__ == "__main__":
    main(auto_envvar_prefix="GD2P")
