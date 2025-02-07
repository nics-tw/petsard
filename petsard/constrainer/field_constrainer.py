import re
import warnings

import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer
from petsard.error import ConfigError


class FieldConstrainer(BaseConstrainer):
    def __init__(self, config):
        super().__init__(config)
        self._validate_config_structure()  # Perform basic structure validation during initialization
        self._validate_syntax()  # Perform syntax validation during initialization

    def _validate_config_structure(self) -> None:
        """
        Validate the basic structure of configuration during initialization.
        Checks for list type, string elements, and basic syntax.

        Raises:
            ConfigError: If the configuration structure is invalid
        """
        if not isinstance(self.config, list):
            raise ConfigError("Configuration must be a list")

        if not all(isinstance(item, str) for item in self.config):
            raise ConfigError("All configuration items must be strings")

        # Basic syntax validation
        for idx, constraint in enumerate(self.config):
            if not constraint.strip():
                raise ConfigError(f"Empty constraint at index {idx}")

            # Check for balanced parentheses
            if constraint.count("(") != constraint.count(")"):
                raise ConfigError(
                    f"Unmatched parentheses in constraint at index {idx}: {constraint}"
                )

            # Verify presence of valid operators
            valid_operators = [
                ">",
                ">=",
                "==",
                "!=",
                "<",
                "<=",
                "IS",
                "IS NOT",
                "&",
                "|",
            ]
            has_valid_operator = any(op in constraint for op in valid_operators)
            if not has_valid_operator:
                raise ConfigError(
                    f"No valid operator found in constraint at index {idx}: {constraint}"
                )

    def _validate_syntax(self) -> None:
        """
        Validate constraint syntax without requiring DataFrame
        """
        if not isinstance(self.config, list):
            raise ConfigError("Configuration must be a list")

        if not all(isinstance(item, str) for item in self.config):
            raise ConfigError("All configuration items must be strings")

        valid_operators: list[str] = [
            ">",
            ">=",
            "==",
            "!=",
            "<",
            "<=",
            "IS",
            "IS NOT",
            "&",
            "|",
        ]
        for idx, constraint in enumerate(self.config):
            if not constraint.strip():
                raise ConfigError(f"Empty constraint at index {idx}")

            if constraint.count("(") != constraint.count(")"):
                raise ConfigError(
                    f"Unmatched parentheses in constraint at index {idx}: {constraint}"
                )

            tokens = constraint.split()

            # find operator in constraint
            found_operator = None
            for token in tokens:
                if token in valid_operators:
                    found_operator = token
                    break

                # find invalid operator
                if (
                    ">>" in token
                    or "<<" in token
                    or any(c * 2 in token for c in "><=!")
                ):
                    raise ConfigError(
                        f"Invalid operator in constraint at index {idx}: {constraint}"
                    )

            if not found_operator:
                raise ConfigError(
                    f"No valid operator found in constraint at index {idx}: {constraint}"
                )

    def validate_config(self, df: pd.DataFrame) -> bool:
        """
        Validate field existence in DataFrame
        """
        for idx, constraint in enumerate(self.config):
            fields = self._extract_fields(constraint)
            for field in fields:
                if field not in df.columns:
                    raise ConfigError(
                        f"Column '{field}' in constraint at index {idx} does not exist in DataFrame"
                    )
        return True

    def _extract_fields(self, constraint: str) -> list[str]:
        """
        Extract field names from a constraint string.
        Handles field references in complex expressions including date functions.

        Args:
            constraint: Input constraint string to analyze

        Returns:
            list[str]: List of unique field names found in the constraint
        """
        # Remove DATE function calls to avoid treating dates as field names
        constraint = re.sub(r"DATE\(\d{4}-\d{2}-\d{2}\)", "", constraint)

        # Clean special syntax elements
        constraint = (
            constraint.replace("(", " ")
            .replace(")", " ")
            .replace("IS pd.NA", "")
            .replace("IS NOT pd.NA", "")
        )

        # Extract and validate field names
        parts = constraint.split()
        fields = []
        i = 0
        while i < len(parts):
            part = parts[i].strip()

            # Skip operators
            if part in ["&", "|", ">", "<", ">=", "<=", "==", "!=", "IS", "NOT"]:
                i += 1
                continue

            # Skip literals
            if part == "pd.NA" or part.replace(".", "").isdigit():
                i += 1
                continue

            # Handle field addition expressions
            if i + 2 < len(parts) and parts[i + 1] == "+":
                if not any(
                    op in part for op in [">", "<", ">=", "<=", "==", "!=", "&", "|"]
                ):
                    fields.append(part)
                    fields.append(parts[i + 2])
                i += 3
                continue

            # Process potential field names
            if not any(
                op in part for op in [">", "<", ">=", "<=", "==", "!=", "&", "|"]
            ):
                fields.append(part)
            i += 1

        return list(set(fields))

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply field constraints to DataFrame.
        Performs validation before applying constraints.

        Args:
            df: Input DataFrame to be filtered

        Returns:
            DataFrame: Filtered DataFrame based on constraints

        Raises:
            ConfigError: If any required columns are missing
        """
        # Perform complete validation before applying constraints
        _ = self.validate_config(df)

        result = df.copy()
        for constraint in self.config:
            tokens = self._tokenize(constraint)
            involved_columns: list[str] = []

            mask, involved_columns = self._parse_expression(
                tokens.copy(), result, involved_columns
            )
            if mask is None:
                warnings.warn(f"Warning: Constraint '{constraint}' parsing failed")
                continue

            # Apply the constraint
            result = result.loc[mask].reset_index(drop=True)

        return result.reset_index(drop=True)

    def _tokenize(self, condition: str) -> list:
        """
        Break condition string into tokens

        Args:
            condition: Condition string to tokenize

        Returns:
            list of tokens
        """
        condition = " ".join(condition.split())
        tokens = []
        i = 0

        while i < len(condition):
            # Handle DATE() function
            if condition[i : i + 5] == "DATE(":
                end = condition.find(")", i)
                if end != -1:
                    tokens.append(condition[i : end + 1])
                    i = end + 1
                    continue

            # Handle parentheses
            if condition[i] in "()":
                tokens.append(condition[i])
                i += 1
                continue

            # Handle operators
            if condition[i : i + 2] in ["IS", "<=", ">=", "==", "!="]:
                if condition[i : i + 7] == "IS NOT ":
                    tokens.append(condition[i : i + 7])
                    i += 7
                    continue
                tokens.append(condition[i : i + 2])
                i += 2
                continue

            if condition[i] in ["<", ">", "&", "|"]:
                tokens.append(condition[i])
                i += 1
                continue

            # Handle expressions
            if condition[i].isalnum() or condition[i] in "_.":
                expr_end = i
                while expr_end < len(condition) and (
                    condition[expr_end].isalnum() or condition[expr_end] in "_. +-"
                ):
                    if condition[expr_end : expr_end + 4] == " IS ":
                        break
                    expr_end += 1

                expr = condition[i:expr_end].strip()
                tokens.append(expr)
                i = expr_end
                continue

            i += 1

        return [token for token in tokens if token.strip()]

    def _get_value(
        self, expr: str, df: pd.DataFrame, involved_columns: list[str]
    ) -> tuple[pd.Series | float | None, list[str]]:
        """
        Get value from expression. Handles fields, literals, and date functions.

        Args:
            expr: Expression to evaluate (field name, literal value, or DATE function)
            df: DataFrame containing the data
            involved_columns: List of columns involved in the expression

        Returns:
            Tuple of (evaluated value, updated involved columns)
        """
        if expr is None:
            return None, involved_columns

        expr = expr.strip()

        # Handle DATE function calls
        date_match = re.match(r"DATE\((\d{4}-\d{2}-\d{2})\)", expr)
        if date_match:
            try:
                date_str = date_match.group(1)
                return pd.Timestamp(date_str), involved_columns
            except Exception as e:
                print(f"Date parsing error: {e}")
                return None, involved_columns

        if "+" in expr:
            col1, col2 = map(str.strip, expr.split("+"))

            if col1 not in df.columns or col2 not in df.columns:
                warnings.warn(
                    f"Warning: Column '{col1}' or '{col2}' does not exist",
                    UserWarning,
                )
                return None, involved_columns
            involved_columns = list(set(involved_columns + [col1, col2]))

            try:
                col1_data = df[col1].copy()
                col2_data = df[col2].copy()

                if isinstance(col1_data, pd.DatetimeIndex):
                    col1_data = pd.Series(col1_data, index=df.index)
                if isinstance(col2_data, pd.DatetimeIndex):
                    col2_data = pd.Series(col2_data, index=df.index)

                if pd.api.types.is_datetime64_any_dtype(
                    col1_data.dtype
                ) and pd.api.types.is_numeric_dtype(col2_data.dtype):
                    result = col1_data + pd.to_timedelta(col2_data, unit="D")
                elif pd.api.types.is_numeric_dtype(
                    col1_data.dtype
                ) and pd.api.types.is_datetime64_any_dtype(col2_data.dtype):
                    result = col2_data + pd.to_timedelta(col1_data, unit="D")
                else:
                    result = col1_data + col2_data

                return pd.Series(result, index=df.index), involved_columns

            except Exception as e:
                warnings.warn(f"Warning: Operation failed '{str(e)}'", UserWarning)
                return None, involved_columns

        if expr in df.columns:
            col_data = df[expr].copy()
            involved_columns = list(set(involved_columns + [expr]))

            if isinstance(col_data, pd.DatetimeIndex):
                col_data = pd.Series(col_data, index=df.index)

            return col_data, involved_columns

        try:
            return float(expr), involved_columns
        except Exception:
            if expr != "pd.NA":
                warnings.warn(f"Warning: Cannot parse value '{expr}'", UserWarning)
            return None, involved_columns

    def _process_comparison(
        self,
        left: list[pd.Series | float],
        op: str,
        right: list[pd.Series | float],
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Process comparison operations

        Args:
            left: Left operand
            op: Operator string
            right: Right operand
            df: DataFrame for index alignment

        Returns:
            Boolean Series with comparison results
        """
        try:
            if left is None or right is None:
                return pd.Series(False, index=df.index)

            if not isinstance(left, pd.Series):
                left = pd.Series(left, index=df.index)
            if not isinstance(right, pd.Series):
                right = pd.Series(right, index=df.index)

            left = left.reindex(df.index)
            right = right.reindex(df.index)

            if op == ">":
                result = left > right
            elif op == ">=":
                result = left >= right
            elif op == "<":
                result = left < right
            elif op == "<=":
                result = left <= right
            elif op == "==":
                result = left == right
            elif op == "!=":
                result = left != right
            else:
                warnings.warn(f"Warning: Unsupported operator '{op}'")
                return pd.Series(False, index=df.index)

            return result
        except Exception as e:
            print(f"Comparison failed: {e}")
            warnings.warn(f"Warning: Comparison operation failed '{str(e)}'")
            return pd.Series(False, index=df.index)

    def _parse_expression(
        self, tokens: list, df: pd.DataFrame, involved_columns: list[str]
    ) -> tuple[pd.Series, list[str]]:
        """
        Parse and evaluate expression

        Args:
            tokens: List of tokens to parse
            df: DataFrame containing the data
            involved_columns: List of columns involved in the expression

        Returns:
            Tuple of (boolean mask, updated involved columns)
        """

        class Parser:
            def __init__(self, tokens_input):
                self.tokens = tokens_input
                self.pos = 0

            def peek(self) -> str:
                if self.pos < len(self.tokens):
                    return self.tokens[self.pos]
                return None

            def consume(self) -> str:
                if self.pos < len(self.tokens):
                    token = self.tokens[self.pos]
                    self.pos += 1
                    return token
                return None

            def has_more(self) -> bool:
                return self.pos < len(self.tokens)

        parser = Parser(tokens)

        def parse_primary(involved_columns: list[str]) -> tuple[pd.Series, list[str]]:
            token = parser.peek()

            if token == "(":
                parser.consume()  # Skip '('
                result, involved_columns = parse_or(involved_columns)
                if parser.peek() == ")":
                    parser.consume()  # Skip ')'
                    return result, involved_columns
                raise ConfigError("Expected closing parenthesis")

            left, involved_columns = self._get_value(
                parser.consume(), df, involved_columns
            )

            if parser.peek() == "IS":
                parser.consume()
                is_not = False
                if parser.peek() == "NOT":
                    parser.consume()
                    is_not = True

                if parser.peek() == "pd.NA":
                    parser.consume()
                    if is_not:
                        return ~pd.isna(left), involved_columns
                    return pd.isna(left), involved_columns

            if parser.peek() in [">", ">=", "==", "!=", "<", "<="]:
                op = parser.consume()
                right, involved_columns = self._get_value(
                    parser.consume(), df, involved_columns
                )
                return self._process_comparison(left, op, right, df), involved_columns

            if not isinstance(left, pd.Series):
                return pd.Series(False, index=df.index), involved_columns

            return left.notna() & (left != 0), involved_columns

        def parse_and(involved_columns: list[str]) -> tuple[pd.Series, list[str]]:
            result, involved_columns = parse_primary(involved_columns)
            while parser.peek() == "&":
                parser.consume()
                right, involved_columns = parse_primary(involved_columns)
                result = result & right
            return result, involved_columns

        def parse_or(involved_columns: list[str]) -> tuple[pd.Series, list[str]]:
            result, involved_columns = parse_and(involved_columns)
            while parser.peek() == "|":
                parser.consume()
                right, involved_columns = parse_and(involved_columns)
                result = result | right
            return result, involved_columns

        return parse_or(involved_columns)
