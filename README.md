### 接口认证
- 认证信息放在http头部 "Authorization:Bearer $access_token"

### 获取手机验证码
- 请求地址：**POST /verify_code**
- 请求参数: zone=&number=
- 成功响应:

        {
            "code":"验证码 用于测试"
        }

- 操作失败:
  400

### 获取access_token
- 请求地址：**POST /auth/token**
- 请求内容:

        {
            "code":"验证码",
            "zone":"国家区号",
            "number":"手机号"
            "apns_device_token":"IOS device token",
        }
        
- 成功响应:

		{
            "access_token":"访问token",
            "refresh_token":"刷新token",
            "expires_in":"过期时间 单位秒",
            "user_id":"用户id"
		}

- 操作失败:
  400

### 刷新access_token
- 请求地址：**POST /auth/refresh_token**
- 是否认证：是
- 请求内容:

        {
            "refresh_token":"刷新token"
        }
    
- 成功响应:

		{
			"access_token":"访问token",
			"refresh_token":"刷新token",
			"expires_in":"过期时间 单位秒",
		}

- 操作失败:
  400
  
### 上传图片
- 请求地址:**POST /images**
- 是否认证：是
- 请求内容：图片数据
- 成功响应:

    {
        "src":"image路径",
        "src_url":"image URL"
    }

- 操作失败:
  400

### 下载图片
- 请求地址:**GET /<image_path>**

### 下载缩略图
- 在原图URL后面添加"@{width}w_{heigth}h_{1|0}c", 支持128x128, 256x256
- 比如：http://www.baidu.com/images/test.png ---> http://www.baidu.com/images/test.png@128w_128h_1c

### 上传音频
- 请求地址:**POST /audios**
- 是否认证：是
- 请求内容：音频数据
- 成功响应:

        {
            "src":"audio路径",
            "src_url":"audio URL"
        }

- 操作失败:
  400

### 下载音频
- 请求地址：**GET /<audio_path>**


### 设置头像
- 请求地址:**PUT /users/me/avatar**
- 是否认证：是
- 请求内容：头像数据
- 成功响应:

        {
            "src":"avatar路径",
            "src_url":"avatar URL"
        }

- 操作失败:
  400

### 设置昵称
- 请求地址:**PUT /users/me/nickname**
- 是否认证：是
- 请求内容：

        {
            "value":"昵称"
        }

- 成功响应: 200

- 操作失败:
  400


### 自定义状态
- 请求地址:**PUT /users/me/state**
- 是否认证:是
- 请求内容:

        {
            "value":"状态"
        }

- 成功响应: 200

- 操作失败:
  400

### 获取手机号注册状态
- 请求地址:**GET /users**
- 是否认证:是
- 请求内容:

        [
            {
                "zone":"国家区号",
                "number":"手机号",
            },
            ...
        ]

- 成功响应:


        [
            {
                "zone":"国家区号",
                "number":"手机号",
                "uid":"用户id",
                "state":"用户状态",
                "name":"用户姓名",
                "avatar":"用户头像地址",
                "up_timestamp":"最后上线时间戳"
            },
            ...
        ]

- 操作失败:
  400


- 请求地址:**PATCH /users/me**
- 是否认证:是
- 请求内容:

        
        {
        
            "state":"用户自定状态"
        },

        

- 成功响应:200

- 操作失败:
  400
