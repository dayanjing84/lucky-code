"""
微信自动发送模块
支持多种发送方式:
1. 微信公众号API (推荐)
2. 企业微信API
3. WeChatPy (个人微信,有风险)
"""
from __future__ import annotations

import os
import time
import json
import base64
from pathlib import Path
from typing import Literal
import requests


class WeChatPublicSender:
    """微信公众号API发送器"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        """获取access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "access_token" in data:
            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {data}")

    def upload_image(self, image_path: Path) -> str:
        """上传图片到微信服务器,返回media_id"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image"

        with open(image_path, "rb") as f:
            files = {"media": (image_path.name, f, "image/jpeg")}
            resp = requests.post(url, files=files, timeout=30)
            data = resp.json()

        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"上传图片失败: {data}")

    def create_draft(self, title: str, image_path: Path, content: str = "") -> str:
        """创建草稿"""
        token = self.get_access_token()

        # 上传封面图片
        thumb_media_id = self.upload_image(image_path)

        # 创建草稿
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        # 读取图片并转换为HTML img标签
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()

        article_content = f"""
        <p>{content}</p>
        <p><img src="data:image/jpeg;base64,{img_data}" /></p>
        """

        payload = {
            "articles": [{
                "title": title,
                "author": "南昌县移动",
                "digest": content or "吉祥号码专场,限时优惠!",
                "content": article_content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]
        }

        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"创建草稿失败: {data}")

    def publish_draft(self, media_id: str) -> bool:
        """发布草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"

        payload = {"media_id": media_id}
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        return data.get("errcode", -1) == 0

    def send_image_to_customer(self, openid: str, media_id: str) -> bool:
        """发送图片消息给指定用户"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}"

        payload = {
            "touser": openid,
            "msgtype": "image",
            "image": {
                "media_id": media_id
            }
        }

        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        return data.get("errcode", -1) == 0


class WorkWechatSender:
    """企业微信API发送器"""

    def __init__(self, corp_id: str, agent_id: int, agent_secret: str):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.agent_secret = agent_secret
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        """获取企业微信access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.agent_secret
        }

        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        if "access_token" in data:
            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {data}")

    def upload_image(self, image_path: Path) -> str:
        """上传图片,返回media_id"""
        token = self.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image"

        with open(image_path, "rb") as f:
            files = {"media": (image_path.name, f, "image/jpeg")}
            resp = requests.post(url, files=files, timeout=30)
            data = resp.json()

        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"上传图片失败: {data}")

    def send_image(self, image_path: Path, touser: str = "@all") -> bool:
        """发送图片消息

        Args:
            image_path: 图片路径
            touser: 接收人,多个用|分隔,@all表示全部
        """
        token = self.get_access_token()
        media_id = self.upload_image(image_path)

        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

        payload = {
            "touser": touser,
            "msgtype": "image",
            "agentid": self.agent_id,
            "image": {
                "media_id": media_id
            }
        }

        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        return data.get("errcode", -1) == 0

    def send_news(self, title: str, description: str, image_path: Path,
                  url: str = "", touser: str = "@all") -> bool:
        """发送图文消息"""
        token = self.get_access_token()
        picurl = self.upload_image(image_path)

        api_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

        payload = {
            "touser": touser,
            "msgtype": "news",
            "agentid": self.agent_id,
            "news": {
                "articles": [{
                    "title": title,
                    "description": description,
                    "url": url,
                    "picurl": picurl
                }]
            }
        }

        resp = requests.post(api_url, json=payload, timeout=30)
        data = resp.json()

        return data.get("errcode", -1) == 0


class WeChatSender:
    """统一的微信发送接口"""

    def __init__(self,
                 send_type: Literal["public", "work", "none"] = "none",
                 config: dict = None):
        """
        Args:
            send_type: 发送类型 (public=公众号, work=企业微信, none=不发送)
            config: 配置字典
        """
        self.send_type = send_type
        self.sender = None

        if send_type == "public" and config:
            self.sender = WeChatPublicSender(
                app_id=config.get("app_id"),
                app_secret=config.get("app_secret")
            )
        elif send_type == "work" and config:
            self.sender = WorkWechatSender(
                corp_id=config.get("corp_id"),
                agent_id=config.get("agent_id"),
                agent_secret=config.get("agent_secret")
            )

    def send_poster(self, image_path: Path, title: str = "", description: str = "") -> bool:
        """发送海报

        Args:
            image_path: 海报图片路径
            title: 标题
            description: 描述文案

        Returns:
            是否发送成功
        """
        if self.send_type == "none":
            print("[INFO] 微信发送功能未启用")
            return False

        try:
            if self.send_type == "public":
                # 公众号: 创建草稿
                media_id = self.sender.create_draft(
                    title=title or "吉祥号码专场",
                    image_path=image_path,
                    content=description or "限时优惠,先到先得!"
                )
                print(f"[OK] 公众号草稿已创建: media_id={media_id}")
                print("[INFO] 请登录公众号后台手动发布草稿")
                return True

            elif self.send_type == "work":
                # 企业微信: 直接发送
                success = self.sender.send_image(image_path)
                if success:
                    print("[OK] 企业微信图片已发送")
                return success

        except Exception as e:
            print(f"[ERROR] 微信发送失败: {e}")
            return False

        return False


def load_wechat_config() -> tuple[str, dict]:
    """从环境变量或配置文件加载微信配置

    Returns:
        (send_type, config_dict)
    """
    # 优先从环境变量读取
    send_type = os.getenv("WECHAT_SEND_TYPE", "none")  # public/work/none

    if send_type == "public":
        config = {
            "app_id": os.getenv("WECHAT_APP_ID", ""),
            "app_secret": os.getenv("WECHAT_APP_SECRET", "")
        }
    elif send_type == "work":
        config = {
            "corp_id": os.getenv("WECHAT_CORP_ID", ""),
            "agent_id": int(os.getenv("WECHAT_AGENT_ID", "0")),
            "agent_secret": os.getenv("WECHAT_AGENT_SECRET", "")
        }
    else:
        config = {}

    # 尝试从配置文件读取
    config_file = Path(__file__).parent.parent / "wechat_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                send_type = file_config.get("send_type", send_type)
                config.update(file_config.get("config", {}))
        except Exception as e:
            print(f"[WARN] 读取wechat_config.json失败: {e}")

    return send_type, config


def create_wechat_sender() -> WeChatSender:
    """创建微信发送器实例"""
    send_type, config = load_wechat_config()
    return WeChatSender(send_type=send_type, config=config)
