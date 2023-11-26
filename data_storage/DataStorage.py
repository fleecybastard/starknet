

class DataStorage:

    def __init__(self,
                 private_keys_file: str,
                 successful_accounts_file: str,
                 failed_accounts_file: str) -> None:
        self.private_keys_file = private_keys_file
        self.successful_accounts_file = successful_accounts_file
        self.failed_accounts_file = failed_accounts_file

    def get_private_keys(self) -> list[str]:
        with open(self.private_keys_file, 'r') as f:
            lines = f.readlines()
            return [line.replace('\n', '') for line in lines]

    def add_successful_accounts(self, private_keys: list[str]) -> None:
        with open(self.successful_accounts_file, 'a') as f:
            lines = [private_key + '\n' for private_key in private_keys]
            f.writelines(lines)

    def add_failed_accounts(self, private_keys: list[str]) -> None:
        with open(self.failed_accounts_file, 'a') as f:
            lines = [private_key + '\n' for private_key in private_keys]
            f.writelines(lines)
