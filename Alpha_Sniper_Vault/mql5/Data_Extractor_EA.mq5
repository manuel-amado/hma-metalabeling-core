//+------------------------------------------------------------------+
//|                                        Data_Extractor_EA.mq5     |
//|                                                Copyright 2026    |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "1.00"

int csv_handle;
datetime last_bar_time = 0;

int OnInit() {
    // FILE_COMMON lo guarda en la carpeta global compartida, fuera de las carpetas virtuales del tester
    csv_handle = FileOpen("XAUUSD_M15_10Years.csv", FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ",");
    
    if(csv_handle != INVALID_HANDLE) {
        FileWrite(csv_handle, "time", "open", "high", "low", "close");
        Print("Archivo CSV abierto en la carpeta Common/Files. Iniciando extracción...");
    } else {
        Print("Error al abrir el archivo CSV.");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    if(csv_handle != INVALID_HANDLE) {
        FileClose(csv_handle);
        Print("¡Extracción finalizada! CSV guardado con éxito.");
    }
}

void OnTick() {
    datetime current_time = iTime(_Symbol, _Period, 0);
    
    if(current_time == last_bar_time || current_time == 0) return;
    
    if(last_bar_time != 0) {
        // Obtenemos los datos de la vela que acaba de cerrar (índice 1)
        double o = iOpen(_Symbol, _Period, 1);
        double h = iHigh(_Symbol, _Period, 1);
        double l = iLow(_Symbol, _Period, 1);
        double c = iClose(_Symbol, _Period, 1);
        
        string t_str = TimeToString(last_bar_time, TIME_DATE|TIME_MINUTES);
        FileWrite(csv_handle, t_str, 
                  DoubleToString(o, 5), 
                  DoubleToString(h, 5), 
                  DoubleToString(l, 5), 
                  DoubleToString(c, 5));
    }
    
    last_bar_time = current_time;
}