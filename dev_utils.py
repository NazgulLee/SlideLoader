import hashlib
import os
import json
import requests

import openslide

post_url = "http://ca-data:9099/services/caMicroscope/Slide/submit/json" 



# given a path, get metadata
def getMetadata(filename, upload_folder):
    # TODO consider restricting filepath
    metadata = {}
    filepath = os.path.join(upload_folder, filename)
    if not os.path.isfile(filepath):
        msg = {"error": "No such file"}
        print(msg)
        return msg
    metadata['filename'] = filepath
    try:
        slide = openslide.OpenSlide(filepath)
    except BaseException as e:
        return {"type": "Openslide", "error": str(e)}
    slideData = slide.properties
    metadata['mpp-x'] = slideData.get(openslide.PROPERTY_NAME_MPP_X, None)
    metadata['mpp-y'] = slideData.get(openslide.PROPERTY_NAME_MPP_Y, None)
    metadata['height'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_HEIGHT, None) or slideData.get(
        "openslide.level[0].height", None)
    metadata['width'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_WIDTH, None) or slideData.get(
        "openslide.level[0].width", None)
    metadata['vendor'] = slideData.get(openslide.PROPERTY_NAME_VENDOR, None)
    metadata['level_count'] = int(slideData.get('level_count', 1))
    metadata['objective'] = float(slideData.get("aperio.AppMag", None))
    metadata['md5sum'] = file_md5(filepath)
    print(metadata)
    return metadata


def postslide(img, url):
    print('here')
    payload = json.dumps(img)
    res = requests.post(url, data=payload, headers={'content-type': 'application/json'})
    if res.status_code < 300:
        img['_status'] = 'success'
    else:
        img['_status'] = res.status_code
    print(img)
    return img


# given a list of path, get metadata for each
def getMetadataList(filenames, upload_folder):
    allData = []
    for filename in filenames:
        allData.append(getMetadata(filename, upload_folder))
    return allData


def file_md5(fileName):
    m = hashlib.md5()
    blocksize = 2 ** 20
    with open(fileName, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def hello():
    print('hello!')

