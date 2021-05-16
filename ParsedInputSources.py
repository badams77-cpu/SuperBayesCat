class ParsedInputSources:

    def __init__(self, mime_types ):
        self.files = dict();

    def add_directory(self, cat, dir):
        files = [];
        import os
        for file in os.listdir(dir):
            files.append(os.path.join(dir,file));
        self.files[cat]=files;

    def get_sources(self, cat):
        word_counts = []
        import TextParser
        for file in self.files[cat]:
            parser = TextParser()
            parser.parse(file)
            word_counts.append(parser.get_word_counts())
        return word_counts
