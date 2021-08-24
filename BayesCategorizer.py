

class BayesCategorizer:

    # static data
    stopList = {'and', 'or', 'of', 'the', 'said', 'at', 'it', 'its', 'for', 'to', 'too', 'be'}

    def __init__(self):
        self.categoryNames = []
        self.alpha = 0.5
        self.alpha_pair = 0.75
        self.categoryNumbers = dict()
        self.words = []
        self.wordNumbers = dict()
        self.wordPairs = []
        self.priorProb = []
        self.wordWeights = []
        self.pairWeights = dict()
        self.pairWeightX = []
        self.pairWeightY = []
        self.pairWeightValues = []
        self.informationGainedThresholdWords = 0.52
        self.informationGainedThresholdPairs = 0.0059
        self.percentOfDocumentForStopListWords = 60
        self.superBayesAmount = 1.0
        self.weightBoostForPair = 2.0
        self.correlation_error = []
        self.extra = []

    @staticmethod
    def encode(obj):
        obj.pairWeightsValues = []
        for key in obj.wordPairs:
            weights = obj.pairWeights[key]
            obj.pairWeightsValues.append(weights)

        if isinstance(obj, BayesCategorizer):
            return {"sbc": True,
                    "categoryNames": obj.categoryNames,
                    "categoryNumbers": obj.categoryNumbers,
                    "words": obj.words,
                    "wordNumbers": obj.wordNumbers,
                    "wordPairs": obj.wordPairs,
                    "priorProb": obj.priorProb,
                    "wordWeights": obj.wordWeights,
                    "pairWeightsValues": obj.pairWeightsValues,
                    "correlation_error": obj.correlation_error}

    @staticmethod
    def decode(obj):
        if "sbc" in obj:
            sbc = BayesCategorizer();
            sbc.categoryNames = obj['categoryNames']
            sbc.categoryNumbers = obj['categoryNumbers']
            sbc.words = obj['words']
            sbc.wordNumbers = obj['wordNumbers']
            sbc.wordPairs = obj['wordPairs']
            sbc.priorProb = obj['priorProb']
            sbc.wordWeights = obj['wordWeights']
            sbc.pairWeights = dict()
            sbc.pairWeightsValues = obj['pairWeightsValues']
            i = 0
            for key in sbc.wordPairs:
                pair = (key[0], key[1])
                sbc.pairWeights[pair] = sbc.pairWeightsValues[i]
                if sbc.words[key[0]] == 'natural':
                    print(str(pair )+", (natural"+sbc.words[key[1]]+") ="+str(sbc.pairWeightsValues[i]))
                i += 1
            sbc.correlation_error = obj['correlation_error']
            print("read "+str(len(sbc.wordWeights))+" word weights and "+str(len(sbc.pairWeights))+" pair weights")
            return sbc



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

        for cat_index in range(0, parsed_category_sources.number_of_cats()):
            cat_name = cat_names[cat_index]
            for source in parsed_category_sources.get_sources(cat_name):
                n_documents += 1
                recognition_scores = self.recognition_scores(source)
                best = -1
                best_score = -1e30
                for rec_index in range(0, len(recognition_scores)):
                    rec = recognition_scores[rec_index]
                    if rec > best_score:
                        best_score = rec
                        best = rec_index
                best_cat_name = self.categoryNames[best]
                print(str(n_documents) + " cat= " + cat_name + " best fit " + best_cat_name + " best="+str(best))
                if best_cat_name == cat_name:
                    ok_sources = ok_sources + 1
        print(str(ok_sources)+" out of "+str(n_documents))
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
        cat_count = []
        cat_total = []
        cat_word_count = []
        cat_document_count = []
        average_word_factor = 0.0
        for i in range(0, len(self.categoryNames)):
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
                    if word1 in self.stopList:
                        continue
                    score = source.score(word1)
