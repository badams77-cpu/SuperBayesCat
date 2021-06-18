

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
        self.informationGainedThresholdWords = 0.333
        self.percentOfDocumentForStopListWords = 60
        self.superBayesAmount = 1.0
        self.correlation_error = []


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
        cat_names = []
        parsed_category_sources = ParsedInputSources()
        cat_numbers = dict()
        for cat in os.listdir(directory):
            if not cat in self.categoryNumbers:
                continue
            print("test category found: "+cat)
            cat_numbers[cat] = cat_num
            cat_names.append(cat);
            parsed_category_sources.add_directory(cat, os.path.join(directory, cat))
            cat_num += 1
        n_documents = 0
        cat_index = 0
        while cat_index < parsed_category_sources.number_of_cats():
            cat_name = cat_names[cat_index]
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
                if best_cat_name == cat_name:
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
                    cat_count[i][word1] = cat_count[i].get(word1, 0) + score
                    cat_total[i][word1] = cat_total[i].get(word1, 0) + score
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
        self.makeSuperBayes(sources);
        return document_count

    def makeSuperBayes(self, sources):
        import math
        document_num_by_word = []
        word_occur = []
        total_occur = []
        category_total_word_count = []
        word_count_by_document = []
        category_for_document = []
        iword = 0
        while iword < len(self.wordNumbers):
            word_occur.append([])
            document_num_by_word.append([])
            word_count_by_document.append([0] * len(self.categoryNumbers))
            iword += 1
        n_document = 0
        category_number = 0
        while category_number < len(self.categoryNames):
            total_occur.append([0] * len(self.wordNumbers))
            cat_total = 0
            category_name = self.categoryNames[category_number]

            for source in sources.get_sources(category_name):
                for word in source.keys():
                    word1 = word.lower()
                    if word.upper() == word1:
                        continue
                    if word in self.stopList:
                        continue
                    if not word1 in self.wordNumbers:
                        continue
                    word_num = self.wordNumbers[word1]
                    occs = source.score(word1)
                    cat_total += occs
                    word_occur[word_num].append(occs)
                    document_num_by_word[word_num].append(n_document)
                    word_count_by_document[word_num].append(occs)
                    total_occur[category_number][word_num] += occs
                category_for_document.append(category_number)
                n_document += 1
            category_total_word_count.append(cat_total)

            category_number += 1
            if cat_total == 0:
                print("Warning category: "+category_name+" has no documents")
        prob_words = []
        iword = 0
        while iword < len(self.wordNumbers):
            cat_prob = []
            icat = 0
            while icat < len(self.categoryNames):
                count = category_total_word_count[icat]
                if count == 0:
                    cat_prob.append(0)
                    continue
                cat_prob.append(total_occur[icat][iword]/count)
                icat += 1
            prob_words.append(cat_prob)
            iword += 1
        aword = 1
        corr_err = []
        while aword < len(self.wordNumbers):
            print("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bCorrelations for word "+self.words[aword])
#                 " "+ str(aword)+"<"+str(len(self.wordNumbers)))
            bword = 0
            occ_a = word_count_by_document[aword]
            loc_a = document_num_by_word[aword]
            corr_err_inner = [0] * aword
            while bword < aword:
                occ_b = word_count_by_document[bword]
                loc_b = document_num_by_word[bword]
                pa = loc_a[0];
                pb = loc_b[0];
                ia = 0
                ib = 0
                corr = [0] * len(self.categoryNames)
                n_corr = 0
                while True:
                    if pa < pb:
                        ia += 1
                        if ia >= len(loc_a):
                            break
                        pa = loc_a[ia]
                    elif pb < pa:
                        ib += 1
                        if ib >= len(loc_b):
                            break
                        pb = loc_b[ib]
                    else:
                        if ia >= len(loc_a):
                            break
                        if ib >= len(loc_b):
                            break
#                        print(" category for document pa="+str(pa), " ia="+str(ia)+"<"+str(len(occ_a))+" ib="+str(ib)+ "<"+str(len(occ_b)));
#                        print(" is "+str(category_for_document[pa]))
                        corr[category_for_document[pa]] += occ_a[ia] * occ_b[ib]
                        ia += 1
                        ib += 1
                        if ia >= len(loc_a):
                            break
                        pa = loc_a[ia]
                        if ib >= len(loc_b):
                            break
                        pb = loc_b[ib]
                        n_corr += 1
                if n_corr == 0:
                    bword += 1
                    continue
                d_corr = [0] * len(self.categoryNames)
                j = 0
                while j < len(self.categoryNames):
                    count = category_total_word_count[j]
                    if count < 2:
                        continue
                        d_corr[j] = corr[j] / (count - 1.0)
                    j += 1
                dotprod = 0.0
                papb_sq = 0.0
                corr_sq = 0.0
                j = 0
                while j < len(self.categoryNames):
                    if len(prob_words[aword]) <= j:
                        print(" error aword "+str(aword)+" cat len "+str(len(prob_words[aword])));
                    pcata = prob_words[aword][j]
                    pcatb = prob_words[bword][j]
                    p2 = pcata*pcatb
                    corr = d_corr[j]
                    dotprod += p2 * corr
                    corr_sq += corr * corr
                    papb_sq += p2 * p2
                    j += 1
                if (papb_sq < 1.0e-20) or (corr_sq < 1.0e-20):
                    bword += 1
                    continue
                corr_err_inner[bword] = (1.0 - dotprod / math.sqrt(corr_sq * papb_sq))
                bword += 1
            corr_err.append(corr_err_inner)
            aword += 1
        self.correlation_error = corr_err
        print("")


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
        import math
        rec_scores = []
        i = 0
        while i < len(self.priorProb):
            rec_scores.append(self.priorProb[i])
            i += 1
        word_num = []
        number_of_words = 0
        for word in word_count.keys():
            word1 = word.lower()
            if word1 == word.upper():
                continue
            if word1 in self.wordNumbers:
                word_num.append(self.wordNumbers[word])
                number_of_words += 1

        correlation_factor = [0] * len(self.wordNumbers)
        iword = 1
        while iword < number_of_words:
            jword = 0
            while jword < number_of_words:
                word_a = word_num[iword]
                word_b = word_num[jword]
                if word_a < word_b:
                    x = self.correlation_error[word_b][word_a]
                else:
                    x = self.correlation_error[word_a][word_b]
                if correlation_factor[word_a] < x:
                    correlation_factor[word_a] = x
                if correlation_factor[word_b] < x:
                    correlation_factor[word_b] = x
                jword += 1
            iword += 1
        i = 0
        sb_factor = [0] * len(self.wordNumbers)
        while i < len(self.wordNumbers):
            x = correlation_factor[i]
            if x == 0:
                sb_factor[i] = 1
            else:
                sb_factor[i] = pow(2, -x)
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
                    rec_scores[cat_num] += score * sb_factor[word_number] * self.wordWeights[word_number][cat_num]
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