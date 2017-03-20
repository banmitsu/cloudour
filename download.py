import subprocess, os
import argparse
import youtube_dl
from subprocess import check_call
from common.log import setup_logging
import logging
import json
# http://cs.uky.edu/~jacobs/datasets/timelapse_clouds/
file_dirpath = os.path.dirname(__file__)
setup_logging()
logger = logging.getLogger(__name__)

class Video(object):
    def __init__(self, d_set_dir, yt_id):
        self.logger = logger = logging.getLogger(__name__)
        self.d_set_dir = d_set_dir
        self.yt_id = yt_id

    def dl_and_cut(self):
        d_set_dir = self.d_set_dir

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
                '-f','best[ext=mp4]', \
                '-o',self.output_path, \
                'https://www.youtube.com/watch?v='+self.yt_id ], \
                stdout=FNULL,stderr=subprocess.STDOUT)
                #   'youtu.be/'+vid.yt_id ], 
            except:
                logger.error(self.yt_id)

    def extract(self):
        pass

def main():
    pass

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Arguments for youtube_dl')   
    # Set input video path
    parser.add_argument('--input', dest='json_path', help='json file of playlist. (youtube-dl -j <playlist> >> <json_path>)',
                        required=True, type = str)    
    parser.add_argument('--output', dest='output_folder', help='output folder',
                        required=True, type = str)    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    #main()
    with open(args.json_path) as f:
        json_data = json.load(f)
    
    for i in range(5): #retry 5 times
        for entry in json_data['entries']:
            v = Video(d_set_dir=args.output_folder, yt_id=entry['id'])
            v.dl_and_cut()

