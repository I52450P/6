import json
import os
import requests

def handler(event, context):
    # 处理 CORS 预检请求（浏览器在 POST 前会发送 OPTIONS）
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }

    # 仅允许 POST 方法
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    try:
        # 解析请求体
        body = json.loads(event.get('body', '{}'))
        prompt = body.get('prompt')
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing prompt'})
            }

        # 从环境变量获取 API Key（在 Netlify 后台配置）
        api_key = os.environ.get('ZHIPU_API_KEY')
        if not api_key:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Server configuration error: ZHIPU_API_KEY not set'})
            }

        # 调用智谱 AI API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'glm-4-flash',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3
        }

        response = requests.post(
            'https://open.bigmodel.cn/api/paas/v4/chat/completions',
            headers=headers,
            json=payload,
            timeout=55
        )
        result = response.json()

        # 返回结果，并添加 CORS 头
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }