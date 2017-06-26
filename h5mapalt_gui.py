#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import h5mapalt as mapalt
import wx


class MyFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, wx.ID_ANY, "MMH55 Mapmixer", style=wx.DEFAULT_FRAME_STYLE & ~ wx.RESIZE_BORDER)
        
        self.mapFileEdit = None
        self.mapFileBtn = None
        self.creaChangeCheck = None
        self.creaChangeOnlyRandomCheck = None
        self.creaRandomCheck = None
        self.creaNcfCheck = None
        self.creaPowerRatioSpin = None
        self.creaNeutralRatioSpin = None
        self.creaGroupRatioSlider = None
        self.creaMoodChangeCheck = None
        self.creaMoodFriendlyCheck = None
        self.creaMoodAggressiveCheck = None
        self.creaMoodHostileCheck = None
        self.creaMoodWildCheck = None
        self.artChangeCheck = None
        self.artChangeOnlyRandomCheck = None
        self.artRandomCheck = None
        self.enableScriptsCheck = None
        self.waterChangeCheck = None
        self.dwellChangeCheck = None
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
        creaHeadSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.creaChangeCheck = wx.CheckBox(creaBox, wx.ID_ANY, "swap")
        self.creaChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaChangeCheckChange, self.creaChangeCheck)
        creaHeadSizer.Add(self.creaChangeCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        creaHeadSizer.AddStretchSpacer(1)
        comp = wx.StaticLine(creaBox, wx.ID_ANY, style=wx.LI_VERTICAL)
        creaHeadSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        creaHeadSizer.AddStretchSpacer(1)
        
        self.creaChangeOnlyRandomCheck = wx.CheckBox(creaBox, wx.ID_ANY, "only random blocks")
        creaHeadSizer.Add(self.creaChangeOnlyRandomCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        creaSizer.Add(creaHeadSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        comp = wx.StaticLine(creaBox, wx.ID_ANY)
        creaSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        
        creaGridSizer = wx.FlexGridSizer(2)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "power ratio")
        self.creaPowerRatioSpin = wx.SpinCtrlDouble(creaBox, wx.ID_ANY, min=0.1, max=100.0, inc=0.1, initial=1.0)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaPowerRatioSpin, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "neutral ratio")
        self.creaNeutralRatioSpin = wx.Slider(creaBox, wx.ID_ANY, -2, -6, 6, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaNeutralRatioSpin, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        label = wx.StaticText(creaBox, wx.ID_ANY, "mixed stacks (%)")
        self.creaGroupRatioSlider = wx.Slider(creaBox, wx.ID_ANY, 55, 0, 100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        creaGridSizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        creaGridSizer.Add(self.creaGroupRatioSlider, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        creaSizer.Add(creaGridSizer, 1, wx.EXPAND, 0)
        
        self.creaRandomCheck = wx.CheckBox(creaBox, wx.ID_ANY, "random blocks")
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
        creaMoodSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.creaMoodChangeCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "swap")
        self.creaMoodChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaMoodChangeCheckChange, self.creaMoodChangeCheck)
        creaMoodSizer.Add(self.creaMoodChangeCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        comp = wx.StaticLine(creaMoodBox, wx.ID_ANY)
        creaMoodSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        
        creaMoodGridSizer = wx.GridSizer(2)
        
        self.creaMoodFriendlyCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "friendly")
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaMoodCheckChange, self.creaMoodFriendlyCheck)
        creaMoodGridSizer.Add(self.creaMoodFriendlyCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodAggressiveCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "aggressive")
        self.creaMoodAggressiveCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaMoodCheckChange, self.creaMoodAggressiveCheck)
        creaMoodGridSizer.Add(self.creaMoodAggressiveCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodHostileCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "hostile")
        self.creaMoodHostileCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaMoodCheckChange, self.creaMoodHostileCheck)
        creaMoodGridSizer.Add(self.creaMoodHostileCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.creaMoodWildCheck = wx.CheckBox(creaMoodBox, wx.ID_ANY, "wild")
        self.Bind(wx.EVT_CHECKBOX, self.OnCreaMoodCheckChange, self.creaMoodWildCheck)
        creaMoodGridSizer.Add(self.creaMoodWildCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        creaMoodSizer.Add(creaMoodGridSizer, 1, wx.EXPAND, 0)
        
        creaMoodBorderSizer = wx.BoxSizer(wx.VERTICAL)
        creaMoodBorderSizer.Add(creaMoodSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        creaMoodBox.SetSizerAndFit(creaMoodBorderSizer)
        leftSizer.Add(creaMoodBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # moods end
        # creatures end
        
        
        # artifacts
        
        artBox = wx.StaticBox(self, wx.ID_ANY, "artifacts")
        artSizer = wx.BoxSizer(wx.VERTICAL)
        artHeadSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.artChangeCheck = wx.CheckBox(artBox, wx.ID_ANY, "swap")
        self.artChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnArtChangeCheckChange, self.artChangeCheck)
        artHeadSizer.Add(self.artChangeCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        artHeadSizer.AddStretchSpacer(1)
        comp = wx.StaticLine(artBox, wx.ID_ANY, style=wx.LI_VERTICAL)
        artHeadSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        artHeadSizer.AddStretchSpacer(1)
        
        self.artChangeOnlyRandomCheck = wx.CheckBox(artBox, wx.ID_ANY, "only random blocks")
        artHeadSizer.Add(self.artChangeOnlyRandomCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        artSizer.Add(artHeadSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        comp = wx.StaticLine(artBox, wx.ID_ANY)
        artSizer.Add(comp, 0, wx.ALL|wx.EXPAND, 5)
        
        self.artRandomCheck = wx.CheckBox(artBox, wx.ID_ANY, "random blocks")
        artSizer.Add(self.artRandomCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        sizer = wx.FlexGridSizer(2)
        artSizer.Add(sizer)
        
        artBorderSizer = wx.BoxSizer(wx.VERTICAL)
        artBorderSizer.Add(artSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        artBox.SetSizerAndFit(artBorderSizer)
        rightSizer.Add(artBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # artifacts end
        
        
        # mmh55
        
        mmh55Box = wx.StaticBox(self, wx.ID_ANY, "MMH55")
        mmh55Sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.enableScriptsCheck = wx.CheckBox(mmh55Box, wx.ID_ANY, "make hotseat/LAN compatible")
        self.enableScriptsCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnEnableScriptsCheckChange, self.enableScriptsCheck)
        mmh55Sizer.Add(self.enableScriptsCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        mmh55BorderSizer = wx.BoxSizer(wx.VERTICAL)
        mmh55BorderSizer.Add(mmh55Sizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        mmh55Box.SetSizerAndFit(mmh55BorderSizer)
        rightSizer.Add(mmh55Box, 0, wx.ALL|wx.EXPAND, 5)
        
        # mmh55 end
        
        
        # other
        
        otherBox = wx.StaticBox(self, wx.ID_ANY, "other")
        otherSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.waterChangeCheck = wx.CheckBox(otherBox, wx.ID_ANY, "swap water objects")
        self.waterChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnWaterChangeCheckChange, self.waterChangeCheck)
        otherSizer.Add(self.waterChangeCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        self.dwellChangeCheck = wx.CheckBox(otherBox, wx.ID_ANY, "swap dwellings")
        self.dwellChangeCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnDwellChangeCheckChange, self.dwellChangeCheck)
        otherSizer.Add(self.dwellChangeCheck, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        
        otherBorderSizer = wx.BoxSizer(wx.VERTICAL)
        otherBorderSizer.Add(otherSizer, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 20)
        otherBox.SetSizerAndFit(otherBorderSizer)
        rightSizer.Add(otherBox, 0, wx.ALL|wx.EXPAND, 5)
        
        # other end
        
        
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
        self.creaChangeOnlyRandomCheck.Enable(enable)
        self.creaRandomCheck.Enable(enable)
        self.creaNcfCheck.Enable(enable)
        self.creaPowerRatioSpin.Enable(enable)
        
        randomEnable = enable and not self.creaRandomCheck.GetValue()
        self.creaNeutralRatioSpin.Enable(randomEnable)
        self.creaGroupRatioSlider.Enable(randomEnable)
        
        self.creaMoodChangeCheck.Enable(enable)
        creaMoodChangeEnable = enable and self.creaMoodChangeCheck.GetValue()
        
        # at least one mood should be checked
        checkedCreaMoodCount = 0
        creaMoodInputs = [
            self.creaMoodFriendlyCheck,
            self.creaMoodAggressiveCheck,
            self.creaMoodHostileCheck,
            self.creaMoodWildCheck
        ]
        for creaMoodInput in creaMoodInputs:
            if creaMoodInput.GetValue():
                checkedCreaMoodCount += 1
        for creaMoodInput in creaMoodInputs:
            if not creaMoodChangeEnable or checkedCreaMoodCount != 1:
                creaMoodInput.Enable(creaMoodChangeEnable)
            else:
                creaMoodInput.Enable(not creaMoodInput.GetValue())
    
    def RefreshArtifactInputsState(self):
        enable = self.artChangeCheck.GetValue()
        self.artChangeOnlyRandomCheck.Enable(enable)
        self.artRandomCheck.Enable(enable)
    
    def OnCreaChangeCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
        self.CheckOkButtonState()
        
    def OnCreaMoodChangeCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
        
    def OnCreaRandomCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
    
    def OnArtChangeCheckChange(self, pEvent):
        self.RefreshArtifactInputsState()
        self.CheckOkButtonState()
    
    def OnCreaMoodCheckChange(self, pEvent):
        self.RefreshCreatureInputsState()
        
    def OnEnableScriptsCheckChange(self, pEvent):
        self.CheckOkButtonState()
    
    def OnWaterChangeCheckChange(self, pEvent):
        self.CheckOkButtonState()
    
    def OnDwellChangeCheckChange(self, pEvent):
        self.CheckOkButtonState()
    
    def CheckOkButtonState(self):
        enableOkButton = (self.creaChangeCheck.GetValue() or self.artChangeCheck.GetValue() 
                            or self.enableScriptsCheck.GetValue() or self.waterChangeCheck.GetValue() 
                            or self.dwellChangeCheck.GetValue())
        self.okBtn.Enable(enableOkButton)
    
    def OnMapFileBtnClick(self, pEvent):
        fileDlg = wx.FileDialog(self, "Open h5m file", "../Maps", "", "h5m (*.h5m)|*.h5m", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST);
        if fileDlg.ShowModal() != wx.ID_CANCEL:
            self.mapFileEdit.SetValue(fileDlg.GetPath())
    
    def OnOkBtnClick(self, pEvent):
        argMapFile = self.mapFileEdit.GetValue()

        argArtChange = "--artChange=" + ("true" if self.artChangeCheck.GetValue() else "false")
        argCreaChange = "--creaChange=" + ("true" if self.creaChangeCheck.GetValue() else "false")

        argArtChangeOnlyRandom = "--artChangeOnlyRandom=" + ("true" if self.artChangeOnlyRandomCheck.GetValue() else "false")
        argArtRandom = "--artRandom=" + ("true" if self.artRandomCheck.GetValue() else "false")
        argCreaChangeOnlyRandom = "--creaChangeOnlyRandom=" + ("true" if self.creaChangeOnlyRandomCheck.GetValue() else "false")
        argCreaRandom = "--creaRandom=" + ("true" if self.creaRandomCheck.GetValue() else "false")
        
        argCreaPowerRatio = "--creaPowerRatio=" + str(self.creaPowerRatioSpin.GetValue())
        argCreaGroupRatio = "--creaGroupRatio=" + str(self.creaGroupRatioSlider.GetValue() / 100)
        argCreaNeutralRatio = "--creaNeutralRatio=" + str(self.creaNeutralRatioSpin.GetValue())
        argCreaNCF = "--creaNCF=" + ("true" if self.creaNcfCheck.GetValue() else "false")
        
        argCreaMoodChange = "--creaMoodChange=" + ("true" if self.creaMoodChangeCheck.GetValue() else "false")
        argCreaMoodRatio = "--creaMoodRatio="
        argCreaMoodRatio += ("1" if self.creaMoodFriendlyCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodAggressiveCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodHostileCheck.GetValue() else "0")
        argCreaMoodRatio += "," + ("1" if self.creaMoodWildCheck.GetValue() else "0")
        
        argEnableScripts = "--enableScripts=" + ("true" if self.enableScriptsCheck.GetValue() else "false")
        argWaterChange = "--waterChange=" + ("true" if self.waterChangeCheck.GetValue() else "false")
        argDwellChange = "--dwellChange=" + ("true" if self.dwellChangeCheck.GetValue() else "false")
        
        argGuiIsShown = "--guiIsShown=true"
        
        args = [
            argMapFile, argArtChange, argCreaChange, argArtChangeOnlyRandom, argArtRandom, 
            argCreaChangeOnlyRandom, argCreaRandom, argCreaPowerRatio, argCreaGroupRatio, 
            argCreaNeutralRatio, argCreaNCF, argCreaMoodChange, argCreaMoodRatio, 
            argEnableScripts, argWaterChange, argDwellChange, argGuiIsShown
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


