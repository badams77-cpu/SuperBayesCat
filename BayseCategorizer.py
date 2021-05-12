

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

    def build_categorizer(self, directory):


    def test_categorizer(self, directory):
        import os
        if not os.path.isdir(directory):
            raise RuntimeError(directory + " is not a directory")
        cat_num = 0
        parsed_category_sources = [] #parsedInputMultipleSource()
        for file in os.listdir(directory):
            cat = os.path.splitext(file)
            self.categoryNames.extend(cat)
            self.categoryNumbers[cat]= cat_num
            cat_num += 1
#           parsedCategorySource.addDirectory( p)
        ok_sources = 0
        n_documents = 0
        cat_index = 0
        while cat_index < len(self.categoryNames) :
            catName = self.categoryNames[cat_index]
            for  sources in parsed_category_sources :
                n_documents += 1
                recognition_weights = recWeights(sources)
                best = -1
                best_score = -1e30
                rec_index = 0
                while rec_index < len(recognition_weights) :
                    rec = recognition_weights[rec_index]
                    if rec > best_score :
                        best_score = rec
                        best = rec_index

                    rec_index = rec_index + 1
                bestcatname = self.categoryNames[best]
                if best==cat_index
                    ok_sources = ok_sources + 1
        cat_index = cat_index + 1
        return (100.0 * ok_sources)/n_documents

    def list_files(self , path):
    # returns a list of names (with extension, without full path) of all files
    # in folder path
        files = []
        for name in os.listdir(path):
           file = os.path.join(path, name)
           if os.path.isfile(file):
              files.append(file)
        return files

    def list_filenames(self, path):
 # returns a list of names (with extension, without full path) of all files
    # in folder path
        files = []
        for name in os.listdir(path):
           file = os.path.join(path, name)
           if os.path.isfile(file):
              files.append(name)
        return files

    def make_categorizer(self):