import os
import subprocess
import sys
from pathlib import Path

import requests


def quick_setup(
    yaml_file: str | list[str] = None,
    benchmark_data: list[str] = None,
    branch: str = "main",
    example_files: list[str] = None,
) -> tuple[bool, str, Path | list[Path] | None]:
    """
    Quick and silent setup for notebooks with minimal output.
    筆記本的快速靜默設定，輸出最少。

    This function displays PETsARD version info and sets up the environment.
    此函數顯示 PETsARD 版本資訊並設定環境。

    Example / 範例:
        # Single YAML file
        is_colab, branch, yaml_path = quick_setup(
            yaml_file="config.yaml",
            benchmark_data=["dataset"],
            branch="main",
            example_files=["path/to/example.py"]
        )
        from petsard import Executor
        exec_case = Executor(config=yaml_path)

        # Multiple YAML files
        is_colab, branch, yaml_paths = quick_setup(
            yaml_file=["config1.yaml", "config2.yaml"],
            benchmark_data=["dataset"],
            branch="main"
        )
        # yaml_paths will be a list of Path objects

    Args:
        yaml_file (str | list[str], optional): YAML configuration file name(s)
        benchmark_data (list[str], optional): Benchmark datasets to load
        branch (str, optional): GitHub branch to use. Defaults to "main"
        example_files (list[str], optional): Example files to download from GitHub

    Returns:
        tuple: (is_colab, branch, yaml_path)
            - yaml_path will be Path if yaml_file is str, list[Path] if yaml_file is list[str], or None
    """
    import os
    import sys
    from datetime import datetime
    from pathlib import Path

    # Basic setup
    is_colab = "COLAB_GPU" in os.environ

    # Handle utils.py for Colab
    if is_colab:
        utils_url = (
            f"https://raw.githubusercontent.com/nics-tw/petsard/{branch}/demo/utils.py"
        )
        response = requests.get(utils_url)
        if response.status_code == 200:
            with open("utils.py", "w") as f:
                f.write(response.text)
            Path("__init__.py").touch()
    else:
        # Silent utils.py search for local
        current_path = Path.cwd()
        for i in range(5):
            utils_candidate = current_path / "utils.py"
            if utils_candidate.exists():
                sys.path.insert(0, str(current_path))
                break
            current_path = current_path.parent

    # Setup environment (internalized from setup_environment function)
    _internal_setup_environment(
        is_colab=is_colab,
        branch=branch,
        benchmark_data=benchmark_data,
        example_files=example_files,
    )

    # Get version from pyproject.toml or package metadata
    try:
        import importlib.metadata

        version = importlib.metadata.version("petsard")
    except Exception:
        # Fallback to reading pyproject.toml directly
        try:
            import tomllib

            current_dir = Path.cwd()
            # Search for pyproject.toml
            for parent in [current_dir] + list(current_dir.parents):
                pyproject_path = parent / "pyproject.toml"
                if pyproject_path.exists():
                    with open(pyproject_path, "rb") as f:
                        pyproject_data = tomllib.load(f)
                    version = pyproject_data.get("project", {}).get(
                        "version", "unknown"
                    )
                    break
            else:
                version = "unknown"
        except Exception:
            version = "unknown"

    # Display version and timestamp
    now = datetime.now()
    # Get UTC offset in hours
    utc_offset = now.astimezone().utcoffset()
    offset_hours = int(utc_offset.total_seconds() / 3600)
    offset_str = f"UTC{offset_hours:+d}" if offset_hours != 0 else "UTC"
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    print(f"🚀 PETsARD v{version}")
    print(f"📅 {timestamp} {offset_str}")

    # Handle example files first if specified
    if example_files:
        if is_colab:
            print("📥 Downloading example files:")
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
                    print(f"✅ Downloaded: {local_file}")
                except Exception as e:
                    print(f"❌ Failed to download {local_file}: {e}")
        else:
            print("📁 Example files specified (local environment):")
            for repo_path in example_files:
                local_file = Path(repo_path).name
                # Check if file exists locally
                if Path(local_file).exists():
                    print(f"✅ Found locally: {local_file}")
                else:
                    print(f"ℹ️ Expected file: {local_file} (from {repo_path})")

    # Get YAML path(s) if specified (YAML content display should be last)
    yaml_path = None
    if yaml_file:
        # Get subfolder info
        subfolder = auto_detect_subfolder() if not is_colab else None
        print(f"📁 Subfolder: {subfolder or 'demo root'}")

        # Handle single or multiple YAML files
        if isinstance(yaml_file, str):
            # Single YAML file
            yaml_path = _get_yaml_path(
                is_colab=is_colab,
                yaml_file=yaml_file,
                branch=branch,
                subfolder=subfolder,
                silent=True,
            )

            # Display privacy-friendly path (from petsard onwards)
            yaml_str = str(yaml_path)
            if "petsard" in yaml_str:
                privacy_path = "petsard/" + yaml_str.split("petsard/", 1)[1]
            else:
                privacy_path = yaml_path.name  # Just filename if petsard not found
            print(f"📄 YAML path: {privacy_path}")

            # Display YAML content (this should be the last output)
            try:
                with open(yaml_path) as f:
                    content = f.read()
                    print("⚙️ Configuration content:")
                    print(content)
            except Exception as e:
                print(f"❌ Failed to read YAML content: {e}")

        elif isinstance(yaml_file, list):
            # Multiple YAML files
            yaml_path = []
            for i, single_yaml_file in enumerate(yaml_file):
                single_yaml_path = _get_yaml_path(
                    is_colab=is_colab,
                    yaml_file=single_yaml_file,
                    branch=branch,
                    subfolder=subfolder,
                    silent=True,
                )
                yaml_path.append(single_yaml_path)

                # Display privacy-friendly path (from petsard onwards)
                yaml_str = str(single_yaml_path)
                if "petsard" in yaml_str:
                    privacy_path = "petsard/" + yaml_str.split("petsard/", 1)[1]
                else:
                    privacy_path = (
                        single_yaml_path.name
                    )  # Just filename if petsard not found
                print(f"📄 YAML path ({i + 1}/{len(yaml_file)}): {privacy_path}")

            # Display YAML content for all files (this should be the last output)
            for i, single_yaml_path in enumerate(yaml_path):
                try:
                    with open(single_yaml_path) as f:
                        content = f.read()
                        print(
                            f"⚙️ Configuration content ({i + 1}/{len(yaml_file)}) - {yaml_file[i]}:"
                        )
                        print(content)
                        if (
                            i < len(yaml_path) - 1
                        ):  # Add separator between files except for the last one
                            print("---")
                except Exception as e:
                    print(f"❌ Failed to read YAML content for {yaml_file[i]}: {e}")

    return is_colab, branch, yaml_path


