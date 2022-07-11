#include "libfdm_api.h"
#include <string.h>
#include <cmath>
#include <iostream>
using namespace std;

inline void fill_lrud(int &l, int &r, int &u, int &d, int* cache){
    l = cache[0];
    r = cache[1];
    u = cache[2];
    d = cache[3];
}

class FDM{
public:
    FDM(int height, int width): height(height), width(width){
        imgCache = new int[height * width * 4];
        img = new unsigned char [height * width];
    }

    virtual ~FDM(){
        delete []imgCache;
        delete []img;
    }

    unsigned char* pixelInterpolation(float* vertices, int verticesNum){
        //cout<<verticesNum<<" "<<width<<" "<<height<<endl;
        float minDepth = 1e32;
        float maxDepth = 0;
        for(int i = 0; i < verticesNum; ++i){
            auto curVector = vertices + i * 3;
            if(curVector[0] < width && curVector[1] < height){
                minDepth = fmin(minDepth, curVector[2]);
                maxDepth = fmax(maxDepth, curVector[2]);
            }
        }
        float deltaDepth = maxDepth - minDepth;
        //cout<<minDepth<<" "<<maxDepth<<endl;

        // 填写深度图
        memset(img, 0, height * width * sizeof (unsigned char));
        for(int i = 0; i < verticesNum; ++i){
            auto curVector = vertices + i * 3;
            if(curVector[0] < width && curVector[1] < height){
                float depth = (curVector[2] - minDepth) / deltaDepth * 0.98f;
                img[int(curVector[1]) * width + int(curVector[0])] = (unsigned char)(depth * depth * 255.f);
            }
        }

        // 填写晚深度图后会有很多漏空的像素，先填写缓存，记录镂空像素周围那个点有颜色
        memset(imgCache, 0, height * width * 4 * sizeof (float ));
        for(int j = 0; j < width; ++j){
            int l = -1;
            int r = -1;
            for(int i = 0; i < height; ++i){
                auto offset = i * width + j;
                if(img[offset] > 0)
                    l = i;
                imgCache[offset * 4] = l;

                offset = (height - 1 - i) * width + j;
                if(img[offset] > 0)
                    r = height - 1 - i;
                imgCache[offset * 4 + 1] = r;
            }
        }

        for(int i = 0; i < height; ++i){
            int u = -1;
            int d = -1;
            for(int j = 0; j < width; ++j){
                auto offset = i * width + j;
                if(img[offset] > 0)
                    u = j;
                imgCache[offset * 4 + 2] = u;
                offset = i * width + (width - 1 - j);
                if(img[offset] > 0)
                    d = width - 1 - j;
                imgCache[offset * 4 + 3] = d;
            }
        }

        // 开始填写镂空像素
        int l, r, u, d;
        for(int i = 0; i < height; ++i){
            for(int j = 0; j < width; ++j){
                auto offset = i * width + j;
                if(img[offset] > 2)
                    continue;
                auto curCache = imgCache + offset * 4;
                fill_lrud(l, r, u, d, curCache);
                if(l >= 0 && r >= 0){
                    if(r-l <= d-u || d < 0 || u < 0){
                        auto lc = img[l * width + j];
                        auto rc = img[r * width + j];
                        img[offset] = (unsigned char)((lc * (r - i) + rc * (i - l)) / (r - l + 1e-5));
                    } else {
                        auto uc = img[i * width + u];
                        auto dc = img[i * width + d];
                        img[offset] = (unsigned char)((uc * (d - j) + dc * (j - u)) / (d - u + 1e-5));
                    }
                } else if(curCache[2] >= 0 && curCache[3] >= 0){
                    auto uc = img[i * width + u];
                    auto dc = img[i * width + d];
                    img[offset] = (unsigned char)((uc * (d - j) + dc * (j - u)) / (d - u + 1e-5));
                }
            }
        }
        return img;
    }

protected:
    int height;
    int width;

    // 缓存一个像素上下左右第一个有值的像素位置
    int* imgCache;
    // 缓存深度图
    unsigned char* img;
};

extern "C"
{
// 创建程序对象
DLLEXPORT FDM* createLibFDM(int height, int width){
    return new FDM(height, width);
}

// 释放程序对象
DLLEXPORT void releaseLibFDM(FDM* libfdm){
    delete libfdm;
}

DLLEXPORT unsigned char* pixelInterpolation(FDM* libfdm, float* vertices, int verticesNum){
    return libfdm->pixelInterpolation(vertices, verticesNum);
}

}
