#!/usr/bin/python

import wx, glob, os, GraphTools
import MainTools
import cPickle
import shutil

#paths:
PRJDATA = "/ProjectData/"
PRJDATA_MTRX_TXT = PRJDATA+"Matrix.txt"
SETT_PICKL = "Settings.pickle"
PRJDATA_PICKL = PRJDATA+SETT_PICKL
PRJDATA_LSA = PRJDATA+"lsa.lsi"
PRJDATA_SIMMTRX = PRJDATA+"SimilarityMatrix"
PRJDATA_CORPMM = PRJDATA+"corpus.mm"
PRJDATA_MTRX_INDX = PRJDATA+"Matrix"   

class PrjSettings(object):
    ''' This class is used to hold all user settings. ''' 
    
    def __init__(self):        
        ''' Store all project related information into the following variables. '''
        # For creating/storing students-related dependencies
        self.name = "" # project folder name
        self.info = "" # information about a new project
        self.path = "" # path to .csv file on disk
        self.topics = "" #
        self.stopIndex = -1 # number of notes to be processed from a .csv file
        self.heading = False # first row is not a heading in .csv file
        self.studNames = None # keeps the same student names order as similarity matrix in txt file
        self.columns = [] # 1st element is student name column, 2nd element is student note column
        self.avg_val = None # a list of average values of student interactions
        self.edges = {} # Set up after matrix have been processed for node graph
        self.commun = {} # Holds sub-communities of collection of students
        self.DataEdgDistGraph = None # data for Edge Distribution Graph 
	self.WeekCount = 1
	self.periodic_avg_val = {}
        
        # For creating/storing expert corpus related dependencies
        self.name_of_all_docs = []
        self.corpus_batch_name = ""
        
    def MergeWithPrevPeriods(self):#,studNames, avg_val):
	#self.studNames=studNames
	#self.avg_val=avg_val
	
	if self.periodic_avg_val == {}:
	    for name in self.studNames:
		self.periodic_avg_val[name]=[self.avg_val[self.studNames.index(name)]]
	else:
	    print self.studNames, len(self.studNames), len(self.periodic_avg_val)
	    for name in self.periodic_avg_val:
		self.periodic_avg_val[name].append(self.avg_val[self.studNames.index(name)])
	    for name in self.studNames:
		if name not in self.periodic_avg_val:
		    self.periodic_avg_val[name] = [0]*(self.WeekCount-1)+[self.avg_val[self.studNames.index(name)]]
	   
	
    
    def PickleMeAsStudents(self, path = None):
        ''' Pickle all information for students project into its directory. '''
        
        if path == None:
            path = self.name + PRJDATA
        file = open(path + SETT_PICKL, "wb")
        cPickle.dump(self, file, protocol = -1)        
        file.close()
        
        
    def PickleMeAsExpCorp(self, dir_name):
        ''' Pickle all information for expert corpus project into directory dir_name. '''
        
        file = open(dir_name + "/" + SETT_PICKL, "wb")
        cPickle.dump(self, file, protocol = -1)        
        file.close()
        
        
    def UnPickleMe(self, file_name=None): 
        ''' Return previously pickled class object with all saved project information. '''    
        if file_name == None:
	    file_name = self.name + PRJDATA + SETT_PICKL
        return cPickle.load( open(file_name, "rb") )
    
        
    def ClearStudNames(self):
        ''' Cut off full path to student's .txt file and leave only their names. '''
        
        newNames = []
        for path in self.studNames:
            name = path[:-4].split("/")[-1]
            newNames.append(str(name))
        self.studNames = newNames    

    def IncrementWeekCount(self):
	self.WeekCount+=1
	

    def getCurWeekStr(self):
	return "Week"+str(self.WeekCount)
    
'''=================================================================================='''

