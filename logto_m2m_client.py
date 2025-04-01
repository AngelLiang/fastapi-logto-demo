import httpx
import base64
import os
from typing import Dict, Any
import asyncio

from dotenv import load_dotenv
load_dotenv()

# Logto配置
logto_url = os.getenv('LOGTO_MANAGEMENT_URL', '')  # 替换为你的Logto端点
logto_api_url = logto_url + '/api'
token_url = logto_url + '/oidc/token'
LOGTO_APPID = os.getenv('LOGTO_M2M_APPID', '')
LOGTO_APPSECRET = os.getenv('LOGTO_M2M_APPSECRET', '')
# tenant_id = 'defualt'


class LogtoM2MClient:

    def __init__(self) -> None:
        self.access_token = ''
        self.timeout = 60
        self.headers = {}

    def generate_headers(self, access_token):
        return {
            'Authorization': f'Bearer {access_token}',
        }

    async def fetch_access_token(self) -> Dict:
        """
        获取Logto访问令牌

        返回:
            Dict[str, Any]: 包含访问令牌的响应数据
        """
        url = logto_url + '/oidc/token'
        # 创建Basic认证头
        auth_str = f"{LOGTO_APPID}:{LOGTO_APPSECRET}"
        auth_bytes = auth_str.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

        # 准备请求头和请求体
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_b64}'
        }

        data = {
            'grant_type': 'client_credentials',
            # 'resource': logto_api_url,

            # NOTE: logto默认的api链接，根据logto控制台来修改，如果不对则会返回 resource indicator is missing, or unknown 错误
            'resource': 'https://default.logto.app/api',

            'scope': 'all'
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, timeout=self.timeout)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def get_applications(self, access_token: str) -> Dict:
        """获取应用列表

        ref: https://openapi.logto.io/operation/operation-listapplications
        """
        url = logto_url + '/api/applications'
        headers = self.generate_headers(access_token)

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=self.timeout)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def verify_user_password(self, access_token: str, user_id, password) -> int:
        """获取应用列表

        ref: https://openapi.logto.io/operation/operation-verifyuserpassword


        204
        User password matches.

        400
        Bad Request

        401
        Unauthorized

        403
        Forbidden

        404
        Not Found

        422
        User password does not match.

        """
        url = logto_url + f'/api/users/{user_id}/password/verify'
        headers = self.generate_headers(access_token)

        data = {
            "password": password
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.status_code

    async def update_user_password(self, access_token: str, user_id, password) -> Dict:
        """更新用户密码

        ref: https://openapi.logto.io/operation/operation-updateuserpassword

        """
        url = logto_url + f'/api/users/{user_id}/password'
        headers = self.generate_headers(access_token)

        data = {
            "password": password
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, data=data)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def create_user(self, access_token: str, json={}) -> Dict:
        """
        创建用户

        json example

        {
            "primaryPhone": "string",
            "primaryEmail": "string",
            "username": "string",
            "password": "string",
            "passwordDigest": "string",
            "passwordAlgorithm": "Argon2i",
            "name": "string",
            "avatar": "string",
            "customData": {},
            "profile": {
                "familyName": "string",
                "givenName": "string",
                "middleName": "string",
                "nickname": "string",
                "preferredUsername": "string",
                "profile": "string",
                "website": "string",
                "gender": "string",
                "birthdate": "string",
                "zoneinfo": "string",
                "locale": "string",
                "address": {
                "formatted": "string",
                "streetAddress": "string",
                "locality": "string",
                "region": "string",
                "postalCode": "string",
                "country": "string"
                }
            }
        }

        ref: https://openapi.logto.io/operation/operation-createuser
        """
        url = logto_url + f'/api/users'
        headers = self.generate_headers(access_token)

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def get_users(self, access_token: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        Get users with filters and pagination.

        ref: https://openapi.logto.io/operation/operation-listusers
        """
        url = logto_url + f'/api/users'
        headers = self.generate_headers(access_token)

        params = {
            'page': page,
            'page_size': page_size
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def get_total_user_count(self, access_token: str) -> Dict:
        url = logto_url + f'/api/dashboard/users/total'
        headers = self.generate_headers(access_token)

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def get_roles_for_user(self, access_token: str, user_id: str, page: int = 1, page_size: int = 20) -> Dict:
        """

        ref: https://openapi.logto.io/operation/operation-listuserroles
        """
        url = logto_url + f'/api/users/{user_id}/roles'
        headers = self.generate_headers(access_token)

        params = {
            'page': page,
            'page_size': page_size
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def send_phone_code(self, access_token: str, phone: str) -> int:
        """
        发送手机短信验证码

        ref: https://openapi.logto.io/operation/operation-createverificationcode

        Responses
            204
            Verification code requested and sent successfully.

            400
            Bad request. The payload may be invalid.

            401
            Unauthorized

            403
            Forbidden

            501
            Not Implemented
        """
        url = logto_url + f'/api/verification-codes'
        headers = self.generate_headers(access_token)

        data = {
            "phone": phone
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.status_code

    async def verfiy_phone_code(self, access_token: str, phone: str, code: str) -> int:
        """
        验证手机短信验证码

        ref: https://openapi.logto.io/operation/operation-verifyverificationcode

        Responses
            204
            Verification code requested and sent successfully.

            400
            Bad request. The payload may be invalid.

            401
            Unauthorized

            403
            Forbidden

            501
            Not Implemented
        """
        url = logto_url + f'/api/verification-codes'
        headers = self.generate_headers(access_token)

        data = {
            "phone": phone,
            "verificationCode": code
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.status_code

    async def add_personal_access_tokens(self, access_token: str, user_id: str, name: str = 'app', expires_at=None) -> int:
        """
        创建个人访问令牌

        ref: https://openapi.logto.io/operation/operation-createuserpersonalaccesstoken


        示例

            {
                "tenantId": "string",
                "userId": "string",
                "name": "string",
                "value": "string",
                "createdAt": 42.0,
                "expiresAt": 42.0
            }

        """
        url = logto_url + f'/api/users/{user_id}/personal-access-tokens'
        headers = self.generate_headers(access_token)

        data = {
            "name": name,
            "expiresAt": expires_at
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()

    async def get_personal_access_tokens(self, access_token: str, user_id: str) -> Dict:
        """
        获取个人所有访问令牌

        ref: https://openapi.logto.io/operation/operation-listuserpersonalaccesstokens


        示例

            {
                "tenantId": "string",
                "userId": "string",
                "name": "string",
                "value": "string",
                "createdAt": 42.0,
                "expiresAt": 42.0
            }
        """
        url = logto_url + f'/api/users/{user_id}/personal-access-tokens'
        headers = self.generate_headers(access_token)

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            # response.raise_for_status()  # 如果请求失败则抛出异常
            return response.json()


client = LogtoM2MClient()


async def main():
    client = LogtoM2MClient()
    result = await client.fetch_access_token()
    client.access_token = result['access_token']
    print(result)
    # result = await client.get_applications(client.access_token)
    # print(result)

    # result = await client.get_total_user_count(client.access_token)
    # print(result)

    # result = await client.send_phone_code(client.access_token, '')
    # print(result)

    result = await client.verfiy_phone_code(client.access_token, '', '')
    print(result)

    user_id = ''

    # result = await client.add_personal_access_tokens(client.access_token, user_id)
    # print(result)

    # result = await client.get_users(client.access_token)
    # print(result)

    # result = await client.create_user(client.access_token, {})
    # print(result)

    # result = await client.create_user(client.access_token, {})
    # print(result)

if __name__ == '__main__':
    asyncio.run(main())
