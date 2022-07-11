//
// Created by EDY on 2022/7/11.
//

#ifndef FDMLIB_LIBFDM_API_H
#define FDMLIB_LIBFDM_API_H

#ifndef WIN32 // or something like that...
#define DLLEXPORT
#else
#define DLLEXPORT __declspec(dllexport)
#endif

class FDM;

extern "C"
{
// 创建程序对象
DLLEXPORT FDM* createLibFDM(int height=256, int width=256);

// 释放程序对象
DLLEXPORT void releaseLibFDM(FDM* libfdm);

DLLEXPORT unsigned char* pixelInterpolation(FDM* libfdm, float* vertices, int verticesNum);
}

#endif //FDMLIB_LIBFDM_API_H
