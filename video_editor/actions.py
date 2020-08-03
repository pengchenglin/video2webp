from video_editor._helpers import get_ffmpeg_binary, run_command
from abc import ABC, abstractmethod
from math import log2, floor
import os
import ffmpeg


class BaseAction(ABC):
    def __init__(self, input_path, output_path):
        self.input = input_path
        self.output = output_path

    @abstractmethod
    def run(self):
        pass


class CutAction(BaseAction):

    def __init__(self, input_path, output_path, start_time, end_time, reencode=False):
        super().__init__(input_path, output_path)
        self.reencode = reencode
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        cmd = '{ffmpeg} -y -ss {s:.2f} -t {d:.2f} -i "{fn}" -async 1 {re} "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            s=self.start_time/1000,
            d=(self.end_time-self.start_time)/1000,
            re="" if self.reencode else "-c copy",
            o=self.output,
        )
        return run_command(cmd)


class WebpAction(BaseAction):
    def __init__(self, input_path, output_path, start_time, end_time):
        super().__init__(input_path, output_path)
        # self.reencode = reencode
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        # '-vcodec libwebp -r 20  -lossless 0 -compression_level 2 -q:v 50  -loop 0 -preset photo -an -vsync 0 -vf scale=480:-1  '
        cmd = '{ffmpeg}  -i "{fn}" -ss {s} -to {d} ' \
              '-vcodec libwebp -lossless 0 -qscale 50 -preset default -loop 0 -vf scale={scale},fps=10 -an -vsync 0 ' \
              '"{o}"'.format(
                ffmpeg=get_ffmpeg_binary(),
                fn=self.input,
                s=get_time_str(self.start_time),
                d=get_time_str(self.end_time),
                scale=make_scale(self.input),
                o=self.output,
        )
        print(cmd)
        return run_command(cmd)

class GifAction(BaseAction):
    def __init__(self, input_path, output_path, start_time, end_time):
        super().__init__(input_path, output_path)
        # self.reencode = reencode
        self.start_time = start_time
        self.end_time = end_time

    def run(self):

        # '-vcodec libwebp -r 20  -lossless 0 -compression_level 2 -q:v 50  -loop 0 -preset photo -an -vsync 0 -vf scale=480:-1  '
        # cmd = '{ffmpeg}  -i "{fn}" -ss {s} -to {d} -vf scale=300:-1,fps=10  -an -vsync 0 "{o}"'.format(
        #     ffmpeg=get_ffmpeg_binary(),
        #     fn=self.input,
        #     s=get_time_str(self.start_time),
        #     d=get_time_str(self.end_time),
        #     # re="" if self.reencode else "-c copy",
        #     o=self.output,
        # )
        # print(cmd)
        # return run_command(cmd)

        '''
        'http://www.unixlinux.online/unixlinux/linuxjc/linuxjc/201702/19148.html'
        'http://ffmpeg.org/ffmpeg-filters.html#palettegen'
        'https://ffmpeg.org/ffmpeg-scaler.html'
        '''
        palette = os.path.join(os.path.dirname(self.input), "palette.png")
        filters = "fps=10,scale=%s:flags=bicubic" % make_scale(self.input, 300)
        palette_cmd = '{ffmpeg}  -ss {s} -to {d} -i "{fn}"  ' \
                      '-vf "{filters},palettegen" -y {palette}'.format(
                        ffmpeg=get_ffmpeg_binary(),
                        fn=self.input,
                        s=get_time_str(self.start_time),
                        d=get_time_str(self.end_time),
                        filters=filters,
                        palette=palette,
        )
        print(palette_cmd)
        run_command(palette_cmd)
        cmd = '{ffmpeg}  -ss {s} -to {d} -i "{fn}" -i "{palette}"  ' \
              '-lavfi "{filters} [x]; [x][1:v] paletteuse" -y "{o}"'.format(
                    ffmpeg=get_ffmpeg_binary(),
                    fn=self.input,
                    s=get_time_str(self.start_time),
                    d=get_time_str(self.end_time),
                    filters=filters,
                    palette=palette,
                    o=self.output,
        )
        print(cmd)
        run = run_command(cmd)
        if os.path.exists(palette):
            os.remove(palette)
        return run



class ExportAuidoAction(BaseAction):
    def __init__(self, input_path, output_path):
        super().__init__(input_path, output_path)

    def run(self):
        cmd = '{ffmpeg}  -i "{fn}" -vn "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            o=self.output,
        )
        return run_command(cmd)


class ExportJpgAction(BaseAction):
    def __init__(self, input_path, output_path, position):
        super().__init__(input_path, output_path)
        self.p = position

    def run(self):
        cmd = '{ffmpeg}  -i "{fn}" -f  image2  -ss {draction} -vframes 1 "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            draction=get_time_str(self.p),
            o=self.output,
        )
        print(cmd)
        return run_command(cmd)


class CompressAction(BaseAction):

    def __init__(self, input_path, output_path):
        super().__init__(input_path, output_path)

    def run(self):
        cmd = '{ffmpeg} -y -i "{fn}" -vcodec h264 -acodec aac "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            o=self.output,
        )
        return run_command(cmd)


class RemoveAudioAction(BaseAction):

    def __init__(self, input_path, output_path):
        super().__init__(input_path, output_path)

    def run(self):
        cmd = '{ffmpeg} -y -i "{fn}" -c:v copy -af volume=0 "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            o=self.output,
        )
        return run_command(cmd)


class SpeedupAction(BaseAction):

    def __init__(self, input_path, output_path, speed_factor, drop_frames=True):
        super().__init__(input_path, output_path)
        self.factor = speed_factor
        self.drop_frames = drop_frames

    def get_complex_filter(self):
        rep = floor(log2(self.factor))
        additional = round(self.factor / (2 ** rep), 2)
        atempo_filters = ["atempo=2.0"] * rep + ["atempo={}".format(additional)]
        return '[0:v]setpts=PTS/{factor}[v];[0:a]{atempo}[a]'.format(
            factor=self.factor,
            atempo=",".join(atempo_filters),
        )

    def run(self):
        cmd = '{ffmpeg} -y -i "{fn}" -filter_complex "{filter}" -map "[v]" -map "[a]" "{o}"'.format(
            ffmpeg=get_ffmpeg_binary(),
            fn=self.input,
            filter=self.get_complex_filter(),
            o=self.output,
        )
        return run_command(cmd)


def get_time_str(time):
    hh = time // 3600000
    mm = (time % 3600000) // 60000
    ss = ((time % 3600000) % 60000)/1000
    return "{:02d}:{:02d}:{:.3f}".format(hh, mm, ss)


def get_video_size(movie_path):
    probe = ffmpeg.probe(movie_path)
    video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
    return video_streams[0]['width'], video_streams[0]['height']


def make_scale(movie_path,scale=400):
    video_size = get_video_size(movie_path)
    if video_size[0] < video_size[1]:
        return '-1:%s' % scale
    else:
        return '%s:-1' % scale

if __name__ == '__main__':
    print(get_time_str(3723067))