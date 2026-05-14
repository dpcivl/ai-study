import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

print("스트림에서 발생하는 모든 이벤트 관찰\n")

with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{
        "role": "user", "content": "RTOS의 장점 3가지를 짧게"
    }]
) as stream:
    
    # 모든 이벤트 순회
    for event in stream:
        event_type = event.type

        if event_type == "message_start":
            print(f"[message_start] 메시지 시작")
            print(f" model: {event.message.model}")
            print(f" input_tokens: {event.message.usage.input_tokens}")

        elif event_type == "content_block_start":
            print(f"\n[content_block_start] 컨텐츠 블록 시작")
            print(f" block_type: {event.content_block.type}")

        elif event_type == "content_block_delta":
            # 실제 텍스트 청크
            if event.delta.type == "text_delta":
                print(f" 텍스트 청크: '{event.delta.text}'")

        elif event_type == "content_block_stop":
            print(f"[content_block_stop] 컨텐츠 블록 종료")

        elif event_type == "message_delta":
            print(f"\n[message_delta]")
            if hasattr(event, 'usage'):
                print(f" output_tokens: {event.usage.output_tokens}")
            if hasattr(event.delta, 'stop_reason'):
                print(f" stop_reason: {event.delta.stop_reason}")

        elif event_type == "message_stop":
            print(f"[message_stop] 메시지 종료")


# 스트림 종료 후 최종 메시지 가져오기
print("\n" + "=" * 60)
print("최종 메시지 객체:")
print("=" * 60)
final_message = stream.get_final_message()
print(f"전체 텍스트: {final_message.content[0].text}")
print(f"총 토큰: input={final_message.usage.input_tokens}, output={final_message.usage.output_tokens}")