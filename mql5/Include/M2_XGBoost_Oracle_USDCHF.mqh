//+------------------------------------------------------------------+
//| M2_XGBoost_Oracle_USDCHF.mqh |
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
        if (features[2] < 19.59) {
            var0 = 0.071428575;
        } else {
            if (features[2] < 28.58) {
                var0 = -0.0125;
            } else {
                var0 = 0.04418605;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var0 = 0.020000001;
        } else {
            var0 = -0.060000002;
        }
    }
    double var1;
    if (features[1] < 0.000041) {
        if (features[0] < 239.50128) {
            if (features[0] < 74.50584) {
                var1 = 0.017035563;
            } else {
                var1 = 0.05735242;
            }
        } else {
            var1 = -0.0011784558;
        }
    } else {
        if (features[1] < 0.000063) {
            var1 = -0.065364264;
        } else {
            var1 = 0.011446925;
        }
    }
    double var2;
    if (features[1] < 0.000041) {
        if (features[5] < 0.004622) {
            var2 = 0.06761561;
        } else {
            if (features[1] < 0.00001) {
                var2 = -0.030671204;
            } else {
                var2 = 0.038161334;
            }
        }
    } else {
        if (features[1] < 0.00006) {
            var2 = -0.06049198;
        } else {
            var2 = 0.011110984;
        }
    }
    double var3;
    if (features[1] < 0.000052) {
        if (features[5] < 0.004622) {
            if (features[3] < -1.9766) {
                var3 = 0.0076867524;
            } else {
                var3 = 0.06441667;
            }
        } else {
            if (features[2] < 19.59) {
                var3 = 0.06584652;
            } else {
                var3 = -0.0036833477;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var3 = -0.010226263;
        } else {
            var3 = -0.052979726;
        }
    }
    double var4;
    if (features[5] < 0.004622) {
        if (features[2] < 27.19) {
            var4 = 0.003685794;
        } else {
            var4 = 0.06806573;
        }
    } else {
        if (features[2] < 19.2) {
            var4 = 0.04581686;
        } else {
            if (features[3] < -4.0441) {
                var4 = 0.053487796;
            } else {
                var4 = -0.022241829;
            }
        }
    }
    double var5;
    if (features[0] < 81.13815) {
        if (features[2] < 19.96) {
            var5 = 0.034693148;
        } else {
            if (features[0] < 53.54351) {
                var5 = -0.042397834;
            } else {
                var5 = -0.0023245916;
            }
        }
    } else {
        if (features[4] < -0.999834) {
            var5 = -0.013293314;
        } else {
            if (features[6] < 0.000101) {
                var5 = 0.05038045;
            } else {
                var5 = 0.010688546;
            }
        }
    }
    double var6;
    if (features[5] < 0.004622) {
        if (features[3] < 3.7212) {
            if (features[6] < 0.000099) {
                var6 = 0.06650131;
            } else {
                var6 = 0.0067763575;
            }
        } else {
            var6 = -0.017507266;
        }
    } else {
        if (features[2] < 19.57) {
            var6 = 0.043218642;
        } else {
            if (features[3] < -4.0441) {
                var6 = 0.05087925;
            } else {
                var6 = -0.034101956;
            }
        }
    }
    double var7;
    if (features[5] < 0.007826) {
        if (features[4] < -0.999803) {
            if (features[5] < 0.004254) {
                var7 = 0.023628587;
            } else {
                var7 = -0.040901493;
            }
        } else {
            if (features[5] < 0.005179) {
                var7 = 0.012921669;
            } else {
                var7 = 0.054644834;
            }
        }
    } else {
        if (features[3] < -1.6679) {
            if (features[5] < 0.012507) {
                var7 = -0.011022407;
            } else {
                var7 = 0.051244933;
            }
        } else {
            if (features[3] < 1.2628) {
                var7 = -0.05931901;
            } else {
                var7 = -0.013010516;
            }
        }
    }
    double var8;
    if (features[5] < 0.005876) {
        if (features[0] < 116.42616) {
            if (features[5] < 0.00374) {
                var8 = 0.0064190193;
            } else {
                var8 = 0.071966946;
            }
        } else {
            if (features[3] < -0.456) {
                var8 = -0.036168143;
            } else {
                var8 = 0.03665626;
            }
        }
    } else {
        if (features[3] < -1.6679) {
            if (features[2] < 23.09) {
                var8 = -0.010071336;
            } else {
                var8 = 0.0541388;
            }
        } else {
            if (features[2] < 25.94) {
                var8 = 0.029777853;
            } else {
                var8 = -0.034510113;
            }
        }
    }
    double var9;
    if (features[2] < 46.88) {
        if (features[2] < 23.0) {
            if (features[6] < 0.000029) {
                var9 = -0.0030335428;
            } else {
                var9 = 0.0580796;
            }
        } else {
            if (features[3] < -4.0441) {
                var9 = 0.048298713;
            } else {
                var9 = -0.006668584;
            }
        }
    } else {
        var9 = 0.053118058;
    }
    double var10;
    if (features[3] < -4.0441) {
        var10 = 0.05104213;
    } else {
        if (features[5] < 0.007826) {
            if (features[3] < 3.3756) {
                var10 = 0.026932186;
            } else {
                var10 = -0.027855337;
            }
        } else {
            if (features[2] < 25.94) {
                var10 = 0.025348982;
            } else {
                var10 = -0.046376728;
            }
        }
    }
    double var11;
    if (features[1] < 0.000041) {
        if (features[0] < 53.54351) {
            if (features[0] < 34.271854) {
                var11 = 0.03115174;
            } else {
                var11 = -0.034219142;
            }
        } else {
            if (features[1] < 0.00001) {
                var11 = 0.0061845016;
            } else {
                var11 = 0.048113;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var11 = -0.05700902;
        } else {
            var11 = 0.0023322573;
        }
    }
    double var12;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000021) {
            if (features[6] < 0.000067) {
                var12 = 0.027648166;
            } else {
                var12 = -0.042967588;
            }
        } else {
            if (features[1] < 0.000031) {
                var12 = 0.051666975;
            } else {
                var12 = 0.008680938;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var12 = -0.009440656;
        } else {
            var12 = -0.053914666;
        }
    }
    double var13;
    if (features[1] < 0.000041) {
        if (features[2] < 19.98) {
            var13 = 0.04749061;
        } else {
            if (features[2] < 46.88) {
                var13 = -0.0067343167;
            } else {
                var13 = 0.04759405;
            }
        }
    } else {
        if (features[3] < -1.5541) {
            var13 = -0.007943759;
        } else {
            var13 = -0.06112793;
        }
    }
    double var14;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000007) {
            var14 = -0.025425723;
        } else {
            if (features[6] < 0.00008) {
                var14 = 0.037444096;
            } else {
                var14 = 0.0028241824;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var14 = -0.05584943;
        } else {
            var14 = 0.013723145;
        }
    }
    double var15;
    if (features[2] < 46.88) {
        if (features[2] < 19.59) {
            if (features[2] < 17.58) {
                var15 = 0.0010317268;
            } else {
                var15 = 0.048615362;
            }
        } else {
            if (features[3] < -4.0441) {
                var15 = 0.044366937;
            } else {
                var15 = -0.015443498;
            }
        }
    } else {
        var15 = 0.05908983;
    }
    double var16;
    if (features[0] < 53.54351) {
        if (features[2] < 19.65) {
            var16 = 0.030734215;
        } else {
            var16 = -0.04957715;
        }
    } else {
        if (features[5] < 0.004816) {
            var16 = 0.053670872;
        } else {
            if (features[3] < -0.5899) {
                var16 = 0.021161098;
            } else {
                var16 = -0.026854446;
            }
        }
    }
    double var17;
    if (features[0] < 111.446) {
        if (features[0] < 81.13815) {
            if (features[2] < 19.65) {
                var17 = 0.034612123;
            } else {
                var17 = -0.012458906;
            }
        } else {
            var17 = 0.059122033;
        }
    } else {
        if (features[4] < -0.999762) {
            if (features[6] < 0.000045) {
                var17 = -0.020571375;
            } else {
                var17 = 0.042988855;
            }
        } else {
            var17 = -0.05409954;
        }
    }
    double var18;
    if (features[1] < 0.000041) {
        if (features[1] < 0.00001) {
            if (features[0] < 328.27634) {
                var18 = -0.030730663;
            } else {
                var18 = 0.022199394;
            }
        } else {
            if (features[6] < 0.00008) {
                var18 = 0.046442907;
            } else {
                var18 = 0.0049451166;
            }
        }
    } else {
        var18 = -0.049129277;
    }
    double var19;
    if (features[1] < 0.000041) {
        if (features[4] < -0.999816) {
            var19 = -0.014596969;
        } else {
            if (features[0] < 53.54351) {
                var19 = -0.0064835697;
            } else {
                var19 = 0.039714333;
            }
        }
    } else {
        if (features[5] < 0.011602) {
            var19 = -0.05522759;
        } else {
            var19 = -0.0015902249;
        }
    }
    double var20;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000007) {
            var20 = -0.02419561;
        } else {
            if (features[6] < 0.00008) {
                var20 = 0.04128611;
            } else {
                var20 = 0.012329143;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var20 = -0.04633535;
        } else {
            var20 = 0.0071082423;
        }
    }
    double var21;
    if (features[1] < 0.000041) {
        if (features[5] < 0.003656) {
            var21 = -0.007142483;
        } else {
            if (features[1] < 0.00001) {
                var21 = 0.00026964993;
            } else {
                var21 = 0.04115669;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var21 = -0.045005623;
        } else {
            var21 = 0.015538412;
        }
    }
    double var22;
    if (features[5] < 0.004816) {
        if (features[5] < 0.003656) {
            if (features[5] < 0.003244) {
                var22 = 0.047635168;
            } else {
                var22 = -0.042491835;
            }
        } else {
            var22 = 0.055532556;
        }
    } else {
        if (features[2] < 19.96) {
            if (features[6] < 0.00005) {
                var22 = 0.002288345;
            } else {
                var22 = 0.045417283;
            }
        } else {
            if (features[0] < 58.47312) {
                var22 = -0.044665795;
            } else {
                var22 = -0.0012128922;
            }
        }
    }
    double var23;
    if (features[5] < 0.007826) {
        if (features[4] < -0.999816) {
            if (features[2] < 23.0) {
                var23 = 0.02192318;
            } else {
                var23 = -0.036573336;
            }
        } else {
            if (features[5] < 0.005181) {
                var23 = 0.013025112;
            } else {
                var23 = 0.057264615;
            }
        }
    } else {
        if (features[5] < 0.011602) {
            if (features[6] < 0.000181) {
                var23 = -0.055398103;
            } else {
                var23 = -0.0046604397;
            }
        } else {
            if (features[3] < -1.6679) {
                var23 = 0.036656585;
            } else {
                var23 = -0.010235131;
            }
        }
    }
    double var24;
    if (features[6] < 0.000029) {
        if (features[3] < -0.6133) {
            var24 = -0.049819417;
        } else {
            var24 = -0.0008670915;
        }
    } else {
        if (features[3] < 1.1782) {
            if (features[0] < 108.36528) {
                var24 = 0.03431296;
            } else {
                var24 = -0.0012210638;
            }
        } else {
            if (features[6] < 0.000063) {
                var24 = 0.016210169;
            } else {
                var24 = -0.038560178;
            }
        }
    }
    double var25;
    if (features[5] < 0.005876) {
        if (features[3] < -1.2931) {
            var25 = -0.0050340127;
        } else {
            if (features[3] < 3.3756) {
                var25 = 0.047670852;
            } else {
                var25 = -0.008255053;
            }
        }
    } else {
        if (features[3] < -1.6679) {
            if (features[2] < 23.09) {
                var25 = -0.011861081;
            } else {
                var25 = 0.031896725;
            }
        } else {
            if (features[0] < 81.13815) {
                var25 = -0.058104314;
            } else {
                var25 = -0.011154452;
            }
        }
    }
    double var26;
    if (features[1] < 0.000041) {
        if (features[0] < 96.89966) {
            if (features[1] < 0.000031) {
                var26 = 0.04942209;
            } else {
                var26 = -0.0037399342;
            }
        } else {
            if (features[2] < 48.17) {
                var26 = -0.0031981946;
            } else {
                var26 = 0.041618984;
            }
        }
    } else {
        if (features[3] < -1.5541) {
            var26 = 0.01525219;
        } else {
            var26 = -0.046466958;
        }
    }
    double var27;
    if (features[0] < 53.54351) {
        if (features[1] < 0.000031) {
            var27 = 0.036846813;
        } else {
            if (features[4] < -0.999654) {
                var27 = -0.0069291675;
            } else {
                var27 = -0.053680714;
            }
        }
    } else {
        if (features[4] < -0.999669) {
            if (features[4] < -0.999761) {
                var27 = 0.021883883;
            } else {
                var27 = -0.03065606;
            }
        } else {
            if (features[6] < 0.000099) {
                var27 = 0.016494883;
            } else {
                var27 = 0.060008716;
            }
        }
    }
    double var28;
    if (features[2] < 46.88) {
        if (features[5] < 0.004622) {
            if (features[5] < 0.003707) {
                var28 = -0.011448975;
            } else {
                var28 = 0.04854538;
            }
        } else {
            if (features[2] < 19.2) {
                var28 = 0.026507333;
            } else {
                var28 = -0.029515868;
            }
        }
    } else {
        var28 = 0.046701416;
    }
    double var29;
    if (features[0] < 53.54351) {
        if (features[2] < 21.58) {
            var29 = 0.022314837;
        } else {
            var29 = -0.05310327;
        }
    } else {
        if (features[4] < -0.999674) {
            if (features[1] < 0.000022) {
                var29 = 0.014804176;
            } else {
                var29 = -0.037268348;
            }
        } else {
            if (features[1] < 0.000024) {
                var29 = 0.004078306;
            } else {
                var29 = 0.047046687;
            }
        }
    }
    double var30;
    if (features[5] < 0.004622) {
        if (features[1] < 0.000025) {
            if (features[2] < 23.0) {
                var30 = 0.013717862;
            } else {
                var30 = 0.05046446;
            }
        } else {
            var30 = -0.0035608911;
        }
    } else {
        if (features[2] < 19.59) {
            var30 = 0.03283233;
        } else {
            if (features[3] < -4.0441) {
                var30 = 0.037831582;
            } else {
                var30 = -0.029622406;
            }
        }
    }
    double var31;
    if (features[0] < 111.446) {
        if (features[0] < 81.13815) {
            if (features[5] < 0.005853) {
                var31 = 0.025653873;
            } else {
                var31 = -0.017569726;
            }
        } else {
            if (features[3] < 1.1288) {
                var31 = 0.05598548;
            } else {
                var31 = 0.012648739;
            }
        }
    } else {
        if (features[4] < -0.999761) {
            if (features[2] < 21.13) {
                var31 = -0.027213434;
            } else {
                var31 = 0.026501393;
            }
        } else {
            var31 = -0.051739313;
        }
    }
    double var32;
    if (features[1] < 0.000031) {
        if (features[3] < 3.3756) {
            if (features[4] < -0.999816) {
                var32 = -0.013332821;
            } else {
                var32 = 0.033549726;
            }
        } else {
            var32 = -0.022298511;
        }
    } else {
        if (features[3] < -2.6973) {
            var32 = 0.0137226945;
        } else {
            if (features[6] < 0.000232) {
                var32 = -0.049134154;
            } else {
                var32 = 0.00398911;
            }
        }
    }
    double var33;
    if (features[0] < 53.54351) {
        if (features[0] < 37.45875) {
            var33 = 0.0026089852;
        } else {
            var33 = -0.05174933;
        }
    } else {
        if (features[4] < -0.999669) {
            if (features[3] < -3.6845) {
                var33 = 0.03643457;
            } else {
                var33 = -0.0147431595;
            }
        } else {
            if (features[0] < 58.47312) {
                var33 = 0.0030305227;
            } else {
                var33 = 0.049929295;
            }
        }
    }
    double var34;
    if (features[5] < 0.006356) {
        if (features[1] < 0.000007) {
            var34 = -0.02328909;
        } else {
            if (features[1] < 0.000019) {
                var34 = 0.018867025;
            } else {
                var34 = 0.05003376;
            }
        }
    } else {
        if (features[1] < 0.000019) {
            var34 = 0.022791924;
        } else {
            if (features[4] < -0.999669) {
                var34 = -0.05193263;
            } else {
                var34 = 0.011182796;
            }
        }
    }
    double var35;
    if (features[1] < 0.00004) {
        if (features[1] < 0.000021) {
            if (features[5] < 0.00607) {
                var35 = -0.016112527;
            } else {
                var35 = 0.024049658;
            }
        } else {
            if (features[1] < 0.000031) {
                var35 = 0.054856893;
            } else {
                var35 = 0.007478276;
            }
        }
    } else {
        if (features[3] < -1.2931) {
            var35 = -0.0065916292;
        } else {
            var35 = -0.040602814;
        }
    }
    double var36;
    if (features[6] < 0.000033) {
        if (features[4] < -0.999811) {
            var36 = -0.002166332;
        } else {
            var36 = -0.04716912;
        }
    } else {
        if (features[2] < 25.94) {
            if (features[4] < -0.999618) {
                var36 = 0.0568385;
            } else {
                var36 = 0.0059052603;
            }
        } else {
            if (features[6] < 0.000068) {
                var36 = 0.023226531;
            } else {
                var36 = -0.020809539;
            }
        }
    }
    double var37;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000021) {
            if (features[0] < 99.38378) {
                var37 = -0.026215747;
            } else {
                var37 = 0.013742675;
            }
        } else {
            if (features[3] < 2.1348) {
                var37 = 0.045678418;
            } else {
                var37 = 0.0032728133;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var37 = -0.04650792;
        } else {
            var37 = 0.008529354;
        }
    }
    double var38;
    if (features[1] < 0.00004) {
        if (features[0] < 111.446) {
            if (features[0] < 74.50584) {
                var38 = -0.00041832076;
            } else {
                var38 = 0.055115577;
            }
        } else {
            if (features[0] < 127.20731) {
                var38 = -0.040268786;
            } else {
                var38 = 0.011587149;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var38 = 0.0042363326;
        } else {
            var38 = -0.043446947;
        }
    }
    double var39;
    if (features[5] < 0.005876) {
        if (features[6] < 0.00008) {
            if (features[2] < 21.13) {
                var39 = -0.0080400305;
            } else {
                var39 = 0.051973652;
            }
        } else {
            if (features[5] < 0.004875) {
                var39 = -0.030093526;
            } else {
                var39 = 0.038873564;
            }
        }
    } else {
        if (features[3] < -1.8727) {
            if (features[1] < 0.000033) {
                var39 = -0.016965006;
            } else {
                var39 = 0.030632133;
            }
        } else {
            if (features[2] < 25.94) {
                var39 = 0.01475536;
            } else {
                var39 = -0.04301556;
            }
        }
    }
    double var40;
    if (features[2] < 19.57) {
        var40 = 0.03783231;
    } else {
        if (features[3] < -4.0441) {
            var40 = 0.037576985;
        } else {
            if (features[5] < 0.003244) {
                var40 = 0.02479853;
            } else {
                var40 = -0.023028066;
            }
        }
    }
    double var41;
    if (features[5] < 0.003273) {
        var41 = 0.03995543;
    } else {
        if (features[0] < 111.446) {
            if (features[0] < 81.13815) {
                var41 = -0.0055775805;
            } else {
                var41 = 0.035624236;
            }
        } else {
            if (features[3] < -2.3807) {
                var41 = -0.00047142452;
            } else {
                var41 = -0.03288306;
            }
        }
    }
    double var42;
    if (features[1] < 0.000041) {
        if (features[5] < 0.00607) {
            if (features[1] < 0.000021) {
                var42 = -0.019167267;
            } else {
                var42 = 0.032035515;
            }
        } else {
            if (features[0] < 74.50584) {
                var42 = -0.006889637;
            } else {
                var42 = 0.058318496;
            }
        }
    } else {
        if (features[3] < -0.8769) {
            var42 = -0.003714847;
        } else {
            var42 = -0.041006643;
        }
    }
    double var43;
    if (features[1] < 0.000041) {
        if (features[1] < 0.00001) {
            if (features[5] < 0.004507) {
                var43 = 0.017559422;
            } else {
                var43 = -0.029084072;
            }
        } else {
            if (features[4] < -0.999761) {
                var43 = 0.046793103;
            } else {
                var43 = 0.016304405;
            }
        }
    } else {
        if (features[4] < -0.999669) {
            var43 = -0.038858682;
        } else {
            var43 = 0.013687125;
        }
    }
    double var44;
    if (features[2] < 22.54) {
        if (features[1] < 0.00001) {
            var44 = -0.0022950477;
        } else {
            var44 = 0.041936226;
        }
    } else {
        if (features[5] < 0.004622) {
            if (features[2] < 27.76) {
                var44 = -0.009456983;
            } else {
                var44 = 0.032908436;
            }
        } else {
            if (features[5] < 0.006037) {
                var44 = -0.041301474;
            } else {
                var44 = 0.0019269843;
            }
        }
    }
    double var45;
    if (features[0] < 53.54351) {
        if (features[2] < 19.65) {
            var45 = 0.022761516;
        } else {
            var45 = -0.05330966;
        }
    } else {
        if (features[1] < 0.00001) {
            if (features[2] < 36.23) {
                var45 = -0.03276198;
            } else {
                var45 = 0.020943252;
            }
        } else {
            if (features[1] < 0.00004) {
                var45 = 0.03088021;
            } else {
                var45 = -0.0118102105;
            }
        }
    }
    double var46;
    if (features[0] < 111.446) {
        if (features[0] < 81.13815) {
            if (features[1] < 0.000022) {
                var46 = -0.037457407;
            } else {
                var46 = 0.0071068043;
            }
        } else {
            if (features[3] < 1.1288) {
                var46 = 0.0497486;
            } else {
                var46 = 0.007381507;
            }
        }
    } else {
        if (features[0] < 128.48354) {
            var46 = -0.05373768;
        } else {
            if (features[1] < 0.00001) {
                var46 = -0.028838996;
            } else {
                var46 = 0.01794627;
            }
        }
    }
    double var47;
    if (features[1] < 0.000031) {
        if (features[0] < 96.89966) {
            if (features[1] < 0.00002) {
                var47 = 0.004223337;
            } else {
                var47 = 0.04716796;
            }
        } else {
            if (features[0] < 127.20731) {
                var47 = -0.030311942;
            } else {
                var47 = 0.012974485;
            }
        }
    } else {
        if (features[0] < 53.54351) {
            if (features[2] < 20.99) {
                var47 = -0.011788498;
            } else {
                var47 = -0.042922728;
            }
        } else {
            if (features[5] < 0.007826) {
                var47 = 0.023014087;
            } else {
                var47 = -0.0110539;
            }
        }
    }
    double var48;
    if (features[2] < 46.88) {
        if (features[3] < -2.8421) {
            var48 = 0.024854226;
        } else {
            if (features[2] < 31.6) {
                var48 = 0.005788069;
            } else {
                var48 = -0.039890777;
            }
        }
    } else {
        var48 = 0.036446642;
    }
    double var49;
    if (features[1] < 0.000041) {
        if (features[5] < 0.005181) {
            if (features[5] < 0.004622) {
                var49 = 0.033974517;
            } else {
                var49 = -0.032674987;
            }
        } else {
            if (features[5] < 0.007826) {
                var49 = 0.03887662;
            } else {
                var49 = 0.012297898;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var49 = -0.036486387;
        } else {
            var49 = 0.011184829;
        }
    }
    double var50;
    if (features[0] < 111.446) {
        if (features[0] < 81.13815) {
            if (features[4] < -0.999576) {
                var50 = 0.013384326;
            } else {
                var50 = -0.03269911;
            }
        } else {
            if (features[5] < 0.004738) {
                var50 = 0.012133705;
            } else {
                var50 = 0.050004493;
            }
        }
    } else {
        if (features[4] < -0.999761) {
            if (features[4] < -0.999821) {
                var50 = -0.02887855;
            } else {
                var50 = 0.02890492;
            }
        } else {
            var50 = -0.048049357;
        }
    }
    double var51;
    if (features[0] < 252.47371) {
        if (features[2] < 19.98) {
            if (features[2] < 15.96) {
                var51 = 0.0045798947;
            } else {
                var51 = 0.045539886;
            }
        } else {
            if (features[2] < 48.17) {
                var51 = -0.0059952526;
            } else {
                var51 = 0.03492199;
            }
        }
    } else {
        var51 = -0.022887148;
    }
    double var52;
    if (features[4] < -0.999669) {
        if (features[5] < 0.004593) {
            if (features[5] < 0.003656) {
                var52 = -0.009526867;
            } else {
                var52 = 0.035565328;
            }
        } else {
            if (features[0] < 220.83095) {
                var52 = -0.037805285;
            } else {
                var52 = 0.007300881;
            }
        }
    } else {
        if (features[0] < 58.47312) {
            if (features[0] < 37.45875) {
                var52 = 0.018634869;
            } else {
                var52 = -0.030647565;
            }
        } else {
            var52 = 0.044918384;
        }
    }
    double var53;
    if (features[4] < -0.999664) {
        if (features[2] < 48.17) {
            if (features[2] < 31.6) {
                var53 = 0.005180246;
            } else {
                var53 = -0.03863303;
            }
        } else {
            var53 = 0.023343733;
        }
    } else {
        if (features[1] < 0.000031) {
            var53 = 0.03883562;
        } else {
            if (features[3] < -1.5541) {
                var53 = 0.025927046;
            } else {
                var53 = -0.016966924;
            }
        }
    }
    double var54;
    if (features[2] < 28.58) {
        if (features[2] < 23.0) {
            if (features[6] < 0.000029) {
                var54 = -0.023449829;
            } else {
                var54 = 0.026086533;
            }
        } else {
            if (features[5] < 0.004622) {
                var54 = -0.011002853;
            } else {
                var54 = -0.043139704;
            }
        }
    } else {
        if (features[2] < 31.15) {
            var54 = 0.045021657;
        } else {
            if (features[2] < 46.88) {
                var54 = -0.015754895;
            } else {
                var54 = 0.02626052;
            }
        }
    }
    double var55;
    if (features[3] < -4.0441) {
        var55 = 0.03501996;
    } else {
        if (features[2] < 46.88) {
            if (features[2] < 23.0) {
                var55 = 0.008877802;
            } else {
                var55 = -0.02821667;
            }
        } else {
            var55 = 0.027011273;
        }
    }
    double var56;
    if (features[2] < 48.17) {
        if (features[5] < 0.003707) {
            var56 = -0.038220376;
        } else {
            if (features[5] < 0.005853) {
                var56 = 0.025755867;
            } else {
                var56 = -0.019326761;
            }
        }
    } else {
        var56 = 0.036110193;
    }
    double var57;
    if (features[0] < 53.54351) {
        if (features[4] < -0.999578) {
            if (features[0] < 37.45875) {
                var57 = 0.037903618;
            } else {
                var57 = -0.029250924;
            }
        } else {
            var57 = -0.042314406;
        }
    } else {
        if (features[4] < -0.999669) {
            if (features[2] < 28.15) {
                var57 = -0.017335478;
            } else {
                var57 = 0.013763318;
            }
        } else {
            if (features[2] < 42.06) {
                var57 = 0.046278503;
            } else {
                var57 = 0.015304255;
            }
        }
    }
    double var58;
    if (features[2] < 46.88) {
        if (features[4] < -0.999803) {
            if (features[3] < 1.8366) {
                var58 = -0.037652966;
            } else {
                var58 = -0.00023453303;
            }
        } else {
            if (features[0] < 79.61589) {
                var58 = -0.0074354927;
            } else {
                var58 = 0.029908082;
            }
        }
    } else {
        var58 = 0.04055193;
    }
    double var59;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000021) {
            if (features[6] < 0.00004) {
                var59 = 0.02972556;
            } else {
                var59 = -0.019410845;
            }
        } else {
            if (features[3] < -2.3031) {
                var59 = 0.011886076;
            } else {
                var59 = 0.048676617;
            }
        }
    } else {
        if (features[3] < -1.2931) {
            var59 = -0.007198756;
        } else {
            var59 = -0.037642837;
        }
    }
    double var60;
    if (features[5] < 0.011602) {
        if (features[0] < 53.54351) {
            if (features[1] < 0.000031) {
                var60 = 0.01587583;
            } else {
                var60 = -0.04116493;
            }
        } else {
            if (features[4] < -0.999747) {
                var60 = -0.009734079;
            } else {
                var60 = 0.03638184;
            }
        }
    } else {
        var60 = 0.035954878;
    }
    double var61;
    if (features[3] < -3.6409) {
        var61 = 0.03701022;
    } else {
        if (features[4] < -0.999669) {
            if (features[4] < -0.999811) {
                var61 = 0.0014731531;
            } else {
                var61 = -0.028178131;
            }
        } else {
            if (features[3] < 0.728) {
                var61 = 0.031064663;
            } else {
                var61 = -0.0052412874;
            }
        }
    }
    double var62;
    if (features[2] < 19.98) {
        if (features[5] < 0.004254) {
            var62 = -0.0038828265;
        } else {
            var62 = 0.04357125;
        }
    } else {
        if (features[3] < -4.0441) {
            var62 = 0.033160493;
        } else {
            if (features[5] < 0.004622) {
                var62 = 0.019182837;
            } else {
                var62 = -0.020926706;
            }
        }
    }
    double var63;
    if (features[1] < 0.000041) {
        if (features[6] < 0.000181) {
            if (features[6] < 0.00008) {
                var63 = 0.012411642;
            } else {
                var63 = -0.018998219;
            }
        } else {
            var63 = 0.04149195;
        }
    } else {
        var63 = -0.033585586;
    }
    double var64;
    if (features[2] < 23.0) {
        if (features[0] < 111.446) {
            var64 = 0.043229766;
        } else {
            var64 = -0.019608974;
        }
    } else {
        if (features[2] < 48.17) {
            if (features[0] < 96.89966) {
                var64 = -0.0042677107;
            } else {
                var64 = -0.02730605;
            }
        } else {
            var64 = 0.024966339;
        }
    }
    double var65;
    if (features[0] < 53.54351) {
        if (features[3] < 1.2628) {
            var65 = -0.032763965;
        } else {
            var65 = 0.0012118198;
        }
    } else {
        if (features[0] < 96.89966) {
            if (features[5] < 0.007326) {
                var65 = 0.045508664;
            } else {
                var65 = 0.00044469401;
            }
        } else {
            if (features[2] < 48.17) {
                var65 = -0.01502573;
            } else {
                var65 = 0.02440558;
            }
        }
    }
    double var66;
    if (features[1] < 0.000031) {
        if (features[1] < 0.000021) {
            if (features[6] < 0.00004) {
                var66 = 0.0349866;
            } else {
                var66 = -0.017485807;
            }
        } else {
            var66 = 0.04611059;
        }
    } else {
        if (features[6] < 0.000165) {
            var66 = -0.034613755;
        } else {
            if (features[3] < -1.8727) {
                var66 = 0.011074685;
            } else {
                var66 = -0.0062821144;
            }
        }
    }
    double var67;
    if (features[1] < 0.00001) {
        var67 = -0.03216033;
    } else {
        if (features[1] < 0.000041) {
            if (features[2] < 24.3) {
                var67 = 0.048453357;
            } else {
                var67 = 0.0020417848;
            }
        } else {
            if (features[5] < 0.012507) {
                var67 = -0.03391863;
            } else {
                var67 = 0.0028029287;
            }
        }
    }
    double var68;
    if (features[3] < -4.0441) {
        var68 = 0.032989204;
    } else {
        if (features[2] < 22.54) {
            if (features[6] < 0.000022) {
                var68 = -0.016336493;
            } else {
                var68 = 0.034749217;
            }
        } else {
            if (features[2] < 48.17) {
                var68 = -0.024997037;
            } else {
                var68 = 0.022905115;
            }
        }
    }
    double var69;
    if (features[5] < 0.004622) {
        if (features[2] < 25.29) {
            var69 = -0.008860723;
        } else {
            var69 = 0.04199741;
        }
    } else {
        if (features[3] < -1.6679) {
            if (features[3] < -2.7338) {
                var69 = -0.004528135;
            } else {
                var69 = 0.027022544;
            }
        } else {
            if (features[2] < 25.94) {
                var69 = 0.006313491;
            } else {
                var69 = -0.031493064;
            }
        }
    }
    double var70;
    if (features[4] < -0.999761) {
        if (features[2] < 28.15) {
            var70 = -0.015423077;
        } else {
            if (features[4] < -0.999821) {
                var70 = 0.011578816;
            } else {
                var70 = 0.04728067;
            }
        }
    } else {
        if (features[2] < 19.96) {
            var70 = 0.01665875;
        } else {
            if (features[6] < 0.000181) {
                var70 = -0.033132736;
            } else {
                var70 = -0.004150757;
            }
        }
    }
    double var71;
    if (features[0] < 53.54351) {
        if (features[2] < 19.65) {
            var71 = 0.018613935;
        } else {
            var71 = -0.030496934;
        }
    } else {
        if (features[0] < 156.66748) {
            if (features[0] < 74.50584) {
                var71 = 0.006181453;
            } else {
                var71 = 0.049067967;
            }
        } else {
            if (features[2] < 45.65) {
                var71 = -0.019288713;
            } else {
                var71 = 0.021654023;
            }
        }
    }
    double var72;
    if (features[0] < 96.89966) {
        if (features[0] < 79.61589) {
            if (features[2] < 19.96) {
                var72 = 0.013789179;
            } else {
                var72 = -0.02015883;
            }
        } else {
            var72 = 0.042545136;
        }
    } else {
        if (features[2] < 39.95) {
            if (features[1] < 0.000011) {
                var72 = -0.02278932;
            } else {
                var72 = 0.020737432;
            }
        } else {
            if (features[0] < 219.13855) {
                var72 = -0.042721584;
            } else {
                var72 = -0.0065291324;
            }
        }
    }
    double var73;
    if (features[2] < 48.17) {
        if (features[2] < 31.6) {
            if (features[3] < -1.2931) {
                var73 = -0.023392161;
            } else {
                var73 = 0.021217942;
            }
        } else {
            if (features[3] < -2.8421) {
                var73 = 0.023767568;
            } else {
                var73 = -0.04533567;
            }
        }
    } else {
        var73 = 0.021770943;
    }
    double var74;
    if (features[1] < 0.000041) {
        if (features[4] < -0.999759) {
            if (features[0] < 123.80968) {
                var74 = -0.025086036;
            } else {
                var74 = 0.023328336;
            }
        } else {
            if (features[5] < 0.004875) {
                var74 = 0.002248517;
            } else {
                var74 = 0.0361981;
            }
        }
    } else {
        var74 = -0.025984544;
    }
    double var75;
    if (features[5] < 0.003273) {
        var75 = 0.034176197;
    } else {
        if (features[5] < 0.003707) {
            var75 = -0.040495668;
        } else {
            if (features[5] < 0.004622) {
                var75 = 0.03912885;
            } else {
                var75 = -0.0033219082;
            }
        }
    }
    double var76;
    if (features[5] < 0.005181) {
        if (features[4] < -0.999814) {
            var76 = 0.033371862;
        } else {
            if (features[5] < 0.004593) {
                var76 = -0.009545847;
            } else {
                var76 = -0.052287377;
            }
        }
    } else {
        if (features[4] < -0.999821) {
            var76 = -0.014023158;
        } else {
            if (features[5] < 0.006446) {
                var76 = 0.048638385;
            } else {
                var76 = 0.004611596;
            }
        }
    }
    double var77;
    if (features[0] < 53.54351) {
        if (features[0] < 37.45875) {
            var77 = 0.0006462445;
        } else {
            var77 = -0.04280856;
        }
    } else {
        if (features[1] < 0.000007) {
            var77 = -0.025838688;
        } else {
            if (features[6] < 0.00004) {
                var77 = 0.030761901;
            } else {
                var77 = 0.0011947197;
            }
        }
    }
    double var78;
    if (features[0] < 52.246082) {
        var78 = -0.031425707;
    } else {
        if (features[0] < 111.446) {
            if (features[4] < -0.999669) {
                var78 = 0.004001479;
            } else {
                var78 = 0.042417146;
            }
        } else {
            if (features[4] < -0.999761) {
                var78 = 0.015589341;
            } else {
                var78 = -0.03750765;
            }
        }
    }
    double var79;
    if (features[3] < 3.3756) {
        if (features[1] < 0.000009) {
            if (features[3] < -1.8892) {
                var79 = -0.033634085;
            } else {
                var79 = -0.00009257689;
            }
        } else {
            if (features[1] < 0.000031) {
                var79 = 0.022544695;
            } else {
                var79 = -0.006970055;
            }
        }
    } else {
        var79 = -0.04210049;
    }
    double var80;
    if (features[1] < 0.00004) {
        if (features[1] < 0.00001) {
            if (features[2] < 21.13) {
                var80 = -0.031444307;
            } else {
                var80 = 0.015186638;
            }
        } else {
            if (features[6] < 0.000068) {
                var80 = 0.033676587;
            } else {
                var80 = 0.0006682824;
            }
        }
    } else {
        if (features[1] < 0.000063) {
            var80 = -0.032193772;
        } else {
            var80 = 0.014409067;
        }
    }
    double var81;
    if (features[2] < 45.84) {
        if (features[5] < 0.003707) {
            var81 = -0.03089119;
        } else {
            if (features[5] < 0.004622) {
                var81 = 0.033122554;
            } else {
                var81 = -0.0050241966;
            }
        }
    } else {
        var81 = 0.036607698;
    }
    double var82;
    if (features[0] < 53.54351) {
        if (features[5] < 0.004866) {
            var82 = -0.034897994;
        } else {
            var82 = -0.0074546905;
        }
    } else {
        if (features[5] < 0.005123) {
            var82 = 0.038527347;
        } else {
            if (features[1] < 0.00001) {
                var82 = -0.030808253;
            } else {
                var82 = 0.010076893;
            }
        }
    }
    double var83;
    if (features[2] < 19.59) {
        var83 = 0.03208958;
    } else {
        if (features[2] < 48.17) {
            if (features[4] < -0.999833) {
                var83 = 0.014987451;
            } else {
                var83 = -0.016423259;
            }
        } else {
            var83 = 0.01959118;
        }
    }
    double var84;
    if (features[1] < 0.000041) {
        if (features[1] < 0.000007) {
            var84 = -0.017251795;
        } else {
            if (features[2] < 40.78) {
                var84 = 0.027816815;
            } else {
                var84 = -0.00072934903;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var84 = 0.010162181;
        } else {
            var84 = -0.032548007;
        }
    }
    double var85;
    if (features[2] < 46.88) {
        if (features[5] < 0.003707) {
            var85 = -0.035621647;
        } else {
            if (features[5] < 0.004622) {
                var85 = 0.03652821;
            } else {
                var85 = -0.0057226797;
            }
        }
    } else {
        var85 = 0.027258297;
    }
    double var86;
    if (features[2] < 48.17) {
        if (features[3] < -3.6409) {
            var86 = 0.018357512;
        } else {
            if (features[4] < -0.999669) {
                var86 = -0.026318906;
            } else {
                var86 = 0.0014229951;
            }
        }
    } else {
        var86 = 0.02173917;
    }
    double var87;
    if (features[4] < -0.999761) {
        if (features[5] < 0.00607) {
            if (features[5] < 0.004816) {
                var87 = 0.02145308;
            } else {
                var87 = -0.02653478;
            }
        } else {
            var87 = 0.041767616;
        }
    } else {
        if (features[4] < -0.999669) {
            if (features[2] < 28.58) {
                var87 = -0.0041463305;
            } else {
                var87 = -0.041993927;
            }
        } else {
            if (features[5] < 0.005179) {
                var87 = -0.015829926;
            } else {
                var87 = 0.02180243;
            }
        }
    }
    double var88;
    if (features[6] < 0.000049) {
        if (features[3] < 1.6192) {
            if (features[4] < -0.999821) {
                var88 = -0.033391643;
            } else {
                var88 = -0.007830157;
            }
        } else {
            var88 = 0.016291285;
        }
    } else {
        if (features[3] < 1.7186) {
            if (features[1] < 0.000041) {
                var88 = 0.04667441;
            } else {
                var88 = -0.004847469;
            }
        } else {
            var88 = -0.009246669;
        }
    }
    double var89;
    if (features[6] < 0.00008) {
        if (features[5] < 0.005582) {
            if (features[5] < 0.003656) {
                var89 = -0.0022181864;
            } else {
                var89 = 0.035197925;
            }
        } else {
            if (features[5] < 0.00607) {
                var89 = -0.030463437;
            } else {
                var89 = 0.0101000285;
            }
        }
    } else {
        if (features[5] < 0.008811) {
            if (features[4] < -0.999664) {
                var89 = -0.042067938;
            } else {
                var89 = -0.009563609;
            }
        } else {
            if (features[6] < 0.000201) {
                var89 = 0.017067818;
            } else {
                var89 = -0.0037578084;
            }
        }
    }
    double var90;
    if (features[4] < -0.999575) {
        if (features[6] < 0.000029) {
            if (features[3] < -0.2987) {
                var90 = -0.031267967;
            } else {
                var90 = 0.002188791;
            }
        } else {
            if (features[3] < 3.3756) {
                var90 = 0.0162257;
            } else {
                var90 = -0.020485224;
            }
        }
    } else {
        var90 = -0.030232657;
    }
    double var91;
    if (features[2] < 31.6) {
        if (features[5] < 0.00374) {
            var91 = -0.020370407;
        } else {
            if (features[6] < 0.000029) {
                var91 = -0.0017103344;
            } else {
                var91 = 0.034582116;
            }
        }
    } else {
        if (features[3] < -2.8421) {
            var91 = 0.0248567;
        } else {
            if (features[2] < 48.17) {
                var91 = -0.03977741;
            } else {
                var91 = 0.019651366;
            }
        }
    }
    double var92;
    if (features[5] < 0.012507) {
        if (features[5] < 0.004622) {
            if (features[1] < 0.000022) {
                var92 = 0.04180469;
            } else {
                var92 = -0.01330923;
            }
        } else {
            if (features[4] < -0.999816) {
                var92 = -0.035447046;
            } else {
                var92 = 0.0035476044;
            }
        }
    } else {
        var92 = 0.029894484;
    }
    double var93;
    if (features[3] < -0.4109) {
        if (features[6] < 0.000033) {
            var93 = -0.012493289;
        } else {
            if (features[6] < 0.000101) {
                var93 = 0.044557452;
            } else {
                var93 = 0.0017396094;
            }
        }
    } else {
        if (features[3] < 0.8925) {
            var93 = -0.03168397;
        } else {
            if (features[2] < 31.6) {
                var93 = 0.030309483;
            } else {
                var93 = -0.021876683;
            }
        }
    }
    double var94;
    if (features[2] < 46.88) {
        if (features[2] < 19.59) {
            var94 = 0.017458959;
        } else {
            if (features[0] < 96.89966) {
                var94 = -0.008997223;
            } else {
                var94 = -0.03562869;
            }
        }
    } else {
        var94 = 0.02433667;
    }
    double var95;
    if (features[4] < -0.999574) {
        if (features[4] < -0.999664) {
            if (features[1] < 0.000041) {
                var95 = 0.0027848482;
            } else {
                var95 = -0.033661623;
            }
        } else {
            if (features[4] < -0.999639) {
                var95 = 0.033344414;
            } else {
                var95 = 0.0042322148;
            }
        }
    } else {
        var95 = -0.029791906;
    }
    double var96;
    if (features[2] < 19.98) {
        if (features[6] < 0.00008) {
            var96 = 0.003512358;
        } else {
            var96 = 0.033038966;
        }
    } else {
        if (features[0] < 81.13815) {
            if (features[2] < 28.58) {
                var96 = -0.039249584;
            } else {
                var96 = -0.0026916747;
            }
        } else {
            if (features[0] < 96.89966) {
                var96 = 0.038512595;
            } else {
                var96 = -0.0015942622;
            }
        }
    }
    double var97;
    if (features[5] < 0.004622) {
        if (features[2] < 27.19) {
            var97 = -0.013671341;
        } else {
            var97 = 0.038776506;
        }
    } else {
        if (features[2] < 19.59) {
            var97 = 0.019270448;
        } else {
            if (features[1] < 0.000021) {
                var97 = -0.035989743;
            } else {
                var97 = -0.004483407;
            }
        }
    }
    double var98;
    if (features[1] < 0.00001) {
        var98 = -0.029000718;
    } else {
        if (features[0] < 128.48354) {
            if (features[4] < -0.999759) {
                var98 = -0.03560729;
            } else {
                var98 = 0.007881785;
            }
        } else {
            if (features[6] < 0.000052) {
                var98 = 0.034348693;
            } else {
                var98 = 0.0066042715;
            }
        }
    }
    double var99;
    if (features[5] < 0.012507) {
        if (features[1] < 0.000041) {
            if (features[1] < 0.000034) {
                var99 = -0.0028605338;
            } else {
                var99 = 0.02749399;
            }
        } else {
            var99 = -0.030957742;
        }
    } else {
        var99 = 0.024283743;
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
