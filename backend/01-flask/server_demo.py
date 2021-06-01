from cors import crossdomain
from flask import Flask, jsonify, request


app = Flask(__name__)


def get_args(req):
    if request.method == 'POST':
        args = request.json
    elif request.method == "GET":
        args = request.args
    return args


@app.route("/plugin_test", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def plugin_test():
    args = get_args(request)
    sentence = args.get("keyword", "Error: nothing input")
    # 处理输入返回数据
    results = []
    for i in range(5):
        results.append(sentence + " test: " + str(i))
    return jsonify({"data": results})


def main(host="127.0.0.1", port=9078):
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
