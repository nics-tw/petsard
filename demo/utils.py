import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Tuple, Type

import requests

from petsard.utils import load_external_module


def setup_environment(
    is_colab: bool,
    branch: str = "main",
    benchmark_data: list[str] = None,
    example_files: list[str] = None,
    subfolder: Optional[str] = None,
) -> None:
    """
    Setup the environment for both Colab and local development

    Args:
        is_colab (bool): Whether running in Colab environment
        branch (str, optional): The GitHub branch to use, defaults to "main"
        benchmark_data (list[str], optional):
            The dataset list of benchmark data to load by PETsARD Loader
        example_files (list[str], optional):
            List of example files to download from GitHub
        subfolder (str, optional):
            The subfolder in the demo directory. Defaults to None
    """
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Requires Python 3.10+, "
            f"current version is {sys.version_info.major}.{sys.version_info.minor}"
        )

    # Ensure pip is installed
    subprocess.run([sys.executable, "-m", "ensurepip"], check=True)
    # avoid pip version warning
    os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

    if is_colab:
        # Install petsard directly from GitHub
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"git+https://github.com/nics-tw/petsard.git@{branch}#egg=petsard",
            ],
            check=True,
        )
        from IPython.display import clear_output

        clear_output(wait=True)
    else:
        # Find the project root directory
        demo_dir = Path.cwd()

        # Calculate project root based on current directory structure
        if subfolder:
            # If we're in a subfolder like demo/use-cases/preproc/
            # we need to go up to find the project root (where pyproject.toml is)
            current_path = demo_dir
            project_root = None

            # Search upwards for pyproject.toml
            for parent in [current_path] + list(current_path.parents):
                if (parent / "pyproject.toml").exists():
                    project_root = parent
                    break

            if project_root is None:
                raise FileNotFoundError(
                    "Could not find project root with pyproject.toml"
                )
        else:
            # If we're directly in demo/, project root is parent
            project_root = demo_dir.parent

        # Local installation
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root)],
            check=True,
        )

    print("Installation complete!")

    if benchmark_data:
        from petsard.loader import Loader

        for benchmark in benchmark_data:
            try:
                loader = Loader(filepath=f"benchmark://{benchmark}")
                loader.load()
                print(f"Successful loading benchmark data: {benchmark}")
            except Exception as e:
                print(f"Failed to loading {benchmark}: {e}")

    # Download example files if specified
    if example_files and is_colab:
        for repo_path in example_files:
            # Get just the filename for local path
            local_file = Path(repo_path).name

            # Construct GitHub raw content URL
            file_url = f"https://raw.githubusercontent.com/nics-tw/petsard/{branch}/{repo_path}"

            try:
                response = requests.get(file_url)
                response.raise_for_status()

                # Write to current directory
                with open(local_file, "w") as f:
                    f.write(response.text)
                print(f"Successfully downloaded: {repo_path} -> {local_file}")
            except Exception as e:
                print(f"Failed to download {repo_path}: {e}")


def get_yaml_path(
    is_colab: bool,
    yaml_file: str,
    branch: str = "main",
    subfolder: Optional[str] = None,
) -> Path:
    """
    Get the YAML file path and display its content,
        supporting both Colab and local environments

    Args:
        is_colab (bool): Whether running in Colab environment
        yaml_file (str): Name of the YAML file
        branch (str, optional):
            The branch name to fetch YAML from GitHub. Defaults to "main"
        subfolder (str, optional):
            The subfolder in the demo directory. Defaults to None

    Returns:
        Path: Path to the YAML file

    Raises:
        FileNotFoundError: When file not found in local environment
        requests.RequestException: When failed to download file in Colab
    """
    if is_colab:
        import tempfile

        import requests

        yaml_url = (
            "https://raw.githubusercontent.com/nics-tw/"
            f"petsard/{branch}/yaml/{yaml_file}"
        )

        response = requests.get(yaml_url)
        if response.status_code != 200:
            raise requests.RequestException(
                f"Failed to download YAML file. Status code: {response.status_code}, URL: {yaml_url}"
            )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as tmp_file:
            tmp_file.write(response.text)
            print("Configuration content:\n\n")
            print(response.text)
            return Path(tmp_file.name)
    else:
        demo_dir = Path.cwd()

        # Calculate project root based on current directory structure
        if subfolder:
            # Search upwards for pyproject.toml to find project root
            current_path = demo_dir
            project_root = None

            for parent in [current_path] + list(current_path.parents):
                if (parent / "pyproject.toml").exists():
                    project_root = parent
                    break

            if project_root is None:
                raise FileNotFoundError(
                    "Could not find project root with pyproject.toml"
                )

            yaml_path = project_root / "demo" / subfolder / yaml_file
        else:
            # If we're directly in demo/, project root is parent
            project_root = demo_dir.parent
            yaml_path = project_root / "demo" / yaml_file

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"YAML file not found at {yaml_path}. "
                "Please make sure you have forked the project "
                "and are in the correct directory"
            )

        with open(yaml_path) as f:
            content = f.read()
            print("Configuration content:")
            print(content)

        return yaml_path


def load_demo_module(
    module_path: str,
    class_name: str,
    logger: logging.Logger,
    required_methods: dict[str, list[str]] = None,
) -> Tuple[Any, Type]:
    """
    Load external Python module for demo purposes with intelligent path resolution.

    This function is specifically designed for demo environments and supports
    multi-level subdirectory searching within the demo folder structure.

    Args:
        module_path (str): Path to the external module (relative or absolute)
        class_name (str): Name of the class to load from the module
        logger (logging.Logger): Logger for recording messages
        required_methods (Dict[str, List[str]], optional):
            Dictionary mapping method names to required parameter names
            e.g. {"fit": ["data"], "sample": []}

    Returns:
        Tuple[Any, Type]: A tuple containing the module instance and the class

    Raises:
        FileNotFoundError: If the module file does not exist
        ConfigError: If the module cannot be loaded or doesn't contain the specified class
    """
    # Create demo-specific search paths
    demo_search_paths = _get_demo_search_paths(module_path)

    # Use the core petsard function with demo search paths
    return load_external_module(
        module_path, class_name, logger, required_methods, demo_search_paths
    )


def _get_demo_search_paths(module_path: str) -> list[str]:
    """
    Get demo-specific search paths for module resolution.

    Args:
        module_path (str): The module path to create search paths for

    Returns:
        List[str]: List of demo-specific search paths
    """
    # Get the current working directory
    cwd = os.getcwd()

    # Demo-specific search locations
    demo_search_paths = [
        # 3. Relative to current working directory with demo prefix
        os.path.join(cwd, "demo", module_path),
        # 4. Search in demo subdirectories for multi-level support
        os.path.join(cwd, "demo", "use-cases", module_path),
        os.path.join(cwd, "demo", "use-cases", "preproc", module_path),
        os.path.join(cwd, "demo", "best-practices", module_path),
        os.path.join(cwd, "demo", "developer-guide", module_path),
    ]

    return demo_search_paths
