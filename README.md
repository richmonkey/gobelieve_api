# RestAPI

##接口地址
* 正式:https://api.gobelieve.io

## 获取用户token
* 第三方应用的客户端通过应用服务器作为桥梁获取连接im服务器使用到的token
* 从im api服务器返回的用户token是永久有效的

## 接口规范
接口支持4种HTTP方法

- **GET** 获取对象
- **PUT** 替换和更新对象
- **POST** 创建新的对象
- **DELETE** 删除对象

HTTP返回码

- 200 成功
- 其他 失败

HTTP 接口返回值结构

    {
        "meta": 
        {
            "code": "业务码",
            "message": "状态信息"
        },
        "data": ...
    }
    *若无特殊说明以下接口响应结果指的是此结构的data字段的值。*


第三方服务端授权

- 请求地址: 所有可供第三方服务端访问的接口
- 请求头部: Authorization: Basic $base64(appid:$hex_md5(appsecret))


客户端授权

- 请求地址: 所有可供客户端访问的接口
- 请求头部: Authorization: Bearer $token


### 第三方应用获取永久有效的access token
- 请求地址：** POST /auth/grant**
- 是否认证：服务端授权
- 请求内容:

        {
            "uid":"用户id（整型）"
            "user_name":"用户名"
            "platform_id":"平台id,1:ios, 2:android, 3:web(可选)"
            "device_id":"设备id(可选)"
        }
        
- 成功响应：200

        {
            "token":"访问token"
        }
    
- 操作失败：
  400 非法参数

### 个人设置
- 请求地址：** POST /users/{uid}**
- 是否认证：服务端授权
- 请求内容:

        {
            "name":"用户名",
        
            "do_not_disturb": {"peer_uid":"联系人id", "on":"开/关"},

            "mute":"手机静音(布尔类型)"
        }
        
- 成功响应：200
    
- 操作失败：
  400 非法参数


服务端群组管理接口
==========
### 创建群组
- 请求地址：**POST /groups**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
           "master":"管理员id(整型)",
           "name":"群主题名",
           "super":"超级群(布尔类型,可选)"
           "members":[{"uid":"群成员id", "name":"群组成员名", "avatar":"群组成员头像"},...]
        }


- 成功响应：200

        {
            "group_id":"群组id(整型)"
        }


- 操作失败:
  400 非法的输入参数

### 修改群组名称
- 请求地址：**PATCH /groups/{gid}**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
           "name":"群主题名",
        }


- 成功响应：200

- 操作失败:
  400 非法的输入参数


### 解散群组
- 请求地址：**DELETE /groups/{gid}**
- 是否认证：服务端授权
- 成功响应：200
- 操作失败：
  400 非法的群id

### 添加群组成员
- 请求地址：**POST /groups/{gid}/members**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
            "members":[
                {
                    "uid":"群成员id"
                    "name":"群组成员名",
                    "avatar":"群组成员头像"
                },
                ...
            ],
            "inviter":{"uid":"邀请人id", "name":"邀请人昵称"}
        }
    

- 成功响应：200
- 操作失败：
  400 非法的群成员id

### 离开群
- 请求地址：**DELETE /groups/{gid}/members/{mid}**
- 是否认证：服务端授权
- 成功响应：200
- 操作失败：
  400 非法参数


### 移除群成员
- 请求地址：**DELETE /groups/{gid}/members**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:



        ["uid1", "uid2", ...]

        or
         
        [
            {
                "uid:", "群组成员id",
                "name":"群组成员名",
                "avatar":"群组成员头像"
            },
            ...
        ]
         
- 成功响应：200
- 操作失败：
  400 非法参数



### 普通群升级成超级群
- 请求地址：**POST /groups/{gid}/upgrade**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json

- 成功响应：200
- 操作失败：
  400 非法参数



### 群设置
- 请求地址：**PATCH /groups/{gid}/members/{memberid}**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "do_not_disturb":"免打扰选项(布尔类型)",
        
            "nickname":"群内昵称",

            "mute":"群内禁言"
        }


do_not_disturb和nickname一次只能设置一个选项

- 成功响应：200
- 操作失败：
  400 非法参数






消息接口
===============