class StartWin ( wx.Panel ):
    ''' Welcome window that allows user to create new project or select existing project. '''
    
    def __init__( self, parent ):
        ''' Auto generated code for UI using wxFormBuilder v3.1 - Beta. '''
        
        wx.Panel.__init__  ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 223,407 ), style = wx.TAB_TRAVERSAL )
        parent.Center()
        
        
        bSizer18 = wx.BoxSizer( wx.VERTICAL ) # Main box sizer    
        bSizer36 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_bitmap3 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,150 ), 0 )
        bSizer36.Add( self.m_bitmap3, 0, wx.ALL|wx.EXPAND, 5 )
        
        bSizer18.Add( bSizer36, 3, wx.EXPAND, 5 )        
        bSizer37 = wx.BoxSizer( wx.VERTICAL )
        
        self.bt_NewProject = wx.Button( self, wx.ID_ANY, "New Project", wx.DefaultPosition, wx.Size( 200,50 ), 0 )
        self.bt_NewProject.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_NewProject.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
        
        bSizer37.Add( self.bt_NewProject, 0, wx.ALL|wx.EXPAND, 5 )        
        bSizer18.Add( bSizer37, 1, wx.EXPAND, 5 )                
        bSizer38 = wx.BoxSizer( wx.VERTICAL )    
            
        self.bt_SelectProject = wx.Button( self, wx.ID_ANY, "Saved Projects", wx.DefaultPosition, wx.Size( 200,50 ), 0 )
        self.bt_SelectProject.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_SelectProject.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
        
        bSizer38.Add( self.bt_SelectProject, 0, wx.ALL|wx.EXPAND, 5 )        
        bSizer18.Add( bSizer38, 1, wx.EXPAND, 5 )        
        
        
        bSizer38_5 = wx.BoxSizer( wx.VERTICAL )
        self.bt_ExpCorpus = wx.Button( self, wx.ID_ANY, "Expert Corpus", wx.DefaultPosition, wx.Size( 200,50 ), 0 )
        self.bt_ExpCorpus.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_ExpCorpus.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
        self.bt_ExpCorpus.Disable()
        
        bSizer38_5.Add(self.bt_ExpCorpus, 0, wx.ALL|wx.EXPAND, 5 )
        bSizer18.Add( bSizer38_5, 1, wx.EXPAND, 5 )
        bSizer39 = wx.BoxSizer( wx.VERTICAL )
        
        # Exit button
        self.bt_Exit = wx.Button( self, wx.ID_ANY, "EXIT", wx.DefaultPosition, wx.Size( 200,50 ), 0 )
        self.bt_Exit.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Exit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
        
        bSizer39.Add( self.bt_Exit, 0, wx.ALL|wx.EXPAND, 5 )        
        bSizer18.Add( bSizer39, 1, wx.EXPAND, 5 )
        
        # Binding events for buttons
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.bt_Exit)
        self.Bind(wx.EVT_BUTTON, self.OnCreate, self.bt_NewProject)
        self.Bind(wx.EVT_BUTTON, self.OnSelect, self.bt_SelectProject)
        self.Bind(wx.EVT_BUTTON, self.OnExpCorpus, self.bt_ExpCorpus)
        
        self.SetSizer( bSizer18 )
        self.Layout()
        
        
    def OnExit(self, event):  
        ''' Close application. '''
        
        self.Parent.Destroy()     
        self.Destroy()       
        
    
    def OnCreate(self, event):
        ''' Start new project. '''        
        
        self.Parent.Destroy()
        self.Destroy() 
        frame = wx.Frame(None, -1, "New Project")
	frame.SetSize((400,600))
        NewProjectWin(frame)
        frame.Show(True)    
           
        
    def OnSelect(self, event):
        ''' Select existing project. '''
        
        self.Parent.Destroy()
        self.Destroy()        
        newFrame = wx.Frame(None, -1, "Available Projects")
	newFrame.SetSize((400,600))
        SelectPrjWin(newFrame)
        newFrame.Show()
    
    def OnExpCorpus (self, event):
        ''' Open create expert corpus window. '''
        
        self.Parent.Destroy()
        self.Destroy()
        
        newFrame = wx.Frame(None, -1, "New Expert Corpus")
	newFrame.SetSize((400,600))
        CreateExpertCorpus(newFrame)
        newFrame.Show()

        

