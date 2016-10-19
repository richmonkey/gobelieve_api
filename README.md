gobelieve API
=============
官方主页: http://developer.gobelieve.io
文档地址: http://developer.gobelieve.io/static/docs/im/Server.html



### 获取认证token
- 请求地址：** POST /auth/customer **
- 是否认证：否
- 请求内容:

        {
            "appid":"应用id(整型)",
            "uid":"用户id(整型)",
            "user_name":"用户名称",
            "platform_id":"平台id,1:ios, 2:android, 3:web(可选)",
            "device_id":"设备id(可选)"
        }
        
- 成功响应：200

        {
            "token":"访问token",
            "store_id":"咨询台id"
        }

- 操作失败：
  400 非法参数