#                    print("word: "+word+", score="+str(score))
                    cat_word_count[i] += score
                    is_new = word_document_count.get(word1, 0) == 0
                    word_document_count[word1] = 1 + word_document_count.get(word1, 0)
                    cat_total[i][word1] = cat_total[i].get(word1, 0) + score
                    if is_new:
                        cat_count[i][word1] = cat_count[i].get(word1, 0) + score
                        total_count[word1] = total_count.get(word1, 0) + score
        words_to_use = []
        max_doc_count = (self.percentOfDocumentForStopListWords * document_count)/100.0
        for word in total_count.keys():
            if word_document_count.get(word, 0) < 2:
                continue
            square_info_gained = 0.0
            for i in range(0, len(self.categoryNames)):
                prob_word = word_document_count[word]/document_count
                prob_cat = cat_document_count[i] / document_count
                prob_cat_given_word = cat_count[i].get(word, 0) / cat_document_count[i]
                information = prob_word * self.entropy(prob_cat_given_word) + (1.0 - prob_word) * self.entropy(1.0 - prob_cat_given_word) - self.entropy(prob_cat)
                if information < 0:
                    continue
                square_info_gained += information*information
#                print("Word: "+word+" info "+str(square_info_gained)+" prop="+str(prob_word)+" prob_cat_given_word="+str(prob_cat_given_word))
            if square_info_gained > self.informationGainedThresholdWords * self.informationGainedThresholdWords:
#                print("Use word: "+word)
                words_to_use.append(word)
#            else:
#                print("Word: "+word+" info "+str(square_info_gained)+" skipping ")
        self.wordNumbers = dict()
        self.words = words_to_use
        print("Using "+str(len(words_to_use)) + " words");
        i = 0
        for word in words_to_use:
            self.wordNumbers[word] = i
            i += 1
        self.priorProb = []
        for i in range(0, len(self.categoryNames)):
            category_name = self.categoryNames[i]
            prob_cat = cat_document_count[i]/document_count
#            print("cat: "+str(i)+" : "+str(cat_document_count[i])+"/ "+str(document_count))
            self.priorProb.append(math.log(prob_cat))
