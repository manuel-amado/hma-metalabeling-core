//+------------------------------------------------------------------+
//|                                       Export_Historical_Data.mq5 |
//|                                                Copyright 2026    |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "1.01"
#property script_show_inputs

input datetime InpStartDate = D'2015.01.01 00:00:00';

void OnStart() {
    string timeframe = EnumToString(_Period);
    StringReplace(timeframe, "PERIOD_", "");
    string file_name = _Symbol + "_" + timeframe + "_Historical.csv";
    
    Print("Solicitando datos de ", _Symbol, " en ", timeframe, "... Esto puede tardar unos minutos.");
    
    datetime end_date = TimeCurrent();
    MqlRates rates[];
    
    int copied = 0;
    int attempts = 0;
    
    while(attempts < 10) {
        copied = CopyRates(_Symbol, _Period, InpStartDate, end_date, rates);
        if(copied > 100000) {
            break; 
        }
        Print("Descargando... Barras obtenidas: ", copied, ". Reintentando en 3s...");
        Sleep(3000);
        attempts++;
    }
    
    if(copied <= 0) {
        Print("ERROR: No se pudieron descargar los datos.");
        return;
    }
    
    Print("Descarga completa. ", copied, " barras obtenidas. Exportando a CSV...");
    
    int handle = FileOpen(file_name, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
    if(handle == INVALID_HANDLE) {
        Print("ERROR: No se pudo crear el archivo ", file_name);
        return;
    }
    
    FileWrite(handle, "time", "open", "high", "low", "close", "tick_volume", "spread");
    
    for(int i = 0; i < copied; i++) {
        string t_str = TimeToString(rates[i].time, TIME_DATE|TIME_MINUTES);
        FileWrite(handle, 
                  t_str, 
                  DoubleToString(rates[i].open, 5),
                  DoubleToString(rates[i].high, 5),
                  DoubleToString(rates[i].low, 5),
                  DoubleToString(rates[i].close, 5),
                  IntegerToString(rates[i].tick_volume),
                  IntegerToString(rates[i].spread));
    }
    
    FileClose(handle);
    Print("¡ÉXITO! Archivo guardado en MQL5/Files/", file_name);
}