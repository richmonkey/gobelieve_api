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



### 获取历史消息
- 请求地址：** GET /supporters?store_id=咨询台id **
- 是否认证：客户端认证
- 请求参数: store=(可选)

        
- 成功响应：200


        {
            "seller_id":"客服id",
            "name":"客服名称",
            "avatar":"客服头像",
            "status":"客服状态 online/offline"
        }
        
            
- 操作失败：
  400 非法参数

### 获取离线消息数目
- 请求地址：** GET /messages/offline **
- 是否认证：服务器认证
- 请求参数: customer_id=&platform_id=(可选)&device_id=(可选)
        
- 成功响应：200

        {
            "new":"1或者0"
        }

- 操作失败：
  400 非法参数




### 获取历史消息
- 请求地址：** GET /messages **
- 是否认证：客户端认证
- 请求参数: store=(可选)

        
- 成功响应：200

        [
            {
               "id":"消息id",
               "content":"消息内容",
               "timestamp":"消息时间"
            }
            ...
        ]

- 操作失败：
  400 非法参数


### 将消息移出离线队列
- 请求地址：** POST /messages/dequeue **
- 是否认证：客户端认证
- 请求内容:


        {
            "msgid":"最近消息id",
        }
        
- 成功响应：200

- 操作失败：
  400 非法参数

