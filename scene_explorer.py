import argparse
import annotator
import cv2
import json
import os
from unrealcv import client
import sys
from time import sleep

TIME = 2.0

# TODO: Document how to create camera_traj.json
# TODO: Utilitaire de changement de luminosite
# TODO: Utilitaire de changement de materiaux, pour les murs notamment

def import_labels(labels_file):
    array = []
    with open(labels_file, "r") as ins:
        for line in ins:
            if line[-1] == '\n':
                line = line[:-1]
            array.append(line)
    return array


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Unreal Scene explorator')
    parser.add_argument('--camera_traj',
                        help='Path to camera trajectory (JSON) (e.g. camera_traj.json)',
                        default='camera_trajectory.json')
    parser.add_argument('--bboxes_path',
                        help='Path to bounding boxes folder contained in JSON (id: xmin, xmax, ymin, ymax) '
                             '(e.g. camera_trajectory.json)',
                        default='0.json')
    parser.add_argument('--images_folder',
                        help='Path to screenshots taken by UE/UnrealCV (Have same name)',
                        default='D:/Unreal Projects/demo2/Saved/Screenshots/Windows/')
    parser.add_argument('--output_folder',
                        help='Folder to save outputs',
                        default='output')
    parser.add_argument('--labels',
                        help="Path to labels list. Be careful that labels aren't ambiguous",
                        default='labels.txt')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Make folders if they don't already exist
    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)

    image_dir = os.path.join(args.output_folder, 'JPEGImages')
    annot_dir = os.path.join(args.output_folder, 'Annotations')
    for dir in [image_dir, annot_dir]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    # get the most recent file already in files
    offset = 0
    already_here = os.listdir(annot_dir)
    if already_here:
        for it in already_here:
            it_value = int(os.path.splitext(it)[0])
            if it_value > offset:
                offset = it_value
    offset += 1

    client.connect()
    if not client.isconnected():
        print('UnrealCV server is not running. Run the game first.')
        sys.exit(-1)
    res = client.request('vget /unrealcv/status')
    print(res)

    # Imports
    with open(args.camera_traj) as f:
        camera_traj = json.load(f)
    labels = import_labels(args.labels)
    num_cameras = len(camera_traj)
    for idx in range(num_cameras):
        loc, rot = camera_traj[idx]
        client.request('vset /camera/{id}/location {x} {y} {z}'.format(id=idx, **loc))
        client.request('vset /camera/{id}/rotation {pitch} {yaw} {roll}'.format(id=idx, **rot))

        client.request('vget /camera/bbox')

        # res = client.request('vget /camera/{id}/lit screen.png'.format(id=idx))
        # HighResShot rendering is way better and much more adapted to context
        client.request('vrun HighResShot 2')
        sleep(TIME)
        screenshots = os.listdir(args.images_folder)
        res = max(screenshots)
        res = os.path.join(args.images_folder, res)

        # Save image to image folder and delete older file
        # while 5 tries
            # Try to find image
            # If doesn't exist, sleep enough time.
        # TODO: Watchdog ? for event listenerw

        im = cv2.imread(res)
        im_path = os.path.join(image_dir, '{id}.jpeg'.format(id=idx+offset))
        cv2.imwrite(im_path, im)

        # Generate and save XML
        annotator.annotate_image(im_path,
                                 args.bboxes_path,
                                 labels,
                                 annot_dir)
        print('Image {id} annotated and saved.'.format(id=idx+offset))
    print('Scene explored.')