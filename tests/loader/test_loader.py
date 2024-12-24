import pytest

from petsard import Loader


class Test_Loader:

    def test_handle_filepath_with_complex_name(self):
        # 5. extract file extension
        #    - issue 375, with complex file name
        test = 'Splitter[0.8][1-1][train].csv'
        load = Loader(filepath=test)

        assert load.config['file_ext'] == '.csv'