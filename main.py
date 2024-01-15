import click
import os
import logging
import porkbun_api as pb  # type: ignore
from ruamel.yaml import YAML
from typing import Optional


def set_log_level(log_level: Optional[str] = None) -> None:
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        format=(
           "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
        )
    )
    log = logging.getLogger()  # Gets the root logger
    log.setLevel(log_level.upper())
    log.info(f"log_level was set to {log_level}")


def extract_records(
    log: logging.Logger,
    yamls_folder: str
) -> list[dict]:
    yaml = YAML(typ="safe")
    records: list[dict] = []
    for filename in os.listdir(yamls_folder):
        log.info(f"Processing {filename}")
        if filename.lower().endswith(".yaml"):
            domain: str = filename.lower().replace(".yaml", "")
            log.info(f"Working on {domain=}")
            with open(os.path.join(yamls_folder, filename), "r") as f:
                data = yaml.load_all(f)
                for doc in data:
                    subdomain = doc["name"].replace(domain, "").replace(".", "")
                    rtype = doc["type"]
                    ttl = doc["ttl"]
                    for record in doc["rrdatas"]:
                        priority = None
                        content = record
                        if rtype == "MX":
                            priority = record.split(" ")[0]
                            content = record.split(" ")[1]
                        records.append(
                            {
                                "domain": domain,
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
    try:
        if dry_run:
            log.info(
                f"Would create record {subdomain}.{domain} of type {rtype} with content {content} and priority {priority}"
            )
        else:
            log.info(
                f"Creating record {subdomain}.{domain} of type {rtype} with content {content} and priority {priority}"
            )
            pb.create(
                domain=domain,
                rtype=rtype,
                content=content,
                subdomain=subdomain,
                ttl=ttl,
                priority=priority,
            )
    except Exception as e:
        log.exception(f"Error creating record {subdomain}.{domain} of type {rtype} with content {content}: {e}")


@click.command()
@click.option("--porkbun-api-key", help="Porkbun API key")
@click.option("--porkbun-secret-api-key", help="Porkbun Secret API key")
@click.option("--yamls-folder", help="Path to folder containing YAML files")
@click.option(
    "--dry-run/--no-dry-run",
    is_flag=True,
    default=True,
    help="Whether to make changes or not"
)
@click.option(
    "--log-level",
    type=click.Choice(
        list(
            logging._levelToName.values()
        ),
        case_sensitive=False
    ),
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
