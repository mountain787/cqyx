from flask import Flask, request, jsonify, Response
from cqyx_ts import Parser

app = Flask(__name__)
parser = Parser()


@app.route("/", methods=["GET"])
def main():
    try:
        params = request.args.to_dict()

        if "type" in params:
            content, headers = parser.proxy(request.url, {})
            return Response(content, headers=headers)

        result = parser.parse(params)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})
