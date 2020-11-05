from video_editor.actions import v2webp
import os
import time


def get_file_list(folder, keys=None):
    if keys is None:
        keys = []
    report_list = []
    if os.path.exists(folder):
        if keys:
            for file in os.listdir(folder):
                if file.split('.')[-1] in keys:
                    report_list.append(os.path.join(os.path.abspath(folder), file))
        else:
            report_list = os.listdir(folder)
        return report_list
    else:
        return None


def main():
    folder = input('请输入需要转Webp的文件夹路径:')
    videos = get_file_list(folder.strip(), ['MP4', 'mp4'])
    if videos:
        print('发现%s个MP4文件' % len(videos))
        scale = input('请输入导出的分辨率（默认160）：')
        fps = input('请输入导出的帧率（默认10fps）:')
        if not scale:
            scale = 160
        if not fps:
            fps = 10
        print('开始批量导出webp,设定分辨率：%s  帧率：%s' % (scale, fps))
        for i in videos:
            output = os.path.splitext(i)[0] + '.webp'
            v2webp(i, output, int(scale), int(fps)).run()
        print('操作完成')
        time.sleep(3)
    else:
        print('没有找到视频文件内容，请重试')
        time.sleep(3)


if __name__ == '__main__':
    while True:
        main()
