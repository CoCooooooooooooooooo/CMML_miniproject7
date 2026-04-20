
import wx

from HypoModPy.hypoparams import ParamBox



class SpikeBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        self.AddFlag("randomflag", "Fixed Random Seed", 0)  # menu accessed flags for switching model code


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("Vrest", "Vrest", -62, 0.1, 2)
        self.paramset.AddCon("Vthresh", "Vthresh", -50, 0.1, 2)
        self.paramset.AddCon("psprate", "PSP Rate", 300, 1, 0)
        self.paramset.AddCon("pspratio", "PSP ratio", 1, 0.1, 2)
        self.paramset.AddCon("pspmag", "PSP mag", 3, 0.1, 2)
        self.paramset.AddCon("halflifeMem", "halflifeMem", 7.5, 0.1, 2)
        self.paramset.AddCon("kHAP", "kHAP", 60, 0.1, 2)
        self.paramset.AddCon("halflifeHAP", "halflifeHAP", 8, 0.1, 2)
        self.paramset.AddCon("kDAP", "kDAP", 60, 0.1, 2)
        self.paramset.AddCon("halflifeDAP", "halflifeDAP", 8, 0.1, 2)
        self.paramset.AddCon("kAHP", "kAHP", 0.5, 0.01, 2)
        self.paramset.AddCon("halflifeAHP", "halflifeAHP", 500, 1, 2)
        
        # DAP model selection: 0=none, 1=simple(kDAP-based), 2=NMDA-based
        self.paramset.AddCon("DAP_model", "DAP model", 1, 1, 0)  # 0=none, 1=simple, 2=NMDA
        
        # NMDA-based DAP parameters
        self.paramset.AddCon("gNMDA", "gNMDA", 2.0, 0.1, 2)  # NMDA conductance (mS/cm2)
        self.paramset.AddCon("tau_NMDA_rise", "tau NMDA rise", 5, 0.1, 1)  # ms, fast rise time
        self.paramset.AddCon("tau_NMDA_decay", "tau NMDA decay", 100, 1, 0)  # ms, slow decay
        self.paramset.AddCon("tau_x_NMDA", "tau x NMDA", 50, 10, 0)  # ms, glutamate state decay
        self.paramset.AddCon("Mg_conc", "Mg [mM]", 1.0, 0.1, 2)  # extracellular Mg2+ concentration
        self.paramset.AddCon("NMDA_Ca_fraction", "NMDA Ca frac", 0.15, 0.01, 2)  # fraction of current as Ca2+
        self.paramset.AddCon("E_NMDA", "E_NMDA (mV)", 0, 1, 0)  # reversal potential

        self.paramset.GetCon("runtime").SetMinMax(10, 10000)

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()

        databox = wx.BoxSizer(wx.HORIZONTAL)
        self.freq = self.NumPanel(60, wx.ALIGN_RIGHT)
        label = wx.StaticText(self.panel, wx.ID_STATIC, "Freq")
        label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        databox.Add(label,0, (wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE))
        databox.AddSpacer(10)   
        databox.Add(self.freq)

        ID_Grid = wx.NewIdRef()
        self.AddPanelButton(ID_Grid, "Grid", self.mod.gridbox)
        ID_Sec = wx.NewIdRef()
        self.AddPanelButton(ID_Sec, "Sec", self.mod.secbox)

        # Export Data button
        ID_Export = wx.NewIdRef()
        exportbtn = wx.Button(self.panel, ID_Export, "Export Data", size=wx.Size(120, -1))
        exportbtn.SetBackgroundColour(wx.Colour(200, 230, 200))
        self.Bind(wx.EVT_BUTTON, self.OnExportData, id=ID_Export)

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(databox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)    
        self.mainbox.Add(self.buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(exportbtn, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
        self.mainbox.AddSpacer(5)
        self.panel.Layout()


    def SpikeData(self, data):
        self.freq.SetLabel(f"{data.freq:.2f} Hz")


    def OnExportData(self, event):
        try:
            from export_data import export_data
            psp     = int(self.paramset.GetCon("psprate").GetValue())
            dap_model = int(self.paramset.GetCon("DAP_model").GetValue())
            kDAP    = self.paramset.GetCon("kDAP").GetValue()
            label   = f"model{dap_model}_PSP{psp}_kDAP{kDAP:.2f}"
            export_data(self.mod, label=label)
            wx.MessageBox(f"Data exported!\nLabel: {label}", "Export OK", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Export failed:\n{e}", "Export Error", wx.OK | wx.ICON_ERROR)


    def OnStore(self, event):
        if self.synccheck.GetValue():
            filetag = self.storetag.GetValue()
            self.mod.secbox.ParamStore(filetag)   
        return super().OnStore(event)
    

    def OnLoad(self, event):
        if self.synccheck.GetValue():
            filetag = self.storetag.GetValue()
            self.mod.secbox.ParamLoad(filetag)   
        return super().OnLoad(event)



class SecBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.con_labelwidth = 80
        self.paramset.AddCon("kB", "kB", 0.021, 0.001, 3)
        self.paramset.AddCon("halflifeB", "halflifeB", 2000, 50, 0)
        self.paramset.AddCon("Bbase", "Bbase", 0.5, 0.05, 2)
        self.paramset.AddCon("kC", "SlowCa K", 0.0003, 0.00001, 5)
        self.paramset.AddCon("halflifeC", "C HL", 20000, 1000, 0)
        self.paramset.AddCon("kE", "FastCa K", 1.5, 0.02, 2)
        self.paramset.AddCon("halflifeE", "E HL", 100, 5, 1)
        self.paramset.AddCon("Cth", "Cth", 0.14, 0.01, 3)
        self.paramset.AddCon("Cgradient", "C Grad", 5, 0.1, 2)
        self.paramset.AddCon("Eth", "Eth", 12, 0.05, 2)
        self.paramset.AddCon("Egradient", "E Grad", 5, 0.1, 2)
        self.paramset.AddCon("beta", "beta", 120, 1, 1)
        self.paramset.AddCon("Rmax", "Res Max", 1000000, 100000, 0)
        self.paramset.AddCon("Rinit", "Res Init", 1000000, 100000, 0)
        self.paramset.AddCon("Pmax", "Pool Max", 5000, 500, 0)
        self.paramset.AddCon("alpha", "alpha", 0.003, 0.0001, 6)
        self.paramset.AddCon("plasma_hstep", "hstep Plas", 1, 1, 0)
        self.paramset.AddCon("halflifeDiff", "Diff HL", 61, 5, 0)   # 100sec, half life to pass between plasma and ECF. Just a guess.
        self.paramset.AddCon("halflifeClear", "Clear HL", 68, 5, 0)   # 58sec half life to be destroyed through the kidneys.
        self.paramset.AddCon("VolPlasma", "Plasma (ml)", 100, 0.5, 1)   # Total amount of plasma in a rat. 8.5ml for a 250g rat.
        self.paramset.AddCon("VolEVF", "EVFluid (ml)", 9.75, 0.5, 2)   # Total amount of Extra Cellular Fluid (without plasma) in a rat.
        self.paramset.AddCon("secExp", "Sec Exp", 2, 0.1, 2)  # Exponent of the fast [Ca2+], e, when calculating the final secretion.

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        
        self.panel.Layout()