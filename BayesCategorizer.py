

class BayesCategorizer:

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
        self.informationGainedThresholdWords = 0.1
        self.percentOfDocumentForStopListWords = 60
        self.superBayesAmount = 0.0


    def build_categorizer(self, directory):
        import os
        from ParsedInputSources import ParsedInputSources
        if not os.path.isdir(directory):
            raise RuntimeError(directory + " is not a directory")
        cat_num = 0
        parsed_category_sources = ParsedInputSources()
        for cat in os.listdir(directory):
            self.categoryNames.extend(cat)
            self.categoryNumbers[cat] = cat_num
            cat_num += 1
            parsed_category_sources.add_directory( cat,os.path.join(directory, cat))
        ndocs = self.make_categorizer( parsed_category_sources);

    def test_categorizer(self, directory):
        import os
        from ParsedInputSources import ParsedInputSources
        if not os.path.isdir(directory):
            raise RuntimeError(directory + " is not a directory")

        ok_sources = 0
        cat_num = 0
        parsed_category_sources = ParsedInputSources()
        for cat in os.listdir(directory):
            self.categoryNames.extend(cat)
            self.categoryNumbers[cat] = cat_num
            cat_num += 1
            parsed_category_sources.add_directory( cat,os.path.join(directory, cat))
        n_documents = 0
        cat_index = 0
        while cat_index < self.categoryNames.len:
            cat_name = self.categoryNames[cat_index]
            for source in parsed_category_sources.get_sources(cat):
                n_documents += 1
                recognition_scores = self.recognition_scores(source)
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

    def make_categorizer(self, sources):
        import math
        document_word_count = 0
        total_word_count = 0
        document_count = 0
        word_document_count = dict();
        total_count = dict();
        i = 0
        cat_count = []
        cat_total = []
        cat_word_count = []
        cat_document_count = []
        average_word_factor = 0.0
        while i< len(self.categoryNames):
            cat_count.append(dict())
            cat_total.append(dict())
            cat_document_count.append(0)
            category_name = self.categoryNames[i]
            cat_word_count.append( 0)
            for source in sources.get_sources(category_name):
                cat_document_count[i] += 1
                document_count+=1
                for word in source.keys():
                    if self.stopList[word]:
                        continue
                    score = source.score[word]
                    cat_word_count[i]+= score
                    word_document_count[word]+= 1
                    cat_count[i][word]=score
                    total_count[word]+=score
            i += 1
        i = 0
        words_to_use = ()
        max_doc_count = (self.percentOfDocumentForStopListWords * document_count)/100.0
        for word in total_count.keys():
            if word_document_count[word]<3:
                continue
            square_info_gained = 0.0
            while i< len(self.categoryNames):
                prob_word = word_document_count[word]/document_count
                prob_cat_given_word = cat_count[i][word]/cat_document_count[i]
                information = prob_word * self.entropy(prob_cat_given_word) + (1.0 - prob_word) * self.entropy( 1.0 - prob_cat_given_word)
                square_info_gained += information*information
                i+=1
            if square_info_gained > self.informationGainedThresholdWords * self.informationGainedThresholdWords:
                words_to_use.append(word)
        self.wordNumbers = dict();
        i=0
        for word in words_to_use:
            self.wordNumbers[word]=i

        i=0
        while i< len(self.categoryNames):
            category_name = self.categoryNames[i]
            prop_cat = cat_document_count[i]/document_count
            self.priorProb[i]= math.log(prop_cat)
            self.wordWeights = self.laplace_estimator( cat_total, cat_word_count, words_to_use, 1.0 )
            i+=1
        return document_count

    def laplace_estimator(self, word_freq, cat_word_count, keys, weight):
        import math
        ret  = []
        i = 0
        while i<len(keys):
            ret[i] = []
            j = 0
            key = keys[i]
            while j<len(cat_word_count):
               ret[i][j] = weight * math.log( 1.0 + word_freq[j][key]/ (len(keys)+cat_word_count[j]))
        return ret

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

    def entropy(self, prop):
        import math
        if prop<1.0e-7:
            return 0
        return prop * math.log(prop)