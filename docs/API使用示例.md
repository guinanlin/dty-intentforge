# API 使用示例

## 问题说明

在 Windows Git Bash 中，使用 `curl` 发送多行 JSON 请求时可能会遇到 "There was an error parsing the body" 错误。这是因为 Windows Git Bash 对多行字符串的处理方式与 Linux 不同。

## 解决方案

### 方法 1：使用文件方式（推荐）

这是最可靠的方法，适用于所有平台。

**步骤：**

1. 创建请求文件 `request.json`：
```bash
cat > request.json << 'EOF'
{
  "text": "今天我跟一个朋友去吃饭，然后这个朋友是我刚第一次见面，然后我们未来我觉得我们之间可能会有一些生意上的合作。然后逻辑上他应该是我的一个潜在的，一个未来的一个合作伙伴吧。"
}
EOF
```

2. 发送请求：
```bash
curl -X POST http://127.0.0.1:8200/nlu/predict \
  -H "Content-Type: application/json" \
  -d @request.json
```

### 方法 2：使用单行 JSON

对于较短的文本，可以使用单行 JSON（需要转义引号）：

```bash
curl -X POST http://127.0.0.1:8200/nlu/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"你好\"}"
```

### 方法 3：使用 echo 管道

```bash
echo '{"text": "你好"}' | curl -X POST http://127.0.0.1:8200/nlu/predict \
  -H "Content-Type: application/json" \
  -d @-
```

### 方法 4：使用 PowerShell（Windows）

如果在 Windows PowerShell 中：

```powershell
$body = @{
    text = "今天我跟一个朋友去吃饭，然后这个朋友是我刚第一次见面，然后我们未来我觉得我们之间可能会有一些生意上的合作。然后逻辑上他应该是我的一个潜在的，一个未来的一个合作伙伴吧。"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8200/nlu/predict" -Method Post -Body $body -ContentType "application/json"
```

### 方法 5：使用 Python 脚本

```python
import requests
import json

url = "http://127.0.0.1:8200/nlu/predict"
data = {
    "text": "今天我跟一个朋友去吃饭，然后这个朋友是我刚第一次见面，然后我们未来我觉得我们之间可能会有一些生意上的合作。然后逻辑上他应该是我的一个潜在的，一个未来的一个合作伙伴吧。"
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

## 错误处理

如果遇到错误，API 现在会返回更详细的错误信息，包括：
- 错误详情
- 请求体预览（前200字符）
- 使用建议

## 测试脚本

项目根目录提供了 `test_curl.sh` 脚本，可以测试不同的请求方式：

```bash
chmod +x test_curl.sh
./test_curl.sh
```
