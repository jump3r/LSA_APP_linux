try:
    import os, gensim, logging, csv, glob, shutil
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
except(Exception):
    print "Error: did not import needed modules"

from UserInterfaceWindows import PrjSettings

PRJDATA = "/ProjectData/"
SETT_PICKL = "Settings.pickle"


class CreatorLSA(object):    
    ''' Class object used to convert corpus (bag of words) into gensim lsi model and perform
        operations on the model. ''' 
       
    def __init__(self, corpus = None, dic = None, topics=300):
        self.lsa = None
        
        if corpus != None and dic != None:
            self.lsa = gensim.models.LsiModel(corpus, id2word=dic, num_topics=topics)
            
        
    def saveModel(self, model_name):
        ''' Save model with a name model_name. Parameter model_name may include full path to 
            destination folder. ''' 
                       
        self.lsa.save(model_name)
        
            
    def loadModel(self, model_name):
        ''' Load lsi model with a name. Parameter model_name may include full path to folder
            with saved model. '''
                
        self.lsa = gensim.models.lsimodel.LsiModel.load(model_name)
        
        
    def add_documents(self, corpus):
        ''' Update lsi model with a given gensim object corpus. '''        
        if self.lsa != None:
            self.lsa.add_documents(corpus)
        else:
            print "Error: LSA model must be loaded first and then updated with corpus"
            
    
    def print_topic(self, topicno, top_words=10):
        ''' Print a number (topicno) of topics in the model with number (top_words) of words
            for each topic. '''        
        
        return self.lsa.print_topic(topicno, topn=top_words)
    

class LSAutils(object):
    ''' NOT USED '''
    def __init__(self):
        self.lsa = None
        
    def get_lsa(self, name):
        self.lsa = gensim.models.lsimodel.LsiModel.load(name)
        return self.lsa

    def loadModel(self, name):
        self.lsa = gensim.models.lsimodel.LsiModel.load(name)
    
    def saveModel(self, name):
        self.lsa.save(name)    
            
    def add_documents(self, corpus):
        if self.lsa != None:
            self.lsa.add_documents(corpus)
        else:
            print "lsa model is not loaded"    


class CorpusUtils(object):
    ''' Static class to provide set of operations on corpus and dictionary objects. '''
     
    def load_dict(self, dic_name):
        ''' Return gensim dictionary object with name dic_name. Dic_name can be a full path.'''
        
        return gensim.corpora.Dictionary.load(dic_name)
    
    
    def load_corp(self, corp_name):
        ''' Return gensim corpus object with name corp_name. Corp_name can be a full path. '''
        
        return gensim.corpora.MmCorpus(corp_name)
    
    
    def clear_input(self, inputString):
        ''' TO BE REPLACED WITH REGEX '''
        
        ''' Return string representing cleared student text from unmeaningful symbols and numbers. '''
        
        inputString = " " + inputString.lower() + " "
        to_remove = "\" \' ( ) [ ] , . ! ? { } : / \ ; @ # $ % ^ & * - = + "
        to_remove +="1 2 3 4 5 6 7 8 9 0"
        to_remove = to_remove.split()
        
        for symbol in to_remove:
            inputString=inputString.replace(symbol, " ")
        for word in open("stopwords.txt"):
            word = " " + word.strip() + " "            
            inputString = inputString.replace(word, " ")
                        
        return inputString
    
    
    def extractCSVtoTXTbyStudent(self, csvname, studCol, textCol, saveTo = "", 
                                 stopIndex = -1, heading = False, delimiter = ","):
        ''' Extract student conversations from .csv file format with name csvname where studCol 
            represents the column number with student names and textCol represents the column 
            number where text is stored for the student on the same row as student's name.
            If destination where saveTo notes is an empty string all notes will be saved into
            parent directory for this file. If heading is False it will be assumed that the file
            starts off student records right away, otherwise the first line will be skipped.
            If stopIndex is given, the function will only process a specified number of student
            entries. '''
        # Student names should not contain dots because they will be treated as separator
        # for student's names of students who collaborated/participated in writing the
        # same note. 
        
        file_csv = open(csvname, "r")
        csv.field_size_limit(10000000)
        reader_csv = csv.reader(file_csv, delimiter = delimiter, dialect = 'excel')        
        
        # check if directory was given
        if saveTo != "": 
            saveTo +="/"
                
        row_counter = 0 # used to skip the headings and identify line index in .csv file
        for row in reader_csv:
                                         
            studNotes = row[textCol].strip() # student notes
            studName = row[studCol].strip() # student name/names (separated by dot)
            
            # Case: multiple authors for the same note separated by dots
            student_list = studName.split(".")
            if len(student_list) > 1:
                try: student_list.remove("")
                # ValueError 
                # If empty string not in student_list
                except: continue
            
            for studName in student_list:
                studName = studName.strip()
                if heading == False or (heading == True and row_counter != 0):                
                    try:
                        # Check if .txt file was already created in project's directory
                        # for a current student with name studName earlier 
                        old_studNotes = open(saveTo + studName + ".txt", "r").read()
                        allNotes = old_studNotes + "\n\n" + studNotes
                        txt_file = open(saveTo + studName + ".txt", "w")
                        txt_file.writelines(allNotes)
                        txt_file.close()
                    except:
                        # Student with name studName is being processed first time and 
                        # requires separate .txt file to be created to store notes                    
                        txt_file = open(saveTo + studName + ".txt", "wb")
                        txt_file.writelines(studNotes)
                        txt_file.close()
                
                    row_counter += 1            
                else:
                    heading = False
                
            # Used for processing only a sample of all students
            # when stopIndex is specified.
                           
            if (stopIndex - row_counter) == 0:
                break

    
    def extractCSVintoTXT(self, csvname, text_col):        
        ''' Extract each student note in .csv file with name csvname into a separate .txt file with 
            the same name as student's name. If a student has more than one note, append it to already
            created file. '''
        
        file_csv = open(csvname, "r")
        csv.field_size_limit(10000000)
        reader_csv = csv.reader(file_csv, dialect = 'excel')        
        
        all_text = ""
        txt_file = open(csvname[:-4]+".txt", "w")
        for row in reader_csv:                       
            text_column = row[text_col]
            all_text+=text_column+" "
        
        txt_file.writelines(all_text)            
        txt_file.close()
            

