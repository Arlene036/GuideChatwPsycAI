# PscyAgent - AI对话监控系统

PscyAgent 是一个专门设计用于监控AI对话系统的工具，能够实时检测对话中的异常情况，包括情绪波动、行为风险、安全隐患等，并提供相应的处理建议。

## 功能特点

- 实时对话监控与分析
- 多维度异常检测
  - 用户情绪与心理异常场景
  - 用户沟通行为异常场景
  - AI回答质量与逻辑异常场景
  - 互动体验异常场景
  - 敏感与合规风险场景
- 基于严重程度的分级处理
- 自动生成处理建议
- 安全与隐私保护

## 安装

```{bash}
conda create -n pscyAgent python=3.9
conda activate pscyAgent
pip install -r requirements.txt
```

## Quick Start

0. Config Setting
   
   在app/config.py里面配置参数。

   可以选择使用API calling（不本地部署），也可以选择本地部署模型并implement openai api调用（请参考并run `openai_api.py`)


1. 启动服务
   

    ```{bash}
    python run.py
    ```

    可以通过http://localhost:8000/docs查看demo

2. sample input

```
curl -X POST https://<EXTERNAL_URL:PORT>/api/v1/monitor \
-H "Content-Type: application/json" \
-d '{
        "conversation_history": [
            {
                "role": "user",
                "content": "我最近很压抑，感觉活着没有意义",
                "timestamp": "2024-03-15T10:30:00Z"
            },
            {
                "role": "assistant",
                "content": "我理解你现在的心情...",
                "timestamp": "2024-03-15T10:30:05Z"
            }
        ],
  "session_id": "user123_20240315"
}'
```

```
curl -X 'POST' \
  'http://localhost:6006/api/v1/monitor' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_history": [
    {
      "role": "user",
      "content": "感到空虚应该怎么办"
    },
    {
      "role": "assistant",
      "content": "你好，我很愿意为你提供帮助。对于你提到的'\''感到空虚'\''，我想知道更多的情况。你能谈谈是什么原因让你觉得空虚吗？是工作、生活还是其他方面的事情呢？这样我可以更好地理解你的问题。"
    },
    {
      "role": "user",
      "content": "生活"
    },
    {
      "role": "assistant",
      "content": "可以再具体一点吗？比如：感情、家庭、朋友或是事业方面的什么情况让你感觉空虚？"
    },
    {
      "role": "user",
      "content": "学业和未来"
    },
    {
      "role": "assistant",
      "content": "好的，我明白了。你觉得在学业和未来的规划上遇到了什么困扰或挑战了吗？"
    },
    {
      "role": "user",
      "content": "我觉得我根本没有出路"
    },
    {
      "role": "assistant",
      "content": "看到这里的描述，我能感受到你的无助和焦虑。但请记住，无论面对怎样的困境，都有解决的办法。你现在是一名大学生，对吧？那么，是否可以将你认为的'\''出路'\''与所学专业联系起来呢？例如通过进一步学习专业知识、参加相关实习或是社团活动来开拓视野。"
    }
  ],
  "session_id": "testuser_1",
  "metadata": {}
}'
```


3. sample output

```{json}
{
  "status": "alert",
  "anomalies": [
    {
      "type": "emotional",
      "severity": "medium",
      "description": "用户表达了感到空虚和无助的情绪，特别是在学业和未来规划方面，显示出一定程度的焦虑。"
    },
    {
      "type": "risk",
      "severity": "low",
      "description": "用户表现出对未来感到迷茫和自我怀疑，但未直接提及自我伤害或自杀的意图，风险较低。"
    }
  ],
  "risk_level": "medium",
  "suggestions": [
    "1. 首先，表达对用户情绪的理解和共情，确认他们的感受是正常的，特别是在面对学业和未来规划的压力时。",
    "2. 引导用户详细描述他们在学业和未来规划中感到空虚和无助的具体情境，帮助他们更清晰地识别问题的根源。",
    "3. 提供一些缓解焦虑的实用技巧，如深呼吸、时间管理或设定小目标，帮助用户在短期内减轻压力。",
    "4. 鼓励用户探索他们的兴趣和价值观，帮助他们找到对未来规划的方向感，减少迷茫感。",
    "5. 建议用户与信任的朋友、家人或导师讨论他们的感受和困惑，以获得外部支持和不同的视角。",
    "6. 提醒用户关注自我照顾，确保他们有足够的休息和放松时间，避免过度压力积累。",
    "7. 如果用户的焦虑持续或加重，建议他们考虑寻求专业心理咨询师的进一步帮助。"
  ],
  "security_status": {
    "has_issues": false,
    "severity": "low",
    "risk_types": [],
    "description": "对话内容主要围绕用户的情感状态和生活困扰，没有涉及敏感个人信息、违法违规内容、不当内容、数据安全风险或政治敏感内容。",
    "recommendations": [
      "继续提供情感支持和建设性建议，帮助用户缓解焦虑和空虚感。",
      "建议用户寻求专业的心理咨询或辅导，以获得更深入的支持和指导。"
    ],
    "requires_immediate_action": false,
    "session_id": "testuser_1",
    "timestamp": "2025-01-21T15:12:38.919960"
  }
}
```

