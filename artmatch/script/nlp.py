import MeCab
import os

class NLP():
    def __init__(self):
        path = os.environ.get("MECABDIC")
        self._mecab_dic = MeCab.Tagger(f'--unk-feature "unknown" -d {path}')
        self._mecab_dic.parse("")
    
    def extract_legal_nouns_verbs(self,document):
        token = self._mecab_dic.parseToNode(document)
        result = []
        while token:
            if token.feature == "unknown":
                token = token.next
                continue
            part = token.feature.split(",")[0]
            origin = token.feature.split(",")[6]
            if (part == "名詞") or (part == "動詞"):
                result.append(origin)
            token = token.next
        return result
