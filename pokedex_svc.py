import win32serviceutil
import win32event
import win32service
import servicemanager
import pokedex
import sys

class PokedexService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'pokedex-bot'
    _svc_display_name_ = 'Pokedex Bot'
    _svc_type_ = win32service.SERVICE_AUTO_START
    
    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
    
    def SvcStop(self):
        print('Service is stopping...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.stop_event)
    
    def SvcRun(self):
        print('Service is starting...')
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        self.main()
    
    def main(self):
        while self.is_running:
            pokedex.main()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PokedexService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PokedexService)
        