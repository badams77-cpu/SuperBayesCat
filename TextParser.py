class TextParser:



    def __init__(self):
       import WordCount
       self.word_count = WordCount()

    def parse(self, file):
        import os
        word = ""
        score = 1
        mode = 0
        with open(file) as f:
            while True:
                ch = f.read(1)
                if not ch:
                    if word.len() > 0:
                        self.word_count.add_word(word, score)
                        word = ""
                    return
                if ch == "\n":
                    self.word_count.add_word(word, score)
                    word = ""
                    continue
                if mode == 0 or mode == 3:
                    if ch.isalpha():
                        word = ""
                        word = word + ch
                        mode = 1
                        continue
                    if ch.isdigit():
                        word = ""
                        word = word + ch
                        mode = 2
                        continue
                elif mode == 1:
                    if ch.isalpha() or ch.isdigit():
                        word = word +ch
                        mode = 2
                        continue
                    if ch == '.' or ch == ';' or ch == ':':
                        self.word_count.add_word(word, score)
                        mode = 3
                        continue
                    self.word_count.add_word(word, score)
                    mode = 0
                    continue
                elif mode == 2:
                    if ch.isdigit():
                        word = word + ch
                        continue
                    if ch == '.' or ch ==',' or ch == ':' or ch == ';':
                        self.word_count.add_word(word, score)
                        word = ""
                        mode = 3
                        continue
                    if ch.isalpha():
                        word = word + ch
                        mode = 1
                        continue
                        self.word_count.add_word(word, score)
                        mode = 0
                        continue
                else:
                    mode = 0

    def get_word_count(self):
        return self.word_count;