# Author: Ugo Fiasconaro
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",  # Il tuo wrapper
    api_key="null"
)

response = client.chat.completions.create(
    model="meta-ai-openai-proxy",
    messages=[{"role": "user", "content": "Previsioni del meteo di domani ad Alessandria"}]
)

print(response.choices[0].message.content)