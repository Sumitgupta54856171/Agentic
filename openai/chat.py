from openai import OpenAI

client = OpenAI(
  base_url="https://api.fireworks.ai/inference/v1",
  api_key='fw_CDH4NRnimzd9zCCXmo16mR'
)

with client.responses.stream(
    model="accounts/fireworks/models/deepseek-v4-flash",
    input="you build high enterprise level school management system protorype website  all feature working prototype they are the origin website ui/ux  use  html and tailwindcss for building"
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()