## vllm本地部署大模型说明
AutoDL租A100-SXM4-80GB * 1卡，额外存储50GB+


开启学术加速，修改huggingface的存储到autodl-tmp数据盘
```
echo 'source /etc/network_turbo' >> ~/.bashrc
echo 'export HF_HOME=/root/autodl-tmp/huggingface' >> ~/.bashrc
source ~/.bashrc
```

开screen窗口，一个部署大模型，一个部署监督模组
```
# 1. 创建第一个screen窗口用于vllm
screen -S vllm
# 在这个窗口中运行
vllm serve Qwen/Qwen2.5-32B-Instruct \
    --max-model-len 16384 \
    --enforce-eager \
    --gpu-memory-utilization 0.7 \
    --quantization awq \
    --port 8000

# 按 Ctrl+A+D 暂时离开这个窗口


# 2. 修改app/config.py文件里的参数
# MODEL_NAME: str = "Qwen/Qwen2.5-32B-Instruct"
# BASE_URL: str = "http://localhost:8000/v1"


# 3. 创建第二个screen窗口用于监督模组
screen -S supervisor
# 在这个窗口中运行你的监督模组
python run.py  # 或者其他启动命令
# 按 Ctrl+A+D 暂时离开这个窗口
```


测试本地部署的大模型是否可用
```
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-32B-Instruct",
        "prompt": "what is json",
        "max_tokens": 20,
        "temperature": 0.7
    }'
```



## API 说明

### POST /api/v1/monitor

监控对话接口

#### 请求体 (JSON)

| 字段 | 类型 | 描述 |
|------|------|------|
| conversation_history | array | 对话历史记录 |
| session_id | string | 会话ID，同一个用户的多轮对话可以用相同的session_id |

conversation_history 中的每条消息格式：

| 字段 | 类型 | 描述 |
|------|------|------|
| role | string | 角色("user"或"assistant") |
| content | string | 消息内容 |
| [optional] timestamp | string | 时间戳(ISO格式) |

#### 响应 (JSON)

| 字段 | 类型 | 描述 |
|------|------|------|
| status | string | 状态("normal"或"alert") |
| anomalies | array | 检测到的异常列表，分为emotional/behavioral/quality/security |
| risk_level | string | 风险等级(low/medium/high) |
| suggestions | array | 综合的处理建议列表 |

## 异常类型说明

1. 情绪异常 (emotional)
   - 强烈负面情绪
   - 心理危机信号
   - 情绪波动明显

2. 行为异常 (behavioral)
   - 重复性行为
   - 攻击性言论
   - 不当请求

3. 质量异常 (quality)
   - AI响应偏离
   - 信息错误
   - 逻辑混乱

4. 安全风险 (security)
   - 敏感信息泄露
   - 违规内容
   - 隐私问题

## 代码说明

```
pscyAgent/
├── app/
│ ├── api/
│ │ └── routes.py # API路由定义
│ ├── core/
│ │ ├── monitor.py # 模块1: 对话监控
│ │ └── security.py # 模块2: 安全检查
│ ├── main.py # FastAPI应用入口
│ ├── run.py # quick start
│ └── config.py # 设置一些参数
```
可以在`core`文件夹下面添加更多modules，以适应更多需要的监督情况。