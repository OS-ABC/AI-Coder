from keras.preprocessing.text import Tokenizer
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import json

class Server:
    def __init__(self):
        self.model_path = "model/CheckpointModel_2.h5"
        self.word_index = json.load(open('word_dict.json', 'r'))
        self.para = json.load(open('para_dict.json', 'r'))
        self.total_words = self.para['total_words']
        self.max_sequence_len = self.para['max_sequence_len']
        self.model = load_model(self.model_path)
        print("模型初始化成功！")

    def reference(self,keyword):
        result = self.rep(self.generate_text(keyword))
        #print("python预测结果：" + result)
        return result

    def generate_text(self,keyword):
        keyword = keyword.replace("(", " pareleft", ).replace(")", " pareright").replace(".", " dot").replace(",",\
        " comma").replace(" \'\'", " quotMark").replace("=", " equal").replace(":", " colon")
        i = 0
        while i <= 10:
            token_list = self.find_index(keyword)
            if token_list == None:
                return "无法预测"
            # print(token_list)
            token_list = pad_sequences([token_list], maxlen=self.max_sequence_len - 1, padding='pre')
            predicted = self.model.predict_classes(token_list, verbose=0)
            output_word = ""
            for word, index in self.word_index.items():
                if index == predicted:
                    output_word = word
                    break
            if output_word == 'dom':
                break
            keyword += " " + output_word
            i += 1
        return keyword
    
    def find_index(self,keyword):
        index_list = []
        keyword = keyword.split()
        for word in keyword:
            if not word in self.word_index:
                return
            index_list.append(self.word_index[word])
        return index_list

    def rep(self,str):
        return str.replace(" pareleft", "(", ).replace(" pareright", ")").replace(" dot", ".") \
            .replace(" comma", ",").replace(" quotMark ", "\'\'").replace(" equal", "=").replace(" colon", ":") \
            .replace(" quotmark", "\'\'")