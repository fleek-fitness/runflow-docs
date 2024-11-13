# 문서 만들기

## 준비물

- chatGPT
- 프롬프트
- 백앤드 코드 (<https://github.com/fleek-fitness/automation-backend-server>)

## 순서

1. chatGPT를 2개 켠다
2. 각 프롬프트(md, mdx)를 넣는다
3. 문서화 하고 싶은 노드의 백엔드 코드(`v1.py`)를 md를 넣은 chatGPT에 넣는다.
4. 출력물을 mdx를 넣은 chatGPT에 넣는다.
5. 문서 완성!
6. nodes 디렉토리 하위의 적절한 위치에 `문서파일은_백엔드_파일명과_동일.md` 파일을 위치시킨다
7. `mint.json` 파일을 수정한다. 적절한 group에 적절한 pages.

- (선택) i18n.py를 실행시켜 영어버전 문서를 만든다