### 发送点对点消息
- 请求地址：**POST /messages/peers**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "sender":"发送者uid(整型)",
            "receiver":"接受者uid(整型)",
            "content":"消息内容",
        }

- 成功响应：200
- 操作失败：
  状态码:400

### 发送群组消息
- 请求地址：**POST /messages/groups**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "sender":"发送者uid(整型)",
            "receiver":"群组id(整型)",
            "content":"消息内容",
        }

- 成功响应：200
- 操作失败：
  状态码:400

### 发送系统消息
- 请求地址：**POST /messages/systems**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "receiver":"接受者id(整型)",
            "content":"消息内容",
        }

- 成功响应：200
- 操作失败：
  状态码:400



### 发送在线个人通知消息
- 请求地址：**POST /messages/notifications**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "receiver":"接受者id(整型)",
            "content":"消息内容",
        }

- 成功响应：200
- 操作失败：
  状态码:400


### 发送群通知消息
- 请求地址：**POST /messages/groups/notifications**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "group_id":"群id(整型)",
            "content":"消息内容",
        }

- 成功响应：200
- 操作失败：
  状态码:400





#客服接口

### 获取认证token
- 请求地址：** POST /auth/customer **
- 是否认证：否
- 请求内容:

        {
            "appid":"应用id(整型)",
            "customer_id":"顾客id",
            "name":"用户名称",
            "avatar":"头像url",
            "platform_id":"平台id,1:ios, 2:android, 3:web(可选)",
            "device_id":"设备id(可选)"
        }
        
- 成功响应：200

        {
            "token":"访问token",
            "store_id":"咨询台id",
            "client_id":"客户id"
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






客户端群组管理接口
==========
### 创建群组
- 请求地址：**POST /client/groups**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
           "master":"管理员id(整型)",
           "name":"群主题名",
           "super":"超级群(布尔类型,可选)"
           "members":[{"uid":"群成员id", "name":"群组成员名", "avatar":"群组成员头像"},...]
        }


- 成功响应：200

        {
            "group_id":"群组id(整型)"
        }


- 操作失败:
  400 非法的输入参数

### 创建群组
- 请求地址：**GET /client/groups?fields=members,quiet**
- 是否认证：客户端授权



- 成功响应：200

        [
            {
                "id":"群组id(整型)",
                "master":"管理员id",
                "super":"超级群(1/0)",
                "name":"群名",
                "notice":"群公告",
                "members":[
                    "uid":"成员id",
                    "name":"用户昵称",
                    "nickname":"群内昵称",
                ],
                "do_not_disturb":"免打扰设置项"
            }
        ]




### 修改群组名称
- 请求地址：**PATCH /client/groups/{gid}**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
            "name":"群主题名",
            "notice":"群公告",
        }


name和notice一次只能设置一个选项

- 成功响应：200

- 操作失败:
  400 非法的输入参数


### 解散群组
- 请求地址：**DELETE /client/groups/{gid}**
- 是否认证：客户端授权
- 成功响应：200
- 操作失败：
  400 非法的群id

### 添加群组成员
- 请求地址：**POST /client/groups/{gid}/members**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:


        {
            "members":[
                {
                    "uid":"群成员id"
                    "name":"群组成员名",
                    "avatar":"群组成员头像"
                },
                ...
            ],
        }
    

- 成功响应：200
- 操作失败：
  400 非法的群成员id

### 离开群
- 请求地址：**DELETE /client/groups/{gid}/members/{mid}**
- 是否认证：客户端授权
- 成功响应：200
- 操作失败：
  400 非法参数


### 移除群成员
- 请求地址：**DELETE /client/groups/{gid}/members**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

         
        [
            {
                "uid:", "群组成员id",
                "name":"群组成员名",
                "avatar":"群组成员头像"
            },
            ...
        ]
         
- 成功响应：200
- 操作失败：
  400 非法参数


### 群设置
- 请求地址：**PATCH /client/groups/{gid}/members/{memberid}**
- 是否认证：服务端授权
- 请求头:Content-Type:application/json
- 请求内容:

        {
            "do_not_disturb":"免打扰选项(布尔类型)",
        
            "nickname":"群内昵称",
    
        }


do_not_disturb和nickname一次只能设置一个选项

- 成功响应：200
- 操作失败：
  400 非法参数


