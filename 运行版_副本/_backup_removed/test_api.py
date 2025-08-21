#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接测试脚本
"""

import requests
import json
from config import API_KEY, BASE_URL, DEFAULT_MODEL


def test_api_connection():
    """测试API连接"""
    print("🔍 测试SiliconFlow API连接...")
    print("=" * 40)
    
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单介绍一下你自己。"
            }
        ],
        "max_tokens": 100
    }
    
    try:
        print(f"📡 正在连接到: {url}")
        print(f"🤖 使用模型: {DEFAULT_MODEL}")
        print(f"🔑 API密钥: {API_KEY[:10]}...")
        print()
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ API连接成功！")
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"📝 AI回复: {content}")
            else:
                print("⚠️ 响应格式异常")
                
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，请检查网络连接")
    except requests.exceptions.ConnectionError:
        print("🌐 连接错误，请检查网络连接")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")


if __name__ == "__main__":
    test_api_connection()
