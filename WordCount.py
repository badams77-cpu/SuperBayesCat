class WordCount:

    def __init__(self):
        self.word_counts = dict();
        self.wordList = []

    def add_word(self, word1, score):
        word = word1.lower()
        if word.upper() == word:
            return
        old_score = 0
        if word in self.word_counts:
            old_score = self.word_counts[word]
        old_score += score
        self.word_counts[word] = old_score
        self.wordList.append(word)

    def keys(self):
        return list(self.word_counts.keys())

    def score(self, word1):
        word = word1.lower()
        if word in self.word_counts:
            return self.word_counts[word]
        return 0

    def get_words(self):
        return self.wordList
