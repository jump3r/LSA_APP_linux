import matplotlib
matplotlib.use('WXAgg')
import networkx as nx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
from matplotlib.figure import Figure
import wx.aui
import wx.grid
from pylab import *

try:
    import community
except:
    print "Error: community.py was not found"
import MainTools as mp
from UserInterfaceWindows import PrjSettings

PRJDATA = "/ProjectData/"
PRJDATA_DICT = PRJDATA+"dictionary.dict"
PRJDATA_CORPMM = PRJDATA+"corpus.mm"
DPI=50

class GroupNetworkGraph(wx.Panel):
    ''' This graph is used to display edges between group of students based on similarity matrix. '''
    
    def __init__(self, parent , matrix, Settings):
                
        wx.Panel.__init__(self, parent, id = -1)
        self.name = "Group Network Graph"
        self.parent = parent
        self.figure = Figure((7.0, 7.0), dpi=DPI-10)
        self.figure.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98)
        self.axes = self.figure.add_subplot(111)     
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        self.Settings = Settings
        self.matrix = matrix        
        self.names = self.Settings.studNames        
        
        self.CreateControls()
        self.CreateSizers()
        self.CreateNetworkGraph()
        self.RecordCommunityData()
        self.RecordEdgesData()
        self.GetDataEdgDstrGraph()
        
        # To save picture of node graph
        #self.figure.savefig(Settings.name +"\\ProjectData\\WeightedGraphPreview.png")
        
        
    def CreateControls(self):
        ''' Add buttons and other controls to this panel. '''
             
        # Buttons        
        self.bt_draw = wx.Button(self, -1, "More")        
        self.Bind(wx.EVT_BUTTON, self.OnMore, self.bt_draw)
        
        # Check Boxes
        self.cb_grid = wx.CheckBox(self, -1, "Dont Show Names", style = wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.OnMoveSlider, self.cb_grid)
        self.cb_minorConn = wx.CheckBox(self, -1, "Dont Show Minor Connections", style = wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.OnMoveSlider, self.cb_minorConn)
        
        # Slider
        self.slider_label = wx.StaticText(self, -1, "Similarity (%): ")
        self.slider_width = wx.Slider(self, -1, value = 40, minValue = 1, maxValue = 100, size=(400,15),
                                      style = wx.SL_AUTOTICKS|wx.SL_RIGHT)
        self.slider_width.SetTickFreq(3, 1)        
        #self.Bind(wx.EVT_COMMAND_SCROLL_THUMBTRACK, self.OnMoveSlider, self.slider_width)  	
	self.Bind(wx.EVT_SCROLL_CHANGED, self.OnMoveSlider, self.slider_width)                    


        # Native matplotlib Navigation Panel
        self.toolbar = NavigationToolbar2WxAgg(self.canvas)
        
                 
    def OnMoveSlider(self, event):
        ''' Event for a slider on this panel. Updates the graph according to the strength of student
            edges selected. ''' 
        
        show_label = not self.cb_grid.GetValue()
        show_minor = not self.cb_minorConn.GetValue()
        new_value = self.slider_width.GetValue()/100.0
        
        self.axes.clear()
        self.CreateNetworkGraph(wght = new_value, labels = show_label, minor = show_minor)
        self.GetDataEdgDstrGraph()
        self.canvas.draw()
        
    
    def GetDataEdgDstrGraph(self):        
        ''' Count total number of edges for each basket in range 0,5,10,15...100 based on strength
            of each edge (how similar students are) '''
        
        range_dic = {} # ket: freq
        checked_pairs = set([])
        for (u,v,d) in self.G.edges(data = True):            
            key = ( int( 100*d['weight'] )/5 ) * 5
            
            if ((u, v) not in checked_pairs) and ((v, u) not in checked_pairs):        
                checked_pairs.add((u,v))
                if key in range_dic:
                    range_dic[key] += 1
                else:                    
                    range_dic[key] = 1
            else:
                continue
            
        self.Settings.DataEdgDistGraph = range_dic
        
    
    def OnMore(self, event):
        ''' Open a window with two distribution graphs for edges. '''
        
        graph = EdgesDistrCumulGraphsFrame(self.Settings.DataEdgDistGraph)
        graph.Show(True)
        
    def CreateSizers(self):
        ''' Boxsizers for this window. '''   
                
        self.G_sizer = wx.BoxSizer(wx.VERTICAL)
        self.G_sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.G_sizer.Add(self.toolbar, 0, wx.EXPAND)
        self.G_sizer.AddSpacer(10)
        
        self.ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrl_sizer.Add(self.bt_draw, 0, border=3, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        self.ctrl_sizer.Add(self.cb_minorConn, 0, border=3, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL)        
        self.ctrl_sizer.Add(self.cb_grid, 0, border=3, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        self.ctrl_sizer.AddSpacer(30)
        self.ctrl_sizer.Add(self.slider_label, 0, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        self.ctrl_sizer.Add(self.slider_width, 0, border=3, flag = wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL)
                
        self.G_sizer.Add(self.ctrl_sizer, 0, wx.ALIGN_LEFT | wx.TOP)        
        
        self.SetSizer(self.G_sizer)
        self.G_sizer.Fit(self.parent)
        

    def CreateNetworkGraph(self, wght = 0.4, labels = True, minor = True):
        ''' Create student group network graph based on similarity matrix and their names. 
            (names of their .txt files). Weight wght represents numeric value received
            from a slider that represents a point above which all edges will be treated as
            major edges and will be drawn with solid line; every edge connection that is below 
            that number will be treated as minor and will be drawn with dashed line. If parameter
            labels is set to true, each node will be drawn with student name on the top of it.
            If parameter minor set to true, the graph will DrawBarGraph minor connections between nodes,
            otherwise minor connections will be omitted. '''
        
        G=nx.Graph()
        self.G = G
        matrix = []
        for line in open(self.matrix, "r"):
            matrix.append(line.split())
        
        for doc_horiz, index1 in zip(matrix, range(len(matrix))):
                        
            for doc_vert, index2 in zip(doc_horiz, range(len(doc_horiz))):
                
                if index1 != index2:
                    
                    if float(doc_vert) > 0:
                        G.add_edge(self.names[index1], self.names[index2], weight = float(doc_vert))
                    
                    else:                         
                        G.add_node(self.names[index1])
                        G.add_node(self.names[index2])
                else:                    
                    continue
        
        
        nodes_positions = nx.spring_layout(G)
        self.nodes_positions = nodes_positions
        nx.draw_networkx_nodes(G,nodes_positions)#,node_size=700)#, ax = self.axes)    
        
        sort_to_major_edges = []
        sort_to_minor_edges = []        
        for u, v, d in G.edges(data=True):
            
            if d['weight'] > wght:
                sort_to_major_edges.append((u, v))
                
            elif 0 < d['weight'] <= wght:
                sort_to_minor_edges.append((u, v))
                
            else:
                # skip negative values if any
                continue
               
        
        nodes_positions=nx.spring_layout(G)
        self.nodes_positions = nodes_positions
        nx.draw_networkx_nodes(G,nodes_positions)#,node_size=700)#, ax = self.axes)    
        nx.draw_networkx_edges(G, nodes_positions, edgelist = sort_to_major_edges, width = 2, 
                               alpha = 1.0, edge_color='b',style='solid', ax = self.axes)
        if minor == True:
            nx.draw_networkx_edges(G, nodes_positions, edgelist = sort_to_minor_edges, width = 1,
                                   alpha = 0.2, edge_color = 'b', style = 'dashed', ax = self.axes)
        else:
            nx.draw_networkx_edges(G, nodes_positions, edgelist = sort_to_minor_edges, width = 1,
                                   alpha = 0.2, edge_color = 'w', style = 'dashed', ax = self.axes)        
        if labels == True:
            nx.draw_networkx_labels(G, nodes_positions, font_size = 15, font_family = 'sans-serif',
                                    ax = self.axes)
        
        
    def RecordCommunityData(self):
        ''' Find sub-communities within current student group. Used inside student table which appears
            in a weekly interaction tab. '''
        # May be used to display on student group network graph (this graph).  
        
        try:
            partition = community.best_partition(self.G)
            
            for i in set(partition.values()):                            
                self.Settings.commun[i] = [nodes  for  nodes  in  partition.keys()  if  partition[nodes]  ==  i]                
        except:
            print "Error: community.py was not included"
            
        
    def RecordEdgesData(self):
        ''' Store connections between students and their weight. It is used in weekly interaction tab
            by clicking at each student to his or her connections with other students. '''
        self.Settings.edges={} #clean from previous week
        for student1, student2, wght in self.G.edges_iter(data = True):
            
            student1 = str(student1)
            if student1 in self.Settings.edges:                
                self.Settings.edges[student1].append([student2, wght])
                                
            elif student1 not in self.Settings.edges:
                self.Settings.edges[student1] = []
                self.Settings.edges[student1].append([student2, wght])
            
            
            student2 = str(student2)
            if student2 in self.Settings.edges:                
                self.Settings.edges[student2].append([student1, wght])
                                
            elif student2 not in self.Settings.edges:
                self.Settings.edges[student2] = []
                self.Settings.edges[student2].append([student1, wght])
        
            
class StudentInteractionDetailsPanel(wx.Panel):
    ''' This panel holds three graphs, list of students, personal dictionaries, student's notes 
        and connections with others. '''
    
    def __init__(self, parent, matrix, Settings, updateWeek=True):
        ''' Parent is a frame instance being passed to this panel; matrix is a name of similarity matrix;
            Settings is a PrjSettings class that holds all settings for a particular project as well some
            of data that is used accross classes. '''
        
        ''' Auto generated code for UI using wxFormBuilder v3.1 - Beta '''
        wx.Panel.__init__  ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
        self.StudGraph1 = StudentsWeeklyInteractionGraph(self, matrix, Settings, updateWeek=updateWeek)
        self.StudGraph2 = StudSimValueLine(self, matrix, Settings)
        self.StudGraph3 = StudAvgValueDistrBar(self, Settings)
        self.name = self.StudGraph1.name
        self.Settings = Settings
        
        bSizer7 = wx.BoxSizer( wx.HORIZONTAL ) # main box sizer
        bSizer9 = wx.BoxSizer( wx.HORIZONTAL ) 
        bSizer8 = wx.BoxSizer (wx.VERTICAL)
        bSizer11 = wx.BoxSizer (wx.HORIZONTAL)
        bSizer10 = wx.BoxSizer( wx.VERTICAL )
        bSizer12 = wx.BoxSizer ( wx.VERTICAL ) 
        bSizer14 = wx.BoxSizer ( wx.VERTICAL )
        bSizer16 = wx.BoxSizer ( wx.VERTICAL )             
        bSizer15 = wx.BoxSizer ( wx.HORIZONTAL )
        bSizer13 = wx.BoxSizer ( wx.VERTICAL )
        bSizer17 = wx.BoxSizer ( wx.VERTICAL )
        
        self.m_textctrl1 = wx.TextCtrl(self, wx.ID_ANY, "Select a student", size = (-1, 100), 
                                       style = wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.stud_dict = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, 
                                          wx.DefaultSize, [], 0 )
        self.stud_edges = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, 
                                          wx.DefaultSize, [], 0 )                        
        self.label_notes = wx.StaticText( self, wx.ID_ANY, "Student's Notes", wx.DefaultPosition, 
                                          wx.DefaultSize, 0 )
        self.label_notes.Wrap( -1 )
        self.label_edges = wx.StaticText( self, wx.ID_ANY, "Student Connections", wx.DefaultPosition, 
                                          wx.DefaultSize, 0 )
        self.label_edges.Wrap( -1 )
        self.label_dict = wx.StaticText( self, wx.ID_ANY, "Student Dictionary", wx.DefaultPosition, 
                                          wx.DefaultSize, 0 )
        self.label_dict.Wrap( -1 )
        
        bSizer9.Add(self.StudGraph1, 1, wx.ALL | wx.EXPAND )
        bSizer11.Add(self.StudGraph2, 1, wx.ALL | wx.EXPAND )
        bSizer11.Add(self.StudGraph3, 1, wx.ALL | wx.EXPAND )
        bSizer8.Add( bSizer9, 2, wx.ALL | wx.EXPAND, 5 )
        bSizer8.Add( bSizer11, 1, wx.ALL | wx.EXPAND, 5 )
        bSizer7.Add( bSizer8, 3, wx.ALL | wx.EXPAND, 5 )
        bSizer7.Add( bSizer10, 2, wx.ALL | wx.EXPAND, 5 )
        
        bSizer12.Add( self.label_notes, 0, 5 )
        bSizer12.Add( self.m_textctrl1, 1, wx.EXPAND, 5 )
        bSizer14.Add( self.label_edges, 0, 5 )
        bSizer14.Add( self.stud_edges, 1, wx.EXPAND, 5 )
        bSizer16.Add( self.label_dict, 0, 5 )
        bSizer16.Add( self.stud_dict, 1, wx.EXPAND, 5 )
        bSizer15.Add( bSizer14, 2, wx.EXPAND, 5 )
        bSizer15.Add( bSizer16, 1, wx.EXPAND, 5 )
        bSizer17.Add( bSizer12, 1, wx.EXPAND, 5 )
        bSizer17.Add( bSizer15, 1, wx.BOTTOM | wx.EXPAND, 5 )
        
        self.StudentTable()
        self.FillOutTable()
        bSizer13.Add( self.m_grid3, 1, wx.EXPAND, 5 )
        bSizer10.Add(bSizer17, 1, wx.EXPAND, 5)
        bSizer10.Add(bSizer13, 1, wx.TOP | wx.EXPAND, 5)
        self.SetSizer( bSizer7 )
        self.Layout()   
        
     
    def StudentTable(self): 
        ''' Set up student grid to display student names, average score (average similarity), number
            of edges, total score (number of edges * average score) and communities. '''
        
        self.m_grid3 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, 
                                     wx.Size(-1,300), wx.VSCROLL )       
        # Grid
        #self.m_grid3.CreateGrid( len(self.Settings.studNames), 4 )
	self.m_grid3.CreateGrid( len(self.Settings.periodic_avg_val),3+self.Settings.WeekCount )                
        self.m_grid3.EnableGridLines( True )
        self.m_grid3.EnableDragGridSize( False )
        self.m_grid3.SetMargins( 0, 0 )
        
        # Columns
        self.m_grid3.EnableDragColMove( False )
        self.m_grid3.EnableDragColSize( True )
        self.m_grid3.SetColLabelSize( 25 )
        self.m_grid3.SetColSize(0, 130)
        self.m_grid3.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )        
        self.m_grid3.SetColLabelValue(0, "Students")
        self.m_grid3.SetColLabelValue(1, "Avg. Score")
        self.m_grid3.SetColLabelValue(2, "# Of Edges")
        self.m_grid3.SetColLabelValue(3, "Communities")
	
	for week, incr in zip(range(self.Settings.WeekCount, 0, -1), range(1,self.Settings.WeekCount+1)):
	        self.m_grid3.SetColLabelValue(3+incr, "Week "+str(week))           
        
        # Rows
        self.m_grid3.EnableDragRowSize( True )
        self.m_grid3.SetRowLabelSize( 25 )
        self.m_grid3.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        
        # Cell Defaults
        self.m_grid3.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )        
        self.m_grid3.AppendCols()
        
        # Bind events
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnPickStudent)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnPickStudent)
        
        
    def OnPickStudent(self,event):
        ''' Event of clicking on a student record. Updates fields with student's information. '''
        
        row = event.GetRow()
        col = event.GetCol()                
        
        stud_name = self.m_grid3.GetCellValue(row, 0)  
	self.StudGraph1.PlotAverageScore(student = stud_name)
                  
        prjpath = self.Settings.name + "/" + stud_name+ ".txt"     
        
	#Show student's notes
        try: text = open(prjpath, "r").read()            
        except: text = "Error: student's conversation could not be found"
        self.m_textctrl1.SetValue(text)        
        
        # Fill a field with student's edges
        self.stud_edges.Clear()
        for edge in self.Settings.edges[stud_name]:
            self.stud_edges.Append(edge[0] + " " + str(edge[1]["weight"]*100)[:4]+"%\n")
        
        # Fill a field with student's dict
        corppath = self.Settings.name + PRJDATA_CORPMM #"/ProjectData/corpus.mm"
        dictpath = self.Settings.name + PRJDATA_DICT #"/ProjectData/dictionary.dict"
        corpus = mp.CorpusUtils().load_corp(corppath)
        dic = mp.CorpusUtils().load_dict(dictpath)
        
        self.stud_dict.Clear()
	original_row = self.Settings.studNames.index(stud_name)
        for w_ind, freq in corpus[original_row]:            
            word = dic[w_ind]            
            self.stud_dict.Append(str(word) + " " + str(int(freq)))
        
        # Highlight student position in a distribution bar    
        self.StudGraph2.DrawGraph(stud_num = original_row)#row)
        
        # Show student's similarity with other students
        stud_avg_val = float(self.m_grid3.GetCellValue(row, 4)[:-1])                
        self.StudGraph3.OnHighlightDistBar(stud_avg_val)
            
    def FillOutTable(self):
        ''' Fill the table with user names, edges between other students, total score (average),
            and sub-community. '''
        
        column_1 = 0                
        for name in self.Settings.periodic_avg_val:
	    all_scores = self.Settings.periodic_avg_val[name][:] # if no [:] then it is POINTER!!!!
	    all_scores.reverse()
            avg_score = str(all_scores[0]*100)[:5]#[column_1]*100)[:5]
            
            # Fill student name and average similarity score
            self.m_grid3.SetCellValue(column_1, 0, name)            
            
            # Fill # of edges
            if name in self.Settings.edges:
                num_edges = str(len(self.Settings.edges[name]))
                self.m_grid3.SetCellValue(column_1, 2, num_edges)            
                
            else:
                num_edges = 0
                self.m_grid3.SetCellValue(column_1, 2, "#Error!" + name + " is missing from the record")

            # Fill students' total score            
	    total_score = float(avg_score)*float(num_edges)
	    self.m_grid3.SetCellValue(column_1, 1, str(total_score))

            # Fill students' weekly score
	    for week, incr in zip(range(self.Settings.WeekCount), range(1,self.Settings.WeekCount+1)):
            			
		weekly_score = str(all_scores[week]*100)[:5]	
		
            	self.m_grid3.SetCellValue(column_1, 3+incr, weekly_score+"%")
            
            # Fill students' belonging to sub-community
            for com_num in self.Settings.commun:
                if name in self.Settings.commun[com_num]:
                    self.m_grid3.SetCellValue(column_1, 3, str(com_num))
                    break
            
            column_1 += 1
            
            
