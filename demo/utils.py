import subprocess
import sys
from pathlib import Path

import requests


def setup_environment(
    is_colab: bool,
    branch: str = "main",
    benchmark_data: list[str] = None,
    example_files: list[str] = None,
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
    """
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Requires Python 3.10+, "
            f"current version is {sys.version_info.major}.{sys.version_info.minor}"
        )

    # Ensure pip is installed
    subprocess.run([sys.executable, "-m", "ensurepip"], check=True)

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
) -> Path:
    """
    Get the YAML file path and display its content,
        supporting both Colab and local environments

    Args:
        is_colab (bool): Whether running in Colab environment
        yaml_file (str): Name of the YAML file
        branch (str, optional):
            The branch name to fetch YAML from GitHub. Defaults to "main"

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
        demo_dir = Path().absolute()
        project_root = demo_dir.parent
        yaml_path = project_root / "yaml" / yaml_file

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"YAML file not found at {yaml_path}. "
                "Please make sure you have forked the project "
                "and are in the correct directory"
            )

        with open(yaml_path, "r") as f:
            content = f.read()
            print("Configuration content:")
            print(content)

        return yaml_path
