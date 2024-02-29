from abc import ABC, abstractmethod
import re

import pandas as pd

from PETsARD.error import ConfigError, UnsupportedMethodError


class ReporterMap():
    """
    Mapping of Reporter.
    """
    SAVE_DATA:   int = 10
    SAVE_REPORT: int = 11

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method
        """
        try:
            return cls.__dict__[method.upper()]
        except KeyError:
            raise UnsupportedMethodError


class Reporter:
    def __init__(self, method: str, **kwargs):
        self.config = kwargs
        self.config['method'] = method.lower()
        self.reporter = None

        method_code: int = ReporterMap.map(self.config['method'])
        self.config['method_code'] = method_code
        if method_code == ReporterMap.SAVE_DATA:
            self.reporter = ReportSaveData(config=self.config)
        elif method_code == ReporterMap.SAVE_REPORT:
            self.reporter = ReportSaveReport(config=self.config)
        else:
            raise UnsupportedMethodError

    def create(self, data: dict) -> None:
        self.reporter.create(data=data)

    def report(self) -> None:
        self.reporter.report()


class ReportBase(ABC):
    def __init__(self, config: dict):
        self.config: dict = config
        if 'method' not in self.config:
            raise ConfigError
        if not isinstance(self.config.get('output'), str) \
                or not self.config['output']:
            self.config['output'] = 'PETsARD'
        self.data: dict = {}

    @abstractmethod
    def create(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def report(self) -> None:
        raise NotImplementedError

    def _save(self, data: pd.DataFrame, full_output: str) -> None:
        print(f"Now is {full_output} save to csv...")
        data.to_csv(
            path_or_buf=f"{full_output}.csv",
            index=False,
            encoding='utf-8'
        )


class ReportSaveData(ReportBase):
    def __init__(self, config: dict):
        super().__init__(config)

        # Source should be string or list of string: Union[str, List[str]]
        if 'source' not in self.config:
            raise ConfigError
        elif not isinstance(self.config['source'], (str, list)) \
            or (isinstance(self.config['source'], list)
                and not all(isinstance(item, str) for item in self.config['source'])
                ):
            raise ConfigError

        # convert source to list if it is string
        if isinstance(self.config['source'], str):
            self.config['source'] = [self.config['source']]

    def create(self, data: dict) -> None:
        # last 1 of index shoulde remove postifx "_[xxx]" to match source
        pattern = re.compile(r'_(\[[^\]]*\])$')
        for index, df in data.items():
            # check if last 2 element of index in source
            last_module_expt_name = [index[-2], re.sub(pattern, '', index[-1])]
            if any(item in self.config['source'] for item in last_module_expt_name):
                # index tuple should be even number
                if len(index) % 2 != 0:
                    raise ConfigError

                full_expt = '_'.join([
                    f"{index[i]}[{index[i+1]}]"
                    for i in range(0, len(index), 2)
                ])
                self.data[full_expt] = df

    def report(self) -> None:
        for expt_name, df in self.data.items():
            # Some of the data may be None.
            #   e.g. Evaluator.get_global/columnwise/pairwise
            #   just skip it
            if df is None:
                continue

            # PETsARD_{expt_name}
            full_output = f"{self.config['output']}_{expt_name}"
            self._save(data=df, full_output=full_output)


class ReportSaveReport(ReportBase):
    def __init__(self, config: dict):
        super().__init__(config)

    def create(self, data: dict) -> None:
        pass

    def report(self) -> None:
        pass