class StudAvgValueDistrBar(wx.Panel):
    ''' This panel hold a graph that shows distribution of similarity values among students
        in the group. ''' 
    
    def __init__(self, parent, Settings):
        ''' parent is an instance of a frame, settings is an instance of PrSettings. '''
        
        wx.Panel.__init__(self, parent = parent, id = -1)
        self.Setting = Settings
        self.figure = Figure(dpi = DPI, figsize = (2,2))
        self.canvas = FigureCanvas(self, -1, self.figure)        
        
        self.axes = self.figure.add_subplot(111) 
        self.axes.set_title("Distribution of Average Similarity Score Per Student")
        self.axes.set_xlabel("Similarity (%)")
        self.axes.set_ylabel("# Of Students")        
        avg_val = self.Setting.avg_val.values()
        self.SetSizers()
        
        # Count distributed frequencies        
        self.freq_dic = {}
        for sim_num in avg_val:
            new_num = sim_num*100
            factor = int(new_num)/5
            key = factor * 5     
            if key not in self.freq_dic:
                self.freq_dic[key] = 1
            else:
                self.freq_dic[key] += 1
        
        # Draw distributed frequencies
        for key in self.freq_dic:
            self.axes.bar(left = key, height = self.freq_dic[key], width = 5, bottom = 0, color = "b")
            
               
    def SetSizers(self):
        ''' Panel sizers. '''                
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)        
        self.SetSizer(sizer)
        
        
    def OnHighlightDistBar(self, avg_stud_sim):
        ''' Highlight a column of similarity score distribution graph whenever a student is selected
            from the student table. '''
             
        self.axes = None
        self.figure.clear()
        
        self.axes = self.figure.add_subplot(111) 
        self.axes.set_title("Distribution of Average Similarity Score Per Student")
        self.axes.set_xlabel("Similarity (%)")
        self.axes.set_ylabel("# Of Students")
        for key in self.freq_dic:        
            new_sim = int(avg_stud_sim)/5            
            new_sim = new_sim * 5
            
            if int(new_sim) != key: 
                self.axes.bar(left = key, height = self.freq_dic[key], width = 5, bottom = 0, color = "b")
            else:
                self.axes.bar(left = key, height = self.freq_dic[key], width = 5, bottom = 0, color = "r")
        
        self.canvas.draw()
        
                
