from . import constants as c


# Responses

def error(action, msg):
    return {
        'action':       action,
        'error':        msg,
    }


def stitch(flavor, chunk, camera, video_url):
    return {
        'action':       flavor,
        'camera_code':  camera,
        'chunk_name':   chunk,
        'url_stitched': video_url,
    }

# TODO: Fill with proper data once the ML module is integrated. Add other necessary info
def track(video, video_url, thumbnail, timeline):
    return {
        'action' : c.TRACK_ACTION,
        'video_id' : video,
        'video_link' : video_url,
        'thumbnail' : thumbnail,
        'timeline' : timeline
    }

def concatenate(video_id, video_url):
    return {
        'action' : c.CONCATENATE,
        'video_id' : video_id,
        'video_url' : video_url
    }

def crop(video_id, video_url, thumbnail):
    return {
        'action' : c.CROP_ACTION,
        'video_id' : video_id,
        'video_url' : video_url,
        'thumbnail' : thumbnail
    }

# TODO: Modify accordingly once the process no longer needs to mimick 
# fanaty-api's old workflow
def highlight(highlight, camera, video_url, thumbnail):
    return {
        'action': c.HIGHLIGHT_CUT,
        'camera_code': camera,
        'highlight_id': highlight,
        'url_followed': video_url,
        'thumbnail': thumbnail
    }

#TODO: Obsolete, used with user provided coordinates. Remove once we confirm 
# current workflow is working fine
def follow(highlight, camera, video_url):
    return {
        'action': c.CUSTOM_FOLLOW_ACTION,
        'camera_code': camera,
        'highlight_id': highlight,
        'url_followed': video_url
    }


def sleep(status):
    return {
        'action':       c.SLEEP_ACTION,
        'result':       status,
    }


""" Specification for processing requests

All messages should be JSON, in the form:
    {
        "action": <action>,
        ...
    }

# ToDo: add custom stitching inputs
Stitching request payload:
    {
        "action": <"stitch" or "serhii_stitch">,
        "chunk_name": <chunk_name>,
        "camera_code": <camera_code>,
        "inputs": [
            <url_1>
            <url_2>
            ...
        ],
        (optional, must be of same size as "inputs")
        "calibration_images": [
            <url_1>,
            <url_2>,
            ...
        ]
    }

Custom follow (crop equirectangular video following coordinates) request
payload:
    {
        "action": "custom_follow",
        "highlight_id": <highlight_id>,
        "camera_code": <camera_code>,
        "input": <input_video_url>,
        "coordinates": <coordinates_string>,
        (optional, not used at the moment)
        "coordinates_format": <format_specifier>
    }
Format for coordinates:
    "<frame_idx_0>\t<x_0>\t<y_0>\n<frame_idx_1>\t<x_1>\t<y_1>\n..."
# ToDo: revise whether this is the best format for this;
#       maybe replace tabs with spaces, and/or newlines with JSON array
"""
