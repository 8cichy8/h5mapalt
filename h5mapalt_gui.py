#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import h5mapalt as mapalt
import wx


class MyFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, wx.ID_ANY, "H5MapAlt", style=wx.DEFAULT_FRAME_STYLE & ~ wx.RESIZE_BORDER)
        
        self.mapFileEdit = None
        self.mapFileBtn = None
        self.creaChangeCheck = None
        self.creaRandomCheck = None
        self.creaNcfCheck = None
        self.creaPowerRatioSpin = None
        self.creaNeutralReductionSpin = None
        self.creaGroupRatioSlider = None
        self.creaMoodFriendlyCheck = None
        self.creaMoodAggressiveCheck = None
        self.creaMoodHostileCheck = None
        self.creaMoodWildCheck = None
        self.artChangeCheck = None
        self.artRandomCheck = None
        self.okBtn = None
        
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # file line
        
        fileLineSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.mapFileEdit = wx.TextCtrl(self, wx.ID_ANY)
        fileLineSizer.Add(self.mapFileEdit, 1, wx.ALL|wx.ALIGN_RIGHT, 5)
        
        self.mapFileBtn = wx.Button(self, wx.ID_ANY, "...")
        self.Bind(wx.EVT_BUTTON, self.OnMapFileBtnClick, self.mapFileBtn)
        fileLineSizer.Add(self.mapFileBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        
        mainSizer.Add(fileLineSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        # file line end
        
        bodySizer = wx.BoxSizer(wx.HORIZONTAL)
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        bodySizer.Add(leftSizer, 1, wx.EXPAND, 0)
        bodySizer.Add(rightSizer, 1, wx.EXPAND, 0)
        mainSizer.Add(bodySizer, 1, wx.EXPAND, 0)
        
        # creatures
        
        creaBox = wx.StaticBox(self, wx.ID_ANY, "creatures")
        creaSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.creaChangeCheck = wx.CheckBox(creaBox, wx.ID_ANY, "change")
        self.creaChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaChangeCheckChange, self.creaChangeCheck)
        creaSizer.Add(self.creaChangeCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        comp = wx.StaticLine(creaBox, wx.ID_ANY)
        creaSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        
        creaGridSizer = wx.FlexGridSizer(2)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "power ratio")
        self.creaPowerRatioSpin = wx.SpinCtrlDouble(creaBox, wx.ID_ANY, min=0.1, max=100.0, inc=0.1, initial=1.0)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaPowerRatioSpin, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "neutral reduction")
        self.creaNeutralReductionSpin = wx.SpinCtrl(creaBox, wx.ID_ANY, min=0, max=100, initial=2)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaNeutralReductionSpin, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "group ratio")
        self.creaGroupRatioSlider = wx.Slider(creaBox, wx.ID_ANY, 55, 0, 100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaGroupRatioSlider, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        creaSizer.Add(creaGridSizer, 1, wx.EXPAND, 0)
        
        self.creaRandomCheck = wx.CheckBox(creaBox, wx.ID_ANY, "random")
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaRandomCheckChange, self.creaRandomCheck)
        creaSizer.Add(self.creaRandomCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.creaNcfCheck = wx.CheckBox(creaBox, wx.ID_ANY, "NCF")
        creaSizer.Add(self.creaNcfCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        creaBorderSizer = wx.BoxSizer(wx.VERTICAL)
        creaBorderSizer.Add(creaSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        creaBox.SetSizerAndFit(creaBorderSizer)
        leftSizer.Add(creaBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # moods
        
        creaMoodBox = wx.StaticBox(self, wx.ID_ANY, "creatures mood")
        creaMoodBoxSizer = wx.GridSizer(2)
        
        self.creaMoodFriendlyCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "friendly")
        creaMoodBoxSizer.Add(self.creaMoodFriendlyCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodAggressiveCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "aggressive")
        self.creaMoodAggressiveCheck.SetValue(True)
        creaMoodBoxSizer.Add(self.creaMoodAggressiveCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodHostileCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "hostile")
        self.creaMoodHostileCheck.SetValue(True)
        creaMoodBoxSizer.Add(self.creaMoodHostileCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodWildCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "wild")
        creaMoodBoxSizer.Add(self.creaMoodWildCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        creaMoodBorderSizer = wx.BoxSizer(wx.VERTICAL)
        creaMoodBorderSizer.Add(creaMoodBoxSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        creaMoodBox.SetSizerAndFit(creaMoodBorderSizer)
        rightSizer.Add(creaMoodBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # moods end
        # creatures end
        
        
        # artifacts
        
        artBox = wx.StaticBox(self, wx.ID_ANY, "artifacts")
        artSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.artChangeCheck = wx.CheckBox(artBox, wx.ID_ANY, "change")
        self.artChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnArtChangeCheckChange, self.artChangeCheck)
        artSizer.Add(self.artChangeCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        comp = wx.StaticLine(artBox, wx.ID_ANY)
        artSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        
        self.artRandomCheck = wx.CheckBox(artBox, wx.ID_ANY, "random")
        artSizer.Add(self.artRandomCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        sizer = wx.FlexGridSizer(2)
        artSizer.Add(sizer)
        
        artBorderSizer = wx.BoxSizer(wx.VERTICAL)
        artBorderSizer.Add(artSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        artBox.SetSizerAndFit(artBorderSizer)
        rightSizer.Add(artBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # artifacts end
        
        
        self.okBtn = wx.Button(self, wx.ID_ANY, "Ok")
        self.Bind(wx.EVT_BUTTON, self.OnOkBtnClick, self.okBtn)
        mainSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        
        
        borderSizer = wx.BoxSizer(wx.VERTICAL)
        borderSizer.Add(mainSizer, 0, wx.ALL|wx.EXPAND, 0)
        
        self.SetSizerAndFit(borderSizer)
        
        self.RefreshCreatureInputsState()
        self.RefreshArtifactInputsState()
    
    def RefreshCreatureInputsState(self):
        enable = self.creaChangeCheck.GetValue()
        self.creaRandomCheck.Enable(enable)
        self.creaNcfCheck.Enable(enable)
        self.creaPowerRatioSpin.Enable(enable)
        
        randomEnable = enable and not self.creaRandomCheck.GetValue()
        self.creaNeutralReductionSpin.Enable(randomEnable)
        self.creaGroupRatioSlider.Enable(randomEnable)
        
        self.creaMoodFriendlyCheck.Enable(enable)
        self.creaMoodAggressiveCheck.Enable(enable)
        self.creaMoodHostileCheck.Enable(enable)
        self.creaMoodWildCheck.Enable(enable)
        
    def RefreshArtifactInputsState(self):
        enable = self.artChangeCheck.GetValue()
        self.artRandomCheck.Enable(enable)
    
    def OnCreaChangeCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
        self.CheckOkButtonState()
        
    def OnCreaRandomCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
    
    def OnArtChangeCheckChange(self, pEvent):
        self.RefreshArtifactInputsState()
        self.CheckOkButtonState()
    
    def CheckOkButtonState(self):
        enableOkButton = self.creaChangeCheck.GetValue() or self.artChangeCheck.GetValue()
        self.okBtn.Enable(enableOkButton)
    
    def OnMapFileBtnClick(self, pEvent):
        fileDlg = wx.FileDialog(self, "Open h5m file", "../Maps", "", "h5m (*.h5m)|*.h5m", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST);
        if fileDlg.ShowModal() != wx.ID_CANCEL:
            self.mapFileEdit.SetValue(fileDlg.GetPath())
    
    def OnOkBtnClick(self, pEvent):
        argMapFile = self.mapFileEdit.GetValue()

        argArtChange = "--artChange=" + ("true" if self.artChangeCheck.GetValue() else "false")
        argCreaChange = "--creaChange=" + ("true" if self.creaChangeCheck.GetValue() else "false")

        argArtRandom = "--artRandom=" + ("true" if self.artRandomCheck.GetValue() else "false")
        argCreaRandom = "--creaRandom=" + ("true" if self.creaRandomCheck.GetValue() else "false")
        
        argCreaPowerRatio = "--creaPowerRatio=" + str(self.creaPowerRatioSpin.GetValue())
        argCreaGroupRatio = "--creaGroupRatio=" + str(self.creaGroupRatioSlider.GetValue())
        argCreaNeutralReduction = "--creaNeutralReduction=" + str(self.creaNeutralReductionSpin.GetValue())
        argCreaNCF = "--creaNCF=" + ("true" if self.creaNcfCheck.GetValue() else "false")
        
        argCreaMoodRatio = "--creaMoodRatio="
        argCreaMoodRatio += ("1" if self.creaMoodFriendlyCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodAggressiveCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodHostileCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodWildCheck.GetValue() else "0")
        
        argGuiIsShown = "--guiIsShown=true"
        
        args = [
            argMapFile, argArtChange, argCreaChange, argArtRandom, 
            argCreaRandom, argCreaPowerRatio, argCreaGroupRatio, 
            argCreaNeutralReduction, argCreaNCF, argCreaMoodRatio, 
            argGuiIsShown
        ]
        try:
            mapalt.run(args)
            wx.MessageBox("Map was changed")
        except mapalt.MyException as ex:
            wx.MessageBox(str(ex))
	    

class MyApp(wx.App):

    def __init__(self):
        super().__init__(False)
    
    def OnInit(self):
        frame = MyFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


# prog execution
if "-h" in sys.argv or "--help" in sys.argv:
    mapalt.resetArgs()
    mapalt.printHelp()
    sys.exit()
elif "--nogui" in sys.argv:
    try:
        mapalt.run()
    except mapalt.MyException as ex:
        print(str(ex))
        sys.exit()
else:
    app = MyApp()
    app.MainLoop()