class StudSimValueLine(wx.Panel):
    ''' This panel holds a graph of all similarities for selected student from a student table. '''
    
    def __init__(self, parent, matrix, Settings):
        ''' parent is an instance of a frame; matrix is a name of similarity matrix; Settings is
            an instance of PrjSettings class. '''
        
        wx.Panel.__init__(self, parent = parent, id = -1)
        self.Settings = Settings
        self.matrix = matrix
        self.figure = Figure(dpi = DPI, figsize = (2,2))
        self.canvas = FigureCanvas(self, -1, self.figure)
                
        self.SetSizers()
                
        # Draw empty plot
        self.axes = self.figure.add_subplot(111)
        self.canvas.draw()
        
           
    def SetSizers(self):
        ''' Panel sizers. '''
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)        
        self.SetSizer(sizer)
    
    def DrawGraph(self, stud_num = 0):
        ''' Draw/redraw a graph for a selected student from student table. stud_num is a student
            index in the table. '''
        
        self.axes = None
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
                
        self.axes.set_title("Similarity Value For A Given Student")
        self.axes.set_xlabel("Students")
        self.axes.set_ylabel("Similarity (x100%")        
                
        y_val = self.GetStudentSimilarityValues(stud_num)        
        x_val = [0] + range(1, len(y_val)+1)
        y_val = [0] +y_val
        markerline, stemlines, baseline = self.axes.stem(x_val, y_val, '-.')
                
        self.canvas.draw()
        
        
    def GetStudentSimilarityValues(self, stud_num):  
        ''' Return student similarity with other students from a similarity matrix. stud_num is
            a student index in the student table. '''
        
        # Find students similarities string in the matrix      
        file = open(self.matrix, "r")
        stud_sim_val = []
        index = 0         
        for line in file:            
            if index == stud_num:                
                stud_sim_val = line.split()
                break
            index += 1
        
        # Process the string
        new_stud_sim_val = []
        for num in stud_sim_val:
            if "e" in num:
                new_stud_sim_val.append(0)
            else:
                new_stud_sim_val.append(float(num[:4]))
        
        return new_stud_sim_val
    
    
