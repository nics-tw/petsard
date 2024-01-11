from PETsARD.Evaluator.Anonymeter.AnonymeterFactory import AnonymeterFactory


class EvaluatorFactory:
    """
    Factory for "Evaluator".

    EvaluatorFactory defines which library to use
        and implements the Factory for that library.

    ...

    Args:
        evaluating_method (str):
            Follow the 'evaluating_method' logic defined in Evaluator.

    ...
    Returns:
        None

    ...
    TODO As AnonymeterMethodMap,
            use a class to define mappings of string and int,
            avoiding string conditions.

    """

    def __init__(self, **kwargs):
        evaluating_method = kwargs.get('evaluating_method', None)

        if evaluating_method.startswith('anonymeter'):
            self.Evaluator = AnonymeterFactory(**kwargs).create_evaluator()
        else:
            raise ValueError(
                f"Evaluator - EvaluatorFactory: evaluating_method "
                f"{evaluating_method} didn't support."
            )

    def create_evaluator(self):
        """
        Factory method to designated the selected evaluator.
        ...
        TODO As Loader,
                transform the Factory into the main module
                and create a Base module for inheritance
                to address the 'One Library, One Code' issue."

        """
        return self.Evaluator
