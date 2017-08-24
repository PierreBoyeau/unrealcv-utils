import cv2
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


def setup_voc_XML(height, width, depth, image_name):
    annotation = ET.Element("annotation")
    folder = ET.SubElement(annotation, "folder")
    folder.text = "JPEGImages"
    filename = ET.SubElement(annotation, "filename")
    filename.text = os.path.basename(image_name)
    path = ET.SubElement(annotation, "path")
    path.text = image_name
    source = ET.SubElement(annotation, "source")
    database = ET.SubElement(source, "database")
    database.text = "Unknown"
    size = ET.SubElement(annotation, "size")
    width_elem = ET.SubElement(size, "width")
    width_elem.text = str(width)
    height_elem = ET.SubElement(size, "height")
    height_elem.text = str(height)
    depth_elem = ET.SubElement(size, "depth")
    depth_elem.text = str(depth)
    segmented = ET.SubElement(annotation, "segmented")
    segmented.text = "0"
    return annotation

def add_boxes(top, dets, label):
    """Draw detected bounding boxes."""
    obj = ET.SubElement(top, "object")

    name = ET.SubElement(obj, "name")
    name.text = label
    pose = ET.SubElement(obj, "pose")
    pose.text = "Unspecified"
    truncated = ET.SubElement(obj, "truncated")
    truncated.text = "0"
    difficult = ET.SubElement(obj, "difficult")
    difficult.text = "0"
    bndbox = ET.SubElement(obj, "bndbox")

    x1, x2, y1, y2 = int(dets[0]), int(dets[1]), int(dets[2]), int(dets[3])
    xmin = ET.SubElement(bndbox, "xmin")
    xmin.text = str(x1)
    ymin = ET.SubElement(bndbox, "ymin")
    ymin.text = str(y1)
    xmax = ET.SubElement(bndbox, "xmax")
    xmax.text = str(x2)
    ymax = ET.SubElement(bndbox, "ymax")
    ymax.text = str(y2)


def read_voc_shape(elem):
    size = elem.find("size")
    height = int(size.find("height").text)
    width = int(size.find("width").text)
    depth = int(size.find("depth").text)
    return height, width, depth


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    # prettify and remove empty lines
    return "\n".join([ll.rstrip() for ll in reparsed.toprettyxml(indent=" ").splitlines() if ll.strip()])


def sort_and_save_voc_xml(elem, save_path):
    image_name = elem.find("path").text
    height, width, depth = read_voc_shape(elem)
    res_elem = setup_voc_XML(height, width, depth, image_name)
    objects = elem.findall("object")
    objects.sort(key=lambda x: x.find("name").text)
    for o in objects:
        res_elem.append(o)
    with open(save_path, "w") as xmlfile:
        xmlfile.write(prettify(res_elem))


def annotate_image(image_path, bboxes_path, labels, outputFolder):
    with open(bboxes_path) as f:
        bboxes_fn = json.load(f)

    bboxes = []

    def find_label_from_unrealid(id, labels):
        id = id.lower()
        matching_labels = []
        for label in labels:
            if label in id:
                matching_labels.append(label)
        if len(matching_labels) == 0:
            # raise ValueError('Label not found')
            return None
        else:
            # Return label of max lenght (most constraining)
            matching_labels.sort(key=lambda x: len(x), reverse=True)
            return matching_labels[0]

    im = cv2.imread(image_path)
    height, width, depth = im.shape
    print(im.shape)
    for id, bbox in bboxes_fn.iteritems():
        label = find_label_from_unrealid(id, labels)
        if label is not None:
            bbox = [float(x) for x in bbox.split(',')]
            bbox = [bbox[0]*width, bbox[1]*width, bbox[2]*height, bbox[3]*height]
            bboxes.append([label, bbox])
        else:
            print("Could not find label for id {id}".format(id=id))

    top = setup_voc_XML(height, width, depth, image_path)
    for label, bbox in bboxes:  # bboxes should be a list of lists such as ['label1', (xmin, xmax, ymin, ymax)]
        add_boxes(top, bbox, label)
    saving_path = os.path.join(outputFolder, os.path.basename(image_path).split(".")[0] + ".xml")
    sort_and_save_voc_xml(top, saving_path)


if __name__ == '__main__':
    annotate_image('debug.png', '0.json', ['editorcube'], './')
