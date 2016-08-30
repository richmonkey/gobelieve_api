# RestAPI

##接口地址
* 正式:https://api.gobelieve.io

## 获取用户token
* 第三方应用的客户端通过应用服务器作为桥梁获取连接im服务器使用到的token
* 从im api服务器返回的用户token是永久有效的，第三方应用可以将token保存在自己的服务器

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

### 创建群组
- 请求地址：**POST /groups**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:


     {
        "master":"管理员id(整型)",
        "name":"群主题名",
        "super":"超级群(布尔类型,可选)"
        "members":["uid",...]
     }


- 成功响应：200

    {
        "group_id":"群组id(整型)"
    }


- 操作失败:
  400 非法的输入参数

### 获取群信息
- 请求地址：**GET /groups/{gid}**
- 是否认证：客户端授权
- 成功响应：200

    {
        "id":"群组id(整型)"
        "master":"管理员id(整型)",
        "name":"群主题名",
        "super":"是否是超级群"
        "members":[{"uid":"群成员的用户id(整型)", "name":"群成员名称"},...]
    }


- 操作失败:
  400 非法的输入参数

### 获取用户所在的所有群
- 请求地址：**GET /groups**
- 请求参数: fields=members,quiet
- 是否认证：客户端授权
- 成功响应：200

    [
      {
        "id":"群组id(整型)"
        "master":"管理员id(整型)",
        "name":"群主题名",
        "super":"是否超级群"
        "members":[{"uid":"群成员的用户id(整型)", "name":"群成员名称"},...],
        "quiet":"是否静音"
      },
      ...
    ]


- 操作失败:
  400 非法的输入参数


### 修改群组名称
- 请求地址：**PATCH /groups/{gid}**
- 是否认证：服务端授权和客户端授权
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
- 是否认证：服务端授权和客户端授权
- 成功响应：200
- 操作失败：
  400 非法的群id


### 添加群组成员
- 请求地址：**POST /groups/{gid}/members**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:

    ["uid1", "uid2", ...]
    

- 成功响应：200
- 操作失败：
  400 非法的群成员id

### 离开群
- 请求地址：**DELETE /groups/{gid}/members/{mid}**
- 是否认证：客户端授权
- 成功响应：200
- 操作失败：
  400 非法参数



### 移除群成员
- 请求地址：**DELETE /groups/{gid}/members**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:

    ["uid1", "uid2", ...]
    
- 成功响应：200
- 操作失败：
  400 非法参数



### 群组消息免打扰
- 请求地址：**POST /groups/{gid}/members/{mid}**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:

    {
        "quiet":"是否推送离线消息(整形) 0:推送通知 1:不推送通知"
    }

- 成功响应：200
- 操作失败：
状态码:400


### 群组消息免打扰模式
- 请求地址：**POST /notification/groups/{gid}**
- 是否认证：客户端授权
- 请求头:Content-Type:application/json
- 请求内容:

    {
        "quiet":"是否推送离线消息(整形) 0:推送通知 1:不推送通知"
    }

- 成功响应：200
- 操作失败：
状态码:400
