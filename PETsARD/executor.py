from PETsARD.config import Config, Status


class Executor:
    """
    Represents an executor that runs a series of operators based on a given configuration.
    """

    def __init__(self, config: str, sequence: list = None):
        """
        Args:
            config (str): The configuration filename for the executor.

        Attributes:
            status (Status): The status of the executor.
            config (Config): The configuration object.
        """
        self.status = Status()
        self.config = Config(config=config, sequence=sequence)

    def run(self):
        """
        run(): Runs the operators based on the configuration.
        """
        while len(self.config) > 0:
            operator = self.config.pop(0)
            result = operator.run()
            self.status.update(result)
