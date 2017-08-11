""""
Script that allows to generate images / xmls from a digital scene.
WARNING : objects refer to unreal IDs and not labels!
"""


from __future__ import division, absolute_import, print_function
import os, sys, time, re, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from unrealcv import client
import argparse
import json

parser = argparse.ArgumentParser(description='Generate images and xmls from Unreal Scene. The scene must be open in Unreal '
                                             'in order for this script to work')
parser.add_argument('--trajectory', help='Camera trajectories (JSON)', default='./camera_traj.json')
parser.add_argument('--objects', help='Objects categories (JSON). WARNING : objects must refer to unreal IDs and not labels!', default='./object_category.json')
args = parser.parse_args()


# TODO: replace this with a better implementation
class Color(object):
    ''' A utility class to parse color value '''
    regexp = re.compile('\(R=(.*),G=(.*),B=(.*),A=(.*)\)')

    def __init__(self, color_str):
        self.color_str = color_str
        match = self.regexp.match(color_str)
        (self.R, self.G, self.B, self.A) = [int(match.group(i)) for i in range(1, 5)]

    def __repr__(self):
        return self.color_str


def match_color(object_mask, target_color, tolerance=3):
    """Function that returns the coordinates of bbox associated with target_color mask
    The coordinates returned are (xmin, xmax, ymin, ymax)"""

    match_region = np.ones(object_mask.shape[0:2], dtype=bool)
    for c in range(3): # r,g,b
        min_val = target_color[c] - tolerance
        max_val = target_color[c] + tolerance
        channel_region = (object_mask[:,:,c] >= min_val) & (object_mask[:,:,c] <= max_val)
        match_region &= channel_region

    if match_region.sum() != 0:
        xbox, ybox = np.where(match_region)
        xmin, xmax = np.min(xbox), np.max(xbox)
        ymin, ymax = np.min(ybox), np.max(ybox)
        return xmin, xmax, ymin, ymax
    else:
        return None

def get_id2color(scene_objects):
    id2color = {}  # Map from object id to the labeling color
    for obj_id in scene_objects:
        color = Color(client.request('vget /object/%s/color' % obj_id))
        id2color[obj_id] = color
    return id2color


if __name__=='__main__':
    client.connect()
    if not client.isconnected():
        print('UnrealCV server is not running. Run the game downloaded from http://unrealcv.github.io first.')
        sys.exit(-1)
    res = client.request('vget /unrealcv/status')
    # The image resolution and port is configured in the config file.
    print(res)

    camera_trajectory = json.load(open(args.trajectory))

    num_cameras = len(camera_trajectory)
    for idx in range(num_cameras):
        loc, rot = camera_trajectory[idx]
        client.request('vset /camera/{id}/location {x} {y} {z}'.format(id=idx, **loc))
        client.request('vset /camera/{id}/rotation {pitch} {yaw} {roll}'.format(id=idx, **rot))
        # Get image
        res = client.request('vget /camera/{id}/lit {id}.png'.format(id=idx))
        print('The image is saved to %s' % res)

        # Generate image mask
        res = client.request('vget /camera/{id}/object_mask png'.format(id=idx))
        object_mask = mpimg.imread(res)

        # Associate images to all objects ids
        scene_objects = client.request('vget /objects').split(' ')
        print('Number of objects in this scene:', len(scene_objects))

        id2color = get_id2color(scene_objects)
        id2bbox = {}
        for obj_id in scene_objects:
            color = id2color[obj_id]
            bbox = match_color(object_mask, [color.R, color.G, color.B], tolerance=3)
            if bbox is not None:
                id2bbox[obj_id] = bbox
    client.disconnect()



    # TODO Trouver maniere la plus simple de sauvegarder annoations sous format xml