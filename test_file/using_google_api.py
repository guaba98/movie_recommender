
from googletrans import Translator
translator = Translator()
print(translator)

sentence = input("언어를 감지할 문장을 입력해주세요 : ")
detected = translator.detect(sentence)
# print(detected.lang)
result = translator.translate(sentence, dest = 'en')
print(result.text)