#            print("cat: "+str(i)+" prior prob : "+str(self.priorProb[i]))
        self.wordWeights = self.laplace_estimator(cat_total, cat_word_count, words_to_use, 1.0)
        self.makePairs(sources)
        self.makeSuperBayes(sources)

        return document_count

    def makePairs(self, sources):
        n_total_pairs = 0
        n_doc_pairs = 0
        n_cats = len(self.categoryNames)
        n_cat_count_pairs = [0] * n_cats
        n_cat_total_pairs = [0] * n_cats
        doc_pair_count = dict()
        tot_pair_count = dict()
        cat_pair_count = []
        cat_pair_total = []
        cat_docs = []
        n_doc_total = 0
        for i in range(0, n_cats):
            cat_pair_count.append(dict())
            cat_pair_total.append(dict())
            cat_docs.append(0)
        for i in range(0, n_cats):
            category_name = self.categoryNames[i]
            inner_cat_pair_count = cat_pair_count[i]
            inner_cat_pair_total = cat_pair_total[i]
            inner_cat_count_pairs = 0
            inner_cat_total_pairs = 0
            cat_docs[i] += 1
            for source in sources.get_sources(category_name):
                word_array = source.get_words()
                if len(word_array) < 2:
                    continue
                this_doc = dict()
                word_1_num = -1
                n_doc_total += 1
                for word in source.keys():
                    word1 = word.lower()
                    if word.upper() == word1:
                        continue
                    if word in self.stopList:
                        continue
                    if word not in self.wordNumbers:
                        continue
                    word_num = self.wordNumbers[word]
                    if word_1_num == -1:
                        word_1_num = word_num
                        continue
                    word_pair = (word_1_num, word_num)
                    word_1_num = word_num
                    tot_pair_count[word_pair] = tot_pair_count.get(word_pair, 0)+1
                    inner_cat_pair_total[word_pair] = inner_cat_pair_total.get(word_pair, 0)+1
                    new_pair = word_pair not in this_doc
                    this_doc[word_pair] = this_doc.get(word_pair, 0) + 1
                    if new_pair:
                        inner_cat_count_pairs += 1
                        doc_pair_count[word_pair] = doc_pair_count.get(word_pair ,0) + 1
                        inner_cat_pair_count[word_pair] = inner_cat_pair_count.get(word_pair, 0) + 1
            n_total_pairs += inner_cat_total_pairs
            n_cat_total_pairs[i] += inner_cat_count_pairs
        # Pair selection
        pairs_to_use = []
        igtp2 = self.informationGainedThresholdPairs * self.informationGainedThresholdPairs
        for pair in tot_pair_count.keys():
            info_gained2 = 0
            pair_doc_count = doc_pair_count.get(pair, 0)
            for i in range(0, n_cats):
                prob_cat = cat_docs[i] / n_doc_total
                prob_pair = doc_pair_count.get(pair, 0)/ n_doc_total
                prob_cat_given_pair = cat_pair_count[i].get(pair, 0) / cat_docs[i]
                info = prob_pair * self.entropy(prob_cat_given_pair) + (1.0 - prob_pair) * self.entropy(1.0 - prob_cat_given_pair) - self.entropy(prob_cat)
                if info < 0:
                    continue
                info_gained2 += info*info
            if info_gained2 > igtp2:
                pairs_to_use.append(pair)

        self.wordPairs = pairs_to_use
        self.pairWeights = self.laplace_estimator_pairs(cat_pair_total, n_cat_total_pairs, pairs_to_use, self.weightBoostForPair)
        print("Using "+str(len(pairs_to_use))+" word pairs")


    def makeSuperBayes(self, sources):
        import math
        document_num_by_word = []
        word_occur = []
        total_occur = []
        category_total_word_count = []
        word_count_by_document = []
        category_for_document = []
        for iword in range(0, len(self.wordNumbers)):
            word_occur.append([])
            document_num_by_word.append([])
            word_count_by_document.append([])
        n_document = 0
        for category_number in range(0, len(self.categoryNames)):
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
                    if occs == 0:
                        continue
                    cat_total += occs
                    word_occur[word_num].append(occs)
                    document_num_by_word[word_num].append(n_document)
                    word_count_by_document[word_num].append(occs)
                    total_occur[category_number][word_num] += occs
                    if word == 'oilfield' and category_number == 2:
                        print("oilfield occs=" + str(occs)+" n_doc="+str(n_document))
                category_for_document.append(category_number)
                n_document += 1
            category_total_word_count.append(cat_total)
            if cat_total == 0:
                print("Warning category: "+category_name+" has no documents")
        prob_words = []
        ncats = len(self.categoryNames)
        for iword in range(0, len(self.wordNumbers)):
            cat_prob = []
            icat = 0
            while icat < len(self.categoryNames):
                count = category_total_word_count[icat]
                if count == 0:
                    icat += 1
                    cat_prob.append(0)
                    continue
                cat_prob.append(total_occur[icat][iword]/count)
                icat += 1
            prob_words.append(cat_prob)
        corr_err = []
        for aword in range(1, len(self.wordNumbers)):
