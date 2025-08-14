# Author: Ugo Fiasconaro
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",  # Il tuo wrapper
    api_key="null"
)

response = client.chat.completions.create(
    model="meta-ai-openai-proxy",
    messages=[{"role": "user", "content": "Previsioni meteo del 14 agosto 2025 a Torino"}]

)

print(response.choices[0].message.content)