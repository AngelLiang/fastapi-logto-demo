# fastapi logto demo

fastapi 使用 logto 示例

## 依赖

- python3
- uv
- fastapi

## 如何使用

1、初始化开发环境

```
pip install uv
uv sync
```

2、配置logto

到logto的应用配置页面获取endpoint，appid和appsecret，配置的环境变量

```
cp .env.example .env
```

```
LOGTO_ENDPOINT=
LOGTO_APPID=
LOGTO_APPSECRET=
```

到logto的应用配置页面，配置重定向URL

- 重定向 URIs：http://127.0.0.1:8000/callback

4、启动服务

```
uv run python main.py
```

5、测试流程

浏览器访问 http://127.0.0.1:8000/login 即可自动跳转到logto的登录页面

登录之后可以访问 http://127.0.0.1:8000/ 首页查看信息

访问 http://127.0.0.1:8000/protected 可以查看受保护的资源，未登录不能查看

访问 http://127.0.0.1:8000/logout 登出

## 其他

logto_m2m_client.py 是对接 logto 的管理接口模块