def auto_detect_subfolder() -> str | None:
    """
    Auto-detect the current subfolder relative to demo/ directory.

    Returns:
        Optional[str]: The detected subfolder path, or None if in demo root
    """
    current_path = Path.cwd()

    # Try to find the demo directory in the path
    path_parts = current_path.parts

    # Find demo directory index
    demo_index = None
    for i, part in enumerate(path_parts):
        if part == "demo":
            demo_index = i
            break

    if demo_index is None:
        # If not found, try to find it by looking for utils.py
        # Search upwards for demo directory containing utils.py
        for parent in [current_path] + list(current_path.parents):
            if (parent / "utils.py").exists() and parent.name == "demo":
                # Calculate relative path from demo to current directory
                try:
                    relative_path = current_path.relative_to(parent)
                    return str(relative_path) if str(relative_path) != "." else None
                except ValueError:
                    continue
        return None

    # Get the path after demo/
    remaining_parts = path_parts[demo_index + 1 :]

    if not remaining_parts:
        return None

    return "/".join(remaining_parts)


def _internal_setup_environment(
    is_colab: bool,
    branch: str = "main",
    benchmark_data: list[str] = None,
    example_files: list[str] = None,
) -> None:
    """
    Internal environment setup function used by quick_setup.
    內部環境設定函數，由 quick_setup 使用。
    """
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Requires Python 3.10+, "
            f"current version is {sys.version_info.major}.{sys.version_info.minor}"
        )

    # Ensure pip is installed
    subprocess.run(
        [sys.executable, "-m", "ensurepip"],
        check=True,
        capture_output=True,
        text=True,
    )
    # avoid pip version warning
    os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

    if is_colab:
        # Install petsard directly from GitHub with quiet output
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"git+https://github.com/nics-tw/petsard.git@{branch}#egg=petsard",
                "-q",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        from IPython.display import clear_output

        clear_output(wait=True)
    else:
        # Find the project root directory
        demo_dir = Path.cwd()

        # Auto-detect subfolder for local environment
        subfolder = auto_detect_subfolder()

        # Calculate project root based on current directory structure
        if subfolder:
            # If we're in a subfolder, search upwards for pyproject.toml
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

        # Local installation with quiet output
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root), "-q"],
            check=True,
            capture_output=True,
            text=True,
        )

    # Load benchmark data if specified
    if benchmark_data:
        from petsard.loader import Loader

        for benchmark in benchmark_data:
            try:
                loader = Loader(filepath=f"benchmark://{benchmark}")
                loader.load()
            except Exception:
                pass  # Silent failure for quick_setup

    # Note: example_files download is now handled in quick_setup for better user feedback
    # This internal function focuses on core environment setup only


def _get_yaml_path(
    is_colab: bool,
    yaml_file: str,
    branch: str = "main",
    subfolder: str | None = None,
    silent: bool = True,
) -> Path:
    """
    Internal function to get YAML file path for quick_setup.
    內部函數，為 quick_setup 取得 YAML 檔案路徑。
    """
    if is_colab:
        import tempfile

        import requests

        yaml_url = (
            "https://raw.githubusercontent.com/nics-tw/"
            f"petsard/{branch}/demo/{subfolder + '/' if subfolder else ''}{yaml_file}"
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
            return Path(tmp_file.name)
    else:
        # Find the demo directory by searching upwards
        current_path = Path.cwd()
        demo_root = None

        # Search upwards for demo directory containing utils.py
        for parent in [current_path] + list(current_path.parents):
            if (parent / "utils.py").exists() and parent.name == "demo":
                demo_root = parent
                break

        if demo_root is None:
            raise FileNotFoundError(
                "Could not find demo directory with utils.py. "
                "Please ensure you're running from within the demo directory structure."
            )

        # Construct YAML path
        if subfolder:
            yaml_path = demo_root / subfolder / yaml_file
        else:
            yaml_path = demo_root / yaml_file

        if not yaml_path.exists():
            # Try alternative locations
            alternative_paths = []
            if subfolder:
                # Try without subfolder
                alternative_paths.append(demo_root / yaml_file)

            for alt_path in alternative_paths:
                if alt_path.exists():
                    yaml_path = alt_path
                    break
            else:
                raise FileNotFoundError(
                    f"YAML file not found at {yaml_path} or alternative locations."
                )

        return yaml_path
