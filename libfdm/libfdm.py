import ctypes
import platform
import os
import numpy as np
from ctypes import c_void_p

sysstr = platform.system()
curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
lib_path = curr_path + "/"

try:
    fdm = ctypes.windll.LoadLibrary(lib_path + 'fdm_dymc.dll') if sysstr == "Windows" else ctypes.cdll.LoadLibrary(
        lib_path + 'libfdm_dymc.so')
except OSError as e:
    lib_path = curr_path + "/../FDMLib/build/"
    fdm = ctypes.windll.LoadLibrary(
        lib_path + 'Release/fdm_dymc.dll') if sysstr == "Windows" else ctypes.cdll.LoadLibrary(
        lib_path + 'libfdm_dymc.so')

fdm.createLibFDM.restype = c_void_p


class FDM(object):
    def __init__(self, height=256, width=256):
        self.height = height
        self.width = width
        self.libfdm = c_void_p(fdm.createLibFDM(self.height, self.width))
        self.n_img_type = ctypes.c_uint8 * (height * width * 1)
        fdm.pixelInterpolation.restype = ctypes.POINTER(
            ctypes.c_uint8 * (height * width * 1))

    def __del__(self):
        fdm.releaseLibFDM(self.libfdm)

    def cal_depth_face(self, vertices):
        vertices = np.reshape(np.array(vertices, dtype=np.float32), [-1, 3])
        res = fdm.pixelInterpolation(self.libfdm, vertices.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), len(vertices))
        array_pointer = ctypes.cast(res, ctypes.POINTER(self.n_img_type))
        return np.frombuffer(array_pointer.contents, dtype=np.uint8).reshape([self.height, self.width, 1]) * np.ones([1, 1, 3], dtype=np.uint8)
