import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from logto import LogtoClient, LogtoConfig, LogtoException, Storage
from starlette.middleware.sessions import SessionMiddleware
import httpx
import uvicorn
from typing import Optional, Union
from dotenv import load_dotenv


load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(title="FastAPI Logto Demo")

# 添加 session 中间件，用于存储认证状态
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production"  # 在生产环境中请更改为安全的密钥
)

# Logto 配置
logto_config = LogtoConfig(
    endpoint=os.getenv('LOGTO_ENDPOINT', ''),
    appId=os.getenv('LOGTO_APPID', ''),
    appSecret=os.getenv('LOGTO_APPSECRET', ''),
    # scopes=['openid', 'profile', 'email'],
    # resources=['你的API资源ID']  # 可选，如果有受保护的API资源
)


class SessionStorage(Storage):

    def __init__(self, session) -> None:
        self.session = session

    def get(self, key: str) -> Union[str, None]:
        print('get', key)
        return self.session.get(key, None)

    def set(self, key: str, value: Union[str, None]) -> None:
        print('set', key, value)
        self.session[key] = value

    def delete(self, key: str) -> None:
        self.session.pop(key, None)


# # 创建 Logto 客户端
# logto_client = LogtoClient(
#     logto_config,
#     storage=SessionStorage()
# )


async def get_current_user(request: Request):
    """获取当前用户辅助函数"""
    try:
        # 创建 Logto 客户端
        logto_client = LogtoClient(
            logto_config,
            storage=SessionStorage(request.session)
        )
        # 验证 ID Token
        user_info = await logto_client.fetchUserInfo()
        return user_info
    except LogtoException as e:
        print(e)
        return None


@app.get("/")
async def homepage(request: Request):
    """首页路由"""
    user = await get_current_user(request)
    if user:
        return {
            "message": "已登录",
            "user": user,
            "authenticated": True
        }
    else:
        return {
            "message": "未登录",
            "authenticated": False,
            "login_url": "/login"
        }

# 登录路由


@app.get("/login")
async def login(request: Request):
    # 生成登录 URL 并重定向
    # 创建 Logto 客户端
    logto_client = LogtoClient(
        logto_config,
        storage=SessionStorage(request.session)
    )
    sign_in_url = await logto_client.signIn(
        redirectUri="http://127.0.0.1:8000/callback",
    )
    # print(sign_in_url)
    return RedirectResponse(sign_in_url)


@app.get("/logout")
async def logout(request: Request):
    """登出路由"""

    # 创建 Logto 客户端
    logto_client = LogtoClient(
        logto_config,
        storage=SessionStorage(request.session)
    )

    # 生成登出 URL 并重定向
    # sign_out_url = await logto_client.signOut("http://127.0.0.1:8000")
    # return RedirectResponse(sign_out_url)

    await logto_client.signOut()
    return {'code': 200, 'message': '成功登出'}


@app.get("/callback")
async def callback(request: Request):
    """授权回调路由"""
    # print(request.url)
    try:
        # 使用授权码获取令牌
        # tokens = await logto_client.get_oidc_tokens_by_authorization_code(code)

        # 创建 Logto 客户端
        logto_client = LogtoClient(
            logto_config,
            storage=SessionStorage(request.session)
        )

        # Handle a lot of stuff
        await logto_client.handleSignInCallback(str(request.url))

        # 重定向到首页
        return RedirectResponse("/")
    except LogtoException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )


@app.get("/protected")
async def protected_resource(request: Request):
    """受保护的资源路由示例"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {
        "message": "这是受保护的资源",
        "user_id": user.get("sub"),
        "username": user.get("name", "未知用户名")
    }

# 用户信息路由


@app.get("/user-info")
async def user_info(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )
    return user

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
