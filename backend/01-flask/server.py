from cors import crossdomain
from flask import Flask, jsonify, request
from keras.preprocessing.text import Tokenizer
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import json

app = Flask(__name__)

# total_words = 2058
total_words = 0
# max_sequence_len = 9
max_sequence_len = 0
word_index = dict()
model = None


def get_args(req):
    if request.method == 'POST':
        args = request.json
    elif request.method == "GET":
        args = request.args
    return args


@app.route("/plugin_test", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def plugin_test():
    if model == None:
        init()
    args = get_args(request)
    
    for seed in args.keys():
        result = rep(generate_text(seed, model, max_sequence_len))
        return jsonify({"data": result})


def main(host="0.0.0.0", port=9000):
    app.run(host=host, port=port, debug=True)


def init():
    savePath = "model/CheckpointModel_2.h5"
    global word_index
    word_index = json.load(open('word_dict.json', 'r'))
    para = json.load(open('para_dict.json', 'r'))
    global total_words, max_sequence_len
    total_words = para['total_words']
    max_sequence_len = para['max_sequence_len']
    global model
    model = load_model(savePath)


def find_index(seed_text):
    index_list = []
    seed_text = seed_text.split()
    for word in seed_text:
        if not word in word_index:
            index = None
            return
        index_list.append(word_index[word])
    return index_list


def generate_text(seed_text, model, max_sequence_len):
    # for _ in range(next_words):
    seed_text = seed_text.replace("(", " pareleft", ).replace(")", " pareright").replace(".", " dot").replace(",",\
    " comma").replace(" \'\'", " quotMark").replace("=", " equal").replace(":", " colon")
    i = 0
    while i <= 10:
        token_list = find_index(seed_text)
        if token_list == None:
            return "cant predict!"
        # print(token_list)
        token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')
        predicted = model.predict_classes(token_list, verbose=0)
        output_word = ""
        for word, index in word_index.items():
            if index == predicted:
                output_word = word
                break
        if output_word == 'dom':
            break
        seed_text += " " + output_word
        i += 1
    return seed_text


def rep(str):
    return str.replace(" pareleft", "(", ).replace(" pareright", ")").replace(" dot", ".") \
        .replace(" comma", ",").replace(" quotMark ", "\'\'").replace(" equal", "=").replace(" colon", ":") \
        .replace(" quotmark", "\'\'")


if __name__ == "__main__":
    main()
