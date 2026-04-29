import urllib.parse
import time
import re
import json
from datetime import datetime


class Parser:

    def __init__(self):
        self.special_channels = ['cctvseHD', 'cctv17HD']

    def _load_channel_map(self):
        try:
            with open("channel_map.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _is_special_channel(self, channel_id):
        return channel_id in self.special_channels

    def _generate_m3u8_content(self, channel_id, stream_type='master', playseek=''):
        channel_map = self._load_channel_map()

        is_special = self._is_special_channel(channel_id)
        current = int(time.time())
        live_delay = 800

        # 获取路径
        if channel_id in channel_map:
            video_path = channel_map[channel_id]['video']
            audio_path = channel_map[channel_id]['audio']
        else:
            video_path = '2/v4M/' if 'HD' in channel_id else '1/v2M/'
            audio_path = '2/a48k/'

        # 回看
        is_playback = bool(playseek)

        if is_playback and re.match(r'^(\d{14})-(\d{14})$', playseek):
            start = datetime.strptime(playseek[:14], '%Y%m%d%H%M%S')
            end = datetime.strptime(playseek[15:], '%Y%m%d%H%M%S')

            start_ts = int(start.timestamp())
            end_ts = int(end.timestamp())

            seg = 2 if is_special else 10
            start_seq = start_ts // seg
            count = max(1, (end_ts - start_ts) // seg)

        else:
            seg = 2 if is_special else 10
            start_seq = (current - live_delay) // seg
            count = 405 if is_special else 81

        video_base = f'https://tencent.live.cbncdn.cn/__cl/cg:live/__c/{channel_id}/__op/default/__f/{video_path}'
        audio_base = f'https://tencent.live.cbncdn.cn/__cl/cg:live/__c/{channel_id}/__op/default/__f/{audio_path}'

        lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

        if stream_type == 'master':
            lines.append('#EXT-X-STREAM-INF:BANDWIDTH=5000000')
            url = f"/api?type=video&id={channel_id}"
            if playseek:
                url += f"&playseek={playseek}"
            lines.append(url)

        else:
            lines.append(f"#EXT-X-MEDIA-SEQUENCE:{start_seq}")
            lines.append("#EXT-X-TARGETDURATION:10")

            base = video_base if stream_type == 'video' else audio_base

            for i in range(count):
                seq = start_seq + i
                lines.append("#EXTINF:10.0,")
                lines.append(f"{base}{seq}.ts")

        return "\n".join(lines)

    def parse(self, params):
        channel_id = params.get('id', 'CCTV4K')
        playseek = params.get('playseek', '')

        url = f"/api?type=master&id={channel_id}"
        if playseek:
            url += f"&playseek={playseek}"

        return {"url": url}

    def proxy(self, url, headers):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)

        stream_type = qs.get('type', ['master'])[0]
        channel_id = qs.get('id', ['CCTV4K'])[0]
        playseek = qs.get('playseek', [''])[0]

        content = self._generate_m3u8_content(channel_id, stream_type, playseek)

        return content.encode(), {
            "Content-Type": "application/vnd.apple.mpegurl",
            "Access-Control-Allow-Origin": "*"
        }