#            print("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bCorrelations for word "+self.words[aword]+" "+ str(aword)+"<"+str(len(self.wordNumbers)))
            occ_a = word_count_by_document[aword]
            loc_a = document_num_by_word[aword]
            la = len(loc_a)
            corr_err_inner = [0] * aword
            for bword in range(0, aword):
                occ_b = word_count_by_document[bword]
                loc_b = document_num_by_word[bword]
                pa = loc_a[0]
                pb = loc_b[0]
                ia = 0
                ib = 0
                corr = [0] * ncats
                n_corr = 0
                lb = len(loc_b)
                while True:
                    if pa < pb:
                        ia += 1
                        if ia >= la:
                            break
                        pa = loc_a[ia]
                    elif pb < pa:
                        ib += 1
                        if ib >= lb:
                            break
                        pb = loc_b[ib]
                    else:
                        if ia >= la:
                            break
                        if ib >= lb:
                            break
                        if self.words[aword] == 'natural' and self.words[bword] == 'oilfield':
                            print(" category for document pa="+str(pa), " ia="+str(ia)+" occ_a="+str((occ_a[ia]))+" ib="+str(ib)+ " occ_b="+str(occ_b[ib]))
                            print(" is "+str(category_for_document[pa])+" len loc_b="+str(lb)+" len lcc_a="+str(la)+" len occ_a="+str(len(occ_a))+" len occ_b="+str(len(occ_b)))
                        corr[category_for_document[pa]] += self.sign(occ_a[ia]) * self.sign(occ_b[ib])
                        ia += 1
                        ib += 1
                        n_corr += 1
                        if ia >= la:
                            break
                        pa = loc_a[ia]
                        if ib >= lb:
                            break
                        pb = loc_b[ib]
                if n_corr == 0:
                    continue
                d_corr = [0] * ncats
                for j in range(0, ncats):
                    count = category_total_word_count[j]
                    if count < 1:
                        continue
                    d_corr[j] = corr[j] / (count - 1.0)
#                    if self.words[aword] == 'natural' and corr[j] != 0:
#                        print(self.words[bword] + " d_corr["+str(j)+"] = "+str(corr[j]))
                dotprod = 0.0
                papb_sq = 0.0
                corr_sq = 0.0
                for j in range(0, ncats):
#                    if len(prob_words[aword]) <= j:
#                        print(" error aword "+str(aword)+" cat len "+str(len(prob_words[aword])));
                    pcata = prob_words[aword][j]
                    pcatb = prob_words[bword][j]
                    p2 = pcata*pcatb
                    corr1 = d_corr[j]
                    dotprod += p2 * corr1
                    corr_sq += corr1 * corr1
                    papb_sq += p2 * p2
                if (papb_sq < 1.0e-20) or (corr_sq < 1.0e-20):
                    bword += 1
                    continue
                corr_err_inner[bword] = (1 - dotprod / math.sqrt(corr_sq * papb_sq))
#                if self.words[aword] == 'natural' and dotprod != 0:
#                   print("corr_err_inner: "+self.words[bword]+" = " + str(corr_err_inner[bword])+" dotprod "+str(dotprod)+", corr_sq="+str(corr_sq)+", papb_sq="+str(papb_sq))
            corr_err.append(corr_err_inner)
        self.correlation_error = corr_err
        print("")


    def laplace_estimator(self, word_freq, cat_word_count, keys, weight):
        import math
        ret = []
        for i in range(0, len(keys)):
            ret.append([])
            key = keys[i]
            for j in range(0, len(cat_word_count)):
                ret[i].append(weight * math.log((self.alpha + word_freq[j].get(key, 0)) / (self.alpha * len(keys) + cat_word_count[j])))
 #               print(key+","+str(word_freq[j].get(key, 0))+" "+str(i)+","+str(j)+"= "+str(ret[i][j]))
        return ret

    def laplace_estimator_pairs(self, word_freq, cat_word_count, keys, weight):
        import math
        ret = dict()
        for j in range(0, len(keys)):
            key = keys[j]
            ret[key] = [0] * len(cat_word_count)
            for i in range(0, len(cat_word_count)):
                ret[key][i] = weight * math.log((self.alpha_pair + word_freq[i].get(key, 0)) / (self.alpha_pair * len(keys) + cat_word_count[i]))