'''
class CreateExpertCorpus ( wx.Panel ):
    
    # Folder name where all expert corpuses are located
    global ExpCorpusFolder 
    ExpCorpusFolder = "ExpertCorpuses"
    
    global ExpCorpSettings
    ExpCorpSettings = PrjSettings()
    
    def __init__( self, parent ):
        wx.Panel.__init__  ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 434,486 ), style = wx.TAB_TRAVERSAL )
        parent.Centre()
        
        
        bSizer14 = wx.BoxSizer( wx.HORIZONTAL )        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )        
        bSizer5 = wx.BoxSizer( wx.VERTICAL )        
        bSizer8 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Folder with Corpus Files:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer8.Add( self.m_staticText2, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer5.Add( bSizer8, 1, wx.EXPAND, 5 )
        
        bSizer9 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_listBox2 = wx.TextCtrl( self, wx.ID_ANY, "Drag and drop here.", wx.DefaultPosition, wx.DefaultSize, 0|wx.RAISED_BORDER )
        self.m_listBox2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
        self.dropTarget = MyFileDropTarget(self)
        self.m_listBox2.SetDropTarget(self.dropTarget)
        
        bSizer9.Add( self.m_listBox2, 1, wx.ALL|wx.EXPAND, 2 )
        
        bSizer5.Add( bSizer9, 2, wx.EXPAND, 5 )
        
        bSizer2.Add( bSizer5, 1, wx.EXPAND, 5 )
        
        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
        
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer10 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, "Listed Corpus Files:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer10.Add( self.m_staticText3, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer3.Add( bSizer10, 1, wx.EXPAND, 5 )
        
        bSizer11 = wx.BoxSizer( wx.VERTICAL )
        
        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0|wx.ALWAYS_SHOW_SB|wx.HSCROLL|wx.SIMPLE_BORDER )
        self.m_listBox1.SetHelpText( "All documents that will be included in creating expert corpus/n" )
        
        bSizer11.Add( self.m_listBox1, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer3.Add( bSizer11, 6, wx.EXPAND, 5 )
        
        bSizer1.Add( bSizer3, 3, wx.EXPAND, 5 )
        
        bSizer12 = wx.BoxSizer( wx.VERTICAL )
        
        self.bt_CreateExpCorpus = wx.Button( self, wx.ID_ANY, "Create E.C.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.bt_CreateExpCorpus.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_CreateExpCorpus.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer12.Add( self.bt_CreateExpCorpus, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.bt_Back = wx.Button( self, wx.ID_ANY, "Back", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.bt_Back.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Back.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer12.Add( self.bt_Back, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer1.Add( bSizer12, 2, wx.EXPAND, 5 )
        
        bSizer14.Add( bSizer1, 1, wx.EXPAND, 5 )
        
        bSizer13 = wx.BoxSizer( wx.VERTICAL )
        bSizer16 = wx.BoxSizer( wx.VERTICAL )
        
        ExpCorpusListChoices = []
        self.ExpCorpusList = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ExpCorpusListChoices, 0 )
        bSizer16.Add( self.ExpCorpusList, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer13.Add( bSizer16, 4, wx.EXPAND, 5 )
        
        bSizer17 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer18 = wx.BoxSizer( wx.VERTICAL )
        
        self.bt_Settings = wx.Button( self, wx.ID_ANY, "Settings", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.bt_Settings.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Settings.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        self.bt_Settings.Enable(enable = False)
        
        bSizer18.Add( self.bt_Settings, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer17.Add( bSizer18, 1, wx.EXPAND, 5 )
        
        bSizer19 = wx.BoxSizer( wx.VERTICAL )
        
        self.bt_Delete = wx.Button( self, wx.ID_ANY, "Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.bt_Delete.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Delete.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer19.Add( self.bt_Delete, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer17.Add( bSizer19, 1, wx.EXPAND, 5 )
        
        bSizer13.Add( bSizer17, 2, wx.EXPAND, 5 )
        
        bSizer14.Add( bSizer13, 1, wx.EXPAND, 5 )
        
        
        self.Bind(wx.EVT_BUTTON, self.OnCreate, self.bt_CreateExpCorpus)
        self.Bind(wx.EVT_BUTTON, self.OnBack, self.bt_Back)
        self.Bind(wx.EVT_BUTTON, self.OnSettings, self.bt_Settings)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, self.bt_Delete)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListCorpFiles, self.m_listBox1)
        
        self.CreateExpCorDir()
        self.FillExpCorpToList()
        
        self.SetSizer( bSizer14 )
        self.Layout()

    def CreateExpCorDir(self):
         
        if not os.path.exists(ExpCorpusFolder):
            os.mkdir(ExpCorpusFolder)
        
    def FillExpCorpToList(self):
        
        self.ExpCorpusList.Clear()
        exp_corpuses = glob.glob(ExpCorpusFolder + "/*/")
        
        for folder in exp_corpuses:
            self.ExpCorpusList.Append(folder.split("/")[-2])
        
        
    def OnCreate(self,event):       
        path_to_source_files = self.m_listBox2.GetValue()        
        expert_corp_name = path_to_source_files.split("/")[-1]
        path_to_destination_save = ExpCorpusFolder + "/" + expert_corp_name
	
        # Check if expert corpus folder exists
        if not os.path.exists(path_to_destination_save):
            os.mkdir(ExpCorpusFolder + "/" + expert_corp_name)
        
        ExpertCorpus = MainTools.ExpCorpCreator(folder = path_to_source_files)
        path_save_corp_dic = path_to_destination_save + "/" + expert_corp_name
        ExpertCorpus.save(path_save_corp_dic, path_save_corp_dic)
        
        ExpCorpSettings.batch_corpus_name = expert_corp_name
        ExpCorpSettings.name_of_all_docs = ExpertCorpus.getAllDocsNames()
        ExpCorpSettings.PickleMeAsExpCorp(path_to_destination_save)        
        
        self.FillExpCorpToList() 
        
    def OnListCorpFiles(self, event):
        #FIX !!!!!!!!!!!!!!!!!!
        self.m_listBox1.Clear()        
        position = self.ExpCorpusList.GetSelection()
        corpus_name = self.ExpCorpusList.GetItems()[position]
        
        try:
            settings = ExpCorpSettings.UnPickleMe(ExpCorpusFolder + "/"+ 
                                                  corpus_name + "/Settings.pickle")
            for doc in settings.name_of_all_docs:
                self.m_listBox1.Append(doc)
        
        except:
            print "Nothing was selected"
        
    
    def OnSettings(self, event):
        pass
    
    def OnDelete(self, event):
        position = self.ExpCorpusList.GetSelection()
        corpus_name = self.ExpCorpusList.GetItems()[position]
        
        try:            
            shutil.rmtree(ExpCorpusFolder + "/" + corpus_name)
            print "Project " + corpus_name + " has been removed."
        except:
            print "Cannot remove " + corpus_name +"."
                
        self.FillExpCorpToList()
                               
    
    def OnBack(self, event):        
        #Go back to previous window (Welcome). 
        
        self.Parent.Destroy()
        self.Destroy()        
        newFrame = wx.Frame(None, -1, "Welcome")
	newFrame.SetSize((400,400))
        StartWin(newFrame)
        newFrame.Show()
'''        

