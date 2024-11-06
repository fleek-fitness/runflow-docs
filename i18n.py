import os
import shutil
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수에서 OpenAI API 키 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def translate_mdx_content(content, target_lang):
    print(f"\n{target_lang}어로 번역을 시작합니다...")
    client = OpenAI(api_key=openai_api_key)

    # frontmatter와 코드 블록을 분리
    lines = content.split("\n")
    text_to_translate = []
    preserved_blocks = []
    current_block = []
    in_code_block = False
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                if current_block:
                    text_to_translate.append("\n".join(current_block))
                    current_block = []
                preserved_blocks.append(("frontmatter_start", line))
            else:
                preserved_blocks.append(("frontmatter_end", line))
            in_frontmatter = not in_frontmatter
            continue

        if line.strip().startswith("```"):
            if not in_code_block:
                if current_block:
                    text_to_translate.append("\n".join(current_block))
                    current_block = []
                preserved_blocks.append(("code_start", line))
            else:
                preserved_blocks.append(("code_end", line))
            in_code_block = not in_code_block
            continue

        if in_frontmatter or in_code_block:
            preserved_blocks.append(("preserved", line))
        else:
            current_block.append(line)

    if current_block:
        text_to_translate.append("\n".join(current_block))

    # 전체 텍스트 번역
    translated_blocks = []

    system_prompt = (
        "You are Translator, an AI language model specialized in translating natural and casual tones. "
        f"Your task is to translate the given text to {target_lang}, while preserving the original format and style. "
        "Instructions:"
        "1. If the source and target languages are the same, return the input text without translation."
        f"2. For different languages, translate the text to {target_lang}, focusing on natural expression."
        "3. Maintain the exact same format and structure as the input text."
        "4. Preserve all markdown formatting, HTML tags, and special characters exactly as they appear."
        "5. Keep proper nouns and technical terms as they are, unless there's a widely accepted translation."
        "6. Adapt idioms and cultural references to suit the target language while maintaining the original meaning."
        "7. Do not add any additional formatting or restructure the text - translate content only."
        f"Important: If the source text is in {target_lang}, do not translate and return it as is. Only translate when the languages are different."
    )

    for text in text_to_translate:
        if text.strip():
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": text},
                ],
            )
            translated_blocks.append(response.choices[0].message.content.strip())
        else:
            translated_blocks.append("")

    # 번역된 텍스트와 보존된 블록 재조합
    final_content = []
    text_index = 0

    for block_type, content in preserved_blocks:
        if block_type == "frontmatter_start":
            final_content.append(content)
            continue
        elif block_type == "frontmatter_end":
            final_content.append(content)
            if text_index < len(translated_blocks):
                final_content.append(translated_blocks[text_index])
                text_index += 1
        elif block_type == "code_start":
            if text_index < len(translated_blocks):
                final_content.append(translated_blocks[text_index])
                text_index += 1
            final_content.append(content)
        elif block_type == "code_end":
            final_content.append(content)
        else:
            final_content.append(content)

    if text_index < len(translated_blocks):
        final_content.append(translated_blocks[text_index])

    print(f"{target_lang}어 번역 완료!")
    return "\n".join(final_content)


def process_mdx_files(source_dir="."):
    print("MDX 파일 번역 프로세스를 시작합니다...")

    # 대상 언어 설정
    languages = ["en", "ko"]

    # 대상 파일 지정
    target_files = []
    introduction_file = os.path.join(source_dir, "introduction.mdx")
    if os.path.exists(introduction_file):
        target_files.append(introduction_file)
        print(f"번역할 파일을 찾았습니다: {introduction_file}")

    nodes_dir = os.path.join(source_dir, "nodes")
    if os.path.exists(nodes_dir):
        for root, _, files in os.walk(nodes_dir):
            for file in files:
                if file.endswith(".mdx"):
                    full_path = os.path.join(root, file)
                    target_files.append(full_path)

    # 각 언어별로 번역 및 저장
    for lang in languages:
        print(f"\n{lang} 언어 처리를 시작합니다...")
        for target_file in target_files:
            print(f"\n파일 처리 중: {target_file}")

            # 대상 경로 생성
            rel_path = os.path.relpath(target_file, source_dir)
            target_dir = os.path.join(source_dir, lang, os.path.dirname(rel_path))
            target_output = os.path.join(target_dir, os.path.basename(target_file))

            # 이미 번역된 파일이 존재하는지 확인
            if os.path.exists(target_output):
                print(f"이미 번역된 파일이 존재합니다. 건너뜁니다: {target_output}")
                continue

            # 원본 파일 읽기
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 디렉토리 생성
            os.makedirs(target_dir, exist_ok=True)

            # 번역 실행
            translated_content = translate_mdx_content(content, lang)
            with open(target_output, "w", encoding="utf-8") as f:
                f.write(translated_content)
            print(f"파일 저장 완료: {target_output}")

    print("\n모든 번역 작업이 완료되었습니다!")


if __name__ == "__main__":
    process_mdx_files()
