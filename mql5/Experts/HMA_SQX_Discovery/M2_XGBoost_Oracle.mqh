//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| REGIMEN: Rolling Window 2024-2026 (Alta Volatilidad + ADX > 25) |
//| Generado por la Fabrica de Modelos Antigravity                   |
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
        if (features[3] < -0.5982) {
            if (features[1] < 0.185892) {
                var0 = 0.05;
            } else {
                var0 = -0.023076924;
            }
        } else {
            var0 = -0.06363636;
        }
    } else {
        if (features[3] < 3.7988) {
            if (features[2] < 38.93) {
                var0 = 0.07037037;
            } else {
                var0 = 0.020000001;
            }
        } else {
            if (features[3] < 3.9613) {
                var0 = -0.05;
            } else {
                var0 = 0.015789473;
            }
        }
    }
    double var1;
    if (features[1] < 0.173326) {
        if (features[2] < 38.93) {
            if (features[1] < 0.146879) {
                var1 = 0.026027897;
            } else {
                var1 = 0.074825004;
            }
        } else {
            var1 = 0.019422159;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[5] < 0.011373) {
                var1 = 0.010590518;
            } else {
                var1 = -0.05270682;
            }
        } else {
            if (features[4] < 0.055055) {
                var1 = 0.037682034;
            } else {
                var1 = -0.027078852;
            }
        }
    }
    double var2;
    if (features[1] < 0.173326) {
        if (features[0] < 0.033667) {
            var2 = 0.075950354;
        } else {
            if (features[0] < 0.042353) {
                var2 = -0.011957482;
            } else {
                var2 = 0.053156912;
            }
        }
    } else {
        if (features[1] < 0.234905) {
            if (features[3] < 1.113) {
                var2 = -0.053972602;
            } else {
                var2 = 0.0041343034;
            }
        } else {
            var2 = 0.062558845;
        }
    }
    double var3;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[2] < 27.52) {
                var3 = -0.02267334;
            } else {
                var3 = 0.059739966;
            }
        } else {
            if (features[2] < 38.93) {
                var3 = 0.07203786;
            } else {
                var3 = 0.017577022;
            }
        }
    } else {
        if (features[3] < 1.113) {
            if (features[1] < 0.206468) {
                var3 = -0.063169196;
            } else {
                var3 = -0.015415496;
            }
        } else {
            if (features[1] < 0.1861) {
                var3 = -0.027078344;
            } else {
                var3 = 0.040609132;
            }
        }
    }
    double var4;
    if (features[4] < 0.0606) {
        if (features[3] < 0.6619) {
            if (features[4] < 0.024373) {
                var4 = 0.030906403;
            } else {
                var4 = -0.033332486;
            }
        } else {
            if (features[0] < 0.028045) {
                var4 = 0.054857243;
            } else {
                var4 = 0.012938039;
            }
        }
    } else {
        if (features[2] < 41.23) {
            var4 = 0.0101360325;
        } else {
            var4 = -0.05460453;
        }
    }
    double var5;
    if (features[0] < 0.032832) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.479061) {
                var5 = 0.03081281;
            } else {
                var5 = -0.05234594;
            }
        } else {
            if (features[2] < 25.03) {
                var5 = 0.06301267;
            } else {
                var5 = 0.026861671;
            }
        }
    } else {
        if (features[3] < 3.7461) {
            if (features[4] < 0.000325) {
                var5 = 0.058491826;
            } else {
                var5 = -0.013760783;
            }
        } else {
            var5 = -0.05742553;
        }
    }
    double var6;
    if (features[3] < 4.5694) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.479061) {
                var6 = 0.030351168;
            } else {
                var6 = -0.03710897;
            }
        } else {
            if (features[0] < 0.033667) {
                var6 = 0.06015041;
            } else {
                var6 = 0.016696475;
            }
        }
    } else {
        var6 = -0.039570536;
    }
    double var7;
    if (features[0] < 0.032832) {
        if (features[3] < 0.3886) {
            if (features[0] < 0.017003) {
                var7 = 0.012182684;
            } else {
                var7 = -0.050245013;
            }
        } else {
            if (features[6] < 0.071689) {
                var7 = 0.00861054;
            } else {
                var7 = 0.05165198;
            }
        }
    } else {
        if (features[5] < 0.025545) {
            if (features[3] < 2.6256) {
                var7 = -0.009485357;
            } else {
                var7 = -0.06597322;
            }
        } else {
            var7 = 0.019676365;
        }
    }
    double var8;
    if (features[3] < 4.4055) {
        if (features[3] < 0.6619) {
            if (features[4] < 0.024373) {
                var8 = 0.020563506;
            } else {
                var8 = -0.06333892;
            }
        } else {
            if (features[3] < 3.522) {
                var8 = 0.03830029;
            } else {
                var8 = -0.0017436885;
            }
        }
    } else {
        var8 = -0.045478694;
    }
    double var9;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[4] < 0.009792) {
                var9 = 0.036487848;
            } else {
                var9 = -0.033607945;
            }
        } else {
            if (features[6] < 0.074475) {
                var9 = -0.014724654;
            } else {
                var9 = 0.044972047;
            }
        }
    } else {
        if (features[6] < 0.690268) {
            var9 = 0.018217115;
        } else {
            var9 = -0.05156032;
        }
    }
    double var10;
    if (features[3] < 0.6619) {
        if (features[2] < 16.95) {
            var10 = 0.0345597;
        } else {
            if (features[4] < 0.024373) {
                var10 = 0.0059235375;
            } else {
                var10 = -0.060997523;
            }
        }
    } else {
        if (features[3] < 3.7988) {
            if (features[6] < 0.074475) {
                var10 = 0.0064956914;
            } else {
                var10 = 0.05339575;
            }
        } else {
            if (features[2] < 42.61) {
                var10 = 0.016235122;
            } else {
                var10 = -0.043081913;
            }
        }
    }
    double var11;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[1] < 0.139201) {
                var11 = 0.026213465;
            } else {
                var11 = -0.016700089;
            }
        } else {
            var11 = 0.0547157;
        }
    } else {
        if (features[1] < 0.21151) {
            if (features[0] < 0.029075) {
                var11 = -0.011693194;
            } else {
                var11 = -0.06717946;
            }
        } else {
            if (features[0] < 0.040552) {
                var11 = 0.029774144;
            } else {
                var11 = -0.009887093;
            }
        }
    }
    double var12;
    if (features[1] < 0.173326) {
        if (features[3] < 3.7461) {
            if (features[1] < 0.142491) {
                var12 = 0.019064225;
            } else {
                var12 = 0.05582277;
            }
        } else {
            var12 = 0.00080154784;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[3] < 1.113) {
                var12 = -0.04722875;
            } else {
                var12 = -0.0034521415;
            }
        } else {
            if (features[4] < 0.047944) {
                var12 = 0.04393263;
            } else {
                var12 = -0.013169022;
            }
        }
    }
    double var13;
    if (features[6] < 1.245712) {
        if (features[0] < 0.032781) {
            if (features[3] < 0.6619) {
                var13 = -0.012255455;
            } else {
                var13 = 0.05017538;
            }
        } else {
            if (features[0] < 0.041052) {
                var13 = -0.036308166;
            } else {
                var13 = 0.023616608;
            }
        }
    } else {
        if (features[2] < 32.67) {
            var13 = -0.036098104;
        } else {
            var13 = -0.010122291;
        }
    }
    double var14;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[2] < 27.52) {
                var14 = -0.037582822;
            } else {
                var14 = 0.036824245;
            }
        } else {
            var14 = 0.055083204;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[0] < 0.023982) {
                var14 = -0.0004505796;
            } else {
                var14 = -0.053038564;
            }
        } else {
            if (features[4] < 0.060332) {
                var14 = 0.027514795;
            } else {
                var14 = -0.03380662;
            }
        }
    }
    double var15;
    if (features[1] < 0.170628) {
        if (features[1] < 0.146879) {
            if (features[2] < 27.52) {
                var15 = -0.02499826;
            } else {
                var15 = 0.029520933;
            }
        } else {
            var15 = 0.051862366;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[5] < 0.009808) {
                var15 = -0.0042536226;
            } else {
                var15 = -0.04626241;
            }
        } else {
            if (features[3] < -0.9407) {
                var15 = -0.026795784;
            } else {
                var15 = 0.022703547;
            }
        }
    }
    double var16;
    if (features[0] < 0.048898) {
        if (features[2] < 44.24) {
            if (features[0] < 0.01548) {
                var16 = -0.016162833;
            } else {
                var16 = 0.021971444;
            }
        } else {
            if (features[0] < 0.031081) {
                var16 = 0.012759422;
            } else {
                var16 = -0.059030097;
            }
        }
    } else {
        var16 = 0.050790984;
    }
    double var17;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[3] < -1.2873) {
                var17 = 0.030540586;
            } else {
                var17 = -0.041693;
            }
        } else {
            if (features[4] < 0.005752) {
                var17 = -0.007871141;
            } else {
                var17 = 0.041528624;
            }
        }
    } else {
        if (features[6] < 0.578296) {
            var17 = 0.017352795;
        } else {
            var17 = -0.05182436;
        }
    }
    double var18;
    if (features[1] < 0.173326) {
        if (features[6] < 0.742849) {
            if (features[1] < 0.143251) {
                var18 = 0.01409316;
            } else {
                var18 = 0.054592628;
            }
        } else {
            var18 = 0.0026269127;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[4] < 0.026537) {
                var18 = -0.00039715343;
            } else {
                var18 = -0.04334965;
            }
        } else {
            if (features[4] < 0.060332) {
                var18 = 0.022105524;
            } else {
                var18 = -0.029771388;
            }
        }
    }
    double var19;
    if (features[1] < 0.170628) {
        if (features[2] < 38.93) {
            var19 = 0.045854144;
        } else {
            var19 = -0.0024777683;
        }
    } else {
        if (features[1] < 0.234905) {
            if (features[2] < 28.5) {
                var19 = -0.003530084;
            } else {
                var19 = -0.04210438;
            }
        } else {
            if (features[1] < 0.275268) {
                var19 = 0.051969435;
            } else {
                var19 = 0.0014530513;
            }
        }
    }
    double var20;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[1] < 0.139201) {
                var20 = 0.029213628;
            } else {
                var20 = -0.029187528;
            }
        } else {
            var20 = 0.049613435;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[4] < 0.026537) {
                var20 = 0.011944801;
            } else {
                var20 = -0.040693164;
            }
        } else {
            if (features[0] < 0.01288) {
                var20 = -0.01568362;
            } else {
                var20 = 0.029870031;
            }
        }
    }
    double var21;
    if (features[1] < 0.170628) {
        if (features[3] < 3.7461) {
            if (features[2] < 24.58) {
                var21 = 0.014982298;
            } else {
                var21 = 0.048787247;
            }
        } else {
            var21 = -0.0052584377;
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[2] < 17.78) {
                var21 = -0.004296286;
            } else {
                var21 = -0.050579797;
            }
        } else {
            if (features[3] < 4.1438) {
                var21 = 0.041155186;
            } else {
                var21 = -0.04209549;
            }
        }
    }
    double var22;
    if (features[0] < 0.033667) {
        if (features[0] < 0.01548) {
            if (features[2] < 20.21) {
                var22 = -0.03588333;
            } else {
                var22 = 0.015340711;
            }
        } else {
            if (features[5] < 0.016255) {
                var22 = 0.053899284;
            } else {
                var22 = 0.007286499;
            }
        }
    } else {
        if (features[5] < 0.027517) {
            if (features[5] < 0.018909) {
                var22 = -0.0013878549;
            } else {
                var22 = -0.05682641;
            }
        } else {
            if (features[5] < 0.031586) {
                var22 = 0.046963204;
            } else {
                var22 = 0.0012587991;
            }
        }
    }
    double var23;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var23 = 0.020056155;
        } else {
            if (features[2] < 17.78) {
                var23 = -0.0038454928;
            } else {
                var23 = -0.050357085;
            }
        }
    } else {
        if (features[2] < 35.24) {
            if (features[4] < 0.042592) {
                var23 = 0.047763664;
            } else {
                var23 = 0.0007455934;
            }
        } else {
            if (features[4] < 0.031621) {
                var23 = -0.043294095;
            } else {
                var23 = 0.016376747;
            }
        }
    }
    double var24;
    if (features[1] < 0.170628) {
        if (features[3] < 3.7461) {
            if (features[1] < 0.143251) {
                var24 = 0.016097069;
            } else {
                var24 = 0.053298403;
            }
        } else {
            var24 = 0.0063060746;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[0] < 0.020463) {
                var24 = 0.0036079742;
            } else {
                var24 = -0.044665728;
            }
        } else {
            if (features[3] < 3.1043) {
                var24 = 0.039487004;
            } else {
                var24 = 0.00028290515;
            }
        }
    }
    double var25;
    if (features[5] < 0.016424) {
        if (features[0] < 0.015044) {
            if (features[5] < 0.010326) {
                var25 = 0.0028379052;
            } else {
                var25 = -0.03564496;
            }
        } else {
            if (features[0] < 0.024549) {
                var25 = 0.05480616;
            } else {
                var25 = 0.014119165;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[6] < 1.147066) {
                var25 = -0.009939565;
            } else {
                var25 = -0.05312712;
            }
        } else {
            if (features[6] < 0.911085) {
                var25 = -0.01985011;
            } else {
                var25 = 0.029364282;
            }
        }
    }
    double var26;
    if (features[0] < 0.024549) {
        if (features[0] < 0.01548) {
            if (features[2] < 20.21) {
                var26 = -0.046459004;
            } else {
                var26 = 0.013631083;
            }
        } else {
            if (features[6] < 1.011297) {
                var26 = 0.055020947;
            } else {
                var26 = 0.009814962;
            }
        }
    } else {
        if (features[0] < 0.041016) {
            if (features[6] < 0.923543) {
                var26 = -0.04468752;
            } else {
                var26 = 0.014215769;
            }
        } else {
            if (features[1] < 0.161453) {
                var26 = 0.0442571;
            } else {
                var26 = -0.0026624203;
            }
        }
    }
    double var27;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[2] < 27.52) {
                var27 = -0.029936448;
            } else {
                var27 = 0.02646488;
            }
        } else {
            var27 = 0.04355953;
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[2] < 32.47) {
                var27 = -0.002353422;
            } else {
                var27 = -0.043066334;
            }
        } else {
            if (features[4] < 0.058177) {
                var27 = 0.026666213;
            } else {
                var27 = -0.028151784;
            }
        }
    }
    double var28;
    if (features[5] < 0.013877) {
        if (features[3] < -1.0045) {
            var28 = -0.0016141552;
        } else {
            var28 = 0.050631206;
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[3] < 2.8294) {
                var28 = 0.008458572;
            } else {
                var28 = -0.033748057;
            }
        } else {
            if (features[2] < 28.5) {
                var28 = 0.04111257;
            } else {
                var28 = 0.0013877644;
            }
        }
    }
    double var29;
    if (features[2] < 43.81) {
        if (features[0] < 0.01288) {
            var29 = -0.024129823;
        } else {
            if (features[4] < 0.049127) {
                var29 = 0.011257939;
            } else {
                var29 = 0.051414575;
            }
        }
    } else {
        if (features[6] < 0.578296) {
            var29 = 0.02119934;
        } else {
            var29 = -0.04907136;
        }
    }
    double var30;
    if (features[3] < 4.5694) {
        if (features[3] < 0.3886) {
            if (features[1] < 0.160405) {
                var30 = 0.027659873;
            } else {
                var30 = -0.032591164;
            }
        } else {
            if (features[0] < 0.027068) {
                var30 = 0.032709252;
            } else {
                var30 = 0.002669796;
            }
        }
    } else {
        var30 = -0.03683896;
    }
    double var31;
    if (features[0] < 0.027068) {
        if (features[2] < 29.82) {
            if (features[4] < 0.013681) {
                var31 = 0.0419045;
            } else {
                var31 = -0.0088525675;
            }
        } else {
            var31 = 0.04952673;
        }
    } else {
        if (features[0] < 0.048898) {
            if (features[5] < 0.012496) {
                var31 = 0.02377083;
            } else {
                var31 = -0.028958231;
            }
        } else {
            var31 = 0.032210395;
        }
    }
    double var32;
    if (features[1] < 0.170443) {
        if (features[3] < 3.1552) {
            var32 = 0.041718096;
        } else {
            if (features[4] < 0.031621) {
                var32 = -0.014298843;
            } else {
                var32 = 0.017739713;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029075) {
                var32 = -0.0061869742;
            } else {
                var32 = -0.04334886;
            }
        } else {
            if (features[3] < 3.9337) {
                var32 = 0.0076130885;
            } else {
                var32 = 0.044456687;
            }
        }
    }
    double var33;
    if (features[0] < 0.042116) {
        if (features[0] < 0.032781) {
            if (features[3] < 0.6619) {
                var33 = -0.015351431;
            } else {
                var33 = 0.022118397;
            }
        } else {
            if (features[3] < 2.6256) {
                var33 = -0.006707827;
            } else {
                var33 = -0.047466513;
            }
        }
    } else {
        if (features[5] < 0.027517) {
            var33 = -0.012381927;
        } else {
            var33 = 0.04940603;
        }
    }
    double var34;
    if (features[3] < 3.6854) {
        if (features[5] < 0.024644) {
            if (features[4] < 0.013037) {
                var34 = 0.030260641;
            } else {
                var34 = -0.010794067;
            }
        } else {
            var34 = 0.042787295;
        }
    } else {
        if (features[4] < 0.031723) {
            var34 = -0.05198741;
        } else {
            if (features[5] < 0.024766) {
                var34 = 0.025999788;
            } else {
                var34 = -0.01343886;
            }
        }
    }
    double var35;
    if (features[6] < 0.649916) {
        if (features[6] < 0.074475) {
            if (features[1] < 0.21151) {
                var35 = -0.019443376;
            } else {
                var35 = 0.024267344;
            }
        } else {
            var35 = 0.046457525;
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[1] < 0.222827) {
                var35 = -0.04711067;
            } else {
                var35 = -0.0019662767;
            }
        } else {
            if (features[1] < 0.197933) {
                var35 = 0.0491158;
            } else {
                var35 = -0.009047871;
            }
        }
    }
    double var36;
    if (features[1] < 0.173326) {
        if (features[1] < 0.143251) {
            var36 = 0.0009440666;
        } else {
            var36 = 0.04213967;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[0] < 0.032832) {
                var36 = -0.013180837;
            } else {
                var36 = -0.055885345;
            }
        } else {
            if (features[0] < 0.021319) {
                var36 = -0.0020138354;
            } else {
                var36 = 0.021147713;
            }
        }
    }
    double var37;
    if (features[0] < 0.048898) {
        if (features[0] < 0.022883) {
            if (features[0] < 0.01548) {
                var37 = -0.018449007;
            } else {
                var37 = 0.028713206;
            }
        } else {
            if (features[1] < 0.286888) {
                var37 = -0.02496559;
            } else {
                var37 = 0.02702185;
            }
        }
    } else {
        var37 = 0.039949406;
    }
    double var38;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[2] < 27.52) {
                var38 = -0.042291727;
            } else {
                var38 = 0.027075201;
            }
        } else {
            if (features[2] < 37.19) {
                var38 = 0.046681177;
            } else {
                var38 = 0.013002291;
            }
        }
    } else {
        if (features[6] < 0.036636) {
            var38 = 0.019768225;
        } else {
            if (features[1] < 0.236536) {
                var38 = -0.028085146;
            } else {
                var38 = 0.002873984;
            }
        }
    }
    double var39;
    if (features[1] < 0.211673) {
        if (features[1] < 0.173326) {
            if (features[3] < 3.3576) {
                var39 = 0.024615776;
            } else {
                var39 = -0.012904017;
            }
        } else {
            if (features[3] < 1.113) {
                var39 = -0.05088812;
            } else {
                var39 = -0.005812149;
            }
        }
    } else {
        if (features[1] < 0.275268) {
            if (features[6] < 0.773166) {
                var39 = 0.04434769;
            } else {
                var39 = 0.009785803;
            }
        } else {
            var39 = -0.007854675;
        }
    }
    double var40;
    if (features[1] < 0.173326) {
        if (features[5] < 0.025545) {
            if (features[5] < 0.018909) {
                var40 = 0.03105909;
            } else {
                var40 = -0.040615045;
            }
        } else {
            var40 = 0.04427245;
        }
    } else {
        if (features[5] < 0.011552) {
            if (features[4] < 0.032701) {
                var40 = -0.00737396;
            } else {
                var40 = 0.043227796;
            }
        } else {
            if (features[5] < 0.019349) {
                var40 = -0.038162593;
            } else {
                var40 = 0.012934992;
            }
        }
    }
    double var41;
    if (features[5] < 0.013877) {
        if (features[4] < 0.026537) {
            var41 = 0.04682548;
        } else {
            if (features[4] < 0.032843) {
                var41 = -0.015275131;
            } else {
                var41 = 0.025500804;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[0] < 0.02159) {
                var41 = 0.0019377385;
            } else {
                var41 = -0.039176922;
            }
        } else {
            if (features[3] < 3.4124) {
                var41 = 0.040391117;
            } else {
                var41 = 0.0035351557;
            }
        }
    }
    double var42;
    if (features[5] < 0.013877) {
        if (features[0] < 0.013965) {
            var42 = -0.015618985;
        } else {
            if (features[3] < 0.6064) {
                var42 = 0.013127881;
            } else {
                var42 = 0.04621184;
            }
        }
    } else {
        if (features[4] < 0.031621) {
            if (features[1] < 0.195738) {
                var42 = -0.005697644;
            } else {
                var42 = -0.048922054;
            }
        } else {
            if (features[1] < 0.170628) {
                var42 = 0.037229266;
            } else {
                var42 = -0.004554864;
            }
        }
    }
    double var43;
    if (features[1] < 0.236536) {
        if (features[1] < 0.173326) {
            if (features[1] < 0.146879) {
                var43 = -0.014549551;
            } else {
                var43 = 0.037567925;
            }
        } else {
            if (features[0] < 0.023982) {
                var43 = 0.002324484;
            } else {
                var43 = -0.03518237;
            }
        }
    } else {
        if (features[1] < 0.275268) {
            var43 = 0.0419839;
        } else {
            var43 = -0.00037150676;
        }
    }
    double var44;
    if (features[5] < 0.015612) {
        if (features[0] < 0.013965) {
            var44 = -0.0024776321;
        } else {
            var44 = 0.041850004;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[5] < 0.027517) {
                var44 = -0.033785816;
            } else {
                var44 = 0.017296314;
            }
        } else {
            if (features[0] < 0.02844) {
                var44 = -0.0059027844;
            } else {
                var44 = 0.03327194;
            }
        }
    }
    double var45;
    if (features[0] < 0.027068) {
        if (features[0] < 0.01548) {
            if (features[2] < 20.21) {
                var45 = -0.03246588;
            } else {
                var45 = 0.0032753476;
            }
        } else {
            if (features[3] < 0.3886) {
                var45 = 0.00971447;
            } else {
                var45 = 0.052292556;
            }
        }
    } else {
        if (features[6] < 0.920198) {
            if (features[0] < 0.042116) {
                var45 = -0.048233982;
            } else {
                var45 = 0.0013707789;
            }
        } else {
            if (features[0] < 0.036723) {
                var45 = 0.03878524;
            } else {
                var45 = -0.009376702;
            }
        }
    }
    double var46;
    if (features[0] < 0.01548) {
        if (features[4] < 0.029745) {
            var46 = 0.0022302642;
        } else {
            var46 = -0.042110067;
        }
    } else {
        if (features[0] < 0.017479) {
            var46 = 0.04446435;
        } else {
            if (features[1] < 0.165671) {
                var46 = 0.016816195;
            } else {
                var46 = -0.013387077;
            }
        }
    }
    double var47;
    if (features[1] < 0.173326) {
        if (features[6] < 0.742849) {
            if (features[0] < 0.032781) {
                var47 = 0.044698913;
            } else {
                var47 = 0.015439256;
            }
        } else {
            var47 = -0.00031016069;
        }
    } else {
        if (features[5] < 0.031586) {
            if (features[1] < 0.193135) {
                var47 = -0.0302723;
            } else {
                var47 = 0.01493395;
            }
        } else {
            var47 = -0.044864815;
        }
    }
    double var48;
    if (features[3] < 3.6854) {
        if (features[3] < 0.6619) {
            if (features[3] < -0.0693) {
                var48 = 0.015178449;
            } else {
                var48 = -0.0425482;
            }
        } else {
            if (features[6] < 0.074475) {
                var48 = -0.0063092285;
            } else {
                var48 = 0.035817567;
            }
        }
    } else {
        if (features[3] < 3.9613) {
            var48 = -0.035262167;
        } else {
            if (features[3] < 4.3958) {
                var48 = 0.025411684;
            } else {
                var48 = -0.015766382;
            }
        }
    }
    double var49;
    if (features[1] < 0.236536) {
        if (features[1] < 0.173326) {
            if (features[5] < 0.025545) {
                var49 = -0.0029002286;
            } else {
                var49 = 0.039966326;
            }
        } else {
            if (features[1] < 0.193135) {
                var49 = -0.03448461;
            } else {
                var49 = -0.007876621;
            }
        }
    } else {
        if (features[4] < 0.050628) {
            var49 = 0.044562154;
        } else {
            var49 = 0.005083292;
        }
    }
    double var50;
    if (features[4] < 0.013681) {
        if (features[0] < 0.034536) {
            if (features[0] < 0.031081) {
                var50 = 0.039472166;
            } else {
                var50 = -0.031399738;
            }
        } else {
            var50 = 0.041739456;
        }
    } else {
        if (features[6] < 0.773166) {
            if (features[0] < 0.022883) {
                var50 = 0.02519011;
            } else {
                var50 = -0.016682148;
            }
        } else {
            if (features[6] < 0.920198) {
                var50 = -0.052810967;
            } else {
                var50 = -0.012390861;
            }
        }
    }
    double var51;
    if (features[1] < 0.173326) {
        if (features[5] < 0.025545) {
            if (features[5] < 0.018909) {
                var51 = 0.028696416;
            } else {
                var51 = -0.039144196;
            }
        } else {
            var51 = 0.03939785;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[5] < 0.011373) {
                var51 = 0.00513394;
            } else {
                var51 = -0.02598632;
            }
        } else {
            if (features[1] < 0.259479) {
                var51 = 0.034806114;
            } else {
                var51 = -0.008086872;
            }
        }
    }
    double var52;
    if (features[5] < 0.013877) {
        if (features[3] < 1.113) {
            if (features[6] < 0.479061) {
                var52 = 0.027683815;
            } else {
                var52 = -0.027525673;
            }
        } else {
            var52 = 0.04292514;
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[0] < 0.019231) {
                var52 = 0.01128833;
            } else {
                var52 = -0.038729258;
            }
        } else {
            if (features[0] < 0.018145) {
                var52 = -0.024911258;
            } else {
                var52 = 0.027001176;
            }
        }
    }
    double var53;
    if (features[1] < 0.236536) {
        if (features[1] < 0.197933) {
            if (features[2] < 43.81) {
                var53 = 0.018612068;
            } else {
                var53 = -0.017247273;
            }
        } else {
            if (features[4] < 0.041939) {
                var53 = -0.041501377;
            } else {
                var53 = -0.0008889829;
            }
        }
    } else {
        if (features[4] < 0.050628) {
            var53 = 0.041028593;
        } else {
            var53 = 0.0048024105;
        }
    }
    double var54;
    if (features[2] < 16.95) {
        var54 = 0.03235721;
    } else {
        if (features[0] < 0.04888) {
            if (features[0] < 0.032781) {
                var54 = 0.0016174726;
            } else {
                var54 = -0.027889157;
            }
        } else {
            var54 = 0.02596883;
        }
    }
    double var55;
    if (features[0] < 0.048898) {
        if (features[0] < 0.027068) {
            if (features[6] < 1.144717) {
                var55 = 0.018997684;
            } else {
                var55 = -0.03740602;
            }
        } else {
            if (features[6] < 1.114548) {
                var55 = -0.036153093;
            } else {
                var55 = 0.025024;
            }
        }
    } else {
        var55 = 0.02534693;
    }
    double var56;
    if (features[1] < 0.236536) {
        if (features[2] < 24.19) {
            if (features[3] < -1.0045) {
                var56 = 0.00096725096;
            } else {
                var56 = 0.03549195;
            }
        } else {
            if (features[1] < 0.141631) {
                var56 = 0.028073564;
            } else {
                var56 = -0.026518062;
            }
        }
    } else {
        if (features[3] < 2.2372) {
            var56 = -0.0030480619;
        } else {
            var56 = 0.046925794;
        }
    }
    double var57;
    if (features[6] < 0.578296) {
        if (features[4] < 0.02916) {
            if (features[0] < 0.024549) {
                var57 = 0.043752845;
            } else {
                var57 = 0.008635273;
            }
        } else {
            if (features[2] < 39.76) {
                var57 = -0.022542765;
            } else {
                var57 = 0.023375312;
            }
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[4] < 0.032701) {
                var57 = -0.045029886;
            } else {
                var57 = -0.00482444;
            }
        } else {
            if (features[3] < 4.4055) {
                var57 = 0.024935797;
            } else {
                var57 = -0.02350027;
            }
        }
    }
    double var58;
    if (features[3] < 2.8294) {
        if (features[0] < 0.01288) {
            var58 = -0.019314097;
        } else {
            if (features[6] < 0.074475) {
                var58 = -0.019164069;
            } else {
                var58 = 0.03831626;
            }
        }
    } else {
        if (features[2] < 24.73) {
            var58 = 0.035441097;
        } else {
            if (features[4] < 0.041939) {
                var58 = -0.039271332;
            } else {
                var58 = 0.007945609;
            }
        }
    }
    double var59;
    if (features[1] < 0.197933) {
        if (features[0] < 0.033667) {
            if (features[5] < 0.010838) {
                var59 = 0.014542681;
            } else {
                var59 = 0.041764718;
            }
        } else {
            if (features[5] < 0.024235) {
                var59 = -0.02786668;
            } else {
                var59 = 0.023215702;
            }
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[5] < 0.015612) {
                var59 = 0.0105330525;
            } else {
                var59 = -0.062563114;
            }
        } else {
            if (features[3] < 1.9315) {
                var59 = -0.022922015;
            } else {
                var59 = 0.044134278;
            }
        }
    }
    double var60;
    if (features[0] < 0.01548) {
        if (features[4] < 0.029745) {
            var60 = 0.006681643;
        } else {
            var60 = -0.042202886;
        }
    } else {
        if (features[0] < 0.017363) {
            var60 = 0.039539985;
        } else {
            if (features[1] < 0.236536) {
                var60 = -0.009010197;
            } else {
                var60 = 0.03163773;
            }
        }
    }
    double var61;
    if (features[2] < 16.87) {
        var61 = 0.039116513;
    } else {
        if (features[1] < 0.236536) {
            if (features[1] < 0.182103) {
                var61 = 0.014847832;
            } else {
                var61 = -0.027632305;
            }
        } else {
            if (features[3] < 1.9315) {
                var61 = -0.0075408653;
            } else {
                var61 = 0.043894015;
            }
        }
    }
    double var62;
    if (features[1] < 0.170628) {
        if (features[5] < 0.025545) {
            if (features[5] < 0.018909) {
                var62 = 0.013108501;
            } else {
                var62 = -0.035243485;
            }
        } else {
            var62 = 0.038706113;
        }
    } else {
        if (features[5] < 0.013877) {
            var62 = 0.017673574;
        } else {
            if (features[2] < 26.79) {
                var62 = 0.004689961;
            } else {
                var62 = -0.031426076;
            }
        }
    }
    double var63;
    if (features[1] < 0.170628) {
        if (features[3] < 3.7461) {
            if (features[6] < 0.522462) {
                var63 = 0.00030945585;
            } else {
                var63 = 0.032801893;
            }
        } else {
            var63 = -0.01245239;
        }
    } else {
        if (features[1] < 0.234905) {
            if (features[0] < 0.029075) {
                var63 = -0.0024994174;
            } else {
                var63 = -0.048632484;
            }
        } else {
            if (features[1] < 0.275268) {
                var63 = 0.03685884;
            } else {
                var63 = -0.011799071;
            }
        }
    }
    double var64;
    if (features[1] < 0.173326) {
        if (features[1] < 0.143251) {
            var64 = -0.0017556824;
        } else {
            var64 = 0.042512503;
        }
    } else {
        if (features[2] < 17.75) {
            var64 = 0.024837997;
        } else {
            if (features[3] < 1.113) {
                var64 = -0.03566392;
            } else {
                var64 = 0.0009083071;
            }
        }
    }
    double var65;
    if (features[6] < 0.479061) {
        if (features[0] < 0.027068) {
            var65 = 0.042698584;
        } else {
            if (features[0] < 0.039028) {
                var65 = -0.02264533;
            } else {
                var65 = 0.015245465;
            }
        }
    } else {
        if (features[3] < 0.6064) {
            if (features[6] < 0.994769) {
                var65 = -0.04460473;
            } else {
                var65 = -0.01264594;
            }
        } else {
            if (features[3] < 2.8426) {
                var65 = 0.04647277;
            } else {
                var65 = -0.008287875;
            }
        }
    }
    double var66;
    if (features[3] < 3.7988) {
        if (features[2] < 38.93) {
            if (features[2] < 20.4) {
                var66 = 0.0002929371;
            } else {
                var66 = 0.032216407;
            }
        } else {
            if (features[1] < 0.179458) {
                var66 = -0.016991446;
            } else {
                var66 = 0.0073703225;
            }
        }
    } else {
        if (features[3] < 3.9903) {
            var66 = -0.03740314;
        } else {
            if (features[3] < 4.6507) {
                var66 = 0.015576281;
            } else {
                var66 = -0.013170182;
            }
        }
    }
    double var67;
    if (features[1] < 0.173326) {
        if (features[5] < 0.025545) {
            if (features[5] < 0.017934) {
                var67 = 0.020626247;
            } else {
                var67 = -0.03507787;
            }
        } else {
            var67 = 0.03708417;
        }
    } else {
        if (features[5] < 0.031586) {
            if (features[5] < 0.019349) {
                var67 = -0.014414345;
            } else {
                var67 = 0.03083447;
            }
        } else {
            var67 = -0.043533284;
        }
    }
    double var68;
    if (features[6] < 0.649916) {
        if (features[3] < 2.4056) {
            if (features[3] < -0.0693) {
                var68 = 0.026041267;
            } else {
                var68 = -0.018034508;
            }
        } else {
            if (features[0] < 0.027068) {
                var68 = 0.038143393;
            } else {
                var68 = 0.00628568;
            }
        }
    } else {
        if (features[6] < 0.923543) {
            if (features[6] < 0.773166) {
                var68 = -0.007090613;
            } else {
                var68 = -0.04507594;
            }
        } else {
            if (features[6] < 1.147066) {
                var68 = 0.023278072;
            } else {
                var68 = -0.015841914;
            }
        }
    }
    double var69;
    if (features[5] < 0.020334) {
        if (features[5] < 0.015186) {
            if (features[0] < 0.015044) {
                var69 = -0.02695026;
            } else {
                var69 = 0.032618847;
            }
        } else {
            if (features[0] < 0.034536) {
                var69 = -0.029272845;
            } else {
                var69 = 0.00929923;
            }
        }
    } else {
        if (features[3] < 3.6854) {
            var69 = 0.046472684;
        } else {
            if (features[3] < 4.3576) {
                var69 = -0.015530281;
            } else {
                var69 = 0.024616824;
            }
        }
    }
    double var70;
    if (features[1] < 0.207449) {
        if (features[1] < 0.170628) {
            if (features[6] < 0.736291) {
                var70 = 0.025089664;
            } else {
                var70 = -0.0078052296;
            }
        } else {
            if (features[4] < 0.01227) {
                var70 = 0.0007692263;
            } else {
                var70 = -0.048355874;
            }
        }
    } else {
        if (features[1] < 0.311264) {
            if (features[2] < 27.03) {
                var70 = 0.04548486;
            } else {
                var70 = 0.0047399327;
            }
        } else {
            var70 = -0.017876554;
        }
    }
    double var71;
    if (features[3] < 1.113) {
        if (features[0] < 0.023456) {
            if (features[3] < -0.5982) {
                var71 = -0.012511988;
            } else {
                var71 = -0.041753303;
            }
        } else {
            var71 = 0.007434697;
        }
    } else {
        if (features[0] < 0.027068) {
            if (features[6] < 0.773166) {
                var71 = 0.044317644;
            } else {
                var71 = -0.0024630798;
            }
        } else {
            if (features[5] < 0.023757) {
                var71 = -0.045455053;
            } else {
                var71 = 0.02092989;
            }
        }
    }
    double var72;
    if (features[4] < 0.031723) {
        if (features[4] < 0.013681) {
            if (features[2] < 26.89) {
                var72 = 0.03771573;
            } else {
                var72 = -0.014144628;
            }
        } else {
            if (features[2] < 21.12) {
                var72 = -0.009139491;
            } else {
                var72 = -0.044352476;
            }
        }
    } else {
        if (features[2] < 20.4) {
            var72 = -0.022614317;
        } else {
            if (features[4] < 0.047944) {
                var72 = 0.037522875;
            } else {
                var72 = -0.004442458;
            }
        }
    }
    double var73;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            var73 = 0.018291768;
        } else {
            var73 = -0.037030302;
        }
    } else {
        if (features[3] < 3.7988) {
            if (features[3] < 3.0209) {
                var73 = 0.04106401;
            } else {
                var73 = 0.014146589;
            }
        } else {
            if (features[3] < 3.9613) {
                var73 = -0.036126837;
            } else {
                var73 = 0.011398753;
            }
        }
    }
    double var74;
    if (features[4] < 0.032701) {
        if (features[4] < 0.024373) {
            if (features[2] < 26.79) {
                var74 = 0.038409192;
            } else {
                var74 = -0.018787796;
            }
        } else {
            var74 = -0.042935353;
        }
    } else {
        if (features[2] < 44.24) {
            if (features[1] < 0.2333) {
                var74 = 0.03371205;
            } else {
                var74 = -0.0059212786;
            }
        } else {
            var74 = -0.0152486665;
        }
    }
    double var75;
    if (features[1] < 0.236536) {
        if (features[1] < 0.173326) {
            if (features[4] < 0.031621) {
                var75 = 0.0000017951678;
            } else {
                var75 = 0.034429416;
            }
        } else {
            if (features[0] < 0.029075) {
                var75 = 0.0034772586;
            } else {
                var75 = -0.033202685;
            }
        }
    } else {
        if (features[6] < 1.053773) {
            var75 = 0.005216085;
        } else {
            var75 = 0.038809802;
        }
    }
    double var76;
    if (features[0] < 0.022883) {
        if (features[0] < 0.01548) {
            if (features[5] < 0.013877) {
                var76 = -0.0008079745;
            } else {
                var76 = -0.009229333;
            }
        } else {
            var76 = 0.0310351;
        }
    } else {
        if (features[0] < 0.034536) {
            if (features[2] < 42.02) {
                var76 = -0.038630392;
            } else {
                var76 = 0.0154681895;
            }
        } else {
            if (features[2] < 35.24) {
                var76 = 0.043553095;
            } else {
                var76 = -0.01429228;
            }
        }
    }
    double var77;
    if (features[0] < 0.01288) {
        var77 = -0.020550763;
    } else {
        if (features[1] < 0.236536) {
            if (features[2] < 20.08) {
                var77 = 0.029199922;
            } else {
                var77 = -0.00301771;
            }
        } else {
            var77 = 0.033734955;
        }
    }
    double var78;
    if (features[3] < 3.7988) {
        if (features[3] < 1.9315) {
            if (features[4] < 0.020111) {
                var78 = 0.024810478;
            } else {
                var78 = -0.03247076;
            }
        } else {
            if (features[0] < 0.032832) {
                var78 = 0.03973974;
            } else {
                var78 = 0.00762257;
            }
        }
    } else {
        if (features[4] < 0.031723) {
            var78 = -0.036627535;
        } else {
            if (features[5] < 0.024085) {
                var78 = 0.020139836;
            } else {
                var78 = -0.012861622;
            }
        }
    }
    double var79;
    if (features[3] < 0.6619) {
        if (features[3] < -0.0693) {
            if (features[6] < 0.562075) {
                var79 = 0.03020813;
            } else {
                var79 = -0.015886985;
            }
        } else {
            var79 = -0.040142827;
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[6] < 0.074475) {
                var79 = -0.009771552;
            } else {
                var79 = 0.03178495;
            }
        } else {
            if (features[6] < 0.649832) {
                var79 = 0.012317375;
            } else {
                var79 = -0.023292663;
            }
        }
    }
    double var80;
    if (features[1] < 0.236536) {
        if (features[1] < 0.174813) {
            if (features[1] < 0.143251) {
                var80 = -0.007411968;
            } else {
                var80 = 0.03174816;
            }
        } else {
            if (features[6] < 0.036636) {
                var80 = 0.010842194;
            } else {
                var80 = -0.021609182;
            }
        }
    } else {
        var80 = 0.03643076;
    }
    double var81;
    if (features[4] < 0.013037) {
        if (features[2] < 28.26) {
            var81 = 0.041240875;
        } else {
            var81 = -0.006701027;
        }
    } else {
        if (features[4] < 0.049573) {
            if (features[3] < 3.9613) {
                var81 = -0.021758894;
            } else {
                var81 = 0.013556178;
            }
        } else {
            if (features[2] < 43.81) {
                var81 = 0.032720264;
            } else {
                var81 = -0.010701224;
            }
        }
    }
    double var82;
    if (features[0] < 0.032832) {
        if (features[5] < 0.027876) {
            if (features[0] < 0.01548) {
                var82 = -0.0009412802;
            } else {
                var82 = 0.041187126;
            }
        } else {
            var82 = -0.017502261;
        }
    } else {
        if (features[5] < 0.027517) {
            if (features[1] < 0.1861) {
                var82 = -0.04116242;
            } else {
                var82 = -0.001490794;
            }
        } else {
            if (features[5] < 0.034106) {
                var82 = 0.03647256;
            } else {
                var82 = -0.008179218;
            }
        }
    }
    double var83;
    if (features[3] < 0.6619) {
        if (features[3] < -1.2873) {
            var83 = 0.008333477;
        } else {
            var83 = -0.040043283;
        }
    } else {
        if (features[0] < 0.032832) {
            if (features[3] < 1.9315) {
                var83 = 0.00079921057;
            } else {
                var83 = 0.038096704;
            }
        } else {
            if (features[5] < 0.027517) {
                var83 = -0.028819397;
            } else {
                var83 = 0.017847987;
            }
        }
    }
    double var84;
    if (features[6] < 0.736291) {
        if (features[2] < 40.4) {
            if (features[3] < -0.0693) {
                var84 = 0.026511136;
            } else {
                var84 = -0.018047674;
            }
        } else {
            var84 = 0.025365327;
        }
    } else {
        if (features[6] < 0.923543) {
            var84 = -0.048746683;
        } else {
            if (features[3] < 4.0393) {
                var84 = 0.008743121;
            } else {
                var84 = -0.035801243;
            }
        }
    }
    double var85;
    if (features[4] < 0.049573) {
        if (features[5] < 0.015612) {
            if (features[3] < 0.2856) {
                var85 = -0.016485592;
            } else {
                var85 = 0.03023887;
            }
        } else {
            if (features[4] < -0.008698) {
                var85 = 0.017777627;
            } else {
                var85 = -0.037530567;
            }
        }
    } else {
        if (features[2] < 47.35) {
            var85 = 0.03328646;
        } else {
            var85 = -0.021002274;
        }
    }
    double var86;
    if (features[1] < 0.236536) {
        if (features[2] < 16.95) {
            var86 = 0.023950417;
        } else {
            if (features[1] < 0.170443) {
                var86 = 0.0027340145;
            } else {
                var86 = -0.02699392;
            }
        }
    } else {
        if (features[3] < 2.6256) {
            var86 = -0.0031068025;
        } else {
            var86 = 0.03460561;
        }
    }
    double var87;
    if (features[5] < 0.019349) {
        if (features[5] < 0.016424) {
            if (features[2] < 27.52) {
                var87 = -0.009633702;
            } else {
                var87 = 0.027237028;
            }
        } else {
            if (features[1] < 0.192445) {
                var87 = -0.010075315;
            } else {
                var87 = -0.050779093;
            }
        }
    } else {
        if (features[5] < 0.031586) {
            if (features[1] < 0.187603) {
                var87 = -0.0045660394;
            } else {
                var87 = 0.034631394;
            }
        } else {
            if (features[3] < 3.6854) {
                var87 = 0.023381298;
            } else {
                var87 = -0.042864185;
            }
        }
    }
    double var88;
    if (features[1] < 0.236536) {
        if (features[4] < 0.013681) {
            if (features[6] < 0.619303) {
                var88 = 0.03378032;
            } else {
                var88 = -0.0037879094;
            }
        } else {
            if (features[4] < 0.041939) {
                var88 = -0.031472478;
            } else {
                var88 = 0.0075822645;
            }
        }
    } else {
        if (features[4] < 0.047944) {
            var88 = 0.03245912;
        } else {
            var88 = 0.0048199506;
        }
    }
    double var89;
    if (features[4] < 0.013681) {
        if (features[3] < 2.8426) {
            var89 = 0.029352928;
        } else {
            var89 = -0.00822012;
        }
    } else {
        if (features[3] < 1.113) {
            if (features[1] < 0.189394) {
                var89 = -0.0008482921;
            } else {
                var89 = -0.037545603;
            }
        } else {
            if (features[6] < 0.773166) {
                var89 = 0.02721993;
            } else {
                var89 = -0.012208219;
            }
        }
    }
    double var90;
    if (features[0] < 0.032832) {
        if (features[3] < 1.113) {
            if (features[6] < 0.479061) {
                var90 = 0.019797646;
            } else {
                var90 = -0.038805675;
            }
        } else {
            if (features[0] < 0.018001) {
                var90 = 0.0006805686;
            } else {
                var90 = 0.036307096;
            }
        }
    } else {
        if (features[6] < 1.053773) {
            if (features[6] < 0.619303) {
                var90 = -0.0047330926;
            } else {
                var90 = -0.042341933;
            }
        } else {
            var90 = 0.020632206;
        }
    }
    double var91;
    if (features[2] < 17.75) {
        var91 = 0.026808864;
    } else {
        if (features[3] < 0.6619) {
            if (features[4] < 0.024373) {
                var91 = 0.0030621197;
            } else {
                var91 = -0.04027554;
            }
        } else {
            if (features[3] < 3.0209) {
                var91 = 0.02991256;
            } else {
                var91 = -0.00428562;
            }
        }
    }
    double var92;
    if (features[3] < 1.9315) {
        if (features[1] < 0.170443) {
            var92 = 0.015490435;
        } else {
            if (features[5] < 0.019349) {
                var92 = -0.043661617;
            } else {
                var92 = 0.003590811;
            }
        }
    } else {
        if (features[3] < 4.4055) {
            if (features[1] < 0.179458) {
                var92 = -0.006906354;
            } else {
                var92 = 0.034514796;
            }
        } else {
            var92 = -0.029631674;
        }
    }
    double var93;
    if (features[3] < 2.8426) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.479061) {
                var93 = 0.024883363;
            } else {
                var93 = -0.030672539;
            }
        } else {
            if (features[6] < 0.456478) {
                var93 = -0.008653417;
            } else {
                var93 = 0.040652286;
            }
        }
    } else {
        if (features[3] < 3.9613) {
            if (features[6] < 0.923543) {
                var93 = -0.034940075;
            } else {
                var93 = -0.0023559185;
            }
        } else {
            if (features[3] < 4.4055) {
                var93 = 0.028781762;
            } else {
                var93 = -0.01966419;
            }
        }
    }
    double var94;
    if (features[0] < 0.01548) {
        if (features[4] < 0.029745) {
            var94 = 0.008095972;
        } else {
            var94 = -0.033048358;
        }
    } else {
        if (features[2] < 27.03) {
            if (features[1] < 0.155639) {
                var94 = -0.008008555;
            } else {
                var94 = 0.039768893;
            }
        } else {
            if (features[4] < 0.041939) {
                var94 = -0.010962889;
            } else {
                var94 = 0.009998934;
            }
        }
    }
    double var95;
    if (features[1] < 0.197933) {
        if (features[6] < 0.949182) {
            if (features[3] < -0.0693) {
                var95 = 0.027486136;
            } else {
                var95 = -0.009721114;
            }
        } else {
            var95 = 0.03242214;
        }
    } else {
        if (features[5] < 0.031517) {
            if (features[5] < 0.019235) {
                var95 = -0.011301912;
            } else {
                var95 = 0.027160129;
            }
        } else {
            var95 = -0.026836349;
        }
    }
    double var96;
    if (features[2] < 17.75) {
        var96 = 0.028258508;
    } else {
        if (features[2] < 20.4) {
            var96 = -0.027645273;
        } else {
            if (features[1] < 0.173326) {
                var96 = 0.021916116;
            } else {
                var96 = -0.0037839622;
            }
        }
    }
    double var97;
    if (features[5] < 0.013877) {
        if (features[4] < 0.026537) {
            var97 = 0.036556378;
        } else {
            if (features[4] < 0.032843) {
                var97 = -0.01977327;
            } else {
                var97 = 0.020716416;
            }
        }
    } else {
        if (features[4] < -0.008698) {
            var97 = 0.023194848;
        } else {
            if (features[5] < 0.019235) {
                var97 = -0.028760985;
            } else {
                var97 = -0.001666453;
            }
        }
    }
    double var98;
    if (features[5] < 0.031586) {
        if (features[1] < 0.193135) {
            if (features[4] < 0.018382) {
                var98 = 0.019353068;
            } else {
                var98 = -0.015535988;
            }
        } else {
            if (features[0] < 0.01548) {
                var98 = -0.011209946;
            } else {
                var98 = 0.03743743;
            }
        }
    } else {
        var98 = -0.02162233;
    }
    double var99;
    if (features[2] < 17.16) {
        var99 = 0.02638097;
    } else {
        if (features[1] < 0.173326) {
            if (features[5] < 0.025545) {
                var99 = -0.0033807538;
            } else {
                var99 = 0.031051276;
            }
        } else {
            if (features[1] < 0.236536) {
                var99 = -0.019630479;
            } else {
                var99 = 0.010492278;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
