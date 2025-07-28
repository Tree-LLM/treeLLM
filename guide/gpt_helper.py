from openai import OpenAI

client = OpenAI()

def generate_text(prompt: str, model: str = "gpt-4o") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        top_p=0.3,
    )
    return response.choices[0].message.content.strip()
