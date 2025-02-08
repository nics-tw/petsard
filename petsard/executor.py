import logging
import time
from datetime import datetime, timedelta

from petsard.config import Config, Status


class Executor:
    """
    Represents an executor that runs a series of operators based on a given configuration.
    """

    LOG_FILE: str = "PETsARD"
    LOG_LEVEL: str = "INFO"  # DEBUG / INFO / WARNING / ERROR / CRITICAL

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
        self._setup_logger()

        self.config = Config(filename=config)
        self.sequence = self.config.sequence  # sequence default in Config
        self.status = Status(config=self.config)
        self.result: dict = {}

    def run(self):
        """
        run(): Runs the operators based on the configuration.
        """
        start_time: time = time.time()
        self.logger.info("Starting PETsARD execution workflow")
        while self.config.config.qsize() > 0:
            ops = self.config.config.get()
            module = self.config.module_flow.get()
            expt = self.config.expt_flow.get()

            self.logger.info(f"Executing {module} with {expt}")
            ops.run(ops.set_input(status=self.status))

            self.status.put(module, expt, ops)

            # collect result
            self._set_result(module)

        elapsed_time: time = time.time() - start_time
        formatted_elapsed_time: str = str(timedelta(seconds=round(elapsed_time)))
        self.logger.info(
            f"Completed PETsARD execution workflow "
            f"(elapsed: {formatted_elapsed_time})"
        )

    def _set_result(self, module: str):
        """
        Get the result for a final module.

        Args:
            module (str): The name of the module.

        Returns:
            None. Update in self.result
        """
        if module == self.sequence[-1]:
            self.logger.debug(f"Collecting final results for {module}")
            full_expt = self.status.get_full_expt()
            full_expt_name = "_".join(
                [f"{module}[{expt}]" for module, expt in full_expt.items()]
            )
            self.result[full_expt_name] = self.status.get_result(module=module)

    def get_result(self):
        """
        Returns the result of the executor.
        """
        return self.result

    def _setup_logger(self):
        """
        Setting the output method of logger.
        """
        # Disable the root logger
        logging.getLogger().handlers = []

        # setup root logger
        root_logger = logging.getLogger("PETsARD")

        # setup output_type
        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file: str = f"{self.LOG_FILE}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)

        # setup formatter
        formatter = logging.Formatter(
            "%(asctime)s - "  # timestamp
            "%(name)-21s - "  # logger name (left align w/ 21 digits: 'PETsARD.Postprocessor')
            "%(funcName)-17s - "  # function name (left align w/ 17 digits: 'inverse_transform')
            "%(levelname)-8s - "  # logger level (left align w/ 8 digits: 'CRITICAL')
            "%(message)s"  # message
        )
        file_handler.setFormatter(formatter)

        # add file handler to root logger
        root_logger.addHandler(file_handler)

        # setup logging level
        root_logger.setLevel(getattr(logging, self.LOG_LEVEL.upper()))

        # setup this logger as a child of root logger
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
