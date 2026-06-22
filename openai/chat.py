from openai import OpenAI

client = OpenAI(
  base_url="https://api.fireworks.ai/inference/v1",
  api_key=''
)

with client.responses.stream(
    model="accounts/fireworks/models/minimax-m3",
    input="you build high quality enterprise level and high quality animation  School Landing page website  use  html and tailwindcss for building"
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()