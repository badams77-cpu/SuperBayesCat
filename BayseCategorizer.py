

class BayesCategorizer:



    # Constants
    scoreForTitle=5.0
    informationGainedThresholdWords = 0.1
    informationGainedThresholdPairs = 0.1
    percentOfDocumentForStopListWords = 60
    percentOfDocumentForStopListPairs = 60
    weightBoostForPair = 2.0
    rmsInformationCheck = True
    superBayesAmount = 0.0

    # static data
    stopList = {}

    def __init__(self):
        self.categoryNames = []
        self.categoryNumbers = dict()
        self.words = []
        self.wordNumbers = dict()
        self.wordPairs = []
        self.priorProb = []
        self.wordWeights = []

#    def build_categorizer(self, directory):

    def test_categorizer(self, directory):
        import os
        import ParsedInputSources
        if not os.path.isdir(directory):
            raise RuntimeError(directory + " is not a directory")
        cat_num = 0
        parsed_category_sources = ParsedInputSources()
        for cat in os.listdir(directory):
            self.categoryNames.extend(cat)
            self.categoryNumbers[cat] = cat_num
            cat_num += 1
            parsed_category_sources.add_directory( cat,os.path.join(directory, cat))
        ok_sources = 0
        n_documents = 0
        cat_index = 0
        while cat_index < self.categoryNames.len:
            cat_name = self.categoryNames[cat_index]
            for source in parsed_category_sources.get_sources(cat):
                n_documents += 1
                recognition_scores = recognition_scores(source)
                best = -1
                best_score = -1e30
                rec_index = 0
                while rec_index < recognition_scores.len:
                    rec = recognition_scores[rec_index]
                    if rec > best_score:
                        best_score = rec
                        best = rec_index

                    rec_index = rec_index + 1
                best_cat_name = self.categoryNames[best]
                if best == cat_index:
                    ok_sources = ok_sources + 1
        cat_index = cat_index + 1
        return (100.0 * ok_sources)/n_documents

    def list_files(self, path):
        # returns a list of names (with extension, without full path) of all files
        # in folder path
        import os
        files = []
        for name in os.listdir(path):
            file = os.path.join(path, name)
            if os.path.isfile(file):
                files.append(file)
        return files

    def list_filenames(self, path):
        # returns a list of names (with extension, without full path) of all files
        # in folder path
        import os
        files = []
        for name in os.listdir(path):
            file = os.path.join(path, name)
            if os.path.isfile(file):
                files.append(name)
        return files

#    def make_categorizer(self):

    def recognition_scores(self, word_count):
        rec_scores = []
        i = 0
        while i<self.prior_prop.len:
            rec_scores[i] = self.prior_prop[i]
            i += 1
        word_number = -1
        for word in word_count.keys():
            if word in self.wordNumbers:
                word_number = self.wordNumbers[word]
                cat_num = 0
                score = word_count.score[word]
                while cat_num < rec_scores.len:
                    rec_scores[i] += score * self.wordWeights[word_number][cat_num]
                    cat_num += 1
        return rec_scores

    def find_category_of(self, word_count):
        best = -1
        best_score = -1e30
        rec_index = 0
        recognition_scores = self.recognition_scores( word_count)
        while rec_index < recognition_scores.len :
            rec = recognition_scores[rec_index]
            if rec > best_score:
                best_score = rec
                best = rec_index
            rec_index += 1
        best_cat_name = self.categoryNames[best]
        return best_cat_name
