class ParsedInputSources:

    def __init__(self ):
        self.files = dict();

    def number_of_cats(self):
        return len(self.files);

    def add_directory(self, cat, direct):
        #       print("Add directory: "+direct+" to cat: "+cat)
        files = [];
        import os
        for file in os.listdir(direct):
            files.append(os.path.join(direct , file));
        self.files[cat] = files;

    def get_sources(self, cat):
        word_counts = []
        import TextParser
        if not cat in self.files:
            print("category not found: "+cat)
            return word_counts
        for file in self.files[cat]:
            from TextParser import TextParser
            parser = TextParser()

            parser.parse(file)
            word_counts.append(parser.get_word_counts())
        return word_counts
