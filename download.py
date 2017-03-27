import subprocess, os
import argparse
import youtube_dl
from multiprocessing import Queue
from threading import Thread
from subprocess import check_call
from common.log import setup_logging
import logging
import json
import numpy
from PIL import Image
import time
# http://cs.uky.edu/~jacobs/datasets/timelapse_clouds/
file_dirpath = os.path.dirname(__file__)
setup_logging()
logger = logging.getLogger(__name__)

class Video(object):
    def __init__(self, d_set_dir, yt_id, width, height):
        self.logger = logger = logging.getLogger(__name__)
        self.d_set_dir = d_set_dir
        self.yt_id = yt_id
        self.width = width
        self.height = height
        self.queue = Queue()

    def dl_and_cut(self):
        # Use youtube_dl to download the video
        FNULL = open(os.devnull, 'w')
        self.logger.info(self.yt_id)
        self.output_path = os.path.join(self.d_set_dir, self.yt_id)+'.mp4'
        if os.path.exists(self.output_path):
            self.logger.info(self.output_path)
            self.logger.info("already exist.")
        else:
            try:
                self.logger.info("begin to download...")
                self.logger.info(self.output_path)
                check_call(['youtube-dl', \
                #'--no-progress', \
                '-f', 'best[ext=mp4]', \
                '-o', self.output_path, \
                'https://www.youtube.com/watch?v='+self.yt_id ], \
                stdout=FNULL,stderr=subprocess.STDOUT)
            except:
                logger.error(self.yt_id)
        self.logger.info("begin to extract...")
        self._extract()
        #self._extract_by_pipe()

    def _worker(self):
        while not self.queue.empty():    # exit when queue is clear
            (img_id, img_name) = self.queue.get()  # remove and return an item from the queue
            self.img_list[img_id].save(img_name)
            #self.img_list[img_id].save(img_name, compress_level=1)

    def _extract_by_pipe(self):
        proc = subprocess.Popen(['ffmpeg',
            "-i", "{0}".format(self.output_path),
            "-f", "image2pipe",
            "-pix_fmt", "rgb24",
            "-r", "6",
            "-threads", "4",
            "-loglevel", "panic",
            "-vcodec", "rawvideo",
            "-"],
            stdout=subprocess.PIPE,
        )
        img_id = 0
        ## write png
        if not os.path.exists("{0}/{1}".format("sequences", self.yt_id)):
            os.makedirs("{0}/{1}".format("sequences", self.yt_id))
        ## FFMpeg pipe to python
        time_start = time.time()
        self.img_list = []
        while True:
            raw_image = proc.stdout.read(640 * 360 * 3)
            if not raw_image:
                break
            #image =  numpy.fromstring(raw_image, dtype='uint8').reshape((360, 640, 3))
            #img = Image.fromarray(image, 'RGB')
            #self.img_list.append(img)
            #self.queue.put((img_id, "{0}/{1}/{2}.jpg".format("sequences",self.yt_id, img_id)))
            #img.save("{0}/{1}/{2}.png".format("sequences",self.yt_id, img_id), compress_level=1)
            #img_id = img_id + 1

        time_end = time.time()
        print time_end-time_start
        print 'All files are piped'

        #time_start = time.time()
        #NUM_THREADS = 8
        #threads = map(lambda i: Thread(target=self._worker), xrange(NUM_THREADS))
        #map(lambda th: th.start(), threads)
        #map(lambda th: th.join(), threads)
        #time_end = time.time()
        #print time_end-time_start
        #print 'All files are saved'

    def _extract(self):
        time_start = time.time()
        command = "ffmpeg -i {} ".format(self.output_path)
        command = command + "-vf fps={} -threads {} -loglevel panic ".format(6, 4)
        command = command + "{}".format(os.path.join("sequences", self.yt_id, "%d.png"))
        print command
        if not os.path.exists("{0}/{1}".format("sequences", self.yt_id)):
            os.makedirs("{0}/{1}".format("sequences", self.yt_id))
        subprocess.call(command, shell=True)
        time_end = time.time()
        print time_end-time_start
        print 'All files are saved'

def main():
    pass

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Arguments for youtube_dl')
    # Set input video path
    parser.add_argument('--input', dest='json_path',
                        help='json file of playlist. (youtube-dl -j <playlist> >> <json_path>)',
                        required=True, type=str)
    parser.add_argument('--output', dest='output_folder', help='output folder',
                        required=True, type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    #main()
    with open(args.json_path) as f:
        json_data = json.load(f)

    for i in range(1): #retry 5 times
        for entry in json_data['entries']:
            v = Video(d_set_dir=args.output_folder,
                      yt_id=entry['id'],
                      width=entry['width'],
                      height=entry['height'])
            v.dl_and_cut()