class StudentsWeeklyInteractionGraph(wx.Panel):
    ''' This panel holds graph of Average Similarity Score Per Student. '''
        
    def __init__(self, parent, matrix, Settings, updateWeek):
        ''' parent is an instance of a frame; matrix is a matrix name of similarity matrix; Settings
            is an instance of PrjSettings class. '''
        
        wx.Panel.__init__(self, parent = parent, id = -1)
        self.name = "Students Weekly Progress"
        self.Settings = Settings
        self.matrix = matrix
        self.figure = Figure(dpi = DPI, figsize = (2,2))        
        self.canvas = FigureCanvas(self, -1, self.figure)            
        
	self.ShowAllLines=0 #1st click all shown,2nd click selected student shown      
        self.SetSizers()        
	self.GetAverageSimilarityForStudents()
	if updateWeek:
		self.Settings.MergeWithPrevPeriods()
		self.Settings.PickleMeAsStudents()
        self.PlotAverageScore()
        
        
        
    def PlotAverageScore(self, student=None): #plot1
        ''' Plot average student scores. ''' 

	self.axes = None
	self.figure.clear()
	self.axes = self.figure.add_subplot(111)#, axisbg = "b") 
        self.axes.set_title("Average Similarity Score Per Student")
        self.axes.set_ylabel("Similarity (%)")
        self.axes.set_xlabel("Weeks")
	
	# Switch y axes to right
        for tick in self.axes.yaxis.get_major_ticks():
            tick.label1On, tick.label2On = False, True
	
	#if student is picked from the grid
	#display only his/her line
	if student!=None and self.ShowAllLines==1:
	    values = self.Settings.periodic_avg_val[student][:]	    	    
  	    x, y = range(len(values)+1), [0]+values

	    g = self.axes.plot(x, y, label = student) 
	    
	    # best fit line
	    fit = polyfit(x,y,1)
	    fit_in = poly1d(fit)
	    self.axes.plot(x,y, fit_in(x), '--k', label = "Best fit line")
	    self.ShowAllLines=0	
	#display all students lines  
	else:  	    
	    #xf, yf= [], [] # for a best fit line
	    yf = [0 for i in range(self.Settings.WeekCount+1)]
	    for name in self.Settings.periodic_avg_val:
	        values = self.Settings.periodic_avg_val[name][:]

		x, y = range(len(values)+1), [0]+values
		
	        g = self.axes.plot(x, y, label = name) 
	    # best fit line
	        for i in range(len(y)):
		    yf[i] +=y[i]
	    
	    divisor = len(self.Settings.studNames)
	    for i in range(1,len(yf)):
		yf[i] = yf[i]/divisor
	    
	    
	    fit = polyfit(x,yf,1)
	    fit_in = poly1d(fit)
	    self.axes.plot(x,yf, fit_in(x), '--k', label = "Best fit line")
	    
	    self.ShowAllLines=1

	self.axes.legend(loc = 2)
	self.canvas.draw()
	
	
    def GetAverageSimilarityForStudents(self):
        ''' Return average student similarity score. '''
        
        file = open(self.matrix, "r")
        stud_matrix = []
        for stud in file:
            stud_matrix.append(stud.split())
        avg_val_y = {}
        for stud1, index1 in zip(stud_matrix, range(len(stud_matrix))):
            sum = 0
            neg = 0
            for stud2, index2 in zip(stud1, range(len(stud1))):
                stud2 = float(stud2)
                if index1 == index2:
                    continue
                elif stud2 >= 0:
                    sum += stud2
                else:
                    neg += 1
                    
            avg_val_y[index1] = sum/(len(stud1)-neg)
        self.Settings.avg_val = avg_val_y	        
            
            
    def SetSizers(self):
        ''' Panel sizers. '''
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)        
        self.SetSizer(sizer)
        
        
