# from ..Synthesizer import Synthesizer
# (Synthesizer)
# 20231214, Justyn: SDV 不能再繼承 Synthesizer 不然會循環引用

class SDV():
    def __init__(self, data, **kwargs):
        # super().__init__(data, synthesizing_method, **kwargs)
        self.data = data
        pass
