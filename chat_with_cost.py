import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# Haiku 4.5 가격 (per million tokens, USD)
INPUT_PRICE_PER_M = 1.0   # $1 per 1M input tokens
OUTPUT_PRICE_PER_M = 5.0  # $5 per 1M output tokens

messages = []
total_input_tokens = 0
total_output_tokens = 0

print("스트리밍 챗봇 + 비용 추적. 'quit' 종료, 'cost' 비용 확인. \n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break
    
    if user_input.lower() == "cost":
        total_cost = (
            total_input_tokens / 1_000_000 * INPUT_PRICE_PER_M +
            total_output_tokens / 1_000_000 * OUTPUT_PRICE_PER_M
        )
        print(f"\n[누적] input: {total_input_tokens} tokens, "
              f"output: {total_output_tokens} tokens")
        print(f"[비용] ${total_cost:.6f} (약 {total_cost * 1400:.2f}원)\n")
        continue

    messages.append({"role": "user", "content": user_input})

    print("\nClaude: ", end="", flush=True)
    full_response = ""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text


    # 최종 메시지에서 토큰 정보 추출
    final = stream.get_final_message()
    total_input_tokens += final.usage.input_tokens
    total_output_tokens += final.usage.output_tokens

    # 이번 턴 비용
    turn_cost = (
        final.usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_M +
        final.usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_M
    )

    print(f"\n\n[이번 턴] in: {final.usage.input_tokens}, "
          f"out: {final.usage.output_tokens}, "
          f"cost: ${turn_cost:.6f}\n")
    
    messages.append({"role": "assistant", "content": full_response})