class EdgesDistrCumulGraphsFrame(wx.Frame):
    ''' This frame holds two distribution graphs of edges. '''
            
    def __init__(self, freq_dic):
        ''' freq_dic is dictionary with edge frequencies per interval. '''        
        
        wx.Frame.__init__(self,None,-1,'Edges')        
        self.Center()
        self.panel = wx.Panel(self, -1)        
        self.cumulBar = EdgesCumulBarGraph(self.panel)
        self.distrBar = EdgesDistrBarGraph(self.panel)        
                        
        self.DrawGraphGrid(freq_dic)
        bSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer.Add(self.distrBar, 1, wx.ALL)
        bSizer.Add(self.cumulBar, 1, wx.ALL)
                                
        self.panel.SetSizer(bSizer)
        bSizer.Fit(self)
        
        Bar
    def DrawGraphGrid(self, freq_dic):
        ''' Draw distribution and cumulative graphs of edges. '''
        
        cumulative_val = 0
        for key in range(0, 100, 5):
            if key in freq_dic:
                cumulative_val += freq_dic[key]
                self.distrBar.DefineBarGraph(key, freq_dic[key])
                self.cumulBar.DefineBarGraph(key, cumulative_val)                
            else: 
                self.distrBar.DefineBarGraph(key, 0)
                self.cumulBar.DefineBarGraph(key, cumulative_val) 
        
        self.distrBar.DrawBarGraph()
        self.cumulBar.DrawBarGraph() 
        
                         