class SelectPrjWin ( wx.Panel ):
    ''' Application window to select existing projects. '''
    
    def __init__( self, parent ):
        ''' Auto generated code for UI using wxFormBuilder v3.1 - Beta '''   
             
        wx.Panel.__init__  ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 415,420 ), style = wx.TAB_TRAVERSAL )
        parent.Center()
        
        bSizer40 = wx.BoxSizer( wx.HORIZONTAL ) # Main box sizer  
        bSizer41 = wx.BoxSizer( wx.VERTICAL )        
        bSizer51 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, "Projects:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )
        self.m_staticText25.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer51.Add( self.m_staticText25, 1, wx.ALL|wx.EXPAND, 5 )        
        bSizer41.Add( bSizer51, 1, wx.EXPAND, 5 )
        
        bSizer43 = wx.BoxSizer( wx.VERTICAL )
        
        ListOfProjectsChoices = [] # Will contain all projects' names 
        self.ListOfProjects = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,160 ), ListOfProjectsChoices, wx.LB_ALWAYS_SB|wx.LB_HSCROLL|wx.SIMPLE_BORDER )
        self.ListOfProjects.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer43.Add( self.ListOfProjects, 3, wx.ALL|wx.EXPAND, 5 )        
        bSizer41.Add( bSizer43, 11, wx.EXPAND, 5 )
        
        bSizer44 = wx.BoxSizer( wx.VERTICAL )
        # Open button
        self.m_button5 = wx.Button( self, wx.ID_ANY, "Open", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.m_button5.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.m_button5.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer44.Add( self.m_button5, 1, wx.ALL|wx.EXPAND, 5 )
        # Delete button
        self.bt_delete = wx.Button( self, wx.ID_ANY, "Delete", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.bt_delete.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_delete.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer44.Add( self.bt_delete, 1, wx.ALL|wx.EXPAND, 5 )
        # Go to previous(start) window button
        self.m_button6 = wx.Button( self, wx.ID_ANY, "Back", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.m_button6.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.m_button6.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer44.Add( self.m_button6, 1, wx.ALL|wx.EXPAND, 5 )        
        bSizer41.Add( bSizer44, 7, wx.EXPAND, 5 )        
        bSizer40.Add( bSizer41, 1, wx.EXPAND, 5 )        
        bSizer42 = wx.BoxSizer( wx.VERTICAL )        
        bSizer45 = wx.BoxSizer( wx.HORIZONTAL )        
        bSizer47 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticline21 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer47.Add( self.m_staticline21, 0, wx.EXPAND |wx.ALL, 5 )
        
        # Shows project name
        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, "Project Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        self.m_staticText16.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer47.Add( self.m_staticText16, 1, wx.ALL|wx.EXPAND, 10 )
        
        # (Unimplemented) Shows creation date for selected project  
        self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, "Date:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        self.m_staticText17.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer47.Add( self.m_staticText17, 1, wx.ALL|wx.EXPAND, 10 )
        
        # Shows number of students in selected project 
        self.m_staticText18 = wx.StaticText( self, wx.ID_ANY, "Total Students:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText18.Wrap( -1 )
        self.m_staticText18.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer47.Add( self.m_staticText18, 1, wx.ALL, 10 )
        
        # Shows group score for selected project
        self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, "Group Score:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        self.m_staticText19.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer47.Add( self.m_staticText19, 1, wx.ALL|wx.EXPAND, 10 )
        
        self.m_staticline23 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer47.Add( self.m_staticline23, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer45.Add( bSizer47, 1, wx.EXPAND, 5 )        
        bSizer48 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticline22 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer48.Add( self.m_staticline22, 0, wx.EXPAND |wx.ALL, 5 )
        
        # All of the following static fields will dynamically change when user clicks on any project
        # from available projects window to reflect related project information as commented above
        
        # Project name
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        bSizer48.Add( self.m_staticText9, 1, wx.ALIGN_CENTER|wx.ALL, 10 )
        
        # (Unimplemented) Date of creation
        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )
        bSizer48.Add( self.m_staticText21, 1, wx.ALIGN_CENTER|wx.ALL, 10 )
        
        # Number of participants(students) in selected project
        self.m_staticText91 = wx.StaticText( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText91.Wrap( -1 )
        bSizer48.Add( self.m_staticText91, 1, wx.ALIGN_CENTER|wx.ALL, 10 )
        
        # (Unimplemented) Total group score
        self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText23.Wrap( -1 )
        bSizer48.Add( self.m_staticText23, 1, wx.ALIGN_CENTER|wx.ALL, 10 )
        # =====
        
        # Line to separate project's info above and any entered project information at the time of creation
        self.m_staticline24 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer48.Add( self.m_staticline24, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer45.Add( bSizer48, 1, wx.EXPAND, 5 )        
        bSizer42.Add( bSizer45, 2, wx.EXPAND, 5 )        
        bSizer46 = wx.BoxSizer( wx.VERTICAL )        
        bSizer49 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, "Project Information:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        self.m_staticText24.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer49.Add( self.m_staticText24, 1, wx.ALL|wx.EXPAND, 5 )        
        bSizer46.Add( bSizer49, 1, wx.EXPAND, 5 )        
        bSizer50 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_textCtrl17 = wx.TextCtrl( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.Size( -1,150 ), 0 )
        bSizer50.Add( self.m_textCtrl17, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer46.Add( bSizer50, 6, wx.EXPAND, 5 )        
        bSizer42.Add( bSizer46, 2, wx.EXPAND, 5 )        
        bSizer40.Add( bSizer42, 1, wx.EXPAND, 5 )
        
        self.SetSizer( bSizer40 )
        
        self.FillOutTable() # Adds project names to a list of all available projects
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListBoxSelect, self.ListOfProjects)
        self.Bind(wx.EVT_BUTTON, self.OnOpenProject, self.m_button5)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteProject, self.bt_delete)  
        self.Bind(wx.EVT_BUTTON, self.OnGoBack, self.m_button6)        
        self.Layout()
        
        
    def OnGoBack(self, event):
        ''' Go back to previous window (Welcome). '''
        
        self.Parent.Destroy()
        self.Destroy()        
        newFrame = wx.Frame(None, -1, "Welcome")
	newFrame.SetSize((400,400))
        StartWin(newFrame)
        newFrame.Show()
        
        
    def FillOutTable(self):        
        ''' Add project names to a list of available projects. '''
        
        folders = glob.glob("*/") # Select all folders(projects) in app's directory 
        for folder in folders:
            self.ListOfProjects.Append(folder[:-1])
            
    
    def OnListBoxSelect(self, event):
        ''' Update all labels associated with selected project. '''
        ''' Note: date and group score do not update (unimplemented)'''
        
        self.m_staticText9.SetLabel("")
        self.m_staticText91.SetLabel("")
        self.m_textCtrl17.SetLabel("None")
        
        position = self.ListOfProjects.GetSelection()        
        projectName = self.ListOfProjects.GetItems()[position]        
        pathToSet = projectName + PRJDATA+"Settings.pickle"
        Settings = PrjSettings().UnPickleMe(pathToSet)
                
        self.m_staticText9.SetLabel(Settings.name)
        self.m_staticText91.SetLabel("  "+str(len(Settings.studNames)))
        self.m_textCtrl17.SetLabel(Settings.info)
        
    
    def OnDeleteProject(self, event):
        ''' Delete selected project's directory and any related content. '''
        
        position = self.ListOfProjects.GetSelection()
        projectName = self.ListOfProjects.GetItems()[position]
        
        try:            
            shutil.rmtree(projectName)
            print "Project " + projectName + " has been removed."
        except:
            print "Cannot remove " + projectName +"."
               
        self.ListOfProjects.Clear()
        self.FillOutTable()
        
    
    def OnOpenProject(self, event):
        ''' Open selected project. ''' 
        
        position = self.ListOfProjects.GetSelection()
        
        projectName = self.ListOfProjects.GetItems()[position]
        pathTo = projectName + PRJDATA_MTRX_TXT
        pathToSet = projectName + PRJDATA_PICKL
        Settings = PrjSettings().UnPickleMe(pathToSet)        
        
        frameWithTabs = GraphTools.NoteBookTabs(title = "Project: " + Settings.name)
        graph = GraphTools.GroupNetworkGraph(frameWithTabs.panel, pathTo, Settings)
        graph2 = GraphTools.StudentInteractionDetailsPanel(frameWithTabs.panel, pathTo, Settings, updateWeek=False)
        frameWithTabs.AddTab(graph2)
        frameWithTabs.AddTab(graph)
        frameWithTabs.Show()

  
class MyFileDropTarget(wx.FileDropTarget):
    ''' Create on drop object inside application window to allow dropping .csv files to be processed. '''
    
    def __init__(self, parent):        
        wx.FileDropTarget.__init__(self)
        self.parent = parent        
        

    def OnDropFiles(self, x, y, filenames):
        ''' Handle event of dropping file onto target. '''
        
        for file in filenames:            
            #Settings.path = file #not global anymore, needs to change
            self.parent.m_listBox2.SetLabel(file)           
           
            
class NewProjectWin ( wx.Panel ):
    ''' Window for creating new project. '''
    
    def __init__(self, parent):
        ''' Auto generated code for UI using wxFormBuilder v3.1 - Beta '''
        
        wx.Panel.__init__  ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 415,462 ), style = wx.TAB_TRAVERSAL )
        parent.Center()
        self.Settings = PrjSettings()
        bSizer19 = wx.BoxSizer( wx.HORIZONTAL )        
        bSizer23 = wx.BoxSizer( wx.VERTICAL )        
        bSizer25 = wx.BoxSizer( wx.HORIZONTAL)        
        bSizer32 = wx.BoxSizer( wx.VERTICAL )        
        bSizer28 = wx.BoxSizer( wx.VERTICAL )
        #
        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, "Project Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        self.m_staticText12.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer28.Add( self.m_staticText12, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.stat_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        bSizer28.Add( self.stat_name, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer32.Add( bSizer28, 2, wx.EXPAND, 5 )        
        bSizer33 = wx.BoxSizer( wx.HORIZONTAL )
        #
        self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, "Project Information:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )
        self.m_staticText13.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer33.Add( self.m_staticText13, 1, wx.ALL|wx.EXPAND, 5 )        
        bSizer32.Add( bSizer33, 1, wx.EXPAND, 5 )        
        bSizer25.Add( bSizer32, 1, wx.EXPAND, 5 )        
        bSizer23.Add( bSizer25, 1, wx.EXPAND, 5 )        
        bSizer26 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_datePicker2 = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
        self.m_datePicker2.Enable(enable = False)
        bSizer26.Add( self.m_datePicker2, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.stat_info = wx.TextCtrl( self, wx.ID_ANY, "None", wx.DefaultPosition, wx.Size( -1,150 ), 0|wx.SIMPLE_BORDER )
        bSizer26.Add( self.stat_info, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer23.Add( bSizer26, 2, wx.EXPAND, 5 )        
        bSizer27 = wx.BoxSizer( wx.VERTICAL )
        
        self.bt_Proceed = wx.Button( self, wx.ID_ANY, "Create", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.bt_Proceed.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Proceed.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer27.Add( self.bt_Proceed, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.bt_AdvSettings = wx.Button( self, wx.ID_ANY, "Advanced Settings", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.bt_AdvSettings.SetFont( wx.Font( 13, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_AdvSettings.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        self.bt_AdvSettings.Enable(enable = False)
        
        bSizer27.Add( self.bt_AdvSettings, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.bt_Back = wx.Button( self, wx.ID_ANY, "Back", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
        self.bt_Back.SetFont( wx.Font( 15, 75, 90, 90, False, wx.EmptyString ) )
        self.bt_Back.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
        
        bSizer27.Add( self.bt_Back, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizer23.Add( bSizer27, 2, wx.EXPAND, 5 )        
        bSizer19.Add( bSizer23, 2, wx.EXPAND, 5 )        
        bSizer24 = wx.BoxSizer( wx.VERTICAL )        
        bSizer30 = wx.BoxSizer( wx.VERTICAL )        
        bSizer34 = wx.BoxSizer( wx.VERTICAL )
        
        # Drop .csv file onto this TextCtrl
        self.m_listBox2 = wx.TextCtrl( self, wx.ID_ANY, "Drag and drop your .csv file here or /nbrowse below/n", wx.DefaultPosition, wx.Size( -1,40 ), 0|wx.RAISED_BORDER )
        self.m_listBox2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
        self.dropTarget = MyFileDropTarget(self)
        self.m_listBox2.SetDropTarget(self.dropTarget)
        
        bSizer34.Add( self.m_listBox2, 1, wx.ALL|wx.EXPAND, 5 )        
        bSizer30.Add( bSizer34, 1, wx.EXPAND, 5 )        
        bSizer35 = wx.BoxSizer( wx.VERTICAL )
                
        #self.m_dirPicker2 = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, "Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
        #self.m_dirPicker2.Enable(enable = True)
        #bSizer35.Add( self.m_dirPicker2, 1, wx.ALL|wx.EXPAND, 8 )
        self.bt_BrowseFiles = wx.Button(self, -1, "Browse Files", (50,50))
        bSizer35.Add( self.bt_BrowseFiles, 1, wx.ALL | wx.EXPAND, 8)
        
        self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer35.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer30.Add( bSizer35, 1, wx.EXPAND, 5 )        
        bSizer24.Add( bSizer30, 2, wx.EXPAND, 5 )        
        bSizer31 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, "SETTINGS", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        self.m_staticText15.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 92, False, wx.EmptyString ) )
        
        bSizer31.Add( self.m_staticText15, 1, wx.ALIGN_CENTER|wx.ALIGN_TOP, 11 )
        
        self.m_staticline12 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer31.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, "Student Names Column:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        self.m_staticText9.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 90, False, wx.EmptyString ) )
        
        bSizer31.Add( self.m_staticText9, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.stud_namesCol = wx.TextCtrl( self, wx.ID_ANY, "4", wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        bSizer31.Add( self.stud_namesCol, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer31.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, "Student Notes Column:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        self.m_staticText10.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 90, False, wx.EmptyString ) )
        
        bSizer31.Add( self.m_staticText10, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.stud_notesCol = wx.TextCtrl( self, wx.ID_ANY, "6", wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        bSizer31.Add( self.stud_notesCol, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer31.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, "Number Of Topics In LSA:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        self.m_staticText11.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 90, False, wx.EmptyString ) )
        
        bSizer31.Add( self.m_staticText11, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.numTopics = wx.TextCtrl( self, wx.ID_ANY, "300", wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        bSizer31.Add( self.numTopics, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer31.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, "Number Of Notes:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        self.m_staticText14.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 90, False, wx.EmptyString ) )
        
        bSizer31.Add( self.m_staticText14, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.st_numNotes = wx.TextCtrl( self, wx.ID_ANY, "-1", wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        bSizer31.Add( self.st_numNotes, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.m_staticline9 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer31.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.cb_heading = wx.CheckBox( self, wx.ID_ANY, "Omit Headings", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cb_heading.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 74, 90, 90, False, wx.EmptyString ) )
        
        bSizer31.Add( self.cb_heading, 0, wx.ALIGN_CENTER|wx.ALL, 5 )        
        bSizer24.Add( bSizer31, 6, wx.EXPAND, 5 )        
        bSizer19.Add( bSizer24, 2, wx.EXPAND, 5 )
    
        self.Bind(wx.EVT_BUTTON, self.OnProceed, self.bt_Proceed)
        self.Bind(wx.EVT_BUTTON, self.OnGoBack, self.bt_Back)
        self.Bind(wx.EVT_BUTTON, self.OnBrowseFiles, self.bt_BrowseFiles)
        self.SetSizer( bSizer19 )
        self.Layout()
        
    def OnBrowseFiles(self, event):
        wildcard = "CSV (*.csv)|*.csv|"     \
           "Python (*.py)|*.py|" \
           "All files (*.*)|*.*"

        dialog_win = wx.FileDialog(self, message="Choose a .csv file",                         
			            wildcard=wildcard, style=wx.OPEN)

        if dialog_win.ShowModal():
            path = dialog_win.GetPath()  
            self.dropTarget.parent.m_listBox2.SetLabel(path)
 	    self.Settings.path = path
        
        
        #dialog_win.Destroy()
            
        
        
    
    def GetProjectInfo(self):     
        ''' Return project name and info. '''
        	
	projectName = self.stat_name.GetValue()		
        projectInfo = self.stat_info.GetValue()
        return  projectName, projectInfo
    
        
    def OnNext(self):        
        ''' Create directory for new project. ''' 
        
        # Store inputs        
        name, info = self.GetProjectInfo()
        self.Settings.name = name
        self.Settings.info = info
	
        # Make project directory
        if not os.path.exists(self.Settings.name):
            os.mkdir(self.Settings.name)
            os.mkdir(self.Settings.name + PRJDATA)
	    os.mkdir(self.Settings.name + "/" + self.Settings.getCurWeekStr())
            return True
        else:	
            return False
             

    def OnGoBack(self, event):
        ''' Go to previous window. '''
        
        self.Parent.Destroy()
        self.Destroy()
        
        newFrame = wx.Frame(None, -1, "Welcome")
	newFrame.SetSize((400,400))
        StartWin(newFrame)
        newFrame.Show()
        
    
    def OnProceed(self, event):
        ''' Process new project information and open a project window. '''
        
        if self.OnNext():
	    self.AssignAndSaveSettings()
            newWindow = LsaWin(self.Settings.name+PRJDATA+SETT_PICKL)
	    self.Parent.Destroy()
	    self.Destroy()

        else:            
	    out = wx.MessageBox("Project name already exists. Do you want to update the existing project with another period?", "Warning",  wx.YES_NO)
	    
	    if out==2: # 2- YES, 8 - NO
		name, info = self.GetProjectInfo()
		pathToCSV = self.Settings.path	    
		self.Settings = PrjSettings().UnPickleMe(name+PRJDATA+SETT_PICKL)	    
		self.Settings.path = pathToCSV #overwrite old path with the path to a new csv
		self.createNextWeekFolder()
		self.AssignAndSaveSettings()
	    
		newWindow = LsaWin(self.Settings.name+PRJDATA+SETT_PICKL)
		self.Parent.Destroy()
		self.Destroy()


    def createNextWeekFolder(self):
	self.Settings.IncrementWeekCount()
	self.Settings.PickleMeAsStudents()
	os.mkdir(self.Settings.name + "/" +self.Settings.getCurWeekStr())
        
    def AssignAndSaveSettings(self):
        name = self.stud_namesCol.GetValue()
        notes = self.stud_notesCol.GetValue()
        topics = self.numTopics.GetValue()
        numNotes = self.st_numNotes.GetValue()
        heading = self.cb_heading.IsChecked()        
            
        self.Settings.columns.append(int(name))
        self.Settings.columns.append(int(notes))
        self.Settings.numtopics = int(topics)
        self.Settings.stopIndex = int(numNotes)
        self.Settings.heading = heading        
	self.Settings.PickleMeAsStudents()	
        
class LsaWin():
    ''' Main project processing window that calls all graphs and project related analytics. '''
    
    def __init__(self, toSettings):
	self.Settings = PrjSettings().UnPickleMe(toSettings)        
        self.ExtractPeriodicalStudNotes()
        CorDic = self.CreateCorpusDict()
        self.CreateLSA(CorDic.getCorpus(), CorDic.getDict())   
        self.SimilarityAnalysis()	
        self.DisplayGraphs()          
        
    def ExtractPeriodicalStudNotes(self):   
        ''' Extract each student note in .csv file into a separate .txt file for a given peiod in weeks. 
		If a student has more than one note, append it to already created file. '''
        
        pathTocsv = self.Settings.path        
        studNameCol = self.Settings.columns[0]
        studNoteCol = self.Settings.columns[1]        
        prjFolder = self.Settings.name

        saveForThisWeek = prjFolder+"/"+self.Settings.getCurWeekStr()
        preprocess = MainTools.CorpusUtils()
        preprocess.extractCSVtoTXTbyStudent(pathTocsv, studNameCol, studNoteCol, 
                                            saveTo = saveForThisWeek, stopIndex = self.Settings.stopIndex,
                                            heading = self.Settings.heading)
        saveForWholeProj = prjFolder
        preprocess.extractCSVtoTXTbyStudent(pathTocsv, studNameCol, studNoteCol, 
                                            saveTo = saveForWholeProj, stopIndex = self.Settings.stopIndex,
                                            heading = self.Settings.heading)
            
    def CreateCorpusDict(self):
        ''' Create corpus and dictionary out of students' extracted notes inside project folder. '''
         
        corpus = MainTools.ExpCorpCreator(folder = self.Settings.name)        
        
        self.Settings.studNames = corpus.file_paths
        self.Settings.ClearStudNames()
        self.Settings.PickleMeAsStudents()	
        
        pathTo = self.Settings.name + PRJDATA  
        corpus.save(pathTo + "/corpus", pathTo + "/dictionary")
        return corpus
        
    def CreateLSA(self, corpus, dic):
        ''' Create and save LSA model in project folder/ProjectData out of gensim instance of 
            corpus and dictionary dic. '''
         
        lsa = MainTools.CreatorLSA(corpus, dic, topics = self.Settings.numtopics)
        lsa.saveModel(self.Settings.name + PRJDATA_LSA)
            
    def SimilarityAnalysis(self):  
        ''' Perform similarity analysis on lsi corpus of student texts and save result into
            .txt format matrix. '''
        
        corp = MainTools.CorpusUtils().load_corp(self.Settings.name + PRJDATA_CORPMM)   
        model = MainTools.CreatorLSA()
        model.loadModel(self.Settings.name + PRJDATA_LSA)
        
        indexing = MainTools.SimUtils()
        indexing.MatrixSim(model.lsa, corp)        
        indexing.SaveIndex(self.Settings.name + PRJDATA_SIMMTRX)        
        indexing.LoadIndex(self.Settings.name + PRJDATA_SIMMTRX) 
        
        sims = indexing.index[model.lsa[corp]]        
        indexing.saveSimMatrix(sims, self.Settings.name+PRJDATA_MTRX_INDX) 
        
        # Clear variables
        sims = None
        indexing = None
        model = None
        
        
    def DisplayGraphs(self):
        ''' Add graphs to tabs and display window to a user. '''
        
        pathTo = self.Settings.name+PRJDATA_MTRX_TXT 
                
        frameWithTabs = GraphTools.NoteBookTabs(title = "Project: " + self.Settings.name) # Will hold two graph windows        
        # Student group network graph
        graph1 = GraphTools.GroupNetworkGraph(frameWithTabs.panel, pathTo, self.Settings)
        # Other graphs 
        graph2 = GraphTools.StudentInteractionDetailsPanel(frameWithTabs.panel, pathTo, self.Settings)
        # Add graphs to each of two tabs
        frameWithTabs.AddTab(graph1)
        frameWithTabs.AddTab(graph2)        
        frameWithTabs.Show()
            
if __name__ == "__main__":
     
    def exec1():    
        app = wx.App(False)
        frame = wx.Frame(None, -1, "Welcome")
	frame.SetSize((400,400))
        StartWin(frame)
        frame.Show(True)
        app.MainLoop()     
    exec1()
    
