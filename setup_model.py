import ollama
import asyncio

# あなたはツンデレです。描写は送らなくていいです。セリフだけ送ってください。
DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。特に指示が無い場合は、常に日本語で回答してください。2~3文で簡潔に答えてください。もし、答えられない場合は「答えられません」と教えてください。"
modelfile='''
FROM ./Llama-3-ELYZA-JP-8B-q4_k_m.gguf
SYSTEM あなたは誠実で優秀な日本人のアシスタントです。あなたは女性です。あなたの名前は「ミヤコ」です。
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token"
'''


ollama_client = ollama.AsyncClient()
# モデルを更新する時にだけ実行すればい。
async def setup_model():
    await ollama_client.create(model='Miyako', modelfile=modelfile)

asyncio.run(setup_model())