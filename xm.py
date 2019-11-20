#!/usr/bin/env python3
import sys,os 
import subprocess
import click

@click.command()
@click.argument('input_file')
@click.option('--channel','-c',help='The channel access')
def startup(input_file, channel):
    path, file_name = os.path.split(input_file)
    if len(path) == 0:
        path = os.getcwd()
    if (channel):
        subprocess.call(['docker','run','-it','--rm','-v','/dev/snd:/dev/snd','-v','{}:/sound'.format(path),'-v','/home/marc/Desktop/sound_docker/:/temp/','--privileged','audio2','/temp/sel1.py',file_name, channel])
    else:
        subprocess.call(['docker','run','-it','--rm','-v','/dev/snd:/dev/snd','-v','{}:/sound'.format(path),'-v','/home/marc/Desktop/sound_docker/:/temp/','--privileged','audio2','/temp/sel1.py',file_name])

startup()