#                print(str(key)+","+str(i)+","+str(j)+"= "+str(ret[key][i]))
        return ret

    def sign(self, x):
        if x>0:
          return 1
        return 0

    def recognition_scores(self, word_count):
        import math
        rec_scores = []
        for i in range(0, len(self.priorProb)):
            rec_scores.append(self.priorProb[i])
        word_num = []
        number_of_words = 0
        for word in word_count.keys():
            word1 = word.lower()
            if word1 == word.upper():
                continue
            if word1 in self.wordNumbers:
                word_num.append(self.wordNumbers[word1])
                number_of_words += 1
        correlation_factor = [0] * len(self.wordNumbers)
        super_bayes_factor = math.log(2.0)
        for iword in range(1, number_of_words):
            for jword in range(0, number_of_words):
                word_a = word_num[iword]
                word_b = word_num[jword]
                x = 0
                try:
                    if word_a < word_b:
                        x = self.correlation_error[word_b][word_a]
                    elif word_a != word_b:
                        x = self.correlation_error[word_a][word_b]
                except:
                    x = 0
                if correlation_factor[word_a] < x:
#                    print(self.words[word_a]+" "+str(x))
                    correlation_factor[word_a] = x
                if correlation_factor[word_b] < x:
#                    print(self.words[word_b]+" "+str(x))
                    correlation_factor[word_b] = x
        sb_factor = [0] * len(self.wordNumbers)
        for i in range(0, len(self.wordNumbers)):
            x = correlation_factor[i]
            if x == 0:
                sb_factor[i] = 1
            else:
                sb_factor[i] = math.exp(-super_bayes_factor * x)
        last_word = -1
        for word in word_count.wordList:
            word1 = word.lower()
            if word1 == '.':
                last_word = -1
                continue
            if word1 == word.upper():
                continue
            if word1 in self.wordNumbers:
                word_number = self.wordNumbers.get(word1, -1)
                if word_number == -1:
                    last_word = -1
                    continue
                done_pair = False
                if last_word != -1:
                    pair = (last_word, word_number)
                    pair_weights = self.pairWeights.get(pair, [])
                    if len(pair_weights) > 0:
                        if self.words[last_word] == 'natural':
                            print("pair "+self.words[last_word]+","+self.words[word_number]+" found")
                        weights = self.wordWeights[word_number]
                        last_weights = self.wordWeights[last_word]
                        a = sb_factor[word_number]
                        b = sb_factor[last_word]
                        b = 1
                        c = max(a, b)  # Use highest correlation # Ignore correlation for pairs this has best score.
                        for cat_num in range(0, len(pair_weights)):
                            rec_scores[cat_num] += c*pair_weights[cat_num] - b * last_weights[cat_num]
#                        print("pair ("+str(last_word)+","+str(word_number)+" "+self.words[last_word]+","+self.words[word_number]+")  found")
                        last_word = -1
                        done_pair = True
                    else:
                        last_word = word_number
#                        print("pair ("+str(last_word)+","+str(word_number)+" "+self.words[last_word]+","+self.words[word_number]+") not found")
                if not done_pair:
                    for cat_num in range(0, len(rec_scores)):
#                        print("cat_num: "+str(cat_num) + ", score="+str(rec_scores[cat_num]) +" word_number="+str(word_number)+" last word "+str(last_word))
#                        rec_scores[cat_num] += sb_factor[word_number] * self.wordWeights[word_number][cat_num]
                        rec_scores[cat_num] += self.wordWeights[word_number][cat_num]
#                       print("cat_num: "+str(cat_num) + ", score="+str(rec_scores[cat_num]))
                    last_word = word_number
        return rec_scores

    def find_category_of(self, word_count):
        best = -1
        best_score = -1e30
        recognition_scores = self.recognition_scores(word_count)
        for rec_index in range(0, len(recognition_scores)):
            rec = recognition_scores[rec_index]
            if rec > best_score:
                best_score = rec
                best = rec_index
        best_cat_name = self.categoryNames[best]
        return best_cat_name

    def entropy(self, prop):
        import math
        if prop < 1.0e-17:
            return 0
        return prop * math.log(prop, 2)
