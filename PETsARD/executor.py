from PETsARD.config import Config, Status


class Executor:
    """
    Represents an executor that runs a series of operators based on a given configuration.
    """

    def __init__(self, config: str):
        """
        Initialize the executor object.

        Args:
            config (str): The configuration filename for the executor.

        Attributes:
            config (Config): The configuration object.
            status (Status): The status of the executor.
            result (dict): The result of the executor.
        """
        self.config = Config(filename=config)
        self.sequence = self.config.sequence  # sequence default in Config
        self.status = Status(config=self.config)
        self.result: dict = {}

    def run(self):
        """
        run(): Runs the operators based on the configuration.
        """
        while self.config.config.qsize() > 0:
            ops = self.config.config.get()
            module = self.config.module_flow.get()
            expt = self.config.expt_flow.get()

            print(f"Now is {module} with {expt}...")
            ops.run(ops.set_input(status=self.status))

            self.status.put(module, expt, ops)

            # collect result
            self._set_result(module)

    def _set_result(self, module: str):
        """
        Get the result for a final module.

        Args:
            module (str): The name of the module.

        Returns:
            None. Update in self.result
        """
        if module == self.sequence[-1]:
            full_expt = self.status.get_full_expt()
            full_expt_name = '_'.join(
                [f"{module}[{expt}]" for module, expt in full_expt.items()]
            )
            self.result[full_expt_name] = self.status.get_result(module=module)

    def get_result(self):
        """
        Returns the result of the executor.
        """
        return self.result
