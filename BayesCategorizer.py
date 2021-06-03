

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
        self.informationGainedThresholdWords = 0.01
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
            print("training category found: "+cat)
            self.categoryNames.append(cat)
            self.categoryNumbers[cat] = cat_num
            cat_num += 1
            parsed_category_sources.add_directory(cat, os.path.join(directory, cat))
        ndocs = self.make_categorizer(parsed_category_sources)

    def test_categorizer(self, directory):
        import os
        from ParsedInputSources import ParsedInputSources
        if not os.path.isdir(directory):
            raise RuntimeError(directory + " is not a directory")

        ok_sources = 0
        cat_num = 0
        parsed_category_sources = ParsedInputSources()
        cat_numbers = dict()
        for cat in os.listdir(directory):
            if not cat in self.categoryNumbers:
                continue
            print("test category found: "+cat)
#            self.categoryNumbers[cat] = cat_num
            parsed_category_sources.add_directory( cat,os.path.join(directory, cat))
        n_documents = 0
        cat_index = 0
        while cat_index < len(self.categoryNames):
            cat_name = self.categoryNames[cat_index]
            for source in parsed_category_sources.get_sources(cat_name):
                n_documents += 1
                recognition_scores = self.recognition_scores(source)
                best = -1
                best_score = -1e30
                rec_index = 0
                while rec_index < len(recognition_scores):
                    rec = recognition_scores[rec_index]
                    if rec > best_score:
                        best_score = rec
                        best = rec_index
                    rec_index = rec_index + 1
                best_cat_name = self.categoryNames[best]
                print( str(n_documents) + " cat= " + cat_name + " best fit " + best_cat_name + " best="+str(best))
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
        while i < len(self.categoryNames):
            cat_count.append(dict())
            cat_total.append(dict())
            cat_document_count.append(0)
            category_name = self.categoryNames[i]
            cat_word_count.append(0)
            for source in sources.get_sources(category_name):
                cat_document_count[i] += 1
                document_count += 1
                for word in source.keys():
                    word1 = word.lower()
                    if word.upper() == word1:
                        continue
                    if word in self.stopList:
                        continue
                    score = source.score(word1)
#                    print("word: "+word+", score="+str(score))
                    cat_word_count[i] += score
                    word_document_count[word1] = 1 + word_document_count.get(word1, 0)
                    cat_count[i][word1] = score
                    cat_total[i][word1] = score
                    total_count[word1] = total_count.get(word1, 0) + score
            i += 1
        words_to_use = []
        max_doc_count = (self.percentOfDocumentForStopListWords * document_count)/100.0
        for word in total_count.keys():
            if word_document_count.get(word, 0) < 2:
                continue
            square_info_gained = 0.0
            i = 0
            while i < len(self.categoryNames):
                prob_word = word_document_count[word]/document_count
                prob_cat_given_word = cat_count[i].get(word, 0) / cat_document_count[i]
                information = prob_word * self.entropy(prob_cat_given_word) + (1.0 - prob_word) * self.entropy(1.0 - prob_cat_given_word)
                square_info_gained += information*information
                i += 1
#                print("Word: "+word+" info "+str(square_info_gained)+" prop="+str(prob_word)+" prob_cat_given_word="+str(prob_cat_given_word))
            if square_info_gained > self.informationGainedThresholdWords * self.informationGainedThresholdWords:
                print("Use word: "+word)
                words_to_use.append(word)
#            else:
#                print("Word: "+word+" info "+str(square_info_gained)+" skipping ")
        self.wordNumbers = dict()
        self.words = words_to_use
        i = 0
        for word in words_to_use:
            self.wordNumbers[word] = i
            i += 1
        i = 0
        self.priorProb = []
        while i < len(self.categoryNames):
            category_name = self.categoryNames[i]
            prob_cat = cat_document_count[i]/document_count
            self.priorProb.append(math.log(prob_cat))
            i += 1
        self.wordWeights = self.laplace_estimator(cat_total, cat_word_count, words_to_use, 1.0)

        return document_count

    def laplace_estimator(self, word_freq, cat_word_count, keys, weight):
        import math
        ret = []
        i = 0
        while i < len(keys):
            ret.append([])
            j = 0
            key = keys[i]
            while j < len(cat_word_count):
                ret[i].append(weight * math.log( (1.0 + word_freq[j].get(key, 0)) / (len(keys)+cat_word_count[j]) ))
#                print(key+","+str(i)+","+str(j)+"= "+str(ret[i][j]))
                j += 1
            i += 1
        return ret

    def recognition_scores(self, word_count):
        rec_scores = []
        i = 0
        while i < len(self.priorProb):
            rec_scores.append(self.priorProb[i])
            i += 1
        for word in word_count.keys():
            word1 = word.lower()
            if word1 == word.upper():
                continue
            if word1 in self.wordNumbers:
                word_number = self.wordNumbers[word1]
                cat_num = 0
                score = word_count.score(word)
                while cat_num < len(rec_scores):
                    rec_scores[cat_num] += score * self.wordWeights[word_number][cat_num]
#                    print("cat_num: "+str(cat_num)+ ", score="+str(rec_scores[cat_num]))
                    cat_num += 1
        return rec_scores

    def find_category_of(self, word_count):
        best = -1
        best_score = -1e30
        rec_index = 0
        recognition_scores = self.recognition_scores( word_count)
        while rec_index < len(recognition_scores) :
            rec = recognition_scores[rec_index]
            if rec > best_score:
                best_score = rec
                best = rec_index
            rec_index += 1
        best_cat_name = self.categoryNames[best]
        return best_cat_name

    def entropy(self, prop):
        import math
        if prop < 1.0e-17:
            return 0
        return prop * math.log(prop)