//+------------------------------------------------------------------+
//| M2_XGBoost_Oracle_AUDUSD.mqh |
//| REGIMEN: Rolling Window 2024-2026 (LONG ONLY)                    |
//+------------------------------------------------------------------+
double MathExpSafe(double x) { if (x > 100) return MathExp(100); if (x < -100) return MathExp(-100); return MathExp(x); }
double sigmoid(double x) {
    if (x < 0.0) { double z = MathExpSafe(x); return z / (1.0 + z); }
    return 1.0 / (1.0 + MathExpSafe(-x));
}
void GetXGBoostProbability(const double &features[], double &result[]) {
    double var0;
    if (features[3] < -2.6021) {
        var0 = 0.06363636;
    } else {
        if (features[1] < 0.142948) {
            var0 = 0.053846158;
        } else {
            if (features[3] < 2.4463) {
                var0 = -0.034615386;
            } else {
                var0 = 0.0023255814;
            }
        }
    }
    double var1;
    if (features[0] < 0.011685) {
        if (features[2] < 15.4) {
            var1 = 0.03332075;
        } else {
            if (features[1] < 0.18786) {
                var1 = -0.053224534;
            } else {
                var1 = -0.011606413;
            }
        }
    } else {
        if (features[0] < 0.020362) {
            if (features[4] < 0.00945) {
                var1 = 0.008461208;
            } else {
                var1 = 0.05274507;
            }
        } else {
            if (features[1] < 0.228042) {
                var1 = 0.0000068463196;
            } else {
                var1 = -0.05480662;
            }
        }
    }
    double var2;
    if (features[0] < 0.015622) {
        if (features[3] < 4.0232) {
            if (features[1] < 0.22497) {
                var2 = -0.025420407;
            } else {
                var2 = 0.012196573;
            }
        } else {
            var2 = -0.05381119;
        }
    } else {
        if (features[0] < 0.020362) {
            if (features[3] < 2.2479) {
                var2 = 0.0118387;
            } else {
                var2 = 0.06516742;
            }
        } else {
            if (features[4] < 0.013838) {
                var2 = 0.00078961084;
            } else {
                var2 = -0.038801473;
            }
        }
    }
    double var3;
    if (features[3] < -0.6736) {
        if (features[2] < 24.62) {
            var3 = 0.011950222;
        } else {
            var3 = 0.05854692;
        }
    } else {
        if (features[5] < 0.005179) {
            if (features[3] < 0.9618) {
                var3 = 0.04079724;
            } else {
                var3 = 0.002200056;
            }
        } else {
            if (features[2] < 43.71) {
                var3 = -0.03704322;
            } else {
                var3 = 0.02723348;
            }
        }
    }
    double var4;
    if (features[3] < -2.6021) {
        var4 = 0.06004842;
    } else {
        if (features[0] < 0.015076) {
            if (features[2] < 16.99) {
                var4 = 0.018065766;
            } else {
                var4 = -0.03833838;
            }
        } else {
            if (features[0] < 0.020362) {
                var4 = 0.034994826;
            } else {
                var4 = -0.026576472;
            }
        }
    }
    double var5;
    if (features[3] < -2.6021) {
        var5 = 0.058485895;
    } else {
        if (features[6] < 1.324495) {
            if (features[4] < 0.023503) {
                var5 = -0.0012749186;
            } else {
                var5 = -0.047803205;
            }
        } else {
            if (features[2] < 30.11) {
                var5 = -0.04913577;
            } else {
                var5 = 0.010775908;
            }
        }
    }
    double var6;
    if (features[3] < -2.6021) {
        var6 = 0.056742486;
    } else {
        if (features[6] < 1.39132) {
            if (features[6] < 0.452083) {
                var6 = -0.034969553;
            } else {
                var6 = 0.010141793;
            }
        } else {
            if (features[2] < 22.72) {
                var6 = -0.05882609;
            } else {
                var6 = -0.00949514;
            }
        }
    }
    double var7;
    if (features[6] < 0.520815) {
        if (features[5] < 0.005179) {
            if (features[3] < 1.4973) {
                var7 = 0.022897644;
            } else {
                var7 = -0.009566971;
            }
        } else {
            if (features[0] < 0.011427) {
                var7 = -0.013276535;
            } else {
                var7 = -0.050080903;
            }
        }
    } else {
        if (features[5] < 0.006921) {
            if (features[5] < 0.004832) {
                var7 = 0.012138251;
            } else {
                var7 = 0.056909967;
            }
        } else {
            if (features[5] < 0.008057) {
                var7 = -0.029044777;
            } else {
                var7 = 0.014884161;
            }
        }
    }
    double var8;
    if (features[5] < 0.005382) {
        if (features[3] < 0.9618) {
            if (features[5] < 0.004832) {
                var8 = 0.011646401;
            } else {
                var8 = 0.055218626;
            }
        } else {
            var8 = 0.002612853;
        }
    } else {
        if (features[3] < -1.9227) {
            var8 = 0.034678277;
        } else {
            if (features[3] < 1.3778) {
                var8 = -0.043299664;
            } else {
                var8 = -0.004544444;
            }
        }
    }
    double var9;
    if (features[5] < 0.006983) {
        if (features[2] < 19.8) {
            if (features[5] < 0.004832) {
                var9 = -0.010990981;
            } else {
                var9 = 0.009886354;
            }
        } else {
            if (features[4] < -0.007401) {
                var9 = 0.053405102;
            } else {
                var9 = 0.010349485;
            }
        }
    } else {
        if (features[5] < 0.00826) {
            var9 = -0.0675994;
        } else {
            if (features[2] < 27.31) {
                var9 = -0.027111087;
            } else {
                var9 = 0.021222519;
            }
        }
    }
    double var10;
    if (features[3] < -2.6021) {
        var10 = 0.05566926;
    } else {
        if (features[5] < 0.012403) {
            if (features[4] < 0.018688) {
                var10 = -0.0060760924;
            } else {
                var10 = 0.031763557;
            }
        } else {
            if (features[2] < 19.57) {
                var10 = 0.014091469;
            } else {
                var10 = -0.04672503;
            }
        }
    }
    double var11;
    if (features[5] < 0.006921) {
        if (features[0] < 0.00856) {
            if (features[5] < 0.003654) {
                var11 = 0.013564517;
            } else {
                var11 = 0.052899253;
            }
        } else {
            if (features[3] < -0.6736) {
                var11 = 0.03809279;
            } else {
                var11 = -0.00794018;
            }
        }
    } else {
        if (features[5] < 0.00826) {
            if (features[5] < 0.007416) {
                var11 = -0.05637271;
            } else {
                var11 = -0.019106556;
            }
        } else {
            if (features[1] < 0.187757) {
                var11 = -0.018794795;
            } else {
                var11 = 0.022608554;
            }
        }
    }
    double var12;
    if (features[1] < 0.279185) {
        if (features[3] < -2.6021) {
            var12 = 0.04815644;
        } else {
            if (features[6] < 0.967089) {
                var12 = -0.014789051;
            } else {
                var12 = 0.019875107;
            }
        }
    } else {
        var12 = -0.04996757;
    }
    double var13;
    if (features[1] < 0.165947) {
        if (features[6] < 0.640121) {
            if (features[6] < 0.490139) {
                var13 = 0.00796246;
            } else {
                var13 = -0.03748924;
            }
        } else {
            var13 = 0.0655575;
        }
    } else {
        if (features[3] < 1.3778) {
            if (features[2] < 22.05) {
                var13 = -0.0432912;
            } else {
                var13 = -0.00078354403;
            }
        } else {
            if (features[1] < 0.279185) {
                var13 = 0.010751554;
            } else {
                var13 = -0.025660587;
            }
        }
    }
    double var14;
    if (features[1] < 0.169005) {
        if (features[4] < -0.006126) {
            var14 = 0.05999994;
        } else {
            if (features[6] < 0.520815) {
                var14 = -0.02465737;
            } else {
                var14 = 0.01797857;
            }
        }
    } else {
        if (features[2] < 25.02) {
            if (features[2] < 19.57) {
                var14 = -0.010495336;
            } else {
                var14 = -0.04771681;
            }
        } else {
            if (features[4] < 0.002675) {
                var14 = 0.027477661;
            } else {
                var14 = -0.015200381;
            }
        }
    }
    double var15;
    if (features[5] < 0.006983) {
        if (features[2] < 22.5) {
            if (features[4] < -0.00549) {
                var15 = -0.0056881025;
            } else {
                var15 = 0.013230576;
            }
        } else {
            if (features[3] < 1.4591) {
                var15 = 0.050805163;
            } else {
                var15 = 0.013034897;
            }
        }
    } else {
        if (features[2] < 37.14) {
            if (features[1] < 0.18786) {
                var15 = -0.06801172;
            } else {
                var15 = -0.015405227;
            }
        } else {
            if (features[3] < 3.9634) {
                var15 = -0.01609808;
            } else {
                var15 = 0.029151767;
            }
        }
    }
    double var16;
    if (features[3] < -2.6021) {
        var16 = 0.047826838;
    } else {
        if (features[5] < 0.005179) {
            if (features[5] < 0.003993) {
                var16 = -0.0063231373;
            } else {
                var16 = 0.047515478;
            }
        } else {
            if (features[3] < 2.0454) {
                var16 = -0.021183684;
            } else {
                var16 = 0.0073358724;
            }
        }
    }
    double var17;
    if (features[0] < 0.011685) {
        if (features[6] < 0.309287) {
            var17 = 0.01905412;
        } else {
            if (features[2] < 15.4) {
                var17 = 0.0067756632;
            } else {
                var17 = -0.03905758;
            }
        }
    } else {
        if (features[6] < 0.563344) {
            if (features[3] < 2.0454) {
                var17 = -0.03259041;
            } else {
                var17 = 0.0007990706;
            }
        } else {
            if (features[6] < 1.353417) {
                var17 = 0.035365406;
            } else {
                var17 = -0.014494436;
            }
        }
    }
    double var18;
    if (features[4] < 0.011835) {
        if (features[6] < 1.785235) {
            if (features[1] < 0.18786) {
                var18 = -0.0017341216;
            } else {
                var18 = 0.035515435;
            }
        } else {
            var18 = -0.032018133;
        }
    } else {
        if (features[4] < 0.018151) {
            if (features[1] < 0.166868) {
                var18 = -0.011063415;
            } else {
                var18 = -0.057380784;
            }
        } else {
            if (features[6] < 0.949241) {
                var18 = -0.04095983;
            } else {
                var18 = 0.024967877;
            }
        }
    }
    double var19;
    if (features[2] < 22.23) {
        if (features[1] < 0.202152) {
            if (features[5] < 0.005142) {
                var19 = -0.0068143555;
            } else {
                var19 = -0.05834199;
            }
        } else {
            if (features[1] < 0.278388) {
                var19 = 0.019870294;
            } else {
                var19 = -0.023374677;
            }
        }
    } else {
        if (features[4] < 0.002675) {
            var19 = 0.04092233;
        } else {
            if (features[5] < 0.012342) {
                var19 = 0.010091993;
            } else {
                var19 = -0.025573233;
            }
        }
    }
    double var20;
    if (features[0] < 0.011685) {
        if (features[6] < 0.719217) {
            if (features[1] < 0.181583) {
                var20 = -0.01053888;
            } else {
                var20 = 0.01645064;
            }
        } else {
            if (features[4] < -0.007271) {
                var20 = -0.010314442;
            } else {
                var20 = -0.04286614;
            }
        }
    } else {
        if (features[6] < 0.096792) {
            var20 = -0.03156086;
        } else {
            if (features[6] < 1.983364) {
                var20 = 0.027558377;
            } else {
                var20 = -0.02655528;
            }
        }
    }
    double var21;
    if (features[1] < 0.169005) {
        if (features[6] < 0.520815) {
            if (features[5] < 0.005113) {
                var21 = 0.018686807;
            } else {
                var21 = -0.015416696;
            }
        } else {
            if (features[2] < 41.92) {
                var21 = 0.035904486;
            } else {
                var21 = 0.007391788;
            }
        }
    } else {
        if (features[2] < 22.05) {
            if (features[3] < 1.3778) {
                var21 = -0.046335366;
            } else {
                var21 = -0.0045403778;
            }
        } else {
            if (features[5] < 0.007416) {
                var21 = -0.037521224;
            } else {
                var21 = 0.016048461;
            }
        }
    }
    double var22;
    if (features[2] < 22.5) {
        if (features[2] < 18.53) {
            if (features[0] < 0.009377) {
                var22 = -0.0018680509;
            } else {
                var22 = 0.036821637;
            }
        } else {
            if (features[4] < -0.001483) {
                var22 = -0.056123722;
            } else {
                var22 = -0.011894564;
            }
        }
    } else {
        if (features[5] < 0.012434) {
            if (features[0] < 0.011254) {
                var22 = -0.0007839082;
            } else {
                var22 = 0.046831414;
            }
        } else {
            var22 = -0.021518447;
        }
    }
    double var23;
    if (features[3] < -1.9227) {
        var23 = 0.049454045;
    } else {
        if (features[5] < 0.005142) {
            if (features[2] < 20.38) {
                var23 = -0.0015287305;
            } else {
                var23 = 0.054691542;
            }
        } else {
            if (features[3] < 1.4591) {
                var23 = -0.032395575;
            } else {
                var23 = 0.0011290578;
            }
        }
    }
    double var24;
    if (features[1] < 0.279185) {
        if (features[1] < 0.149336) {
            if (features[0] < 0.008745) {
                var24 = 0.05016278;
            } else {
                var24 = 0.0010572573;
            }
        } else {
            if (features[1] < 0.256423) {
                var24 = -0.0023651535;
            } else {
                var24 = 0.04219834;
            }
        }
    } else {
        if (features[1] < 0.301783) {
            var24 = -0.048231374;
        } else {
            var24 = -0.013580396;
        }
    }
    double var25;
    if (features[0] < 0.011685) {
        if (features[3] < 3.2965) {
            if (features[2] < 22.5) {
                var25 = -0.01899811;
            } else {
                var25 = 0.025239436;
            }
        } else {
            var25 = -0.05997634;
        }
    } else {
        if (features[6] < 1.983364) {
            if (features[6] < 0.640121) {
                var25 = -0.0076847966;
            } else {
                var25 = 0.03264077;
            }
        } else {
            var25 = -0.030542368;
        }
    }
    double var26;
    if (features[3] < -2.6021) {
        var26 = 0.037698593;
    } else {
        if (features[2] < 18.53) {
            if (features[3] < 0.2499) {
                var26 = -0.0047635506;
            } else {
                var26 = 0.035799265;
            }
        } else {
            if (features[1] < 0.142948) {
                var26 = 0.01505629;
            } else {
                var26 = -0.01492878;
            }
        }
    }
    double var27;
    if (features[0] < 0.011685) {
        if (features[0] < 0.011427) {
            if (features[0] < 0.009091) {
                var27 = -0.020059519;
            } else {
                var27 = 0.0132580055;
            }
        } else {
            var27 = -0.050304126;
        }
    } else {
        if (features[0] < 0.020362) {
            if (features[4] < -0.004257) {
                var27 = -0.0139358565;
            } else {
                var27 = 0.031830158;
            }
        } else {
            if (features[1] < 0.221962) {
                var27 = -0.037140425;
            } else {
                var27 = 0.008275637;
            }
        }
    }
    double var28;
    if (features[5] < 0.012434) {
        if (features[6] < 0.967089) {
            if (features[3] < -2.6021) {
                var28 = 0.03512099;
            } else {
                var28 = -0.008603849;
            }
        } else {
            if (features[0] < 0.014511) {
                var28 = 0.0061553875;
            } else {
                var28 = 0.048833057;
            }
        }
    } else {
        if (features[2] < 19.57) {
            var28 = 0.010672449;
        } else {
            if (features[2] < 27.31) {
                var28 = -0.05155107;
            } else {
                var28 = -0.012644927;
            }
        }
    }
    double var29;
    if (features[2] < 18.53) {
        if (features[6] < 0.88412) {
            if (features[6] < 0.661964) {
                var29 = 0.017303905;
            } else {
                var29 = -0.012892814;
            }
        } else {
            var29 = 0.023432367;
        }
    } else {
        if (features[2] < 22.72) {
            if (features[0] < 0.008745) {
                var29 = 0.0007211387;
            } else {
                var29 = -0.04405735;
            }
        } else {
            if (features[0] < 0.014511) {
                var29 = -0.017297441;
            } else {
                var29 = 0.012388801;
            }
        }
    }
    double var30;
    if (features[1] < 0.278388) {
        if (features[5] < 0.005142) {
            if (features[5] < 0.003654) {
                var30 = 0.014302892;
            } else {
                var30 = 0.04986895;
            }
        } else {
            if (features[0] < 0.009091) {
                var30 = -0.040169597;
            } else {
                var30 = 0.012657254;
            }
        }
    } else {
        var30 = -0.05740545;
    }
    double var31;
    if (features[3] < -0.6736) {
        if (features[4] < 0.010807) {
            var31 = 0.0454202;
        } else {
            var31 = -0.006073958;
        }
    } else {
        if (features[0] < 0.011685) {
            if (features[5] < 0.006447) {
                var31 = 0.005265187;
            } else {
                var31 = -0.034799196;
            }
        } else {
            if (features[3] < 3.2735) {
                var31 = -0.008437742;
            } else {
                var31 = 0.031098941;
            }
        }
    }
    double var32;
    if (features[1] < 0.279185) {
        if (features[6] < 1.049214) {
            if (features[4] < -0.012473) {
                var32 = 0.04055429;
            } else {
                var32 = -0.0055727786;
            }
        } else {
            if (features[4] < 0.002251) {
                var32 = -0.005063775;
            } else {
                var32 = 0.03547083;
            }
        }
    } else {
        var32 = -0.030994365;
    }
    double var33;
    if (features[5] < 0.012434) {
        if (features[3] < -1.8429) {
            var33 = 0.033195723;
        } else {
            if (features[5] < 0.010639) {
                var33 = -0.0034321495;
            } else {
                var33 = 0.021441586;
            }
        }
    } else {
        if (features[5] < 0.016334) {
            var33 = -0.030763421;
        } else {
            var33 = -0.0101041375;
        }
    }
    double var34;
    if (features[4] < 0.027905) {
        if (features[3] < 0.9618) {
            if (features[1] < 0.165947) {
                var34 = 0.037388552;
            } else {
                var34 = 0.002323992;
            }
        } else {
            if (features[5] < 0.008577) {
                var34 = -0.018650794;
            } else {
                var34 = 0.005627025;
            }
        }
    } else {
        var34 = -0.0372787;
    }
    double var35;
    if (features[5] < 0.006983) {
        if (features[6] < 0.640121) {
            if (features[5] < 0.005113) {
                var35 = 0.017659677;
            } else {
                var35 = -0.014580123;
            }
        } else {
            if (features[4] < -0.005443) {
                var35 = 0.051839855;
            } else {
                var35 = 0.01920789;
            }
        }
    } else {
        if (features[5] < 0.012434) {
            if (features[5] < 0.008736) {
                var35 = -0.026566012;
            } else {
                var35 = 0.0072729304;
            }
        } else {
            if (features[1] < 0.30089) {
                var35 = -0.048750862;
            } else {
                var35 = 0.0030428607;
            }
        }
    }
    double var36;
    if (features[2] < 30.11) {
        if (features[2] < 18.53) {
            if (features[1] < 0.22497) {
                var36 = 0.003606225;
            } else {
                var36 = 0.034260537;
            }
        } else {
            if (features[2] < 22.05) {
                var36 = -0.038145185;
            } else {
                var36 = -0.0020388358;
            }
        }
    } else {
        if (features[4] < 0.009738) {
            if (features[6] < 0.563344) {
                var36 = 0.0123125445;
            } else {
                var36 = 0.043644514;
            }
        } else {
            if (features[6] < 1.151062) {
                var36 = -0.013604927;
            } else {
                var36 = 0.02148973;
            }
        }
    }
    double var37;
    if (features[2] < 30.11) {
        if (features[2] < 18.53) {
            if (features[3] < 0.2499) {
                var37 = -0.0066294097;
            } else {
                var37 = 0.025283614;
            }
        } else {
            if (features[2] < 20.88) {
                var37 = -0.0456939;
            } else {
                var37 = -0.010573349;
            }
        }
    } else {
        if (features[0] < 0.020362) {
            if (features[0] < 0.017075) {
                var37 = -0.0039658914;
            } else {
                var37 = 0.039255798;
            }
        } else {
            if (features[1] < 0.221962) {
                var37 = -0.024623897;
            } else {
                var37 = 0.0021552753;
            }
        }
    }
    double var38;
    if (features[2] < 30.11) {
        if (features[4] < -0.011245) {
            var38 = -0.046281178;
        } else {
            if (features[4] < 0.002675) {
                var38 = 0.005751771;
            } else {
                var38 = -0.019041339;
            }
        }
    } else {
        if (features[0] < 0.023402) {
            if (features[0] < 0.011685) {
                var38 = -0.008218649;
            } else {
                var38 = 0.03353652;
            }
        } else {
            var38 = -0.019127639;
        }
    }
    double var39;
    if (features[3] < -1.7565) {
        if (features[1] < 0.163672) {
            var39 = 0.006046668;
        } else {
            var39 = 0.040951826;
        }
    } else {
        if (features[2] < 18.82) {
            if (features[1] < 0.18262) {
                var39 = -0.001347418;
            } else {
                var39 = 0.026570221;
            }
        } else {
            if (features[1] < 0.169005) {
                var39 = 0.0071058325;
            } else {
                var39 = -0.021530164;
            }
        }
    }
    double var40;
    if (features[3] < -2.6021) {
        var40 = 0.037392672;
    } else {
        if (features[2] < 16.99) {
            if (features[3] < 0.2499) {
                var40 = -0.008787536;
            } else {
                var40 = 0.035503797;
            }
        } else {
            if (features[2] < 41.81) {
                var40 = -0.02061676;
            } else {
                var40 = 0.007739395;
            }
        }
    }
    double var41;
    if (features[3] < -0.6736) {
        if (features[5] < 0.006921) {
            var41 = 0.05199903;
        } else {
            var41 = 0.006603724;
        }
    } else {
        if (features[5] < 0.010568) {
            if (features[1] < 0.136025) {
                var41 = 0.029755507;
            } else {
                var41 = -0.017382659;
            }
        } else {
            if (features[3] < 2.4463) {
                var41 = -0.034270003;
            } else {
                var41 = 0.039089724;
            }
        }
    }
    double var42;
    if (features[5] < 0.006983) {
        if (features[4] < 0.010807) {
            if (features[1] < 0.165947) {
                var42 = 0.034926116;
            } else {
                var42 = 0.008943411;
            }
        } else {
            var42 = -0.0041188914;
        }
    } else {
        if (features[0] < 0.015622) {
            if (features[1] < 0.18786) {
                var42 = -0.057307582;
            } else {
                var42 = -0.016106864;
            }
        } else {
            if (features[3] < 3.2735) {
                var42 = -0.025652928;
            } else {
                var42 = 0.02729091;
            }
        }
    }
    double var43;
    if (features[2] < 18.82) {
        if (features[2] < 16.0) {
            var43 = -0.0014873468;
        } else {
            var43 = 0.028840536;
        }
    } else {
        if (features[2] < 30.11) {
            if (features[0] < 0.013615) {
                var43 = -0.013851623;
            } else {
                var43 = -0.044568695;
            }
        } else {
            if (features[1] < 0.166868) {
                var43 = 0.025937805;
            } else {
                var43 = -0.008994977;
            }
        }
    }
    double var44;
    if (features[0] < 0.011685) {
        if (features[5] < 0.005142) {
            if (features[5] < 0.00443) {
                var44 = -0.014011549;
            } else {
                var44 = 0.033782847;
            }
        } else {
            if (features[1] < 0.18786) {
                var44 = -0.04665585;
            } else {
                var44 = -0.0026683991;
            }
        }
    } else {
        if (features[2] < 19.57) {
            var44 = 0.053880453;
        } else {
            if (features[3] < -0.6736) {
                var44 = 0.0338421;
            } else {
                var44 = -0.006855403;
            }
        }
    }
    double var45;
    if (features[0] < 0.020362) {
        if (features[0] < 0.015622) {
            if (features[6] < 0.738564) {
                var45 = 0.014930243;
            } else {
                var45 = -0.022729814;
            }
        } else {
            if (features[6] < 0.563344) {
                var45 = 0.012355795;
            } else {
                var45 = 0.049755048;
            }
        }
    } else {
        var45 = -0.042960387;
    }
    double var46;
    if (features[0] < 0.011685) {
        if (features[6] < 0.721387) {
            if (features[4] < 0.012872) {
                var46 = 0.015722074;
            } else {
                var46 = -0.022037199;
            }
        } else {
            if (features[4] < -0.005537) {
                var46 = 0.0070331353;
            } else {
                var46 = -0.047724493;
            }
        }
    } else {
        if (features[0] < 0.020362) {
            if (features[4] < 0.002251) {
                var46 = 0.006561053;
            } else {
                var46 = 0.03733889;
            }
        } else {
            if (features[3] < 2.4463) {
                var46 = -0.028863857;
            } else {
                var46 = -0.0018909399;
            }
        }
    }
    double var47;
    if (features[5] < 0.006921) {
        if (features[2] < 20.38) {
            if (features[1] < 0.136025) {
                var47 = 0.012888618;
            } else {
                var47 = -0.0030313425;
            }
        } else {
            var47 = 0.05181851;
        }
    } else {
        if (features[1] < 0.18786) {
            if (features[0] < 0.011685) {
                var47 = -0.04513616;
            } else {
                var47 = -0.0066264383;
            }
        } else {
            if (features[1] < 0.221942) {
                var47 = 0.04074041;
            } else {
                var47 = -0.005892252;
            }
        }
    }
    double var48;
    if (features[2] < 22.72) {
        if (features[2] < 18.53) {
            if (features[3] < 0.2499) {
                var48 = -0.009061886;
            } else {
                var48 = 0.027199298;
            }
        } else {
            if (features[0] < 0.007999) {
                var48 = 0.0072937794;
            } else {
                var48 = -0.04693735;
            }
        }
    } else {
        if (features[3] < 4.9073) {
            if (features[0] < 0.011254) {
                var48 = -0.0070796586;
            } else {
                var48 = 0.01918947;
            }
        } else {
            var48 = -0.030725172;
        }
    }
    double var49;
    if (features[5] < 0.006983) {
        if (features[6] < 0.464329) {
            var49 = -0.013177042;
        } else {
            if (features[2] < 15.4) {
                var49 = 0.010831045;
            } else {
                var49 = 0.03932355;
            }
        }
    } else {
        if (features[5] < 0.007416) {
            var49 = -0.035847627;
        } else {
            if (features[1] < 0.185191) {
                var49 = -0.014297194;
            } else {
                var49 = 0.016796863;
            }
        }
    }
    double var50;
    if (features[3] < -1.7565) {
        var50 = 0.037077364;
    } else {
        if (features[0] < 0.021571) {
            if (features[0] < 0.015622) {
                var50 = -0.005620578;
            } else {
                var50 = 0.02888286;
            }
        } else {
            var50 = -0.035826545;
        }
    }
    double var51;
    if (features[1] < 0.169005) {
        if (features[4] < -0.008306) {
            var51 = 0.044409316;
        } else {
            if (features[0] < 0.012319) {
                var51 = -0.00865175;
            } else {
                var51 = 0.019819347;
            }
        }
    } else {
        if (features[1] < 0.255236) {
            if (features[1] < 0.238683) {
                var51 = -0.010614577;
            } else {
                var51 = -0.045945417;
            }
        } else {
            if (features[1] < 0.278388) {
                var51 = 0.03791949;
            } else {
                var51 = -0.012411769;
            }
        }
    }
    double var52;
    if (features[6] < 1.353417) {
        if (features[4] < -0.007271) {
            var52 = 0.030537728;
        } else {
            if (features[5] < 0.010639) {
                var52 = -0.012234672;
            } else {
                var52 = 0.013038228;
            }
        }
    } else {
        if (features[0] < 0.014121) {
            var52 = -0.037522674;
        } else {
            var52 = -0.00025314366;
        }
    }
    double var53;
    if (features[2] < 30.7) {
        if (features[4] < 0.011835) {
            if (features[4] < -0.00585) {
                var53 = -0.02474969;
            } else {
                var53 = 0.00041027085;
            }
        } else {
            if (features[4] < 0.018151) {
                var53 = -0.05146128;
            } else {
                var53 = -0.015966462;
            }
        }
    } else {
        if (features[2] < 36.5) {
            var53 = 0.024336314;
        } else {
            if (features[3] < 3.4782) {
                var53 = -0.005512992;
            } else {
                var53 = 0.02106381;
            }
        }
    }
    double var54;
    if (features[6] < 0.045366) {
        var54 = -0.026484746;
    } else {
        if (features[6] < 1.39132) {
            if (features[6] < 0.967089) {
                var54 = 0.0005341405;
            } else {
                var54 = 0.026831916;
            }
        } else {
            if (features[5] < 0.013404) {
                var54 = 0.0053085885;
            } else {
                var54 = -0.030286958;
            }
        }
    }
    double var55;
    if (features[3] < -2.6021) {
        var55 = 0.03399673;
    } else {
        if (features[2] < 18.82) {
            if (features[3] < 0.2499) {
                var55 = -0.0092690205;
            } else {
                var55 = 0.031997193;
            }
        } else {
            if (features[0] < 0.008745) {
                var55 = 0.009360373;
            } else {
                var55 = -0.018853312;
            }
        }
    }
    double var56;
    if (features[0] < 0.007363) {
        var56 = 0.049590897;
    } else {
        if (features[2] < 18.82) {
            if (features[3] < 0.2499) {
                var56 = -0.002422197;
            } else {
                var56 = 0.026438674;
            }
        } else {
            if (features[1] < 0.238683) {
                var56 = -0.0013258293;
            } else {
                var56 = -0.03018019;
            }
        }
    }
    double var57;
    if (features[4] < 0.014361) {
        if (features[2] < 22.72) {
            if (features[6] < 1.353417) {
                var57 = 0.001709049;
            } else {
                var57 = -0.03917777;
            }
        } else {
            if (features[4] < 0.002675) {
                var57 = 0.04356847;
            } else {
                var57 = 0.0042035165;
            }
        }
    } else {
        if (features[6] < 0.967089) {
            var57 = -0.047653425;
        } else {
            if (features[0] < 0.015622) {
                var57 = -0.01948901;
            } else {
                var57 = 0.025064444;
            }
        }
    }
    double var58;
    if (features[3] < -1.8429) {
        var58 = 0.043024827;
    } else {
        if (features[4] < -0.001483) {
            if (features[6] < 0.926272) {
                var58 = -0.00079650426;
            } else {
                var58 = -0.044940006;
            }
        } else {
            if (features[4] < 0.016398) {
                var58 = 0.015386775;
            } else {
                var58 = -0.009170392;
            }
        }
    }
    double var59;
    if (features[6] < 0.096792) {
        var59 = -0.03105936;
    } else {
        if (features[5] < 0.006921) {
            if (features[5] < 0.00443) {
                var59 = -0.0031488612;
            } else {
                var59 = 0.026762769;
            }
        } else {
            if (features[5] < 0.007505) {
                var59 = -0.04265609;
            } else {
                var59 = -0.0030726849;
            }
        }
    }
    double var60;
    if (features[1] < 0.165947) {
        if (features[4] < -0.007401) {
            var60 = 0.033716653;
        } else {
            if (features[5] < 0.005382) {
                var60 = 0.015187782;
            } else {
                var60 = -0.010658191;
            }
        }
    } else {
        if (features[1] < 0.221962) {
            if (features[5] < 0.01079) {
                var60 = -0.039289307;
            } else {
                var60 = 0.009518563;
            }
        } else {
            if (features[1] < 0.243949) {
                var60 = 0.01764328;
            } else {
                var60 = -0.016450848;
            }
        }
    }
    double var61;
    if (features[4] < 0.016398) {
        if (features[6] < 1.785235) {
            if (features[6] < 0.096792) {
                var61 = -0.009708623;
            } else {
                var61 = 0.017760646;
            }
        } else {
            var61 = -0.025479889;
        }
    } else {
        if (features[6] < 0.967089) {
            var61 = -0.031839274;
        } else {
            if (features[4] < 0.020107) {
                var61 = -0.014524254;
            } else {
                var61 = 0.014722754;
            }
        }
    }
    double var62;
    if (features[5] < 0.006983) {
        if (features[1] < 0.178296) {
            if (features[0] < 0.008745) {
                var62 = 0.034017842;
            } else {
                var62 = 0.010776786;
            }
        } else {
            var62 = 0.0016098697;
        }
    } else {
        if (features[1] < 0.18786) {
            if (features[0] < 0.011685) {
                var62 = -0.038279247;
            } else {
                var62 = -0.0016718156;
            }
        } else {
            if (features[5] < 0.008577) {
                var62 = -0.0071093673;
            } else {
                var62 = 0.016738541;
            }
        }
    }
    double var63;
    if (features[1] < 0.279185) {
        if (features[3] < -0.3121) {
            if (features[3] < -1.8429) {
                var63 = 0.011999389;
            } else {
                var63 = -0.03397559;
            }
        } else {
            if (features[3] < 4.3566) {
                var63 = 0.018200776;
            } else {
                var63 = -0.0077970275;
            }
        }
    } else {
        var63 = -0.02786178;
    }
    double var64;
    if (features[2] < 22.5) {
        if (features[1] < 0.185191) {
            if (features[1] < 0.149336) {
                var64 = 0.00042238008;
            } else {
                var64 = -0.041270904;
            }
        } else {
            if (features[1] < 0.221942) {
                var64 = 0.022427196;
            } else {
                var64 = -0.007447745;
            }
        }
    } else {
        if (features[4] < -0.001652) {
            var64 = 0.042839985;
        } else {
            if (features[2] < 46.49) {
                var64 = -0.0026280158;
            } else {
                var64 = 0.024739347;
            }
        }
    }
    double var65;
    if (features[3] < -2.6021) {
        var65 = 0.031173114;
    } else {
        if (features[6] < 0.115091) {
            var65 = -0.024762804;
        } else {
            if (features[2] < 24.62) {
                var65 = 0.01278541;
            } else {
                var65 = -0.006460029;
            }
        }
    }
    double var66;
    if (features[3] < 4.1042) {
        if (features[3] < 0.2499) {
            if (features[3] < -1.8429) {
                var66 = 0.009166027;
            } else {
                var66 = -0.033827666;
            }
        } else {
            if (features[1] < 0.180901) {
                var66 = 0.026584616;
            } else {
                var66 = -0.004466859;
            }
        }
    } else {
        if (features[1] < 0.16932) {
            var66 = -0.014154923;
        } else {
            var66 = -0.04805111;
        }
    }
    double var67;
    if (features[1] < 0.145619) {
        if (features[4] < 0.007946) {
            var67 = 0.034036096;
        } else {
            var67 = -0.005526195;
        }
    } else {
        if (features[5] < 0.003993) {
            var67 = 0.022011561;
        } else {
            if (features[5] < 0.008736) {
                var67 = -0.020433601;
            } else {
                var67 = 0.0024133897;
            }
        }
    }
    double var68;
    if (features[0] < 0.020362) {
        if (features[1] < 0.202152) {
            if (features[1] < 0.142948) {
                var68 = 0.026875868;
            } else {
                var68 = -0.0141474;
            }
        } else {
            if (features[1] < 0.278388) {
                var68 = 0.035955545;
            } else {
                var68 = -0.016945885;
            }
        }
    } else {
        if (features[3] < 2.4463) {
            var68 = -0.03610151;
        } else {
            var68 = -0.0016107394;
        }
    }
    double var69;
    if (features[3] < -2.6021) {
        var69 = 0.030939175;
    } else {
        if (features[0] < 0.011685) {
            if (features[0] < 0.00856) {
                var69 = -0.0017649828;
            } else {
                var69 = -0.037538286;
            }
        } else {
            if (features[0] < 0.020362) {
                var69 = 0.012693981;
            } else {
                var69 = -0.03126766;
            }
        }
    }
    double var70;
    if (features[1] < 0.225822) {
        if (features[1] < 0.18786) {
            if (features[1] < 0.165947) {
                var70 = 0.009655545;
            } else {
                var70 = -0.019777773;
            }
        } else {
            if (features[2] < 25.31) {
                var70 = 0.03407022;
            } else {
                var70 = 0.0069293426;
            }
        }
    } else {
        if (features[1] < 0.255236) {
            var70 = -0.043489363;
        } else {
            if (features[6] < 1.18683) {
                var70 = 0.019667251;
            } else {
                var70 = -0.02769636;
            }
        }
    }
    double var71;
    if (features[2] < 22.05) {
        if (features[2] < 17.55) {
            if (features[3] < 0.2499) {
                var71 = -0.014477126;
            } else {
                var71 = 0.026131338;
            }
        } else {
            if (features[3] < 1.9531) {
                var71 = -0.046699636;
            } else {
                var71 = -0.003072539;
            }
        }
    } else {
        if (features[3] < 1.4973) {
            if (features[2] < 33.16) {
                var71 = 0.04018401;
            } else {
                var71 = 0.0029334743;
            }
        } else {
            if (features[2] < 41.73) {
                var71 = -0.013841656;
            } else {
                var71 = 0.016154032;
            }
        }
    }
    double var72;
    if (features[6] < 0.045366) {
        var72 = -0.024420865;
    } else {
        if (features[4] < -0.005443) {
            if (features[6] < 0.640121) {
                var72 = 0.0101707885;
            } else {
                var72 = 0.029946188;
            }
        } else {
            if (features[6] < 0.852906) {
                var72 = 0.01282047;
            } else {
                var72 = -0.00834867;
            }
        }
    }
    double var73;
    if (features[6] < 0.563344) {
        if (features[4] < -0.001046) {
            if (features[1] < 0.180901) {
                var73 = 0.011467709;
            } else {
                var73 = -0.014831773;
            }
        } else {
            if (features[1] < 0.147981) {
                var73 = -0.04770776;
            } else {
                var73 = -0.019175064;
            }
        }
    } else {
        if (features[2] < 30.11) {
            if (features[6] < 1.353417) {
                var73 = 0.011507985;
            } else {
                var73 = -0.017314376;
            }
        } else {
            if (features[1] < 0.210467) {
                var73 = 0.04082363;
            } else {
                var73 = 0.009624697;
            }
        }
    }
    double var74;
    if (features[0] < 0.007088) {
        var74 = 0.02222554;
    } else {
        if (features[0] < 0.009091) {
            if (features[2] < 22.5) {
                var74 = -0.053644534;
            } else {
                var74 = -0.0032794185;
            }
        } else {
            if (features[1] < 0.22497) {
                var74 = -0.014511609;
            } else {
                var74 = 0.0060068234;
            }
        }
    }
    double var75;
    if (features[1] < 0.145619) {
        if (features[4] < 0.007946) {
            var75 = 0.045015402;
        } else {
            var75 = -0.008883986;
        }
    } else {
        if (features[5] < 0.008856) {
            if (features[4] < -0.012099) {
                var75 = 0.01173802;
            } else {
                var75 = -0.03152751;
            }
        } else {
            if (features[5] < 0.012434) {
                var75 = 0.0101994565;
            } else {
                var75 = -0.012454149;
            }
        }
    }
    double var76;
    if (features[3] < -1.0054) {
        if (features[3] < -1.9227) {
            var76 = 0.033412796;
        } else {
            var76 = 0.008160702;
        }
    } else {
        if (features[5] < 0.006983) {
            if (features[5] < 0.004832) {
                var76 = -0.006794867;
            } else {
                var76 = 0.010558023;
            }
        } else {
            if (features[3] < 2.0454) {
                var76 = -0.038161967;
            } else {
                var76 = -0.0053896667;
            }
        }
    }
    double var77;
    if (features[0] < 0.020362) {
        if (features[2] < 46.49) {
            if (features[0] < 0.007088) {
                var77 = 0.022118222;
            } else {
                var77 = -0.0042238054;
            }
        } else {
            var77 = 0.030093541;
        }
    } else {
        if (features[1] < 0.187757) {
            var77 = -0.00027750045;
        } else {
            var77 = -0.03377851;
        }
    }
    double var78;
    if (features[4] < 0.027905) {
        if (features[0] < 0.011685) {
            if (features[3] < -0.4768) {
                var78 = -0.030373065;
            } else {
                var78 = -0.0035991897;
            }
        } else {
            if (features[4] < 0.010177) {
                var78 = 0.0017788431;
            } else {
                var78 = 0.029881144;
            }
        }
    } else {
        var78 = -0.02783583;
    }
    double var79;
    if (features[6] < 1.146532) {
        if (features[6] < 0.852906) {
            if (features[1] < 0.142948) {
                var79 = 0.024871513;
            } else {
                var79 = -0.0040264586;
            }
        } else {
            if (features[4] < 0.017305) {
                var79 = -0.0475176;
            } else {
                var79 = -0.010532678;
            }
        }
    } else {
        if (features[1] < 0.279185) {
            var79 = 0.03622553;
        } else {
            var79 = -0.016303925;
        }
    }
    double var80;
    if (features[0] < 0.009091) {
        if (features[0] < 0.00845) {
            if (features[0] < 0.00837) {
                var80 = -0.008404622;
            } else {
                var80 = 0.028738692;
            }
        } else {
            var80 = -0.032034516;
        }
    } else {
        if (features[1] < 0.278388) {
            if (features[2] < 36.5) {
                var80 = 0.033655968;
            } else {
                var80 = 0.0010401013;
            }
        } else {
            var80 = -0.013719893;
        }
    }
    double var81;
    if (features[2] < 21.21) {
        if (features[2] < 19.54) {
            if (features[4] < -0.002715) {
                var81 = -0.01901821;
            } else {
                var81 = 0.0074528563;
            }
        } else {
            var81 = -0.040142674;
        }
    } else {
        if (features[4] < -0.007271) {
            var81 = 0.043880973;
        } else {
            if (features[2] < 25.31) {
                var81 = 0.0146560045;
            } else {
                var81 = -0.010994357;
            }
        }
    }
    double var82;
    if (features[1] < 0.165947) {
        if (features[3] < 2.4366) {
            if (features[5] < 0.005382) {
                var82 = 0.061828125;
            } else {
                var82 = 0.016509542;
            }
        } else {
            var82 = -0.00044457705;
        }
    } else {
        if (features[5] < 0.008736) {
            if (features[5] < 0.006983) {
                var82 = 0.0032806732;
            } else {
                var82 = -0.03637099;
            }
        } else {
            if (features[5] < 0.011074) {
                var82 = 0.03383785;
            } else {
                var82 = -0.0008942784;
            }
        }
    }
    double var83;
    if (features[0] < 0.014121) {
        if (features[4] < 0.012872) {
            if (features[3] < 2.3825) {
                var83 = 0.009865882;
            } else {
                var83 = -0.01215738;
            }
        } else {
            var83 = -0.039888658;
        }
    } else {
        if (features[3] < 1.2687) {
            var83 = 0.034304783;
        } else {
            if (features[3] < 3.4782) {
                var83 = -0.008044074;
            } else {
                var83 = 0.019233083;
            }
        }
    }
    double var84;
    if (features[2] < 30.7) {
        if (features[1] < 0.18786) {
            if (features[5] < 0.003957) {
                var84 = 0.011918155;
            } else {
                var84 = -0.032708887;
            }
        } else {
            if (features[5] < 0.007383) {
                var84 = -0.02692161;
            } else {
                var84 = 0.0069713667;
            }
        }
    } else {
        if (features[6] < 0.563344) {
            var84 = -0.010970767;
        } else {
            if (features[3] < 4.569) {
                var84 = 0.027852396;
            } else {
                var84 = -0.0016101188;
            }
        }
    }
    double var85;
    if (features[5] < 0.012434) {
        if (features[0] < 0.007088) {
            var85 = 0.033334967;
        } else {
            if (features[5] < 0.008543) {
                var85 = -0.002532017;
            } else {
                var85 = 0.01735319;
            }
        }
    } else {
        if (features[2] < 20.12) {
            var85 = 0.009871634;
        } else {
            var85 = -0.040125277;
        }
    }
    double var86;
    if (features[4] < 0.016303) {
        if (features[3] < -0.6736) {
            if (features[1] < 0.160567) {
                var86 = 0.0038024324;
            } else {
                var86 = 0.042256717;
            }
        } else {
            if (features[4] < 0.004878) {
                var86 = -0.007310126;
            } else {
                var86 = 0.011549503;
            }
        }
    } else {
        if (features[2] < 42.5) {
            var86 = -0.039007176;
        } else {
            if (features[2] < 52.15) {
                var86 = 0.012828006;
            } else {
                var86 = -0.0030793247;
            }
        }
    }
    double var87;
    if (features[3] < -1.9227) {
        var87 = 0.033982106;
    } else {
        if (features[5] < 0.007508) {
            if (features[3] < -0.4768) {
                var87 = -0.011197136;
            } else {
                var87 = 0.01084579;
            }
        } else {
            if (features[1] < 0.199638) {
                var87 = -0.028350184;
            } else {
                var87 = 0.00043118256;
            }
        }
    }
    double var88;
    if (features[6] < 0.490139) {
        if (features[0] < 0.008385) {
            var88 = 0.005063731;
        } else {
            if (features[0] < 0.011254) {
                var88 = -0.0477638;
            } else {
                var88 = -0.009029246;
            }
        }
    } else {
        if (features[0] < 0.011685) {
            if (features[0] < 0.007088) {
                var88 = 0.024840599;
            } else {
                var88 = -0.011786658;
            }
        } else {
            if (features[1] < 0.278388) {
                var88 = 0.025789216;
            } else {
                var88 = -0.008826158;
            }
        }
    }
    double var89;
    if (features[6] < 0.563344) {
        if (features[6] < 0.403888) {
            if (features[5] < 0.005179) {
                var89 = 0.022748722;
            } else {
                var89 = -0.011435051;
            }
        } else {
            if (features[4] < 0.013824) {
                var89 = -0.042865902;
            } else {
                var89 = -0.009550328;
            }
        }
    } else {
        if (features[6] < 1.983364) {
            if (features[5] < 0.007416) {
                var89 = 0.004787569;
            } else {
                var89 = 0.02887981;
            }
        } else {
            var89 = -0.017972436;
        }
    }
    double var90;
    if (features[6] < 1.618661) {
        if (features[4] < 0.016398) {
            if (features[4] < -0.00585) {
                var90 = -0.0079457145;
            } else {
                var90 = 0.02274151;
            }
        } else {
            if (features[6] < 0.967089) {
                var90 = -0.026985591;
            } else {
                var90 = 0.0010837228;
            }
        }
    } else {
        if (features[3] < 2.4463) {
            var90 = -0.03294139;
        } else {
            var90 = -0.008867969;
        }
    }
    double var91;
    if (features[6] < 0.115091) {
        var91 = -0.025041923;
    } else {
        if (features[2] < 24.16) {
            if (features[4] < -0.012099) {
                var91 = -0.023225652;
            } else {
                var91 = 0.022768142;
            }
        } else {
            if (features[5] < 0.010639) {
                var91 = -0.016997369;
            } else {
                var91 = 0.009803564;
            }
        }
    }
    double var92;
    if (features[4] < 0.013838) {
        if (features[3] < 2.7832) {
            if (features[5] < 0.00571) {
                var92 = 0.0038627565;
            } else {
                var92 = 0.03161125;
            }
        } else {
            if (features[3] < 3.9549) {
                var92 = -0.020579217;
            } else {
                var92 = 0.014851867;
            }
        }
    } else {
        if (features[1] < 0.255236) {
            if (features[1] < 0.221192) {
                var92 = -0.0076971287;
            } else {
                var92 = -0.03942793;
            }
        } else {
            var92 = 0.008500719;
        }
    }
    double var93;
    if (features[3] < 4.1042) {
        if (features[2] < 18.53) {
            if (features[1] < 0.221192) {
                var93 = 0.0009992528;
            } else {
                var93 = 0.027965708;
            }
        } else {
            if (features[2] < 19.57) {
                var93 = -0.038795054;
            } else {
                var93 = -0.0020380171;
            }
        }
    } else {
        var93 = -0.038287286;
    }
    double var94;
    if (features[4] < 0.027905) {
        if (features[6] < 1.324495) {
            if (features[6] < 0.88412) {
                var94 = 0.00040612943;
            } else {
                var94 = 0.02953024;
            }
        } else {
            if (features[2] < 22.72) {
                var94 = -0.023952305;
            } else {
                var94 = 0.002716192;
            }
        }
    } else {
        var94 = -0.024432465;
    }
    double var95;
    if (features[1] < 0.169005) {
        if (features[6] < 0.403888) {
            var95 = -0.008547283;
        } else {
            if (features[5] < 0.008543) {
                var95 = 0.044215377;
            } else {
                var95 = 0.0030443005;
            }
        }
    } else {
        if (features[3] < -1.4447) {
            var95 = 0.023204036;
        } else {
            if (features[4] < -0.002715) {
                var95 = -0.019298678;
            } else {
                var95 = -0.0001220135;
            }
        }
    }
    double var96;
    if (features[6] < 0.50258) {
        if (features[0] < 0.012056) {
            if (features[1] < 0.181583) {
                var96 = 0.0041044983;
            } else {
                var96 = 0.042791322;
            }
        } else {
            var96 = -0.009778854;
        }
    } else {
        if (features[5] < 0.006983) {
            if (features[5] < 0.00571) {
                var96 = -0.004753554;
            } else {
                var96 = 0.03369679;
            }
        } else {
            if (features[6] < 1.037619) {
                var96 = -0.038979363;
            } else {
                var96 = 0.0010686282;
            }
        }
    }
    double var97;
    if (features[5] < 0.012434) {
        if (features[5] < 0.011372) {
            if (features[1] < 0.181367) {
                var97 = 0.0052150623;
            } else {
                var97 = -0.011934514;
            }
        } else {
            var97 = 0.023720896;
        }
    } else {
        if (features[4] < -0.004257) {
            var97 = -0.00043296293;
        } else {
            if (features[3] < 2.8741) {
                var97 = -0.037566192;
            } else {
                var97 = -0.0062855156;
            }
        }
    }
    double var98;
    if (features[6] < 1.39132) {
        if (features[6] < 1.151062) {
            if (features[0] < 0.007999) {
                var98 = 0.028317316;
            } else {
                var98 = 0.0016521882;
            }
        } else {
            var98 = 0.039115034;
        }
    } else {
        if (features[5] < 0.016199) {
            var98 = -0.028535543;
        } else {
            var98 = 0.0030316054;
        }
    }
    double var99;
    if (features[2] < 25.31) {
        if (features[6] < 1.175658) {
            if (features[4] < -0.002715) {
                var99 = -0.0058865254;
            } else {
                var99 = 0.02740173;
            }
        } else {
            if (features[2] < 20.12) {
                var99 = -0.0006853128;
            } else {
                var99 = -0.021579998;
            }
        }
    } else {
        if (features[4] < -0.001652) {
            var99 = 0.0061550774;
        } else {
            if (features[5] < 0.005382) {
                var99 = -0.00034110862;
            } else {
                var99 = -0.031218449;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
