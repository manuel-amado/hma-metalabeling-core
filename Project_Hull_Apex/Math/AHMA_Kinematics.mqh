//+------------------------------------------------------------------+
//|                                              AHMA_Kinematics.mqh |
//|                                   Project_Hull_Apex - NEXUS FORK |
//|                                     Bifurcation from Alpha_Sniper|
//+------------------------------------------------------------------+
#property copyright "NEXUS PROTOCOL"
#property link      ""
#property version   "1.00"

//+------------------------------------------------------------------+
//| Class CAHMA_Kinematics                                           |
//| Motor matemático basado en AHMA y cinemática de derivadas        |
//+------------------------------------------------------------------+
class CAHMA_Kinematics
  {
private:
   int               m_min_period;
   int               m_max_period;
   int               m_er_period;
   
   // Funciones matemáticas internas
   double            CalculateWMA(int period, int shift, const double &prices[]);

public:
                     CAHMA_Kinematics(int min_period=10, int max_period=50, int er_period=14);
                    ~CAHMA_Kinematics();

   // Núcleo AHMA
   double            GetKaufmanER(int shift, const double &prices[]);
   int               GetAdaptivePeriod(double er);
   double            GetAHMA(int shift, const double &prices[]);
   
   // Motor Cinemático (Derivadas)
   // No se calculan cruces, sino la curvatura (velocidad y aceleración)
   double            GetVelocity(double ahma_current, double ahma_prev);
   double            GetAcceleration(double velocity_current, double velocity_prev);
   
   // Esqueletos - Matriz de Filtrado Institucional
   bool              Filter_MTF_Alignment(double current_tf_velocity, double higher_tf_velocity);
   bool              Filter_ADX_Momentum(double adx_value, double threshold = 25.0);
   bool              Filter_RSI_FOMO(double rsi_value, int signal_direction, double lower_bound = 30.0, double upper_bound = 70.0);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CAHMA_Kinematics::CAHMA_Kinematics(int min_period=10, int max_period=50, int er_period=14)
  {
   m_min_period = min_period;
   m_max_period = max_period;
   m_er_period = er_period;
  }

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CAHMA_Kinematics::~CAHMA_Kinematics()
  {
  }

//+------------------------------------------------------------------+
//| Ratio de Eficiencia de Kaufman (ER)                              |
//| Mide el ruido del mercado. ER -> 1 (Tendencia), ER -> 0 (Rango)  |
//+------------------------------------------------------------------+
double CAHMA_Kinematics::GetKaufmanER(int shift, const double &prices[])
  {
   int total = ArraySize(prices);
   if(shift + m_er_period >= total) return 0.0;
   
   // Cambio neto en el periodo
   double change = MathAbs(prices[shift] - prices[shift + m_er_period]);
   double volatility = 0.0;
   
   // Suma de la volatilidad barra a barra
   for(int i = 0; i < m_er_period; i++)
     {
      volatility += MathAbs(prices[shift + i] - prices[shift + i + 1]);
     }
     
   if(volatility == 0.0) return 0.0;
   
   return change / volatility;
  }

//+------------------------------------------------------------------+
//| Periodo Adaptativo                                               |
//| Comprime la media (rápida) si ER->1, dilata (lenta) si ER->0     |
//+------------------------------------------------------------------+
int CAHMA_Kinematics::GetAdaptivePeriod(double er)
  {
   // Relación inversa: mayor ER -> menor periodo (mayor velocidad de respuesta)
   double scaled_period = m_min_period + (m_max_period - m_min_period) * (1.0 - er);
   return (int)MathRound(scaled_period);
  }

//+------------------------------------------------------------------+
//| Media Móvil Ponderada (WMA) Auxiliar                             |
//+------------------------------------------------------------------+
double CAHMA_Kinematics::CalculateWMA(int period, int shift, const double &prices[])
  {
   if(period <= 0) return 0.0;
   
   double sum = 0.0;
   double weight_sum = 0.0;
   
   for(int i = 0; i < period; i++)
     {
      // El peso mayor se asigna al dato más reciente (i=0 respecto al shift)
      double weight = (double)(period - i);
      sum += prices[shift + i] * weight;
      weight_sum += weight;
     }
     
   return (weight_sum > 0) ? sum / weight_sum : 0.0;
  }

//+------------------------------------------------------------------+
//| Media Móvil de Hull Adaptativa (AHMA)                            |
//| Calcula la HMA estándar usando el periodo adaptativo (n)         |
//| AHMA = WMA(2 * WMA(n/2) - WMA(n), sqrt(n))                       |
//+------------------------------------------------------------------+
double CAHMA_Kinematics::GetAHMA(int shift, const double &prices[])
  {
   double er = GetKaufmanER(shift, prices);
   int n = GetAdaptivePeriod(er);
   
   int half_n = (int)MathRound(n / 2.0);
   int sqrt_n = (int)MathRound(MathSqrt(n));
   
   if(half_n < 1) half_n = 1;
   if(sqrt_n < 1) sqrt_n = 1;
   
   // Array temporal para la serie interna: 2*WMA(n/2) - WMA(n)
   double inner_series[];
   ArrayResize(inner_series, sqrt_n);
   
   for(int i = 0; i < sqrt_n; i++)
     {
      double wma_half = CalculateWMA(half_n, shift + i, prices);
      double wma_full = CalculateWMA(n, shift + i, prices);
      inner_series[i] = 2.0 * wma_half - wma_full;
     }
     
   // WMA final usando los datos internos calculados
   double ahma = CalculateWMA(sqrt_n, 0, inner_series);
   
   return ahma;
  }

//+------------------------------------------------------------------+
//| Cinemática: Primera Derivada (Velocidad)                         |
//| Representa la pendiente de la AHMA.                              |
//+------------------------------------------------------------------+
double CAHMA_Kinematics::GetVelocity(double ahma_current, double ahma_prev)
  {
   return ahma_current - ahma_prev;
  }

//+------------------------------------------------------------------+
//| Cinemática: Segunda Derivada (Aceleración)                       |
//| Representa la curvatura, útil para detectar puntos de inflexión. |
//+------------------------------------------------------------------+
double CAHMA_Kinematics::GetAcceleration(double velocity_current, double velocity_prev)
  {
   return velocity_current - velocity_prev;
  }

//+------------------------------------------------------------------+
//| Matriz de Filtrado: Sincronización Multi-Timeframe               |
//| Verifica alineación direccional con el marco superior            |
//+------------------------------------------------------------------+
bool CAHMA_Kinematics::Filter_MTF_Alignment(double current_tf_velocity, double higher_tf_velocity)
  {
   // Ambos marcos temporales deben tener la misma dirección
   if(current_tf_velocity > 0 && higher_tf_velocity > 0) return true;
   if(current_tf_velocity < 0 && higher_tf_velocity < 0) return true;
   return false;
  }

//+------------------------------------------------------------------+
//| Matriz de Filtrado: ADX (Momento y Tendencia)                    |
//+------------------------------------------------------------------+
bool CAHMA_Kinematics::Filter_ADX_Momentum(double adx_value, double threshold = 25.0)
  {
   // Requiere inercia institucional para evitar mercados planos
   return (adx_value >= threshold);
  }

//+------------------------------------------------------------------+
//| Matriz de Filtrado: RSI (Bloqueador de FOMO)                     |
//+------------------------------------------------------------------+
bool CAHMA_Kinematics::Filter_RSI_FOMO(double rsi_value, int signal_direction, double lower_bound = 30.0, double upper_bound = 70.0)
  {
   // Bloquea compras (LONG) si RSI está en sobrecompra extrema
   if(signal_direction > 0)
     {
      return (rsi_value < upper_bound);
     }
   // Bloquea ventas (SHORT) si RSI está en sobreventa extrema
   else if(signal_direction < 0)
     {
      return (rsi_value > lower_bound);
     }
     
   return false;
  }
//+------------------------------------------------------------------+
