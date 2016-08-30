# RestAPI

##接口地址
* 正式:https://api.gobelieve.io


## 接口规范
### 接口支持4种HTTP方法

- **GET** 获取对象
- **PUT** 替换和更新对象
- **POST** 创建新的对象
- **DELETE** 删除对象

### HTTP返回码

- 200 成功
- 其他 失败

### HTTP 接口返回值结构

    {
        "meta": 
        {
            "code": "业务码",
            "message": "状态信息"
        },
        "data": ...
    }

*若无特殊说明以下接口响应结果指的是此结构的data字段的值。*


### 客户端授权
-请求头部: Authorization: Bearer $accesstoken


### 绑定用户id和推送token
- 请求地址：**POST /device/bind **
- 是否认证：客户端授权
- 接口说明: 客户端只要设置特定平台的字段即可， apns_device_token对应IOS客户端
           ng_device_token对应android端使用内置推送的客户端
           xg_device_token对应android端使用信鸽推送的客户端
           同一平台的客户端后一个绑定的devicetoken会覆盖前一个客户端绑定的devicetoken
           
- 请求内容：

        {
            "apns_device_token": "IOS设备token，16进制字符串(可选)",
            "ng_device_token": "android设备token，16进制字符串(可选)",
            "xg_device_token": "android 信鸽devicetoken(可选)"
            "xm_device_token": "android 小米推送的devicetoken(可选)"
            "hw_device_token": "android 华为推送的devicetoken(可选)"
            "gcm_device_token": "android google推送的devicetoken(可选)"
        }

- 成功响应 200

- 操作失败:
状态码:400

### 解除用户id和推送token之间的绑定
- 请求地址：**POST /device/unbind **
- 是否认证：客户端授权
- 接口说明: 解绑请求的内容字段和绑定接口要求是一致的，即每个客户端只能解除本客户端绑定的token
           不能解除其它客户端绑定的token
- 请求内容：

        {
            "apns_device_token": "IOS设备token，16进制字符串(可选)",
            "ng_device_token": "android设备token，16进制字符串(可选)",
            "xg_device_token": "android 信鸽devicetoken(可选)"
            "xm_device_token": "android 小米推送的devicetoken(可选)"
            "hw_device_token": "android 华为推送的devicetoken(可选)"
            "gcm_device_token": "android google推送的devicetoken(可选)"
        }

- 成功响应 200

- 操作失败:
状态码:400
