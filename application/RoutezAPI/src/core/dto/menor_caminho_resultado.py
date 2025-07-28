from typing import List

class MenorCaminhoResultado:
    def __init__(self, total_length: float, streets_ids: List[str]):
        self.total_length = total_length
        self.streets_ids = streets_ids

    def __repr__(self):
        return f"<MenorCaminhoResultado total_length={self.total_length}, streets_ids={self.streets_ids}>"
