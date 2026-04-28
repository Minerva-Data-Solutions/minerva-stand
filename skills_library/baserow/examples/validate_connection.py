from config import load_config
from baserow_client import BaserowClient


def main() -> None:
    config = load_config()
    client = BaserowClient(config)
    result = client.list_all_tables(config.default_account)
    print({"status": result.status, "body": result.json()})


if __name__ == "__main__":
    main()