class ExpCorpCreator(object):
    ''' Used to create corpus and dictionary out of multiple .txt files using MyCorpus class '''
    def __init__(self, folder = "", dic = None):
        ''' Process all .txt files inside given folder and create corpus and dictionary. 
            If gensim instance of dictionary is given, create corpus using that dictionary '''
        self.file_paths = []        
        self.corpus = None
        
        # Create list of full paths of each .txt file inside given folder
	#Settings = PrjSettings().UnPickleMe(folder+PRJDATA+SETT_PICKL)

        for doc in glob.glob(folder + "/*.txt"):#+"/"+ Settings.getCurWeekStr()
            path = ""
            for name in doc.split("/"):
                path += name+"/"
            
            self.file_paths.append(path[:-1])
        # ====
        print self.file_paths
	print "==============="
        if dic == None:
            self.corpus = MyCorpus(self.file_paths)
        else:
            self.corpus = MyCorpus()
            self.corpus.dictionary = dic
            self.corpus.input = self.file_paths
            self.corpus.get_texts()
    
    def getAllDocsNames(self):
        only_names = []
        for doc in self.file_paths:
            only_names.append(doc.split("/")[-1])
        return only_names
            
    def getCorpus(self):
        
        return self.corpus
    
    
    def getDict(self):
        
        return self.corpus.dictionary
    
    
    def saveDict(self, name):
        ''' Save gensim instance of dictionary at given name (can be a path). ''' 
        
        self.corpus.dictionary.save(name + ".dict")
        self.corpus.dictionary.save_as_text(name + ".txt")
        
        
    def saveCorpus(self, name):
        ''' Save gensim instance of corpus at given name (can be a path). '''
        
        gensim.corpora.MmCorpus.serialize(name + ".mm", self.corpus)
        
        
    def save(self, nameCorp, nameDic):
        ''' Save both corpus and dictionary. '''
        
        self.saveCorpus(nameCorp)
        self.saveDict(nameDic)
        
            
class MyCorpus(gensim.corpora.TextCorpus):
    '''Used to create corpus and dictionary from multiple .txt files'''
    '''Setup for training LSA model with output corpus and dict'''
    
    def get_texts(self):
        ''' Overriden function of gensim.corpora.TextCorpus to process files. '''
          
        for filename in self.input:
            yield self.clear_input(open(filename).read().lower()).split()  
                      
            
    def clear_input(self, inputString):
        ''' Return string representing cleared student text from unmeaningful symbols and numbers. '''
        
        inputString = " " + inputString.lower() + " "
        to_remove = "\" ( ) [ ] , . ! ? { } : / \ ; @ # $ % ^ & * - = + "
        to_remove +="1 2 3 4 5 6 7 8 9 0"
        to_remove = to_remove.split()
        
        for symbol in to_remove:
            inputString=inputString.replace(symbol, " ")
        
        for word in open("stopwords.txt"):
            word = " " + word.strip() + " "            
            inputString = inputString.replace(word, " ")
        
        return inputString.strip()
    

class SimUtils(object):
    ''' Used to extract similarities matrix out of lsi corpus of processed documents. ''' 
    
    def __init__(self):
        self.index = None
        
    
    def MatrixSim(self, lsa, corpus):
        ''' Find similarities by converting corpus (bag of words) into lsi using already made
            lsi model. '''
        
        index = gensim.similarities.MatrixSimilarity(lsa[corpus])
        self.index = index
    
    def SaveIndex(self, path):
        
        self.index.save(path + ".index")
        self.index = None
                
                
    def LoadIndex(self, path):
        
        self.index = gensim.similarities.MatrixSimilarity.load(path + ".index")
        
        
    def saveSimMatrix(self, matrix, saveTo):
        
        matrixStr = ""
        for sim in matrix:
            for num in sim:                
                new_num = str(float(num))
                matrixStr += new_num + " "
            matrixStr = matrixStr[:-1] + "\n"
        
        fileTo = open(saveTo + ".txt", "w")
        fileTo.writelines(matrixStr[:-2])
        fileTo.close()
    
