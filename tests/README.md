讓 CI/CD 好讀

- test_案子名字
  - e.g. test_loader 就是測 loader 的功能

- 一個 module 一個 functional test
  - 可以一個 module 裡面有很多個 test

- .github/workflow/python-app.yml
  - 跑 pytest
  - 要寫 requirements.txt

<!-- # wait for sunset: conftest.py

import sys
from pathlib import Path


# locate petsard/petsard and add it to sys.path
# path_conftest = Path(__file__)
# path_petsard = path_conftest.parent.parent.joinpath('petsard')
# sys.path.append(path_petsard) -->