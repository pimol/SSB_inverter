import win32api
import win32con

def leggi():
    def newIni():
        win32api.MessageBox(0, "Il file di configurazione manca (prima esecuzione?)\nSarà generato un file di default, da editare", "Rigenerazione file ini", win32con.MB_OK)
        try:
            shutil.copy("SSB_inv.default", "SSB_inv.ini")
        except:
            return False
        return True

    # *************  Inizializzazione  *************

    import shutil

    try:
        fileIni = open("SSB_inv.ini", "r")
    except Exception as arg:
        print("Errore in ini file:", str(arg))
        if not newIni():
            win32api.MessageBox(0, "ini file creation failed!\nInstall again", "Fatal error",
                                win32con.MB_OK | win32con.MB_ICONERROR)
            exit()
    return True

import ast
import sounddevice

def read_devices():

    # Lista dispositivi audio
    with open ("devicesList.txt", "w") as f:
        f.write(str(sounddevice.query_devices()))

    if leggi():    
        with open("SSB_inv.ini", "r") as f:
            content = f.read().strip()
            deviceIn, deviceOut = ast.literal_eval(content)
            l = sounddevice.query_devices()
            deviceInName = l[deviceIn]['name']
            deviceOutName = l[deviceOut]['name']
            messaggio = "Input: " + deviceInName + "  Output: " + deviceOutName
            risposta = (win32api.MessageBox(0, "Corretto?", messaggio,
                                            win32con.MB_YESNO | win32con.MB_ICONQUESTION) == win32con.IDYES)
            if risposta:
                pass
            else:
                messaggio = "CercaScegli i dispositivi audio"
                win32api.MessageBox(0, "Modifica il file ini e rilancia", messaggio,
                                    win32con.MB_OK | win32con.MB_ICONINFORMATION)
                exit()
            return deviceIn, deviceOut
    else:
        exit()  




if __name__ == "__main__":
   read_devices()