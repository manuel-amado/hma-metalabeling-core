//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| REGIMEN: Rolling Window 2024-2026 (Alta Volatilidad)          |
//| Generado automaticamente por Antigravity Quant AI              |
//+------------------------------------------------------------------+
#property copyright "Antigravity Quant AI"

double sigmoid(double x) {
    if (x < 0.0) {
        double z = MathExp(x);
        return z / (1.0 + z);
    }
    return 1.0 / (1.0 + MathExp(-x));
}
void GetXGBoostProbability(const double &features[], double &result[]) {
    double var0;
    if (features[3] < 0.6619) {
        if (features[4] < 0.006997) {
            var0 = 0.025;
        } else {
            var0 = -0.0625;
        }
    } else {
        if (features[1] < 0.146879) {
            var0 = -0.00909091;
        } else {
            if (features[4] < 0.016342) {
                var0 = 0.014285715;
            } else {
                var0 = 0.07058824;
            }
        }
    }
    double var1;
    if (features[0] < 0.019066) {
        if (features[4] < 0.027237) {
            if (features[0] < 0.014185) {
                var1 = 0.04943574;
            } else {
                var1 = -0.010841681;
            }
        } else {
            if (features[0] < 0.013204) {
                var1 = -0.045312177;
            } else {
                var1 = 0.01107734;
            }
        }
    } else {
        if (features[2] < 48.47) {
            var1 = 0.06848215;
        } else {
            var1 = 0.0095989695;
        }
    }
    double var2;
    if (features[3] < 0.6619) {
        if (features[3] < -0.7087) {
            var2 = 0.016938694;
        } else {
            var2 = -0.032873686;
        }
    } else {
        if (features[1] < 0.146244) {
            var2 = -0.010194072;
        } else {
            if (features[4] < 0.047635) {
                var2 = 0.059423964;
            } else {
                var2 = 0.0088650985;
            }
        }
    }
    double var3;
    if (features[3] < 0.6619) {
        if (features[1] < 0.182103) {
            var3 = 0.032493092;
        } else {
            if (features[4] < 0.039543) {
                var3 = -0.048667345;
            } else {
                var3 = -0.008636687;
            }
        }
    } else {
        if (features[1] < 0.146879) {
            var3 = -0.020754455;
        } else {
            if (features[3] < 1.2888) {
                var3 = 0.02334094;
            } else {
                var3 = 0.064604454;
            }
        }
    }
    double var4;
    if (features[3] < 0.6619) {
        if (features[0] < 0.013965) {
            var4 = -0.042654388;
        } else {
            if (features[3] < -0.7087) {
                var4 = 0.031928744;
            } else {
                var4 = -0.03178442;
            }
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[4] < 0.049127) {
                var4 = 0.061874725;
            } else {
                var4 = 0.0070748325;
            }
        } else {
            if (features[2] < 39.27) {
                var4 = 0.04100002;
            } else {
                var4 = -0.03585721;
            }
        }
    }
    double var5;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var5 = 0.031770654;
        } else {
            if (features[6] < 0.757354) {
                var5 = -0.057876207;
            } else {
                var5 = -0.008151333;
            }
        }
    } else {
        if (features[6] < 0.074475) {
            var5 = 0.0033138618;
        } else {
            if (features[0] < 0.017184) {
                var5 = 0.024489416;
            } else {
                var5 = 0.06630011;
            }
        }
    }
    double var6;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var6 = 0.031582672;
        } else {
            if (features[5] < 0.007234) {
                var6 = -0.051907044;
            } else {
                var6 = -0.007927272;
            }
        }
    } else {
        if (features[2] < 39.27) {
            if (features[3] < 1.2888) {
                var6 = 0.02529995;
            } else {
                var6 = 0.06818844;
            }
        } else {
            if (features[0] < 0.027068) {
                var6 = 0.030890971;
            } else {
                var6 = -0.024881354;
            }
        }
    }
    double var7;
    if (features[3] < 0.5167) {
        if (features[6] < 0.430133) {
            var7 = 0.01873388;
        } else {
            var7 = -0.061407816;
        }
    } else {
        if (features[6] < 0.108291) {
            var7 = -0.0164898;
        } else {
            if (features[3] < 3.7988) {
                var7 = 0.05568567;
            } else {
                var7 = 0.008898772;
            }
        }
    }
    double var8;
    if (features[3] < -0.9407) {
        var8 = -0.017611211;
    } else {
        if (features[2] < 39.27) {
            if (features[0] < 0.017184) {
                var8 = 0.022622215;
            } else {
                var8 = 0.058724325;
            }
        } else {
            if (features[3] < 3.6683) {
                var8 = 0.027071608;
            } else {
                var8 = -0.036777932;
            }
        }
    }
    double var9;
    if (features[4] < 0.027338) {
        if (features[5] < 0.015644) {
            if (features[5] < 0.006938) {
                var9 = 0.011257977;
            } else {
                var9 = 0.063229315;
            }
        } else {
            var9 = -0.0012130397;
        }
    } else {
        if (features[6] < 0.922683) {
            if (features[4] < 0.032701) {
                var9 = -0.041801725;
            } else {
                var9 = -0.006679716;
            }
        } else {
            if (features[2] < 22.09) {
                var9 = -0.014292813;
            } else {
                var9 = 0.051180955;
            }
        }
    }
    double var10;
    if (features[4] < 0.027338) {
        if (features[6] < 0.915411) {
            if (features[3] < 0.6619) {
                var10 = 0.017640052;
            } else {
                var10 = 0.06865973;
            }
        } else {
            var10 = 0.007798236;
        }
    } else {
        if (features[6] < 0.922683) {
            if (features[4] < 0.041939) {
                var10 = -0.040988207;
            } else {
                var10 = 0.012616741;
            }
        } else {
            if (features[2] < 22.09) {
                var10 = -0.013897841;
            } else {
                var10 = 0.05492719;
            }
        }
    }
    double var11;
    if (features[1] < 0.146879) {
        var11 = -0.026468849;
    } else {
        if (features[0] < 0.015459) {
            if (features[3] < 0.6619) {
                var11 = -0.045074683;
            } else {
                var11 = 0.016708976;
            }
        } else {
            if (features[0] < 0.024187) {
                var11 = 0.066762604;
            } else {
                var11 = 0.009375109;
            }
        }
    }
    double var12;
    if (features[4] < 0.02916) {
        if (features[6] < 1.044722) {
            if (features[3] < 0.6619) {
                var12 = 0.012171771;
            } else {
                var12 = 0.05302446;
            }
        } else {
            var12 = -0.0139549;
        }
    } else {
        if (features[6] < 0.922683) {
            if (features[4] < 0.032701) {
                var12 = -0.05697719;
            } else {
                var12 = -0.01609485;
            }
        } else {
            if (features[2] < 24.73) {
                var12 = -0.014588381;
            } else {
                var12 = 0.050508298;
            }
        }
    }
    double var13;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var13 = 0.033764265;
        } else {
            var13 = -0.052694548;
        }
    } else {
        if (features[0] < 0.015044) {
            if (features[0] < 0.012627) {
                var13 = 0.03532211;
            } else {
                var13 = -0.03182514;
            }
        } else {
            if (features[3] < 3.6854) {
                var13 = 0.052274805;
            } else {
                var13 = 0.0006144064;
            }
        }
    }
    double var14;
    if (features[0] < 0.017184) {
        if (features[6] < 0.773166) {
            if (features[2] < 20.4) {
                var14 = -0.024735851;
            } else {
                var14 = 0.045053475;
            }
        } else {
            if (features[0] < 0.012627) {
                var14 = 0.002499637;
            } else {
                var14 = -0.046820235;
            }
        }
    } else {
        if (features[1] < 0.142891) {
            var14 = -0.013360167;
        } else {
            if (features[1] < 0.173326) {
                var14 = 0.059521813;
            } else {
                var14 = 0.019226385;
            }
        }
    }
    double var15;
    if (features[3] < 0.6619) {
        if (features[3] < -0.5982) {
            if (features[1] < 0.185065) {
                var15 = 0.039216574;
            } else {
                var15 = -0.019322438;
            }
        } else {
            var15 = -0.040961552;
        }
    } else {
        if (features[1] < 0.146879) {
            var15 = -0.024710044;
        } else {
            if (features[4] < 0.014877) {
                var15 = 0.010133159;
            } else {
                var15 = 0.044861518;
            }
        }
    }
    double var16;
    if (features[0] < 0.015459) {
        if (features[0] < 0.011498) {
            var16 = 0.029861176;
        } else {
            if (features[5] < 0.010262) {
                var16 = 0.00871732;
            } else {
                var16 = -0.036033113;
            }
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[3] < -0.9407) {
                var16 = 0.008379034;
            } else {
                var16 = 0.053742893;
            }
        } else {
            if (features[3] < 4.4598) {
                var16 = -0.02564533;
            } else {
                var16 = 0.042253327;
            }
        }
    }
    double var17;
    if (features[2] < 20.4) {
        if (features[0] < 0.015459) {
            if (features[4] < 0.029745) {
                var17 = -0.011506939;
            } else {
                var17 = -0.050970178;
            }
        } else {
            var17 = 0.02310853;
        }
    } else {
        if (features[3] < -1.0946) {
            var17 = -0.00883749;
        } else {
            if (features[6] < 0.074475) {
                var17 = 0.0007514739;
            } else {
                var17 = 0.041932575;
            }
        }
    }
    double var18;
    if (features[0] < 0.015459) {
        if (features[4] < 0.027237) {
            if (features[4] < 0.013037) {
                var18 = -0.021989897;
            } else {
                var18 = 0.03754778;
            }
        } else {
            var18 = -0.0360896;
        }
    } else {
        if (features[1] < 0.146879) {
            var18 = -0.023934728;
        } else {
            if (features[0] < 0.022883) {
                var18 = 0.060597617;
            } else {
                var18 = 0.008845303;
            }
        }
    }
    double var19;
    if (features[2] < 25.66) {
        if (features[4] < 0.017453) {
            if (features[0] < 0.014969) {
                var19 = -0.0031525537;
            } else {
                var19 = 0.045092728;
            }
        } else {
            if (features[5] < 0.014423) {
                var19 = -0.051757574;
            } else {
                var19 = 0.028160086;
            }
        }
    } else {
        if (features[4] < 0.016342) {
            var19 = 0.0052493904;
        } else {
            if (features[2] < 42.02) {
                var19 = 0.05445334;
            } else {
                var19 = 0.016504094;
            }
        }
    }
    double var20;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[6] < 0.479061) {
                var20 = 0.030504365;
            } else {
                var20 = -0.0154794725;
            }
        } else {
            var20 = 0.056522895;
        }
    } else {
        if (features[1] < 0.208482) {
            if (features[6] < 0.915411) {
                var20 = 0.0041319896;
            } else {
                var20 = -0.044334937;
            }
        } else {
            if (features[0] < 0.015044) {
                var20 = -0.003446818;
            } else {
                var20 = 0.05063833;
            }
        }
    }
    double var21;
    if (features[1] < 0.170264) {
        if (features[3] < 3.5898) {
            var21 = 0.059307046;
        } else {
            var21 = -0.017348053;
        }
    } else {
        if (features[3] < 0.6619) {
            var21 = -0.048672255;
        } else {
            if (features[1] < 0.21151) {
                var21 = -0.0025676275;
            } else {
                var21 = 0.04000062;
            }
        }
    }
    double var22;
    if (features[4] < 0.005991) {
        var22 = 0.048862096;
    } else {
        if (features[0] < 0.015044) {
            if (features[0] < 0.012052) {
                var22 = 0.014153371;
            } else {
                var22 = -0.02938962;
            }
        } else {
            if (features[5] < 0.010245) {
                var22 = -0.015509519;
            } else {
                var22 = 0.03219767;
            }
        }
    }
    double var23;
    if (features[3] < 0.6619) {
        if (features[2] < 18.71) {
            var23 = -0.05110093;
        } else {
            if (features[2] < 23.0) {
                var23 = 0.021392804;
            } else {
                var23 = -0.015030891;
            }
        }
    } else {
        if (features[5] < 0.010031) {
            var23 = 0.04182063;
        } else {
            if (features[4] < 0.016342) {
                var23 = -0.01965425;
            } else {
                var23 = 0.021570046;
            }
        }
    }
    double var24;
    if (features[4] < 0.005991) {
        var24 = 0.052357923;
    } else {
        if (features[3] < 0.6619) {
            if (features[6] < 0.430133) {
                var24 = 0.012289303;
            } else {
                var24 = -0.046935856;
            }
        } else {
            if (features[1] < 0.146244) {
                var24 = -0.033043623;
            } else {
                var24 = 0.024334583;
            }
        }
    }
    double var25;
    if (features[3] < -0.9407) {
        var25 = -0.023592053;
    } else {
        if (features[5] < 0.016872) {
            if (features[3] < 3.6854) {
                var25 = 0.0410067;
            } else {
                var25 = -0.012952332;
            }
        } else {
            if (features[3] < 3.9337) {
                var25 = -0.029688736;
            } else {
                var25 = 0.025378412;
            }
        }
    }
    double var26;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var26 = 0.0077563818;
        } else {
            var26 = -0.035426494;
        }
    } else {
        if (features[1] < 0.146879) {
            var26 = -0.009553126;
        } else {
            if (features[1] < 0.173326) {
                var26 = 0.050006088;
            } else {
                var26 = 0.014500546;
            }
        }
    }
    double var27;
    if (features[0] < 0.015459) {
        if (features[0] < 0.012052) {
            var27 = 0.018572466;
        } else {
            if (features[6] < 0.673935) {
                var27 = -0.047348242;
            } else {
                var27 = -0.0010498557;
            }
        }
    } else {
        if (features[1] < 0.146879) {
            var27 = -0.0087950155;
        } else {
            if (features[6] < 0.915411) {
                var27 = 0.052671906;
            } else {
                var27 = 0.014581829;
            }
        }
    }
    double var28;
    if (features[0] < 0.027068) {
        if (features[0] < 0.015459) {
            if (features[5] < 0.010262) {
                var28 = 0.024815476;
            } else {
                var28 = -0.018875657;
            }
        } else {
            if (features[5] < 0.009506) {
                var28 = -0.0051663183;
            } else {
                var28 = 0.054886233;
            }
        }
    } else {
        var28 = -0.02907906;
    }
    double var29;
    if (features[4] < 0.005991) {
        var29 = 0.051722415;
    } else {
        if (features[2] < 39.27) {
            if (features[2] < 19.63) {
                var29 = -0.018041229;
            } else {
                var29 = 0.017952112;
            }
        } else {
            var29 = -0.0290418;
        }
    }
    double var30;
    if (features[3] < 0.6619) {
        if (features[0] < 0.013965) {
            var30 = -0.03385352;
        } else {
            var30 = 0.0071319784;
        }
    } else {
        if (features[1] < 0.146879) {
            var30 = -0.016024737;
        } else {
            if (features[3] < 2.5506) {
                var30 = 0.0118174525;
            } else {
                var30 = 0.048312858;
            }
        }
    }
    double var31;
    if (features[4] < 0.027338) {
        if (features[5] < 0.014904) {
            if (features[5] < 0.006938) {
                var31 = 0.007861978;
            } else {
                var31 = 0.046169724;
            }
        } else {
            if (features[5] < 0.017209) {
                var31 = -0.024547068;
            } else {
                var31 = 0.018383222;
            }
        }
    } else {
        if (features[0] < 0.014766) {
            var31 = -0.039879255;
        } else {
            if (features[0] < 0.027068) {
                var31 = 0.024828576;
            } else {
                var31 = -0.041949645;
            }
        }
    }
    double var32;
    if (features[1] < 0.146879) {
        if (features[3] < 2.9635) {
            var32 = 0.011666276;
        } else {
            var32 = -0.039168335;
        }
    } else {
        if (features[0] < 0.015044) {
            if (features[0] < 0.013096) {
                var32 = 0.016170716;
            } else {
                var32 = -0.033064056;
            }
        } else {
            var32 = 0.047610078;
        }
    }
    double var33;
    if (features[4] < 0.005991) {
        var33 = 0.049458362;
    } else {
        if (features[3] < 1.2888) {
            if (features[6] < 0.479061) {
                var33 = 0.009055557;
            } else {
                var33 = -0.03857358;
            }
        } else {
            if (features[4] < 0.031723) {
                var33 = -0.004670465;
            } else {
                var33 = 0.038691457;
            }
        }
    }
    double var34;
    if (features[3] < 0.6619) {
        if (features[3] < -0.5982) {
            if (features[1] < 0.185065) {
                var34 = 0.029266763;
            } else {
                var34 = -0.02146057;
            }
        } else {
            var34 = -0.047388908;
        }
    } else {
        if (features[1] < 0.146879) {
            var34 = -0.02124976;
        } else {
            if (features[1] < 0.170628) {
                var34 = 0.046905916;
            } else {
                var34 = 0.011538451;
            }
        }
    }
    double var35;
    if (features[4] < 0.008124) {
        var35 = 0.040514655;
    } else {
        if (features[3] < 0.6619) {
            if (features[6] < 0.430133) {
                var35 = 0.013721933;
            } else {
                var35 = -0.05188006;
            }
        } else {
            if (features[5] < 0.010031) {
                var35 = 0.039754145;
            } else {
                var35 = 0.0011111534;
            }
        }
    }
    double var36;
    if (features[4] < 0.006997) {
        var36 = 0.048369467;
    } else {
        if (features[0] < 0.015044) {
            if (features[0] < 0.013096) {
                var36 = 0.000020218698;
            } else {
                var36 = -0.039791238;
            }
        } else {
            if (features[0] < 0.022743) {
                var36 = 0.03676967;
            } else {
                var36 = -0.017356975;
            }
        }
    }
    double var37;
    if (features[3] < 0.6619) {
        if (features[3] < -0.5982) {
            if (features[0] < 0.013965) {
                var37 = -0.022931105;
            } else {
                var37 = 0.021113832;
            }
        } else {
            var37 = -0.048149463;
        }
    } else {
        if (features[0] < 0.019066) {
            if (features[0] < 0.012627) {
                var37 = 0.029342243;
            } else {
                var37 = -0.01869996;
            }
        } else {
            if (features[2] < 29.04) {
                var37 = 0.011289841;
            } else {
                var37 = 0.052230753;
            }
        }
    }
    double var38;
    if (features[4] < 0.005991) {
        var38 = 0.044369437;
    } else {
        if (features[2] < 48.67) {
            if (features[0] < 0.022743) {
                var38 = -0.00181097;
            } else {
                var38 = -0.048483748;
            }
        } else {
            var38 = 0.03522643;
        }
    }
    double var39;
    if (features[3] < 0.5167) {
        if (features[6] < 0.464117) {
            var39 = 0.023611197;
        } else {
            var39 = -0.04998336;
        }
    } else {
        if (features[1] < 0.146879) {
            var39 = -0.01670258;
        } else {
            if (features[3] < 1.2888) {
                var39 = 0.004611395;
            } else {
                var39 = 0.043764696;
            }
        }
    }
    double var40;
    if (features[1] < 0.173326) {
        if (features[3] < 3.5898) {
            var40 = 0.044641692;
        } else {
            var40 = -0.0035429501;
        }
    } else {
        if (features[1] < 0.18451) {
            var40 = -0.046272557;
        } else {
            if (features[3] < 1.113) {
                var40 = -0.009166832;
            } else {
                var40 = 0.031726796;
            }
        }
    }
    double var41;
    if (features[3] < 0.6619) {
        if (features[1] < 0.185065) {
            var41 = 0.006098583;
        } else {
            var41 = -0.031554703;
        }
    } else {
        if (features[1] < 0.21151) {
            if (features[5] < 0.010031) {
                var41 = 0.03183983;
            } else {
                var41 = -0.018523805;
            }
        } else {
            var41 = 0.035933796;
        }
    }
    double var42;
    if (features[0] < 0.015459) {
        if (features[3] < 2.5506) {
            if (features[5] < 0.011497) {
                var42 = -0.004729141;
            } else {
                var42 = -0.050276395;
            }
        } else {
            var42 = 0.0161781;
        }
    } else {
        if (features[4] < 0.038919) {
            if (features[5] < 0.006453) {
                var42 = -0.00065032364;
            } else {
                var42 = 0.05218764;
            }
        } else {
            if (features[4] < 0.042765) {
                var42 = -0.022912607;
            } else {
                var42 = 0.019337043;
            }
        }
    }
    double var43;
    if (features[4] < 0.005991) {
        var43 = 0.042764172;
    } else {
        if (features[5] < 0.018602) {
            if (features[2] < 29.04) {
                var43 = -0.0342727;
            } else {
                var43 = 0.006086769;
            }
        } else {
            if (features[2] < 39.27) {
                var43 = 0.029049927;
            } else {
                var43 = -0.012368422;
            }
        }
    }
    double var44;
    if (features[1] < 0.178826) {
        if (features[1] < 0.142491) {
            var44 = -0.0011037333;
        } else {
            var44 = 0.047729384;
        }
    } else {
        if (features[3] < 2.2315) {
            if (features[5] < 0.01516) {
                var44 = -0.0329711;
            } else {
                var44 = 0.0022844975;
            }
        } else {
            if (features[3] < 3.7611) {
                var44 = 0.0049883397;
            } else {
                var44 = 0.033993196;
            }
        }
    }
    double var45;
    if (features[0] < 0.017184) {
        if (features[0] < 0.012052) {
            var45 = 0.021198427;
        } else {
            if (features[3] < -0.5982) {
                var45 = 0.0030137699;
            } else {
                var45 = -0.041674126;
            }
        }
    } else {
        if (features[3] < 0.5167) {
            var45 = -0.0155305015;
        } else {
            if (features[6] < 0.108291) {
                var45 = -0.006579912;
            } else {
                var45 = 0.041673854;
            }
        }
    }
    double var46;
    if (features[4] < 0.005991) {
        var46 = 0.042835265;
    } else {
        if (features[3] < 1.2888) {
            if (features[6] < 0.479061) {
                var46 = 0.01748258;
            } else {
                var46 = -0.045143407;
            }
        } else {
            if (features[1] < 0.150823) {
                var46 = -0.023407528;
            } else {
                var46 = 0.029131878;
            }
        }
    }
    double var47;
    if (features[1] < 0.211673) {
        if (features[5] < 0.008222) {
            if (features[6] < 0.464117) {
                var47 = 0.038024865;
            } else {
                var47 = -0.005774045;
            }
        } else {
            if (features[0] < 0.012627) {
                var47 = 0.013782563;
            } else {
                var47 = -0.02795871;
            }
        }
    } else {
        if (features[0] < 0.013965) {
            var47 = 0.0037286978;
        } else {
            var47 = 0.044289645;
        }
    }
    double var48;
    if (features[2] < 36.93) {
        if (features[2] < 25.66) {
            if (features[2] < 24.19) {
                var48 = 0.013400043;
            } else {
                var48 = -0.038763028;
            }
        } else {
            var48 = 0.044328947;
        }
    } else {
        if (features[2] < 47.08) {
            var48 = -0.032731082;
        } else {
            var48 = 0.0052684424;
        }
    }
    double var49;
    if (features[4] < 0.005991) {
        var49 = 0.039590698;
    } else {
        if (features[4] < 0.041939) {
            if (features[2] < 21.12) {
                var49 = 0.006814173;
            } else {
                var49 = -0.02353638;
            }
        } else {
            if (features[6] < 0.766371) {
                var49 = 0.03396782;
            } else {
                var49 = -0.0063375467;
            }
        }
    }
    double var50;
    if (features[4] < 0.005991) {
        var50 = 0.04162863;
    } else {
        if (features[3] < 1.2888) {
            if (features[6] < 0.479061) {
                var50 = 0.0042341626;
            } else {
                var50 = -0.043939482;
            }
        } else {
            if (features[6] < 1.114548) {
                var50 = -0.0026358636;
            } else {
                var50 = 0.034423698;
            }
        }
    }
    double var51;
    if (features[4] < 0.008124) {
        var51 = 0.0382533;
    } else {
        if (features[5] < 0.018602) {
            if (features[1] < 0.234905) {
                var51 = -0.015013297;
            } else {
                var51 = 0.019568631;
            }
        } else {
            if (features[2] < 39.27) {
                var51 = 0.03857998;
            } else {
                var51 = -0.005335909;
            }
        }
    }
    double var52;
    if (features[3] < 1.2888) {
        if (features[4] < 0.012626) {
            var52 = 0.022786172;
        } else {
            if (features[6] < 0.4964) {
                var52 = 0.0067188605;
            } else {
                var52 = -0.038827375;
            }
        }
    } else {
        if (features[4] < 0.01227) {
            var52 = -0.0062672994;
        } else {
            if (features[3] < 3.815) {
                var52 = 0.0437338;
            } else {
                var52 = 0.002709155;
            }
        }
    }
    double var53;
    if (features[1] < 0.211673) {
        if (features[4] < 0.027338) {
            if (features[3] < 1.2888) {
                var53 = -0.0068795807;
            } else {
                var53 = 0.03676104;
            }
        } else {
            if (features[1] < 0.170628) {
                var53 = 0.00036489588;
            } else {
                var53 = -0.0334714;
            }
        }
    } else {
        var53 = 0.036141817;
    }
    double var54;
    if (features[6] < 0.36583) {
        var54 = -0.028262606;
    } else {
        if (features[6] < 0.464117) {
            var54 = 0.03989653;
        } else {
            if (features[5] < 0.01516) {
                var54 = -0.01970975;
            } else {
                var54 = 0.016077558;
            }
        }
    }
    double var55;
    if (features[0] < 0.015459) {
        if (features[0] < 0.011498) {
            var55 = 0.0083848;
        } else {
            if (features[2] < 25.02) {
                var55 = -0.00705625;
            } else {
                var55 = -0.036623895;
            }
        }
    } else {
        if (features[4] < 0.026537) {
            var55 = 0.046626393;
        } else {
            if (features[0] < 0.027068) {
                var55 = 0.018245839;
            } else {
                var55 = -0.018392598;
            }
        }
    }
    double var56;
    if (features[0] < 0.015459) {
        if (features[1] < 0.170264) {
            var56 = 0.020376595;
        } else {
            if (features[2] < 25.02) {
                var56 = -0.004470724;
            } else {
                var56 = -0.03993737;
            }
        }
    } else {
        if (features[1] < 0.146879) {
            var56 = -0.030705301;
        } else {
            if (features[0] < 0.024187) {
                var56 = 0.046880867;
            } else {
                var56 = 0.011957045;
            }
        }
    }
    double var57;
    if (features[3] < -0.9407) {
        var57 = -0.027132008;
    } else {
        if (features[2] < 24.19) {
            if (features[6] < 1.044722) {
                var57 = 0.046067934;
            } else {
                var57 = -0.002725432;
            }
        } else {
            if (features[4] < 0.022571) {
                var57 = -0.029012812;
            } else {
                var57 = 0.015116076;
            }
        }
    }
    double var58;
    if (features[6] < 0.074475) {
        var58 = -0.026320785;
    } else {
        if (features[2] < 42.35) {
            if (features[2] < 25.19) {
                var58 = 0.005187552;
            } else {
                var58 = 0.045775246;
            }
        } else {
            var58 = -0.021902034;
        }
    }
    double var59;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[1] < 0.13185) {
                var59 = 0.020947952;
            } else {
                var59 = -0.023602124;
            }
        } else {
            var59 = 0.04202953;
        }
    } else {
        if (features[1] < 0.21151) {
            if (features[1] < 0.181745) {
                var59 = -0.034156676;
            } else {
                var59 = -0.0043889196;
            }
        } else {
            if (features[5] < 0.016194) {
                var59 = 0.00097291154;
            } else {
                var59 = 0.030723045;
            }
        }
    }
    double var60;
    if (features[1] < 0.211673) {
        if (features[1] < 0.170628) {
            if (features[1] < 0.146879) {
                var60 = -0.01182198;
            } else {
                var60 = 0.03874257;
            }
        } else {
            if (features[5] < 0.014008) {
                var60 = -0.001894475;
            } else {
                var60 = -0.033984154;
            }
        }
    } else {
        if (features[1] < 0.238345) {
            var60 = 0.037920102;
        } else {
            var60 = 0.009362813;
        }
    }
    double var61;
    if (features[4] < 0.005991) {
        var61 = 0.03600382;
    } else {
        if (features[3] < -0.9407) {
            var61 = -0.027246295;
        } else {
            if (features[1] < 0.146879) {
                var61 = -0.017826859;
            } else {
                var61 = 0.010308215;
            }
        }
    }
    double var62;
    if (features[1] < 0.173326) {
        if (features[3] < 3.5898) {
            var62 = 0.045916103;
        } else {
            var62 = -0.03431865;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[5] < 0.007057) {
                var62 = 0.006872115;
            } else {
                var62 = -0.03725158;
            }
        } else {
            if (features[5] < 0.016194) {
                var62 = -0.011020383;
            } else {
                var62 = 0.031322952;
            }
        }
    }
    double var63;
    if (features[1] < 0.211673) {
        if (features[1] < 0.173326) {
            if (features[1] < 0.146879) {
                var63 = -0.006094898;
            } else {
                var63 = 0.041399214;
            }
        } else {
            if (features[0] < 0.013096) {
                var63 = 0.0037023795;
            } else {
                var63 = -0.05838554;
            }
        }
    } else {
        if (features[4] < 0.030596) {
            var63 = -0.0012824442;
        } else {
            var63 = 0.03770159;
        }
    }
    double var64;
    if (features[1] < 0.173326) {
        if (features[1] < 0.142891) {
            var64 = 0.00017653171;
        } else {
            var64 = 0.043068975;
        }
    } else {
        if (features[0] < 0.015044) {
            if (features[2] < 19.64) {
                var64 = -0.005978918;
            } else {
                var64 = -0.039858837;
            }
        } else {
            if (features[0] < 0.023982) {
                var64 = 0.027206734;
            } else {
                var64 = -0.033772346;
            }
        }
    }
    double var65;
    if (features[0] < 0.015459) {
        if (features[0] < 0.014185) {
            if (features[3] < -1.0946) {
                var65 = -0.018460555;
            } else {
                var65 = 0.012969312;
            }
        } else {
            var65 = -0.03205428;
        }
    } else {
        if (features[3] < 0.5167) {
            var65 = -0.00900614;
        } else {
            if (features[3] < 3.6854) {
                var65 = 0.03662162;
            } else {
                var65 = -0.0038258021;
            }
        }
    }
    double var66;
    if (features[4] < 0.005991) {
        var66 = 0.036023684;
    } else {
        if (features[3] < 0.6619) {
            if (features[2] < 22.07) {
                var66 = -0.042715024;
            } else {
                var66 = -0.001691263;
            }
        } else {
            if (features[1] < 0.146879) {
                var66 = -0.02841719;
            } else {
                var66 = 0.018065386;
            }
        }
    }
    double var67;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            var67 = 0.009925044;
        } else {
            var67 = 0.03785645;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[0] < 0.020623) {
                var67 = -0.0038896303;
            } else {
                var67 = -0.036379807;
            }
        } else {
            if (features[1] < 0.234226) {
                var67 = 0.03256887;
            } else {
                var67 = 0.001273758;
            }
        }
    }
    double var68;
    if (features[6] < 0.773166) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.479061) {
                var68 = 0.01395102;
            } else {
                var68 = -0.03929033;
            }
        } else {
            if (features[6] < 0.074475) {
                var68 = -0.013465258;
            } else {
                var68 = 0.03763267;
            }
        }
    } else {
        if (features[3] < 3.4124) {
            if (features[2] < 22.48) {
                var68 = -0.012891145;
            } else {
                var68 = -0.045715548;
            }
        } else {
            var68 = 0.010202582;
        }
    }
    double var69;
    if (features[3] < -0.9407) {
        var69 = -0.018446825;
    } else {
        if (features[3] < 3.6854) {
            if (features[5] < 0.014244) {
                var69 = 0.029211989;
            } else {
                var69 = -0.0042154524;
            }
        } else {
            if (features[2] < 38.59) {
                var69 = 0.009678814;
            } else {
                var69 = -0.02084219;
            }
        }
    }
    double var70;
    if (features[4] < 0.005991) {
        var70 = 0.034144145;
    } else {
        if (features[1] < 0.146879) {
            var70 = -0.021860635;
        } else {
            if (features[3] < 0.1623) {
                var70 = -0.017901637;
            } else {
                var70 = 0.018121827;
            }
        }
    }
    double var71;
    if (features[6] < 0.479061) {
        if (features[0] < 0.013965) {
            var71 = -0.004053641;
        } else {
            var71 = 0.036282495;
        }
    } else {
        if (features[3] < 0.5167) {
            var71 = -0.043059345;
        } else {
            if (features[3] < 3.0209) {
                var71 = 0.02372544;
            } else {
                var71 = -0.008255777;
            }
        }
    }
    double var72;
    if (features[1] < 0.211673) {
        if (features[4] < 0.02916) {
            if (features[6] < 0.773166) {
                var72 = 0.03226915;
            } else {
                var72 = -0.014298662;
            }
        } else {
            if (features[1] < 0.170628) {
                var72 = -0.009768395;
            } else {
                var72 = -0.042906743;
            }
        }
    } else {
        var72 = 0.03846247;
    }
    double var73;
    if (features[4] < 0.008124) {
        var73 = 0.02341228;
    } else {
        if (features[6] < 0.922683) {
            if (features[1] < 0.184677) {
                var73 = -0.033357546;
            } else {
                var73 = 0.004285078;
            }
        } else {
            if (features[1] < 0.2333) {
                var73 = 0.024771204;
            } else {
                var73 = -0.013553216;
            }
        }
    }
    double var74;
    if (features[5] < 0.014244) {
        if (features[2] < 24.61) {
            if (features[4] < 0.017453) {
                var74 = 0.035584573;
            } else {
                var74 = -0.02293328;
            }
        } else {
            var74 = 0.040855464;
        }
    } else {
        if (features[4] < 0.016342) {
            var74 = -0.021438314;
        } else {
            if (features[4] < 0.038919) {
                var74 = 0.028521404;
            } else {
                var74 = -0.007772927;
            }
        }
    }
    double var75;
    if (features[0] < 0.015044) {
        if (features[0] < 0.012052) {
            var75 = 0.01132986;
        } else {
            if (features[1] < 0.229795) {
                var75 = -0.009507065;
            } else {
                var75 = -0.041901287;
            }
        }
    } else {
        if (features[1] < 0.142891) {
            var75 = -0.022073928;
        } else {
            if (features[1] < 0.189594) {
                var75 = 0.040337358;
            } else {
                var75 = 0.008272812;
            }
        }
    }
    double var76;
    if (features[4] < 0.02916) {
        if (features[3] < 2.1855) {
            if (features[5] < 0.006938) {
                var76 = 0.0032515656;
            } else {
                var76 = 0.04152235;
            }
        } else {
            if (features[2] < 25.03) {
                var76 = -0.021638526;
            } else {
                var76 = 0.011534274;
            }
        }
    } else {
        if (features[0] < 0.014766) {
            var76 = -0.04482379;
        } else {
            if (features[0] < 0.027068) {
                var76 = 0.017582964;
            } else {
                var76 = -0.027697345;
            }
        }
    }
    double var77;
    if (features[6] < 0.479061) {
        if (features[1] < 0.189594) {
            var77 = 0.03698107;
        } else {
            var77 = 0.0067722886;
        }
    } else {
        if (features[0] < 0.017184) {
            if (features[0] < 0.012627) {
                var77 = 0.004007335;
            } else {
                var77 = -0.033600833;
            }
        } else {
            if (features[0] < 0.023353) {
                var77 = 0.036715373;
            } else {
                var77 = -0.015816296;
            }
        }
    }
    double var78;
    if (features[3] < 0.6619) {
        if (features[2] < 18.71) {
            var78 = -0.03456288;
        } else {
            var78 = 0.0005225215;
        }
    } else {
        if (features[2] < 39.27) {
            if (features[2] < 24.61) {
                var78 = 0.0045248843;
            } else {
                var78 = 0.03731558;
            }
        } else {
            if (features[2] < 47.08) {
                var78 = -0.036971875;
            } else {
                var78 = 0.016570374;
            }
        }
    }
    double var79;
    if (features[2] < 24.19) {
        if (features[4] < 0.020111) {
            if (features[1] < 0.181438) {
                var79 = 0.009440732;
            } else {
                var79 = 0.038457144;
            }
        } else {
            if (features[6] < 0.430133) {
                var79 = 0.012908486;
            } else {
                var79 = -0.023693813;
            }
        }
    } else {
        if (features[4] < 0.022571) {
            if (features[1] < 0.173326) {
                var79 = -0.0012685218;
            } else {
                var79 = -0.04795901;
            }
        } else {
            if (features[3] < 3.6683) {
                var79 = 0.028345807;
            } else {
                var79 = -0.011956818;
            }
        }
    }
    double var80;
    if (features[6] < 0.529138) {
        if (features[2] < 36.93) {
            var80 = 0.03194554;
        } else {
            var80 = -0.006657599;
        }
    } else {
        if (features[3] < 1.2888) {
            var80 = -0.023592886;
        } else {
            if (features[1] < 0.181438) {
                var80 = -0.01742039;
            } else {
                var80 = 0.022791332;
            }
        }
    }
    double var81;
    if (features[5] < 0.020424) {
        if (features[6] < 0.479061) {
            if (features[6] < 0.108291) {
                var81 = -0.015636122;
            } else {
                var81 = 0.039510574;
            }
        } else {
            if (features[3] < 0.5167) {
                var81 = -0.02917623;
            } else {
                var81 = 0.0012638173;
            }
        }
    } else {
        var81 = 0.030351585;
    }
    double var82;
    if (features[0] < 0.029132) {
        if (features[5] < 0.020424) {
            if (features[0] < 0.015044) {
                var82 = -0.031123629;
            } else {
                var82 = -0.0044159386;
            }
        } else {
            var82 = 0.014082273;
        }
    } else {
        var82 = 0.023142798;
    }
    double var83;
    if (features[4] < 0.027338) {
        if (features[3] < 1.2888) {
            if (features[4] < 0.012626) {
                var83 = 0.018839367;
            } else {
                var83 = -0.025533153;
            }
        } else {
            if (features[4] < 0.01227) {
                var83 = -0.0058959643;
            } else {
                var83 = 0.041387793;
            }
        }
    } else {
        if (features[5] < 0.014884) {
            if (features[5] < 0.010262) {
                var83 = -0.007444908;
            } else {
                var83 = -0.035640016;
            }
        } else {
            if (features[0] < 0.022883) {
                var83 = 0.028455079;
            } else {
                var83 = -0.020816315;
            }
        }
    }
    double var84;
    if (features[6] < 0.915411) {
        if (features[3] < 3.9895) {
            if (features[1] < 0.178826) {
                var84 = 0.040339097;
            } else {
                var84 = 0.0049630078;
            }
        } else {
            var84 = -0.018695947;
        }
    } else {
        if (features[3] < 3.2613) {
            if (features[2] < 25.02) {
                var84 = 0.0023973691;
            } else {
                var84 = -0.044551205;
            }
        } else {
            var84 = 0.01723966;
        }
    }
    double var85;
    if (features[3] < 0.6619) {
        if (features[0] < 0.015459) {
            var85 = -0.033532113;
        } else {
            var85 = -0.0044813524;
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[0] < 0.013204) {
                var85 = -0.0063966173;
            } else {
                var85 = 0.041363817;
            }
        } else {
            if (features[2] < 39.27) {
                var85 = 0.0041705975;
            } else {
                var85 = -0.031773057;
            }
        }
    }
    double var86;
    if (features[2] < 24.19) {
        if (features[0] < 0.013696) {
            if (features[4] < 0.027237) {
                var86 = 0.0134509085;
            } else {
                var86 = -0.020210238;
            }
        } else {
            var86 = 0.0320282;
        }
    } else {
        if (features[4] < 0.022571) {
            if (features[1] < 0.173326) {
                var86 = -0.0024508259;
            } else {
                var86 = -0.04585583;
            }
        } else {
            if (features[3] < 3.6854) {
                var86 = 0.023266718;
            } else {
                var86 = -0.023070356;
            }
        }
    }
    double var87;
    if (features[1] < 0.211673) {
        if (features[4] < 0.027338) {
            if (features[2] < 29.04) {
                var87 = -0.009946173;
            } else {
                var87 = 0.03661434;
            }
        } else {
            if (features[5] < 0.009656) {
                var87 = -0.0054285773;
            } else {
                var87 = -0.041675124;
            }
        }
    } else {
        if (features[3] < 0.6604) {
            var87 = -0.0021415583;
        } else {
            var87 = 0.038303796;
        }
    }
    double var88;
    if (features[1] < 0.146879) {
        if (features[3] < 2.9635) {
            var88 = 0.010641181;
        } else {
            var88 = -0.042236753;
        }
    } else {
        if (features[3] < 0.6619) {
            if (features[3] < -1.2253) {
                var88 = 0.0103821345;
            } else {
                var88 = -0.03760286;
            }
        } else {
            if (features[1] < 0.181438) {
                var88 = 0.006213074;
            } else {
                var88 = 0.042762186;
            }
        }
    }
    double var89;
    if (features[1] < 0.184677) {
        if (features[1] < 0.173326) {
            if (features[1] < 0.146879) {
                var89 = -0.01553686;
            } else {
                var89 = 0.03577131;
            }
        } else {
            var89 = -0.037179198;
        }
    } else {
        if (features[4] < 0.040461) {
            if (features[1] < 0.204366) {
                var89 = 0.020469394;
            } else {
                var89 = -0.01251701;
            }
        } else {
            var89 = 0.031108638;
        }
    }
    double var90;
    if (features[4] < 0.041939) {
        if (features[5] < 0.014904) {
            if (features[0] < 0.019066) {
                var90 = -0.010886006;
            } else {
                var90 = 0.02488223;
            }
        } else {
            if (features[3] < 3.7611) {
                var90 = -0.034278117;
            } else {
                var90 = 0.010858445;
            }
        }
    } else {
        var90 = 0.015664281;
    }
    double var91;
    if (features[4] < 0.008124) {
        var91 = 0.017037837;
    } else {
        if (features[5] < 0.018602) {
            if (features[2] < 29.04) {
                var91 = -0.029251361;
            } else {
                var91 = 0.0016271257;
            }
        } else {
            if (features[2] < 29.82) {
                var91 = 0.025177235;
            } else {
                var91 = -0.002527459;
            }
        }
    }
    double var92;
    if (features[4] < 0.027338) {
        if (features[2] < 21.12) {
            if (features[5] < 0.010031) {
                var92 = 0.004669111;
            } else {
                var92 = 0.034949705;
            }
        } else {
            if (features[4] < 0.020107) {
                var92 = -0.0181305;
            } else {
                var92 = 0.02028012;
            }
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[1] < 0.168867) {
                var92 = -0.010625885;
            } else {
                var92 = -0.03934153;
            }
        } else {
            var92 = 0.012383159;
        }
    }
    double var93;
    if (features[1] < 0.211673) {
        if (features[1] < 0.189594) {
            if (features[6] < 0.529138) {
                var93 = 0.027740462;
            } else {
                var93 = -0.010218869;
            }
        } else {
            var93 = -0.031714864;
        }
    } else {
        if (features[2] < 29.28) {
            var93 = 0.03974409;
        } else {
            var93 = -0.003239865;
        }
    }
    double var94;
    if (features[6] < 0.479061) {
        if (features[6] < 0.074475) {
            var94 = -0.005605311;
        } else {
            var94 = 0.039844874;
        }
    } else {
        if (features[0] < 0.017184) {
            if (features[0] < 0.012627) {
                var94 = 0.011858165;
            } else {
                var94 = -0.029907126;
            }
        } else {
            if (features[0] < 0.022743) {
                var94 = 0.03327393;
            } else {
                var94 = -0.0039152056;
            }
        }
    }
    double var95;
    if (features[1] < 0.146879) {
        var95 = -0.02111428;
    } else {
        if (features[1] < 0.173326) {
            var95 = 0.03452043;
        } else {
            if (features[1] < 0.211673) {
                var95 = -0.016792607;
            } else {
                var95 = 0.016161235;
            }
        }
    }
    double var96;
    if (features[1] < 0.21151) {
        if (features[1] < 0.182103) {
            if (features[2] < 38.59) {
                var96 = 0.012609708;
            } else {
                var96 = -0.024427326;
            }
        } else {
            if (features[5] < 0.011552) {
                var96 = -0.0074363584;
            } else {
                var96 = -0.033304777;
            }
        }
    } else {
        if (features[1] < 0.236536) {
            var96 = 0.030498533;
        } else {
            var96 = -0.005437302;
        }
    }
    double var97;
    if (features[1] < 0.211673) {
        if (features[4] < 0.027338) {
            if (features[2] < 29.04) {
                var97 = -0.01098546;
            } else {
                var97 = 0.035763912;
            }
        } else {
            if (features[5] < 0.010326) {
                var97 = 0.0016962219;
            } else {
                var97 = -0.037782427;
            }
        }
    } else {
        if (features[4] < 0.029851) {
            var97 = -0.005680086;
        } else {
            var97 = 0.032221854;
        }
    }
    double var98;
    if (features[0] < 0.024189) {
        if (features[1] < 0.146879) {
            var98 = -0.016009932;
        } else {
            if (features[0] < 0.015459) {
                var98 = 0.0018531055;
            } else {
                var98 = 0.03903038;
            }
        }
    } else {
        if (features[1] < 0.170628) {
            var98 = 0.0091198;
        } else {
            var98 = -0.039374005;
        }
    }
    double var99;
    if (features[4] < 0.006997) {
        var99 = 0.032736093;
    } else {
        if (features[2] < 47.08) {
            if (features[2] < 17.75) {
                var99 = 0.008325464;
            } else {
                var99 = -0.020107556;
            }
        } else {
            var99 = 0.0160979;
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