class EdgesDistrBarGraph(wx.Panel):
    ''' This panel holds edges distribution bar graph. '''
    
    def __init__(self, parent):
        ''' parent is a frame instance. '''        
        
        wx.Panel.__init__(self, parent = parent, id = -1)        
        self.figure = Figure(dpi = DPI, figsize = (8, 4)) 
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)    
        # Labels
        self.axes.set_title("Major Edges per Interval")
        self.axes.set_ylabel("Number of edges")
        self.axes.set_xlabel("Intervals (%)")      
        # Sizers
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        bSizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(bSizer)
        
    def DefineBarGraph(self, left, height):
        ''' Create bar graph. '''
        
        self.axes.bar(left = left, height = height, width = 5, bottom = 0, color = "b")
        
    
    def DrawBarGraph(self):
        ''' Draw the bar graph. '''
        
        self.canvas.draw()
        
        
class EdgesCumulBarGraph(wx.Panel):
    ''' This panel holds edges cumulative bar graph. '''
    
    def __init__(self, parent):
        ''' parent is a fram instance. '''
        
        wx.Panel.__init__(self, parent = parent, id = -1)        
        self.figure = Figure(dpi = DPI, figsize = (8, 4)) 
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        # Labels
        self.axes.set_title("Cumulative Number of Major Edges per Interval")
        self.axes.set_ylabel("Cumulative number of edges")
        self.axes.set_xlabel("Intervals (%)")        
        # Sizers
        bSizer = wx.BoxSizer(wx.HORIZONTAL)
        bSizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(bSizer)
        
        
    def DefineBarGraph(self, left, height):
        ''' Create bar graph. '''
        
        self.axes.bar(left = left, height = height, width = 5, bottom = 0, color = "b")
        
    
    def DrawBarGraph(self):
        ''' Draw the bar graph. '''
        
        self.canvas.draw()
        
        
class NoteBookTabs(wx.Frame):
    ''' This is the main frame that holds two tabs with all graphs. '''
    
    def __init__(self, title = "Project Window"):
        
        wx.Frame.__init__(self, parent = None, title = title, size=wx.DisplaySize())
        self.Center()
        self.panel = wx.Panel(self, -1)
        self.tabs = wx.aui.AuiNotebook(self.panel)
        sizer = wx.BoxSizer()
        sizer.Add(self.tabs, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        
        
    def AddTab(self, tab):
        ''' Add tab of type panel. '''
        
        self.tabs.AddPage(tab, tab.name)
        
