import re


def convert_full_expt_tuple_to_name(expt_tuple: tuple) -> str:
    """
    Convert a full experiment tuple to a name.

    Args:
        expt_tuple (tuple): A tuple representing a full experiment configuation.
            Each pair within the tuple should consist of a module name
            followed by its corresponding experiment name.
            The tuple can contain multiple such pairs,
            indicating a sequence of module and experiment steps. e.g.
            - A single step experiment: ('Loader', 'default'),
            - A multi-step experiment: ('Loader', 'default', 'Preprocessor', 'default')

    Returns:
        (str): A string representation of the experiment configuration,
            formatted as
            `ModuleName[ExperimentName]` for single-step experiments or
            `ModuleName[ExperimentName]_AnotherModuleName[AnotherExperimentName]`
            for multi-step experiments.
            - A single step experiment: 'Loader[default]'
            - A multi-step experiment: 'Loader[default]_Preprocessor[default]'
    """
    return '_'.join([
        f"{expt_tuple[i]}[{expt_tuple[i+1]}]"
        for i in range(0, len(expt_tuple), 2)
    ])


def convert_full_expt_name_to_tuple(expt_name: str) -> tuple:
    """
    Convert a full experiment name to a tuple.

    Args:
        expt_name (str): A string representation of the experiment configuration,
            formatted as `ModuleName[ExperimentName]` for single-step experiments or
            `ModuleName[ExperimentName]_AnotherModuleName[AnotherExperimentName]`
            for multi-step experiments.
            Examples:
            - 'Loader[default]'
            - 'Loader[default]_Preprocessor[default]'

    Returns:
        tuple: A tuple representing the full experiment configuration, where each
            pair consists of a module name followed by its corresponding experiment
            name. The tuple can contain multiple such pairs, indicating a sequence
            of module and experiment steps.
            Examples:
            - A single step experiment: ('Loader', 'default'),
            - A multi-step experiment: ('Loader', 'default', 'Preprocessor', 'default')
    """
    pattern = re.compile(r'(?:^|_)(\w+)\[([\w-]+)\]')
    matches = pattern.findall(expt_name)
    return tuple([item for match in matches for item in match])