//+------------------------------------------------------------------+
//| M2_XGBoost_Oracle_EURUSD.mqh |
//| REGIMEN: Rolling Window 2024-2026 (LONG ONLY)                    |
//+------------------------------------------------------------------+
double MathExpSafe(double x) { if (x > 100) return MathExp(100); if (x < -100) return MathExp(-100); return MathExp(x); }
double sigmoid(double x) {
    if (x < 0.0) { double z = MathExpSafe(x); return z / (1.0 + z); }
    return 1.0 / (1.0 + MathExpSafe(-x));
}
void GetXGBoostProbability(const double &features[], double &result[]) {
    double var0;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000033) {
            if (features[3] < 0.6248) {
                var0 = 0.007692308;
            } else {
                var0 = -0.039130434;
            }
        } else {
            var0 = 0.053846158;
        }
    } else {
        if (features[2] < 48.9) {
            var0 = -0.060000002;
        } else {
            var0 = 0.0;
        }
    }
    double var1;
    if (features[1] < 0.000041) {
        if (features[5] < 0.003274) {
            if (features[2] < 30.84) {
                var1 = -0.065572284;
            } else {
                var1 = 0.01116318;
            }
        } else {
            if (features[0] < 124.5122) {
                var1 = 0.041559394;
            } else {
                var1 = -0.011911092;
            }
        }
    } else {
        if (features[0] < 73.49218) {
            var1 = -0.06203092;
        } else {
            var1 = -0.01011444;
        }
    }
    double var2;
    if (features[0] < 63.811626) {
        if (features[3] < 0.6619) {
            var2 = -0.06415563;
        } else {
            var2 = -0.015705844;
        }
    } else {
        if (features[5] < 0.005904) {
            if (features[3] < -0.9407) {
                var2 = -0.03900534;
            } else {
                var2 = 0.012003652;
            }
        } else {
            if (features[3] < 0.1535) {
                var2 = 0.05666433;
            } else {
                var2 = 0.00905482;
            }
        }
    }
    double var3;
    if (features[1] < 0.000042) {
        if (features[5] < 0.003788) {
            if (features[3] < -1.1325) {
                var3 = -0.058583885;
            } else {
                var3 = 0.00289755;
            }
        } else {
            if (features[3] < 3.6671) {
                var3 = 0.043349236;
            } else {
                var3 = -0.016299639;
            }
        }
    } else {
        if (features[3] < 0.4199) {
            var3 = -0.059584696;
        } else {
            var3 = -0.008706036;
        }
    }
    double var4;
    if (features[0] < 63.811626) {
        if (features[2] < 24.32) {
            if (features[2] < 18.71) {
                var4 = -0.031196008;
            } else {
                var4 = 0.02078148;
            }
        } else {
            var4 = -0.05622176;
        }
    } else {
        if (features[4] < -0.999716) {
            if (features[0] < 167.8861) {
                var4 = -0.0561528;
            } else {
                var4 = 0.023397718;
            }
        } else {
            if (features[0] < 181.42607) {
                var4 = 0.04782706;
            } else {
                var4 = -0.011459859;
            }
        }
    }
    double var5;
    if (features[2] < 25.03) {
        if (features[3] < -0.9407) {
            var5 = -0.021143816;
        } else {
            var5 = 0.048960295;
        }
    } else {
        if (features[3] < 4.1094) {
            if (features[3] < -0.8758) {
                var5 = 0.012152261;
            } else {
                var5 = -0.045903493;
            }
        } else {
            var5 = 0.026925236;
        }
    }
    double var6;
    if (features[0] < 83.8149) {
        if (features[5] < 0.005243) {
            if (features[3] < 2.3801) {
                var6 = 0.043429714;
            } else {
                var6 = -0.022568544;
            }
        } else {
            if (features[0] < 53.218872) {
                var6 = -0.01066543;
            } else {
                var6 = -0.060930807;
            }
        }
    } else {
        if (features[6] < 0.000039) {
            if (features[2] < 24.74) {
                var6 = 0.0109734405;
            } else {
                var6 = -0.037758704;
            }
        } else {
            if (features[6] < 0.000179) {
                var6 = 0.04683558;
            } else {
                var6 = 0.011141958;
            }
        }
    }
    double var7;
    if (features[6] < 0.000038) {
        if (features[6] < 0.000026) {
            var7 = 0.002797975;
        } else {
            var7 = -0.05247701;
        }
    } else {
        if (features[6] < 0.000088) {
            if (features[5] < 0.003788) {
                var7 = 0.011159878;
            } else {
                var7 = 0.053857833;
            }
        } else {
            if (features[6] < 0.000119) {
                var7 = -0.03666047;
            } else {
                var7 = 0.0040618978;
            }
        }
    }
    double var8;
    if (features[2] < 24.95) {
        if (features[3] < -0.9407) {
            var8 = -0.04650795;
        } else {
            if (features[2] < 20.05) {
                var8 = 0.016567176;
            } else {
                var8 = 0.054037035;
            }
        }
    } else {
        if (features[2] < 32.57) {
            var8 = -0.051459014;
        } else {
            if (features[2] < 37.35) {
                var8 = 0.031118248;
            } else {
                var8 = -0.01617136;
            }
        }
    }
    double var9;
    if (features[5] < 0.003788) {
        if (features[5] < 0.002071) {
            var9 = 0.015256266;
        } else {
            if (features[4] < -0.999644) {
                var9 = -0.063307814;
            } else {
                var9 = -0.008521386;
            }
        }
    } else {
        if (features[6] < 0.000384) {
            if (features[5] < 0.008999) {
                var9 = 0.0036912092;
            } else {
                var9 = 0.044061553;
            }
        } else {
            var9 = -0.02620026;
        }
    }
    double var10;
    if (features[6] < 0.000039) {
        if (features[6] < 0.000026) {
            var10 = -0.005330016;
        } else {
            var10 = -0.039064687;
        }
    } else {
        if (features[6] < 0.000088) {
            if (features[4] < -0.999605) {
                var10 = 0.042440664;
            } else {
                var10 = -0.0062941955;
            }
        } else {
            if (features[6] < 0.000112) {
                var10 = -0.04116077;
            } else {
                var10 = 0.0086016515;
            }
        }
    }
    double var11;
    if (features[1] < 0.000042) {
        if (features[3] < 2.4052) {
            if (features[3] < -1.1325) {
                var11 = -0.014233413;
            } else {
                var11 = 0.056322332;
            }
        } else {
            if (features[3] < 4.1094) {
                var11 = -0.037805106;
            } else {
                var11 = 0.02429923;
            }
        }
    } else {
        if (features[5] < 0.012532) {
            var11 = -0.057708155;
        } else {
            var11 = -0.007106699;
        }
    }
    double var12;
    if (features[3] < 4.1094) {
        if (features[2] < 25.03) {
            if (features[3] < -1.2921) {
                var12 = -0.012125174;
            } else {
                var12 = 0.027489547;
            }
        } else {
            if (features[3] < -2.5399) {
                var12 = 0.010330807;
            } else {
                var12 = -0.04423465;
            }
        }
    } else {
        var12 = 0.041902304;
    }
    double var13;
    if (features[1] < 0.000042) {
        if (features[3] < 2.4052) {
            if (features[3] < -1.1325) {
                var13 = -0.01619543;
            } else {
                var13 = 0.054008454;
            }
        } else {
            if (features[3] < 4.1094) {
                var13 = -0.04181894;
            } else {
                var13 = 0.01561446;
            }
        }
    } else {
        if (features[2] < 37.35) {
            var13 = -0.047524992;
        } else {
            var13 = -0.005728951;
        }
    }
    double var14;
    if (features[2] < 25.03) {
        if (features[1] < 0.000033) {
            if (features[4] < -0.999714) {
                var14 = 0.00418842;
            } else {
                var14 = 0.055695515;
            }
        } else {
            var14 = -0.008867664;
        }
    } else {
        if (features[2] < 32.57) {
            if (features[1] < 0.000032) {
                var14 = -0.051614232;
            } else {
                var14 = -0.0080366805;
            }
        } else {
            if (features[2] < 36.21) {
                var14 = 0.05781541;
            } else {
                var14 = -0.015794137;
            }
        }
    }
    double var15;
    if (features[5] < 0.003788) {
        if (features[4] < -0.999644) {
            var15 = -0.04481918;
        } else {
            if (features[4] < -0.999581) {
                var15 = 0.03283567;
            } else {
                var15 = -0.020465344;
            }
        }
    } else {
        if (features[1] < 0.000042) {
            if (features[3] < 0.4845) {
                var15 = 0.044889614;
            } else {
                var15 = 0.00066092814;
            }
        } else {
            if (features[5] < 0.012101) {
                var15 = -0.047262646;
            } else {
                var15 = 0.015270369;
            }
        }
    }
    double var16;
    if (features[6] < 0.000039) {
        if (features[6] < 0.000019) {
            var16 = -0.0053488724;
        } else {
            var16 = -0.035885308;
        }
    } else {
        if (features[0] < 78.70345) {
            if (features[5] < 0.003964) {
                var16 = 0.026314935;
            } else {
                var16 = -0.03519273;
            }
        } else {
            if (features[2] < 35.59) {
                var16 = 0.047339093;
            } else {
                var16 = 0.0042148493;
            }
        }
    }
    double var17;
    if (features[0] < 47.879524) {
        if (features[4] < -0.999602) {
            var17 = 0.009223994;
        } else {
            var17 = -0.052783545;
        }
    } else {
        if (features[6] < 0.000039) {
            if (features[3] < 1.8738) {
                var17 = -0.027379567;
            } else {
                var17 = -0.0022319413;
            }
        } else {
            if (features[6] < 0.000083) {
                var17 = 0.05823758;
            } else {
                var17 = 0.008488132;
            }
        }
    }
    double var18;
    if (features[1] < 0.000041) {
        if (features[4] < -0.999714) {
            if (features[4] < -0.999753) {
                var18 = 0.011939942;
            } else {
                var18 = -0.035491165;
            }
        } else {
            if (features[0] < 58.492466) {
                var18 = -0.007983656;
            } else {
                var18 = 0.040942352;
            }
        }
    } else {
        if (features[5] < 0.012101) {
            var18 = -0.052245814;
        } else {
            var18 = -0.004184965;
        }
    }
    double var19;
    if (features[1] < 0.000042) {
        if (features[4] < -0.999714) {
            if (features[0] < 167.8861) {
                var19 = -0.058153838;
            } else {
                var19 = 0.021608433;
            }
        } else {
            if (features[1] < 0.000023) {
                var19 = 0.053474586;
            } else {
                var19 = 0.0102493465;
            }
        }
    } else {
        if (features[4] < -0.999604) {
            var19 = -0.0041480376;
        } else {
            var19 = -0.044788014;
        }
    }
    double var20;
    if (features[4] < -0.999714) {
        if (features[0] < 167.8861) {
            if (features[0] < 114.834946) {
                var20 = -0.010106226;
            } else {
                var20 = -0.05511693;
            }
        } else {
            var20 = -0.0035463334;
        }
    } else {
        if (features[1] < 0.000042) {
            if (features[5] < 0.003976) {
                var20 = -0.0000015396712;
            } else {
                var20 = 0.04249235;
            }
        } else {
            if (features[4] < -0.999604) {
                var20 = -0.0024098544;
            } else {
                var20 = -0.047484986;
            }
        }
    }
    double var21;
    if (features[3] < 4.1094) {
        if (features[3] < 3.6671) {
            if (features[6] < 0.000062) {
                var21 = -0.031432237;
            } else {
                var21 = 0.007357031;
            }
        } else {
            var21 = -0.053651106;
        }
    } else {
        var21 = 0.03478856;
    }
    double var22;
    if (features[5] < 0.008999) {
        if (features[2] < 36.21) {
            if (features[2] < 30.84) {
                var22 = -0.018170627;
            } else {
                var22 = 0.04242624;
            }
        } else {
            var22 = -0.04333807;
        }
    } else {
        if (features[4] < -0.999605) {
            var22 = 0.060470354;
        } else {
            var22 = -0.007250629;
        }
    }
    double var23;
    if (features[4] < -0.999756) {
        var23 = 0.03570233;
    } else {
        if (features[2] < 49.88) {
            if (features[3] < 0.9228) {
                var23 = 0.002388417;
            } else {
                var23 = -0.033834618;
            }
        } else {
            var23 = 0.024539893;
        }
    }
    double var24;
    if (features[4] < -0.999714) {
        if (features[3] < -0.9407) {
            var24 = -0.041747853;
        } else {
            if (features[6] < 0.000039) {
                var24 = -0.022856323;
            } else {
                var24 = 0.026227439;
            }
        }
    } else {
        if (features[1] < 0.000042) {
            if (features[3] < 0.9228) {
                var24 = 0.055675603;
            } else {
                var24 = -0.0052736374;
            }
        } else {
            var24 = -0.02216859;
        }
    }
    double var25;
    if (features[2] < 49.88) {
        if (features[2] < 25.03) {
            if (features[3] < -0.9407) {
                var25 = -0.018190922;
            } else {
                var25 = 0.029044453;
            }
        } else {
            if (features[5] < 0.010141) {
                var25 = -0.040719524;
            } else {
                var25 = 0.00032128443;
            }
        }
    } else {
        var25 = 0.035829503;
    }
    double var26;
    if (features[0] < 182.21187) {
        if (features[1] < 0.000042) {
            if (features[3] < 1.7022) {
                var26 = 0.03647498;
            } else {
                var26 = -0.009368583;
            }
        } else {
            var26 = -0.036167026;
        }
    } else {
        var26 = -0.03552083;
    }
    double var27;
    if (features[4] < -0.999627) {
        if (features[2] < 18.3) {
            var27 = 0.03530021;
        } else {
            if (features[0] < 119.32837) {
                var27 = -0.012409357;
            } else {
                var27 = -0.04207634;
            }
        }
    } else {
        if (features[4] < -0.999605) {
            var27 = 0.049947996;
        } else {
            if (features[1] < 0.000041) {
                var27 = 0.012725003;
            } else {
                var27 = -0.03955747;
            }
        }
    }
    double var28;
    if (features[5] < 0.003788) {
        if (features[2] < 24.74) {
            var28 = -0.008683853;
        } else {
            var28 = -0.0546768;
        }
    } else {
        if (features[0] < 78.70345) {
            if (features[0] < 53.218872) {
                var28 = 0.0070648575;
            } else {
                var28 = -0.039355963;
            }
        } else {
            if (features[0] < 182.21187) {
                var28 = 0.035893805;
            } else {
                var28 = -0.017091027;
            }
        }
    }
    double var29;
    if (features[6] < 0.000038) {
        var29 = -0.041310262;
    } else {
        if (features[0] < 78.70345) {
            if (features[1] < 0.00004) {
                var29 = 0.004279319;
            } else {
                var29 = -0.045928128;
            }
        } else {
            if (features[2] < 35.59) {
                var29 = 0.03619556;
            } else {
                var29 = 0.0020319761;
            }
        }
    }
    double var30;
    if (features[1] < 0.000042) {
        if (features[3] < 0.9228) {
            if (features[5] < 0.003788) {
                var30 = 0.0075925314;
            } else {
                var30 = 0.053274423;
            }
        } else {
            if (features[3] < 4.1094) {
                var30 = -0.027786672;
            } else {
                var30 = 0.013317919;
            }
        }
    } else {
        var30 = -0.05403776;
    }
    double var31;
    if (features[3] < -1.1325) {
        if (features[2] < 30.46) {
            var31 = -0.047418132;
        } else {
            var31 = 0.014200385;
        }
    } else {
        if (features[2] < 25.03) {
            if (features[5] < 0.005904) {
                var31 = 0.00136561;
            } else {
                var31 = 0.048421305;
            }
        } else {
            if (features[2] < 32.57) {
                var31 = -0.03132926;
            } else {
                var31 = 0.007401261;
            }
        }
    }
    double var32;
    if (features[1] < 0.000042) {
        if (features[3] < 2.4052) {
            if (features[6] < 0.000032) {
                var32 = -0.024601812;
            } else {
                var32 = 0.03438111;
            }
        } else {
            if (features[3] < 4.1094) {
                var32 = -0.032327715;
            } else {
                var32 = 0.01504103;
            }
        }
    } else {
        if (features[4] < -0.999605) {
            var32 = -0.0045145187;
        } else {
            var32 = -0.038603444;
        }
    }
    double var33;
    if (features[0] < 181.42607) {
        if (features[0] < 167.8861) {
            if (features[4] < -0.999714) {
                var33 = -0.044227865;
            } else {
                var33 = 0.0071868612;
            }
        } else {
            var33 = 0.054300405;
        }
    } else {
        var33 = -0.030364692;
    }
    double var34;
    if (features[5] < 0.006713) {
        if (features[3] < 0.6248) {
            if (features[4] < -0.999724) {
                var34 = -0.031231165;
            } else {
                var34 = 0.019489324;
            }
        } else {
            if (features[6] < 0.00005) {
                var34 = 0.00077107106;
            } else {
                var34 = -0.042468816;
            }
        }
    } else {
        if (features[6] < 0.000225) {
            if (features[3] < 1.7022) {
                var34 = 0.03202505;
            } else {
                var34 = -0.010833403;
            }
        } else {
            var34 = -0.015655559;
        }
    }
    double var35;
    if (features[5] < 0.005243) {
        if (features[3] < 2.4052) {
            if (features[6] < 0.000062) {
                var35 = 0.0068740114;
            } else {
                var35 = 0.048570115;
            }
        } else {
            if (features[3] < 4.1094) {
                var35 = -0.03187205;
            } else {
                var35 = 0.02854975;
            }
        }
    } else {
        if (features[1] < 0.000023) {
            var35 = -0.038476963;
        } else {
            if (features[1] < 0.000042) {
                var35 = 0.02318082;
            } else {
                var35 = -0.022332426;
            }
        }
    }
    double var36;
    if (features[2] < 49.95) {
        if (features[2] < 36.21) {
            if (features[2] < 32.57) {
                var36 = -0.010031173;
            } else {
                var36 = 0.048841618;
            }
        } else {
            var36 = -0.047793888;
        }
    } else {
        var36 = 0.03150827;
    }
    double var37;
    if (features[0] < 182.21187) {
        if (features[0] < 167.8861) {
            if (features[0] < 124.5122) {
                var37 = 0.003711259;
            } else {
                var37 = -0.043884948;
            }
        } else {
            var37 = 0.055800814;
        }
    } else {
        var37 = -0.028978288;
    }
    double var38;
    if (features[1] < 0.000041) {
        if (features[4] < -0.999627) {
            if (features[4] < -0.999737) {
                var38 = 0.030821744;
            } else {
                var38 = -0.012630022;
            }
        } else {
            if (features[4] < -0.999581) {
                var38 = 0.05119741;
            } else {
                var38 = 0.007538238;
            }
        }
    } else {
        if (features[0] < 78.70345) {
            var38 = -0.045303922;
        } else {
            var38 = 0.013733146;
        }
    }
    double var39;
    if (features[2] < 25.03) {
        if (features[3] < -0.9407) {
            var39 = -0.011530438;
        } else {
            if (features[1] < 0.000031) {
                var39 = 0.053270496;
            } else {
                var39 = 0.0082821725;
            }
        }
    } else {
        if (features[1] < 0.000023) {
            if (features[6] < 0.000047) {
                var39 = -0.02603284;
            } else {
                var39 = 0.027068675;
            }
        } else {
            if (features[1] < 0.000032) {
                var39 = -0.05447055;
            } else {
                var39 = -0.008201416;
            }
        }
    }
    double var40;
    if (features[2] < 30.84) {
        if (features[2] < 25.03) {
            if (features[3] < -0.9407) {
                var40 = -0.017340565;
            } else {
                var40 = 0.016876878;
            }
        } else {
            if (features[1] < 0.000032) {
                var40 = -0.049924638;
            } else {
                var40 = -0.007741023;
            }
        }
    } else {
        if (features[3] < 3.5864) {
            if (features[1] < 0.000042) {
                var40 = 0.048476662;
            } else {
                var40 = -0.00771236;
            }
        } else {
            var40 = -0.012993696;
        }
    }
    double var41;
    if (features[0] < 181.42607) {
        if (features[4] < -0.999592) {
            if (features[3] < -1.1325) {
                var41 = 0.004234339;
            } else {
                var41 = 0.041079666;
            }
        } else {
            if (features[4] < -0.999543) {
                var41 = -0.03860193;
            } else {
                var41 = 0.01175747;
            }
        }
    } else {
        if (features[3] < 1.2536) {
            var41 = -0.046546888;
        } else {
            var41 = 0.012790759;
        }
    }
    double var42;
    if (features[3] < 4.1094) {
        if (features[1] < 0.000041) {
            if (features[5] < 0.003788) {
                var42 = -0.023533411;
            } else {
                var42 = 0.010944437;
            }
        } else {
            var42 = -0.047983214;
        }
    } else {
        var42 = 0.026274279;
    }
    double var43;
    if (features[0] < 49.535843) {
        if (features[0] < 37.35741) {
            var43 = -0.0040105553;
        } else {
            var43 = -0.047847994;
        }
    } else {
        if (features[4] < -0.999603) {
            if (features[5] < 0.003788) {
                var43 = -0.02738805;
            } else {
                var43 = 0.008641354;
            }
        } else {
            var43 = 0.046559192;
        }
    }
    double var44;
    if (features[2] < 21.61) {
        if (features[3] < -0.1707) {
            var44 = 0.00015693503;
        } else {
            var44 = 0.047086384;
        }
    } else {
        if (features[2] < 32.57) {
            if (features[3] < 1.7022) {
                var44 = 0.0017317524;
            } else {
                var44 = -0.044817213;
            }
        } else {
            if (features[2] < 36.21) {
                var44 = 0.047676407;
            } else {
                var44 = -0.0010015462;
            }
        }
    }
    double var45;
    if (features[0] < 49.535843) {
        if (features[0] < 32.161324) {
            var45 = 0.011210284;
        } else {
            var45 = -0.051291574;
        }
    } else {
        if (features[0] < 68.0324) {
            var45 = 0.021697855;
        } else {
            if (features[0] < 167.8861) {
                var45 = -0.02306719;
            } else {
                var45 = 0.010130585;
            }
        }
    }
    double var46;
    if (features[1] < 0.000042) {
        if (features[1] < 0.000032) {
            if (features[6] < 0.000053) {
                var46 = 0.017824309;
            } else {
                var46 = -0.016564602;
            }
        } else {
            if (features[3] < 1.7022) {
                var46 = 0.04521263;
            } else {
                var46 = 0.008753035;
            }
        }
    } else {
        if (features[0] < 62.079117) {
            var46 = -0.04093284;
        } else {
            var46 = 0.014325823;
        }
    }
    double var47;
    if (features[0] < 167.8861) {
        if (features[0] < 121.27486) {
            if (features[1] < 0.000042) {
                var47 = 0.015505667;
            } else {
                var47 = -0.032023184;
            }
        } else {
            var47 = -0.040154763;
        }
    } else {
        if (features[0] < 182.21187) {
            var47 = 0.05278319;
        } else {
            var47 = -0.006493725;
        }
    }
    double var48;
    if (features[5] < 0.008999) {
        if (features[2] < 24.65) {
            if (features[0] < 74.24292) {
                var48 = -0.0077967416;
            } else {
                var48 = 0.044700805;
            }
        } else {
            if (features[2] < 30.84) {
                var48 = -0.043791752;
            } else {
                var48 = -0.0033199934;
            }
        }
    } else {
        if (features[3] < -0.4412) {
            var48 = 0.0071874536;
        } else {
            var48 = 0.04957148;
        }
    }
    double var49;
    if (features[2] < 25.03) {
        if (features[2] < 20.05) {
            if (features[5] < 0.004926) {
                var49 = 0.013519036;
            } else {
                var49 = -0.03434079;
            }
        } else {
            if (features[5] < 0.003397) {
                var49 = 0.009497474;
            } else {
                var49 = 0.046574008;
            }
        }
    } else {
        if (features[2] < 30.84) {
            var49 = -0.034836132;
        } else {
            if (features[2] < 36.21) {
                var49 = 0.04141428;
            } else {
                var49 = -0.02349215;
            }
        }
    }
    double var50;
    if (features[4] < -0.999528) {
        if (features[4] < -0.999543) {
            if (features[4] < -0.999605) {
                var50 = 0.014697969;
            } else {
                var50 = -0.021991855;
            }
        } else {
            var50 = 0.044243895;
        }
    } else {
        var50 = -0.025556361;
    }
    double var51;
    if (features[2] < 20.05) {
        var51 = -0.036489144;
    } else {
        if (features[2] < 25.03) {
            if (features[1] < 0.000013) {
                var51 = 0.0017607337;
            } else {
                var51 = 0.030908687;
            }
        } else {
            if (features[2] < 30.46) {
                var51 = -0.040099785;
            } else {
                var51 = 0.0033850407;
            }
        }
    }
    double var52;
    if (features[0] < 182.21187) {
        if (features[0] < 167.8861) {
            if (features[5] < 0.002921) {
                var52 = 0.022575771;
            } else {
                var52 = -0.012295251;
            }
        } else {
            var52 = 0.05148529;
        }
    } else {
        var52 = -0.04103436;
    }
    double var53;
    if (features[3] < 4.0586) {
        if (features[3] < 3.6671) {
            if (features[4] < -0.999603) {
                var53 = -0.0035125443;
            } else {
                var53 = 0.026544154;
            }
        } else {
            var53 = -0.035584226;
        }
    } else {
        var53 = 0.0370945;
    }
    double var54;
    if (features[0] < 78.70345) {
        if (features[5] < 0.003859) {
            if (features[5] < 0.002748) {
                var54 = 0.0017565874;
            } else {
                var54 = 0.027319634;
            }
        } else {
            if (features[0] < 53.218872) {
                var54 = 0.0012997912;
            } else {
                var54 = -0.047860127;
            }
        }
    } else {
        if (features[5] < 0.003788) {
            if (features[5] < 0.002958) {
                var54 = -0.0020940807;
            } else {
                var54 = -0.023251727;
            }
        } else {
            if (features[0] < 182.21187) {
                var54 = 0.040263467;
            } else {
                var54 = -0.0052591595;
            }
        }
    }
    double var55;
    if (features[2] < 49.95) {
        if (features[2] < 35.59) {
            if (features[2] < 30.46) {
                var55 = -0.014172608;
            } else {
                var55 = 0.025595753;
            }
        } else {
            var55 = -0.048672136;
        }
    } else {
        var55 = 0.018553063;
    }
    double var56;
    if (features[2] < 24.95) {
        if (features[3] < -0.9407) {
            var56 = -0.012156257;
        } else {
            if (features[1] < 0.00003) {
                var56 = 0.04901402;
            } else {
                var56 = 0.0064972662;
            }
        }
    } else {
        if (features[3] < 4.1094) {
            if (features[5] < 0.005723) {
                var56 = -0.04338834;
            } else {
                var56 = -0.002473844;
            }
        } else {
            var56 = 0.010695449;
        }
    }
    double var57;
    if (features[3] < 4.1094) {
        if (features[0] < 182.21187) {
            if (features[0] < 167.8861) {
                var57 = -0.016555255;
            } else {
                var57 = 0.050439727;
            }
        } else {
            var57 = -0.049268007;
        }
    } else {
        var57 = 0.024077414;
    }
    double var58;
    if (features[3] < 4.1094) {
        if (features[0] < 182.21187) {
            if (features[0] < 167.8861) {
                var58 = -0.012089305;
            } else {
                var58 = 0.049313724;
            }
        } else {
            var58 = -0.04670955;
        }
    } else {
        var58 = 0.02334408;
    }
    double var59;
    if (features[5] < 0.007226) {
        if (features[0] < 70.983475) {
            if (features[5] < 0.003859) {
                var59 = 0.028268633;
            } else {
                var59 = -0.010203224;
            }
        } else {
            if (features[3] < 0.4845) {
                var59 = -0.0077131414;
            } else {
                var59 = -0.037627544;
            }
        }
    } else {
        if (features[0] < 62.079117) {
            var59 = -0.008032489;
        } else {
            if (features[1] < 0.000037) {
                var59 = 0.009954252;
            } else {
                var59 = 0.043374833;
            }
        }
    }
    double var60;
    if (features[3] < 4.1094) {
        if (features[4] < -0.999603) {
            if (features[4] < -0.999756) {
                var60 = 0.014685866;
            } else {
                var60 = -0.02974164;
            }
        } else {
            if (features[0] < 49.535843) {
                var60 = -0.017049683;
            } else {
                var60 = 0.039725613;
            }
        }
    } else {
        var60 = 0.033848602;
    }
    double var61;
    if (features[1] < 0.000041) {
        if (features[2] < 36.21) {
            if (features[3] < 2.4052) {
                var61 = 0.032782804;
            } else {
                var61 = -0.010209341;
            }
        } else {
            if (features[4] < -0.999627) {
                var61 = -0.036276188;
            } else {
                var61 = 0.004434697;
            }
        }
    } else {
        var61 = -0.019855175;
    }
    double var62;
    if (features[0] < 182.21187) {
        if (features[2] < 20.05) {
            var62 = -0.014440775;
        } else {
            if (features[3] < 3.6671) {
                var62 = 0.0347504;
            } else {
                var62 = 0.0020086572;
            }
        }
    } else {
        var62 = -0.020835439;
    }
    double var63;
    if (features[3] < 4.1094) {
        if (features[0] < 181.42607) {
            if (features[0] < 63.811626) {
                var63 = -0.02237037;
            } else {
                var63 = 0.021569254;
            }
        } else {
            var63 = -0.04641246;
        }
    } else {
        var63 = 0.03270271;
    }
    double var64;
    if (features[0] < 167.8861) {
        if (features[1] < 0.000041) {
            if (features[4] < -0.999714) {
                var64 = -0.027186973;
            } else {
                var64 = 0.012827869;
            }
        } else {
            var64 = -0.03933206;
        }
    } else {
        if (features[0] < 182.21187) {
            var64 = 0.047324084;
        } else {
            var64 = -0.011851995;
        }
    }
    double var65;
    if (features[6] < 0.000128) {
        if (features[2] < 30.78) {
            if (features[0] < 167.8861) {
                var65 = -0.03006137;
            } else {
                var65 = 0.009964938;
            }
        } else {
            if (features[2] < 36.21) {
                var65 = 0.038420588;
            } else {
                var65 = -0.020815434;
            }
        }
    } else {
        if (features[6] < 0.000201) {
            var65 = 0.034502126;
        } else {
            if (features[3] < 1.2536) {
                var65 = -0.03503724;
            } else {
                var65 = 0.03162561;
            }
        }
    }
    double var66;
    if (features[1] < 0.000042) {
        if (features[4] < -0.999627) {
            if (features[6] < 0.000051) {
                var66 = 0.010765572;
            } else {
                var66 = -0.029843492;
            }
        } else {
            if (features[3] < 0.9228) {
                var66 = 0.0504055;
            } else {
                var66 = -0.0002985541;
            }
        }
    } else {
        var66 = -0.026810152;
    }
    double var67;
    if (features[1] < 0.000042) {
        if (features[0] < 38.012768) {
            var67 = 0.036823787;
        } else {
            if (features[4] < -0.999714) {
                var67 = -0.019085882;
            } else {
                var67 = 0.008662171;
            }
        }
    } else {
        if (features[5] < 0.012532) {
            var67 = -0.03597072;
        } else {
            var67 = 0.0007827215;
        }
    }
    double var68;
    if (features[1] < 0.00001) {
        if (features[2] < 20.72) {
            var68 = 0.03922316;
        } else {
            var68 = -0.0011921296;
        }
    } else {
        if (features[2] < 49.95) {
            if (features[2] < 36.21) {
                var68 = -0.0015388503;
            } else {
                var68 = -0.040090453;
            }
        } else {
            var68 = 0.027050717;
        }
    }
    double var69;
    if (features[3] < 4.1094) {
        if (features[2] < 18.3) {
            var69 = 0.016938508;
        } else {
            if (features[2] < 30.03) {
                var69 = -0.031741165;
            } else {
                var69 = 0.0026641304;
            }
        }
    } else {
        var69 = 0.021141483;
    }
    double var70;
    if (features[4] < -0.999627) {
        if (features[2] < 18.3) {
            var70 = 0.02905275;
        } else {
            if (features[6] < 0.000097) {
                var70 = -0.037824016;
            } else {
                var70 = 0.004784187;
            }
        }
    } else {
        if (features[1] < 0.000042) {
            if (features[3] < 1.5562) {
                var70 = 0.041133318;
            } else {
                var70 = 0.012154285;
            }
        } else {
            if (features[2] < 37.35) {
                var70 = -0.034253366;
            } else {
                var70 = 0.0031597042;
            }
        }
    }
    double var71;
    if (features[0] < 182.21187) {
        if (features[0] < 167.8861) {
            if (features[0] < 124.5122) {
                var71 = 0.006180645;
            } else {
                var71 = -0.03726407;
            }
        } else {
            var71 = 0.044961933;
        }
    } else {
        var71 = -0.028105075;
    }
    double var72;
    if (features[1] < 0.000042) {
        if (features[0] < 38.012768) {
            var72 = 0.03526747;
        } else {
            if (features[6] < 0.000134) {
                var72 = -0.017473668;
            } else {
                var72 = 0.027004082;
            }
        }
    } else {
        if (features[4] < -0.999606) {
            var72 = 0.00024000609;
        } else {
            var72 = -0.0343027;
        }
    }
    double var73;
    if (features[3] < 4.1094) {
        if (features[3] < 0.9228) {
            if (features[4] < -0.999724) {
                var73 = -0.023406453;
            } else {
                var73 = 0.023006536;
            }
        } else {
            if (features[6] < 0.000201) {
                var73 = -0.033242162;
            } else {
                var73 = 0.009535738;
            }
        }
    } else {
        var73 = 0.032801364;
    }
    double var74;
    if (features[1] < 0.000042) {
        if (features[1] < 0.000015) {
            if (features[0] < 114.834946) {
                var74 = 0.006589575;
            } else {
                var74 = -0.027731342;
            }
        } else {
            if (features[2] < 20.56) {
                var74 = -0.007829804;
            } else {
                var74 = 0.029177606;
            }
        }
    } else {
        var74 = -0.025383368;
    }
    double var75;
    if (features[5] < 0.006713) {
        if (features[4] < -0.999543) {
            if (features[0] < 167.8861) {
                var75 = -0.028749082;
            } else {
                var75 = 0.012739572;
            }
        } else {
            var75 = 0.012299709;
        }
    } else {
        if (features[1] < 0.000042) {
            if (features[0] < 179.93842) {
                var75 = 0.048589483;
            } else {
                var75 = -0.010086391;
            }
        } else {
            var75 = -0.013012329;
        }
    }
    double var76;
    if (features[2] < 25.03) {
        if (features[2] < 20.05) {
            if (features[4] < -0.999714) {
                var76 = 0.011514372;
            } else {
                var76 = -0.028528828;
            }
        } else {
            var76 = 0.0410384;
        }
    } else {
        if (features[3] < 4.1094) {
            if (features[0] < 70.983475) {
                var76 = 0.007940634;
            } else {
                var76 = -0.036826994;
            }
        } else {
            var76 = 0.018751016;
        }
    }
    double var77;
    if (features[2] < 36.21) {
        if (features[2] < 30.84) {
            if (features[0] < 38.012768) {
                var77 = 0.02165176;
            } else {
                var77 = -0.017351447;
            }
        } else {
            var77 = 0.049158815;
        }
    } else {
        if (features[2] < 49.95) {
            if (features[0] < 115.90355) {
                var77 = -0.046816107;
            } else {
                var77 = 0.0008918067;
            }
        } else {
            var77 = 0.007197302;
        }
    }
    double var78;
    if (features[2] < 49.95) {
        if (features[2] < 24.65) {
            if (features[3] < -0.9407) {
                var78 = -0.011517539;
            } else {
                var78 = 0.0242125;
            }
        } else {
            if (features[5] < 0.003274) {
                var78 = -0.04016029;
            } else {
                var78 = -0.0034595951;
            }
        }
    } else {
        var78 = 0.030930731;
    }
    double var79;
    if (features[2] < 49.88) {
        if (features[2] < 35.59) {
            if (features[2] < 30.84) {
                var79 = -0.006859187;
            } else {
                var79 = 0.035386767;
            }
        } else {
            if (features[6] < 0.000162) {
                var79 = -0.038766693;
            } else {
                var79 = 0.0053416244;
            }
        }
    } else {
        var79 = 0.029215002;
    }
    double var80;
    if (features[3] < -1.1325) {
        if (features[2] < 30.46) {
            var80 = -0.04406918;
        } else {
            var80 = 0.009407266;
        }
    } else {
        if (features[2] < 36.21) {
            if (features[1] < 0.000031) {
                var80 = 0.03409116;
            } else {
                var80 = -0.0069295466;
            }
        } else {
            if (features[6] < 0.000162) {
                var80 = -0.04350035;
            } else {
                var80 = 0.018587774;
            }
        }
    }
    double var81;
    if (features[3] < 4.1094) {
        if (features[2] < 18.72) {
            var81 = 0.018725203;
        } else {
            if (features[6] < 0.000062) {
                var81 = -0.03802097;
            } else {
                var81 = -0.00026805195;
            }
        }
    } else {
        var81 = 0.022954939;
    }
    double var82;
    if (features[5] < 0.008999) {
        if (features[6] < 0.000053) {
            if (features[3] < -1.418) {
                var82 = -0.014217684;
            } else {
                var82 = 0.025907857;
            }
        } else {
            if (features[0] < 38.012768) {
                var82 = 0.020076098;
            } else {
                var82 = -0.026109422;
            }
        }
    } else {
        if (features[1] < 0.000042) {
            var82 = 0.04092898;
        } else {
            var82 = -0.00043535396;
        }
    }
    double var83;
    if (features[4] < -0.999537) {
        if (features[0] < 182.21187) {
            if (features[3] < 3.6671) {
                var83 = 0.02062982;
            } else {
                var83 = -0.012160949;
            }
        } else {
            var83 = -0.015806077;
        }
    } else {
        var83 = -0.021633182;
    }
    double var84;
    if (features[2] < 49.88) {
        if (features[2] < 36.21) {
            if (features[2] < 32.57) {
                var84 = -0.0077657537;
            } else {
                var84 = 0.0399916;
            }
        } else {
            if (features[5] < 0.00741) {
                var84 = -0.035828095;
            } else {
                var84 = 0.0023696416;
            }
        }
    } else {
        var84 = 0.023192624;
    }
    double var85;
    if (features[2] < 25.03) {
        if (features[3] < -0.9407) {
            var85 = -0.006010502;
        } else {
            var85 = 0.037930723;
        }
    } else {
        if (features[4] < -0.999627) {
            if (features[2] < 35.59) {
                var85 = -0.007273345;
            } else {
                var85 = -0.036198027;
            }
        } else {
            if (features[4] < -0.999605) {
                var85 = 0.023021856;
            } else {
                var85 = -0.014253944;
            }
        }
    }
    double var86;
    if (features[0] < 83.8149) {
        if (features[0] < 68.0324) {
            if (features[1] < 0.000037) {
                var86 = 0.017126566;
            } else {
                var86 = -0.029514525;
            }
        } else {
            var86 = -0.032961175;
        }
    } else {
        if (features[0] < 182.21187) {
            if (features[0] < 153.5601) {
                var86 = 0.010678983;
            } else {
                var86 = 0.044517215;
            }
        } else {
            var86 = -0.015669962;
        }
    }
    double var87;
    if (features[2] < 30.84) {
        if (features[2] < 25.03) {
            if (features[1] < 0.000023) {
                var87 = -0.015744263;
            } else {
                var87 = 0.017044676;
            }
        } else {
            if (features[3] < -1.0137) {
                var87 = -0.0016581519;
            } else {
                var87 = -0.039677914;
            }
        }
    } else {
        if (features[2] < 36.21) {
            var87 = 0.035849463;
        } else {
            if (features[5] < 0.010141) {
                var87 = -0.01899177;
            } else {
                var87 = 0.027499575;
            }
        }
    }
    double var88;
    if (features[6] < 0.000071) {
        if (features[3] < -0.9407) {
            var88 = -0.008156048;
        } else {
            if (features[3] < 2.4052) {
                var88 = 0.033622574;
            } else {
                var88 = 0.005239;
            }
        }
    } else {
        if (features[0] < 83.8149) {
            if (features[4] < -0.999592) {
                var88 = -0.0072432566;
            } else {
                var88 = -0.040763598;
            }
        } else {
            if (features[0] < 124.5122) {
                var88 = 0.032483254;
            } else {
                var88 = -0.024029141;
            }
        }
    }
    double var89;
    if (features[3] < 2.6519) {
        if (features[6] < 0.000225) {
            if (features[4] < -0.999714) {
                var89 = -0.002575523;
            } else {
                var89 = 0.035730712;
            }
        } else {
            var89 = -0.022152843;
        }
    } else {
        if (features[3] < 4.1094) {
            var89 = -0.040047307;
        } else {
            var89 = 0.015014122;
        }
    }
    double var90;
    if (features[5] < 0.008999) {
        if (features[3] < 4.1094) {
            if (features[3] < 0.9228) {
                var90 = -0.0027516675;
            } else {
                var90 = -0.040106088;
            }
        } else {
            var90 = 0.013107135;
        }
    } else {
        if (features[4] < -0.999623) {
            var90 = 0.040734343;
        } else {
            var90 = -0.0019622676;
        }
    }
    double var91;
    if (features[3] < -0.9407) {
        if (features[5] < 0.006387) {
            if (features[5] < 0.003788) {
                var91 = -0.034599237;
            } else {
                var91 = -0.009517559;
            }
        } else {
            var91 = 0.009438711;
        }
    } else {
        if (features[2] < 24.65) {
            var91 = 0.042252187;
        } else {
            if (features[2] < 49.95) {
                var91 = -0.0121421935;
            } else {
                var91 = 0.021864638;
            }
        }
    }
    double var92;
    if (features[2] < 20.05) {
        var92 = -0.035653517;
    } else {
        if (features[3] < 4.1094) {
            if (features[3] < 3.6671) {
                var92 = 0.007815739;
            } else {
                var92 = -0.033704426;
            }
        } else {
            var92 = 0.029406277;
        }
    }
    double var93;
    if (features[2] < 49.95) {
        if (features[2] < 35.42) {
            if (features[3] < -0.9407) {
                var93 = -0.02162289;
            } else {
                var93 = 0.010864838;
            }
        } else {
            if (features[0] < 115.90355) {
                var93 = -0.042844158;
            } else {
                var93 = -0.005076311;
            }
        }
    } else {
        var93 = 0.017089596;
    }
    double var94;
    if (features[1] < 0.000042) {
        if (features[2] < 36.21) {
            if (features[1] < 0.000023) {
                var94 = 0.0017598997;
            } else {
                var94 = 0.0288475;
            }
        } else {
            if (features[1] < 0.00003) {
                var94 = -0.020780345;
            } else {
                var94 = 0.00015788764;
            }
        }
    } else {
        var94 = -0.019641837;
    }
    double var95;
    if (features[1] < 0.000042) {
        if (features[3] < 2.4052) {
            if (features[3] < 1.4902) {
                var95 = 0.0037284337;
            } else {
                var95 = 0.043243375;
            }
        } else {
            if (features[5] < 0.002593) {
                var95 = -0.0009518098;
            } else {
                var95 = -0.02103403;
            }
        }
    } else {
        if (features[5] < 0.012532) {
            var95 = -0.031613097;
        } else {
            var95 = -0.000489606;
        }
    }
    double var96;
    if (features[2] < 49.95) {
        if (features[6] < 0.000053) {
            if (features[2] < 20.72) {
                var96 = 0.04214709;
            } else {
                var96 = -0.0058825854;
            }
        } else {
            if (features[0] < 32.161324) {
                var96 = 0.012769835;
            } else {
                var96 = -0.02159837;
            }
        }
    } else {
        var96 = 0.031020159;
    }
    double var97;
    if (features[5] < 0.005243) {
        if (features[4] < -0.999581) {
            if (features[2] < 35.59) {
                var97 = 0.037614316;
            } else {
                var97 = 0.0009171671;
            }
        } else {
            var97 = -0.0079405485;
        }
    } else {
        if (features[5] < 0.006713) {
            var97 = -0.029853925;
        } else {
            if (features[4] < -0.999624) {
                var97 = 0.022305418;
            } else {
                var97 = -0.015697654;
            }
        }
    }
    double var98;
    if (features[4] < -0.999605) {
        if (features[0] < 182.21187) {
            if (features[4] < -0.999714) {
                var98 = 0.00049886474;
            } else {
                var98 = 0.038389314;
            }
        } else {
            var98 = -0.019619374;
        }
    } else {
        if (features[1] < 0.000026) {
            var98 = 0.004302866;
        } else {
            if (features[4] < -0.999592) {
                var98 = -0.009232776;
            } else {
                var98 = -0.032683294;
            }
        }
    }
    double var99;
    if (features[6] < 0.000053) {
        if (features[5] < 0.003274) {
            var99 = -0.012197434;
        } else {
            var99 = 0.032589685;
        }
    } else {
        if (features[4] < -0.999652) {
            var99 = -0.046694905;
        } else {
            if (features[6] < 0.000223) {
                var99 = 0.012559809;
            } else {
                var99 = -0.02449252;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
