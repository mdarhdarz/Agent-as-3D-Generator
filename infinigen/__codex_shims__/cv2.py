import numpy as np
import OpenEXR
from PIL import Image

IMREAD_ANYCOLOR = 0
IMREAD_ANYDEPTH = 0
COLOR_BGR2RGB = 1
COLOR_RGB2BGR = 2
INTER_LINEAR = 1
INTER_LANCZOS4 = 4
MORPH_ELLIPSE = 2
MORPH_OPEN = 3


def _normalize_dsize(dsize):
    if not isinstance(dsize, (tuple, list)) or len(dsize) != 2:
        raise ValueError(f"Unsupported resize target: {dsize}")
    width, height = int(dsize[0]), int(dsize[1])
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid resize target: {dsize}")
    return width, height


def resize(arr, dsize, interpolation=None):
    del interpolation
    arr = np.asarray(arr)
    width, height = _normalize_dsize(dsize)

    if arr.ndim < 2:
        raise ValueError("cv2.resize shim expects at least 2D input")

    y_idx = np.linspace(0, arr.shape[0] - 1, height).round().astype(int)
    x_idx = np.linspace(0, arr.shape[1] - 1, width).round().astype(int)

    if arr.ndim == 2:
        return arr[np.ix_(y_idx, x_idx)]

    return arr[y_idx][:, x_idx]


def cvtColor(img, code):
    arr = np.asarray(img)
    if code in (COLOR_BGR2RGB, COLOR_RGB2BGR) and arr.ndim == 3 and arr.shape[2] >= 3:
        if arr.shape[2] == 3:
            return arr[..., ::-1].copy()
        return arr[..., [2, 1, 0, *range(3, arr.shape[2])]].copy()
    raise NotImplementedError(f"cv2 shim does not support color code {code}")


def _exr_numpy_dtype(channel_type):
    channel_name = str(channel_type)
    if channel_name == "HALF":
        return np.float16
    if channel_name == "FLOAT":
        return np.float32
    if channel_name == "UINT":
        return np.uint32
    raise NotImplementedError(f"Unsupported EXR channel type: {channel_name}")


def _read_exr(path):
    exr = OpenEXR.InputFile(str(path))
    header = exr.header()
    channels = list(header["channels"].keys())
    dw = header["dataWindow"]
    height = dw.max.y - dw.min.y + 1
    width = dw.max.x - dw.min.x + 1

    if {"B", "G", "R"}.issubset(channels):
        read_order = ["B", "G", "R"]
    elif {"X", "Y", "Z"}.issubset(channels):
        # load_exr() in Infinigen applies BGR->RGB after imread(), so feed
        # channels in reverse here to recover XYZ after cvtColor().
        read_order = ["Z", "Y", "X"]
    elif len(channels) >= 3:
        read_order = list(reversed(channels[:3]))
    else:
        read_order = channels[:1]

    arrays = []
    for channel_name in read_order:
        channel_type = header["channels"][channel_name].type
        np_type = _exr_numpy_dtype(channel_type)
        channel = np.frombuffer(exr.channel(channel_name, channel_type), dtype=np_type)
        channel = channel.reshape((height, width))
        if channel.dtype == np.float16:
            channel = channel.astype(np.float32)
        arrays.append(channel)

    if len(arrays) == 1:
        return arrays[0]
    return np.stack(arrays, axis=-1)


def imread(path, flags=None):
    del flags
    if str(path).lower().endswith(".exr"):
        return _read_exr(path)
    with Image.open(path) as img:
        return np.array(img)


def imwrite(path, img):
    arr = np.asarray(img)
    if arr.dtype.kind == "f":
        arr = np.clip(arr, 0, 1)
        arr = (arr * 255).astype(np.uint8)
    Image.fromarray(arr).save(path)
    return True


def getStructuringElement(shape, ksize):
    del shape
    return np.ones(tuple(ksize), dtype=np.uint8)


def morphologyEx(src, op, kernel):
    del op, kernel
    return np.asarray(src)
