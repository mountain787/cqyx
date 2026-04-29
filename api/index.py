from cqyx_ts import Parser

parser = Parser()

def handler(请求):
    try:
        params = request.args

        # m3u8代理
        if "type" in params:
            content, headers = parser.proxy(request.url, {})
            return content, 200, headers

        # 获取播放入口
        result = parser.parse(params)

        return result, 200

    except Exception as e:
        return {"error": str(e)}, 500
