//+------------------------------------------------------------------+
//| M2_XGBoost_Oracle_GBPUSD.mqh |
//| REGIMEN: Rolling Window 2024-2026 (LONG ONLY)                    |
//+------------------------------------------------------------------+
double MathExpSafe(double x) { if (x > 100) return MathExp(100); if (x < -100) return MathExp(-100); return MathExp(x); }
double sigmoid(double x) {
    if (x < 0.0) { double z = MathExpSafe(x); return z / (1.0 + z); }
    return 1.0 / (1.0 + MathExpSafe(-x));
}
void GetXGBoostProbability(const double &features[], double &result[]) {
    double var0;
    if (features[3] < 3.0169) {
        if (features[1] < 0.191158) {
            if (features[2] < 18.83) {
                var0 = -0.020000001;
            } else {
                var0 = 0.023809524;
            }
        } else {
            if (features[1] < 0.288811) {
                var0 = -0.043589745;
            } else {
                var0 = -0.007692308;
            }
        }
    } else {
        if (features[1] < 0.204024) {
            if (features[1] < 0.132288) {
                var0 = 0.05;
            } else {
                var0 = -0.01764706;
            }
        } else {
            if (features[4] < 0.012339) {
                var0 = 0.05714286;
            } else {
                var0 = 0.0;
            }
        }
    }
    double var1;
    if (features[1] < 0.132288) {
        var1 = 0.044115644;
    } else {
        if (features[0] < 0.007492) {
            if (features[5] < 0.004831) {
                var1 = -0.019944148;
            } else {
                var1 = -0.06921509;
            }
        } else {
            if (features[0] < 0.009577) {
                var1 = 0.012096278;
            } else {
                var1 = -0.03422324;
            }
        }
    }
    double var2;
    if (features[1] < 0.217331) {
        if (features[0] < 0.00718) {
            if (features[3] < 2.1753) {
                var2 = 0.0006468162;
            } else {
                var2 = -0.05364417;
            }
        } else {
            if (features[0] < 0.009577) {
                var2 = 0.05840334;
            } else {
                var2 = -0.016558552;
            }
        }
    } else {
        if (features[0] < 0.012363) {
            if (features[4] < 0.000401) {
                var2 = -0.070491016;
            } else {
                var2 = -0.025240317;
            }
        } else {
            if (features[5] < 0.010078) {
                var2 = 0.0010919658;
            } else {
                var2 = -0.019394917;
            }
        }
    }
    double var3;
    if (features[5] < 0.007712) {
        if (features[3] < 3.6563) {
            if (features[4] < 0.012339) {
                var3 = 0.014900452;
            } else {
                var3 = -0.030978447;
            }
        } else {
            if (features[4] < -0.001712) {
                var3 = 0.009631088;
            } else {
                var3 = 0.054702338;
            }
        }
    } else {
        if (features[4] < 0.000401) {
            if (features[4] < -0.007209) {
                var3 = -0.017317899;
            } else {
                var3 = -0.06326358;
            }
        } else {
            if (features[2] < 42.78) {
                var3 = 0.011915035;
            } else {
                var3 = -0.050464906;
            }
        }
    }
    double var4;
    if (features[2] < 31.25) {
        if (features[4] < 0.001561) {
            if (features[5] < 0.00344) {
                var4 = -0.012609677;
            } else {
                var4 = -0.05820268;
            }
        } else {
            if (features[4] < 0.011427) {
                var4 = 0.009730605;
            } else {
                var4 = -0.035697084;
            }
        }
    } else {
        if (features[5] < 0.00823) {
            if (features[3] < 3.8756) {
                var4 = 0.061644513;
            } else {
                var4 = 0.008470473;
            }
        } else {
            if (features[5] < 0.009091) {
                var4 = 0.0036427379;
            } else {
                var4 = -0.01876921;
            }
        }
    }
    double var5;
    if (features[2] < 18.69) {
        if (features[3] < -0.948) {
            var5 = -0.06326381;
        } else {
            var5 = -0.016915394;
        }
    } else {
        if (features[4] < 0.011427) {
            if (features[0] < 0.009577) {
                var5 = 0.031101305;
            } else {
                var5 = -0.01556657;
            }
        } else {
            if (features[0] < 0.008038) {
                var5 = -0.059325516;
            } else {
                var5 = -0.0059204604;
            }
        }
    }
    double var6;
    if (features[5] < 0.0121) {
        if (features[3] < -0.948) {
            if (features[3] < -2.3912) {
                var6 = 0.0028490266;
            } else {
                var6 = -0.0698783;
            }
        } else {
            if (features[0] < 0.00969) {
                var6 = 0.018867237;
            } else {
                var6 = -0.023579005;
            }
        }
    } else {
        var6 = -0.061124194;
    }
    double var7;
    if (features[3] < 2.9349) {
        if (features[5] < 0.005847) {
            if (features[4] < 0.006047) {
                var7 = 0.008863593;
            } else {
                var7 = -0.037227698;
            }
        } else {
            if (features[4] < 0.001677) {
                var7 = -0.062207114;
            } else {
                var7 = -0.023136219;
            }
        }
    } else {
        if (features[0] < 0.009577) {
            if (features[0] < 0.00718) {
                var7 = -0.0174169;
            } else {
                var7 = 0.050969314;
            }
        } else {
            if (features[3] < 3.1423) {
                var7 = 0.01584593;
            } else {
                var7 = -0.022811342;
            }
        }
    }
    double var8;
    if (features[3] < 2.9349) {
        if (features[0] < 0.012363) {
            if (features[3] < -0.0725) {
                var8 = -0.044825893;
            } else {
                var8 = -0.013108778;
            }
        } else {
            if (features[2] < 41.52) {
                var8 = 0.034943413;
            } else {
                var8 = -0.0153737785;
            }
        }
    } else {
        if (features[0] < 0.010065) {
            if (features[0] < 0.00718) {
                var8 = -0.022841556;
            } else {
                var8 = 0.04968114;
            }
        } else {
            if (features[5] < 0.00945) {
                var8 = -0.03120105;
            } else {
                var8 = 0.016008643;
            }
        }
    }
    double var9;
    if (features[2] < 18.69) {
        var9 = -0.052503955;
    } else {
        if (features[6] < 0.646526) {
            if (features[5] < 0.010934) {
                var9 = 0.048695836;
            } else {
                var9 = -0.024326442;
            }
        } else {
            if (features[3] < -0.0725) {
                var9 = -0.042862833;
            } else {
                var9 = -0.0018602938;
            }
        }
    }
    double var10;
    if (features[5] < 0.007383) {
        if (features[2] < 31.25) {
            if (features[4] < 0.012339) {
                var10 = 0.003325957;
            } else {
                var10 = -0.04552306;
            }
        } else {
            if (features[5] < 0.005533) {
                var10 = 0.0015844613;
            } else {
                var10 = 0.0455094;
            }
        }
    } else {
        if (features[3] < 4.1167) {
            if (features[6] < 1.469204) {
                var10 = -0.043027554;
            } else {
                var10 = 0.00026876925;
            }
        } else {
            if (features[6] < 0.996399) {
                var10 = 0.039528895;
            } else {
                var10 = -0.026625408;
            }
        }
    }
    double var11;
    if (features[3] < 4.1755) {
        if (features[0] < 0.009571) {
            if (features[0] < 0.008761) {
                var11 = -0.013278933;
            } else {
                var11 = 0.044468403;
            }
        } else {
            if (features[5] < 0.004266) {
                var11 = 0.011045701;
            } else {
                var11 = -0.03958718;
            }
        }
    } else {
        if (features[6] < 0.804706) {
            var11 = 0.049343716;
        } else {
            if (features[3] < 4.7427) {
                var11 = 0.015149379;
            } else {
                var11 = -0.01119409;
            }
        }
    }
    double var12;
    if (features[3] < 2.8513) {
        if (features[1] < 0.188638) {
            if (features[4] < 0.006047) {
                var12 = 0.022777677;
            } else {
                var12 = -0.029789943;
            }
        } else {
            if (features[3] < 1.4352) {
                var12 = -0.050831664;
            } else {
                var12 = -0.009845945;
            }
        }
    } else {
        if (features[6] < 0.646526) {
            var12 = 0.044075757;
        } else {
            if (features[6] < 0.753678) {
                var12 = -0.04862438;
            } else {
                var12 = 0.011755362;
            }
        }
    }
    double var13;
    if (features[1] < 0.13275) {
        var13 = 0.03645298;
    } else {
        if (features[2] < 26.8) {
            if (features[0] < 0.0046) {
                var13 = -0.047076788;
            } else {
                var13 = 0.012692021;
            }
        } else {
            if (features[6] < 1.031165) {
                var13 = -0.04130543;
            } else {
                var13 = -0.0001996546;
            }
        }
    }
    double var14;
    if (features[1] < 0.13275) {
        var14 = 0.033051673;
    } else {
        if (features[4] < 0.011394) {
            if (features[4] < 0.001561) {
                var14 = -0.025812555;
            } else {
                var14 = 0.014881457;
            }
        } else {
            if (features[6] < 0.852638) {
                var14 = -0.05528332;
            } else {
                var14 = -0.0069299773;
            }
        }
    }
    double var15;
    if (features[1] < 0.13275) {
        var15 = 0.038450953;
    } else {
        if (features[4] < 0.00648) {
            if (features[5] < 0.007477) {
                var15 = 0.032104246;
            } else {
                var15 = -0.024500977;
            }
        } else {
            if (features[5] < 0.005549) {
                var15 = -0.055173762;
            } else {
                var15 = -0.0043115593;
            }
        }
    }
    double var16;
    if (features[0] < 0.00718) {
        if (features[6] < 0.582428) {
            var16 = -0.0011801489;
        } else {
            if (features[6] < 0.926016) {
                var16 = -0.05487832;
            } else {
                var16 = -0.013184564;
            }
        }
    } else {
        if (features[0] < 0.008025) {
            if (features[2] < 27.48) {
                var16 = 0.00861107;
            } else {
                var16 = 0.049544614;
            }
        } else {
            if (features[2] < 31.25) {
                var16 = -0.019661447;
            } else {
                var16 = 0.019639006;
            }
        }
    }
    double var17;
    if (features[2] < 31.25) {
        if (features[4] < 0.010063) {
            if (features[0] < 0.008396) {
                var17 = 0.012746743;
            } else {
                var17 = -0.029570151;
            }
        } else {
            if (features[2] < 17.05) {
                var17 = -0.005694729;
            } else {
                var17 = -0.05541519;
            }
        }
    } else {
        if (features[0] < 0.009577) {
            if (features[0] < 0.007132) {
                var17 = -0.002514907;
            } else {
                var17 = 0.051383194;
            }
        } else {
            if (features[4] < 0.019644) {
                var17 = 0.0062182248;
            } else {
                var17 = -0.033359416;
            }
        }
    }
    double var18;
    if (features[0] < 0.00718) {
        if (features[4] < 0.011394) {
            if (features[5] < 0.005118) {
                var18 = 0.011671567;
            } else {
                var18 = -0.025418505;
            }
        } else {
            var18 = -0.045221854;
        }
    } else {
        if (features[5] < 0.007477) {
            if (features[5] < 0.005475) {
                var18 = 0.0042363275;
            } else {
                var18 = 0.034233317;
            }
        } else {
            if (features[6] < 1.570634) {
                var18 = -0.01674193;
            } else {
                var18 = 0.025734594;
            }
        }
    }
    double var19;
    if (features[1] < 0.217331) {
        if (features[2] < 30.73) {
            if (features[0] < 0.00718) {
                var19 = -0.039168343;
            } else {
                var19 = 0.0015068392;
            }
        } else {
            if (features[0] < 0.00969) {
                var19 = 0.052847136;
            } else {
                var19 = -0.012004076;
            }
        }
    } else {
        if (features[2] < 26.4) {
            if (features[2] < 18.69) {
                var19 = -0.031635333;
            } else {
                var19 = 0.008146849;
            }
        } else {
            if (features[4] < 0.013201) {
                var19 = -0.05611834;
            } else {
                var19 = -0.01611673;
            }
        }
    }
    double var20;
    if (features[1] < 0.132288) {
        var20 = 0.047376093;
    } else {
        if (features[1] < 0.178783) {
            if (features[0] < 0.012278) {
                var20 = -0.033671036;
            } else {
                var20 = -0.0048877946;
            }
        } else {
            if (features[1] < 0.218488) {
                var20 = 0.03157171;
            } else {
                var20 = -0.019883191;
            }
        }
    }
    double var21;
    if (features[3] < -0.948) {
        if (features[3] < -2.0303) {
            var21 = -0.0022732948;
        } else {
            var21 = -0.05851245;
        }
    } else {
        if (features[5] < 0.008775) {
            if (features[2] < 31.25) {
                var21 = 0.0070451084;
            } else {
                var21 = 0.04902482;
            }
        } else {
            if (features[6] < 1.364463) {
                var21 = -0.034187112;
            } else {
                var21 = 0.027438004;
            }
        }
    }
    double var22;
    if (features[2] < 18.69) {
        var22 = -0.03812203;
    } else {
        if (features[5] < 0.005877) {
            if (features[4] < 0.010468) {
                var22 = 0.027274448;
            } else {
                var22 = -0.02540176;
            }
        } else {
            if (features[6] < 1.441825) {
                var22 = -0.026998362;
            } else {
                var22 = 0.018767323;
            }
        }
    }
    double var23;
    if (features[2] < 18.83) {
        if (features[3] < 0.634) {
            var23 = -0.049772292;
        } else {
            var23 = -0.010068397;
        }
    } else {
        if (features[2] < 47.91) {
            if (features[4] < 0.000401) {
                var23 = -0.0047962572;
            } else {
                var23 = 0.0153928865;
            }
        } else {
            if (features[6] < 0.926761) {
                var23 = -0.03995379;
            } else {
                var23 = 0.0033708948;
            }
        }
    }
    double var24;
    if (features[4] < -0.002919) {
        if (features[3] < 2.955) {
            if (features[0] < 0.009667) {
                var24 = -0.015361944;
            } else {
                var24 = -0.041654732;
            }
        } else {
            var24 = -0.007351252;
        }
    } else {
        if (features[0] < 0.010128) {
            if (features[4] < 0.011394) {
                var24 = 0.027407652;
            } else {
                var24 = -0.011835687;
            }
        } else {
            if (features[0] < 0.014606) {
                var24 = -0.02983259;
            } else {
                var24 = 0.013547971;
            }
        }
    }
    double var25;
    if (features[0] < 0.00718) {
        if (features[2] < 20.9) {
            var25 = -0.05316114;
        } else {
            if (features[3] < 2.1753) {
                var25 = 0.012494115;
            } else {
                var25 = -0.043457866;
            }
        }
    } else {
        if (features[3] < 1.4352) {
            if (features[0] < 0.011329) {
                var25 = -0.03111711;
            } else {
                var25 = 0.019721111;
            }
        } else {
            if (features[0] < 0.00969) {
                var25 = 0.036300693;
            } else {
                var25 = -0.004797869;
            }
        }
    }
    double var26;
    if (features[2] < 19.61) {
        if (features[3] < 0.364) {
            var26 = -0.045201816;
        } else {
            var26 = -0.005251652;
        }
    } else {
        if (features[3] < 4.9629) {
            if (features[6] < 0.936665) {
                var26 = -0.0014248936;
            } else {
                var26 = 0.029743632;
            }
        } else {
            var26 = -0.026213318;
        }
    }
    double var27;
    if (features[2] < 18.83) {
        var27 = -0.058280982;
    } else {
        if (features[1] < 0.132288) {
            var27 = 0.044731744;
        } else {
            if (features[2] < 21.14) {
                var27 = 0.029189575;
            } else {
                var27 = -0.0063900957;
            }
        }
    }
    double var28;
    if (features[0] < 0.009577) {
        if (features[0] < 0.008761) {
            if (features[0] < 0.005807) {
                var28 = -0.02825667;
            } else {
                var28 = 0.0026831152;
            }
        } else {
            var28 = 0.04600204;
        }
    } else {
        if (features[0] < 0.014606) {
            if (features[5] < 0.010853) {
                var28 = -0.04573475;
            } else {
                var28 = -0.0014908693;
            }
        } else {
            if (features[3] < 0.72) {
                var28 = 0.021114646;
            } else {
                var28 = -0.001882432;
            }
        }
    }
    double var29;
    if (features[1] < 0.225463) {
        if (features[2] < 18.83) {
            var29 = -0.03210546;
        } else {
            if (features[0] < 0.00718) {
                var29 = -0.012827416;
            } else {
                var29 = 0.018669076;
            }
        }
    } else {
        if (features[4] < 0.000401) {
            var29 = -0.042367104;
        } else {
            if (features[2] < 28.54) {
                var29 = 0.004646388;
            } else {
                var29 = -0.024901977;
            }
        }
    }
    double var30;
    if (features[3] < -1.5131) {
        if (features[3] < -2.3874) {
            var30 = -0.0012854462;
        } else {
            var30 = -0.05188482;
        }
    } else {
        if (features[0] < 0.010128) {
            if (features[0] < 0.00718) {
                var30 = -0.0036669262;
            } else {
                var30 = 0.02594467;
            }
        } else {
            if (features[1] < 0.204024) {
                var30 = -0.031142807;
            } else {
                var30 = 0.00253641;
            }
        }
    }
    double var31;
    if (features[2] < 31.25) {
        if (features[0] < 0.008626) {
            if (features[0] < 0.00718) {
                var31 = -0.029626707;
            } else {
                var31 = 0.0120022325;
            }
        } else {
            if (features[0] < 0.013446) {
                var31 = -0.05198262;
            } else {
                var31 = 0.0043906807;
            }
        }
    } else {
        if (features[5] < 0.00823) {
            if (features[4] < -0.000094) {
                var31 = -0.0046360716;
            } else {
                var31 = 0.04569818;
            }
        } else {
            if (features[3] < 3.1924) {
                var31 = 0.010639537;
            } else {
                var31 = -0.0138691515;
            }
        }
    }
    double var32;
    if (features[0] < 0.008463) {
        if (features[4] < 0.011394) {
            if (features[0] < 0.00718) {
                var32 = -0.00023388064;
            } else {
                var32 = 0.044630643;
            }
        } else {
            if (features[1] < 0.235512) {
                var32 = -0.038209464;
            } else {
                var32 = 0.0040089623;
            }
        }
    } else {
        if (features[4] < 0.010712) {
            if (features[4] < 0.003507) {
                var32 = -0.0045711244;
            } else {
                var32 = -0.044448055;
            }
        } else {
            if (features[0] < 0.013675) {
                var32 = 0.019404445;
            } else {
                var32 = -0.009388154;
            }
        }
    }
    double var33;
    if (features[0] < 0.014606) {
        if (features[0] < 0.009819) {
            if (features[3] < -0.948) {
                var33 = -0.0351656;
            } else {
                var33 = 0.005895144;
            }
        } else {
            if (features[4] < -0.007209) {
                var33 = -0.0017303874;
            } else {
                var33 = -0.051854234;
            }
        }
    } else {
        if (features[6] < 1.42029) {
            var33 = 0.041281264;
        } else {
            var33 = 0.004111696;
        }
    }
    double var34;
    if (features[3] < 2.8513) {
        if (features[1] < 0.225463) {
            if (features[3] < 2.528) {
                var34 = 0.018093586;
            } else {
                var34 = -0.011474722;
            }
        } else {
            var34 = -0.03731797;
        }
    } else {
        if (features[1] < 0.204024) {
            if (features[1] < 0.13275) {
                var34 = 0.03073958;
            } else {
                var34 = -0.010098959;
            }
        } else {
            if (features[5] < 0.00677) {
                var34 = 0.05491476;
            } else {
                var34 = 0.021668;
            }
        }
    }
    double var35;
    if (features[3] < 4.7427) {
        if (features[6] < 0.753678) {
            if (features[3] < -2.0303) {
                var35 = 0.011138258;
            } else {
                var35 = -0.030911112;
            }
        } else {
            if (features[5] < 0.010853) {
                var35 = -0.0092702415;
            } else {
                var35 = 0.03809023;
            }
        }
    } else {
        if (features[6] < 0.804706) {
            var35 = 0.04307756;
        } else {
            var35 = -0.0008777599;
        }
    }
    double var36;
    if (features[2] < 18.69) {
        var36 = -0.031242345;
    } else {
        if (features[1] < 0.13275) {
            var36 = 0.029573977;
        } else {
            if (features[2] < 26.8) {
                var36 = 0.013345447;
            } else {
                var36 = -0.009141557;
            }
        }
    }
    double var37;
    if (features[4] < 0.010896) {
        if (features[0] < 0.008463) {
            if (features[3] < -1.6693) {
                var37 = -0.008571126;
            } else {
                var37 = 0.04821713;
            }
        } else {
            if (features[0] < 0.013446) {
                var37 = -0.02250362;
            } else {
                var37 = 0.028849382;
            }
        }
    } else {
        if (features[0] < 0.008038) {
            var37 = -0.051006556;
        } else {
            if (features[2] < 47.91) {
                var37 = 0.019653577;
            } else {
                var37 = -0.026501684;
            }
        }
    }
    double var38;
    if (features[2] < 48.27) {
        if (features[4] < 0.000401) {
            if (features[0] < 0.00718) {
                var38 = -0.0342466;
            } else {
                var38 = -0.0036552132;
            }
        } else {
            if (features[4] < 0.002829) {
                var38 = 0.053391;
            } else {
                var38 = 0.0007841216;
            }
        }
    } else {
        var38 = -0.0528571;
    }
    double var39;
    if (features[3] < 3.6014) {
        if (features[1] < 0.225463) {
            if (features[1] < 0.177114) {
                var39 = -0.010885992;
            } else {
                var39 = 0.037126288;
            }
        } else {
            if (features[3] < 2.8513) {
                var39 = -0.017248431;
            } else {
                var39 = 0.009198575;
            }
        }
    } else {
        if (features[6] < 0.646526) {
            var39 = 0.025674833;
        } else {
            if (features[3] < 4.8986) {
                var39 = -0.046596114;
            } else {
                var39 = -0.0072435657;
            }
        }
    }
    double var40;
    if (features[1] < 0.176768) {
        if (features[2] < 24.14) {
            var40 = 0.0028353746;
        } else {
            if (features[1] < 0.155455) {
                var40 = -0.013468387;
            } else {
                var40 = -0.054453045;
            }
        }
    } else {
        if (features[1] < 0.225463) {
            if (features[3] < 3.5707) {
                var40 = 0.028947746;
            } else {
                var40 = -0.019738687;
            }
        } else {
            if (features[3] < 2.6178) {
                var40 = -0.022980586;
            } else {
                var40 = 0.0027924136;
            }
        }
    }
    double var41;
    if (features[5] < 0.004301) {
        if (features[0] < 0.005075) {
            var41 = -0.01696421;
        } else {
            if (features[4] < 0.006047) {
                var41 = 0.051569115;
            } else {
                var41 = -0.002861548;
            }
        }
    } else {
        if (features[3] < 2.8513) {
            if (features[0] < 0.006593) {
                var41 = 0.0025652607;
            } else {
                var41 = -0.036357086;
            }
        } else {
            if (features[1] < 0.192462) {
                var41 = -0.016714254;
            } else {
                var41 = 0.019676609;
            }
        }
    }
    double var42;
    if (features[3] < 4.5092) {
        if (features[5] < 0.005929) {
            if (features[5] < 0.005549) {
                var42 = -0.00066896115;
            } else {
                var42 = 0.03799692;
            }
        } else {
            if (features[1] < 0.239949) {
                var42 = -0.031700622;
            } else {
                var42 = -0.006562432;
            }
        }
    } else {
        if (features[4] < -0.000094) {
            var42 = 0.0046442174;
        } else {
            var42 = 0.053304326;
        }
    }
    double var43;
    if (features[4] < 0.001561) {
        if (features[0] < 0.00718) {
            var43 = -0.04845769;
        } else {
            if (features[0] < 0.00908) {
                var43 = 0.008690144;
            } else {
                var43 = -0.022365307;
            }
        }
    } else {
        if (features[2] < 52.06) {
            if (features[4] < 0.003507) {
                var43 = 0.037247606;
            } else {
                var43 = 0.011048292;
            }
        } else {
            var43 = -0.0216303;
        }
    }
    double var44;
    if (features[0] < 0.00969) {
        if (features[3] < -1.5131) {
            if (features[3] < -2.0303) {
                var44 = 0.009720608;
            } else {
                var44 = -0.04169886;
            }
        } else {
            if (features[2] < 34.92) {
                var44 = 0.009401076;
            } else {
                var44 = 0.051145513;
            }
        }
    } else {
        if (features[5] < 0.007533) {
            if (features[0] < 0.014307) {
                var44 = -0.007346316;
            } else {
                var44 = 0.027808586;
            }
        } else {
            if (features[2] < 40.22) {
                var44 = -0.008173708;
            } else {
                var44 = -0.05244827;
            }
        }
    }
    double var45;
    if (features[0] < 0.0046) {
        var45 = -0.033732094;
    } else {
        if (features[0] < 0.010128) {
            if (features[3] < -1.5131) {
                var45 = -0.015204678;
            } else {
                var45 = 0.025265694;
            }
        } else {
            if (features[1] < 0.189921) {
                var45 = 0.01419615;
            } else {
                var45 = -0.01913893;
            }
        }
    }
    double var46;
    if (features[1] < 0.235512) {
        if (features[1] < 0.218488) {
            if (features[1] < 0.204024) {
                var46 = -0.010775386;
            } else {
                var46 = 0.027608765;
            }
        } else {
            var46 = -0.044334702;
        }
    } else {
        if (features[6] < 0.936173) {
            if (features[6] < 0.176453) {
                var46 = 0.0027614783;
            } else {
                var46 = 0.03769562;
            }
        } else {
            if (features[3] < 3.0169) {
                var46 = -0.017772935;
            } else {
                var46 = 0.00909714;
            }
        }
    }
    double var47;
    if (features[6] < 0.890643) {
        if (features[1] < 0.132288) {
            var47 = 0.015032791;
        } else {
            if (features[2] < 26.8) {
                var47 = -0.002767851;
            } else {
                var47 = -0.030814115;
            }
        }
    } else {
        if (features[2] < 18.69) {
            var47 = -0.020764964;
        } else {
            if (features[0] < 0.007132) {
                var47 = -0.003713467;
            } else {
                var47 = 0.025674034;
            }
        }
    }
    double var48;
    if (features[5] < 0.004475) {
        if (features[6] < 0.590591) {
            if (features[3] < -1.5131) {
                var48 = 0.0021653513;
            } else {
                var48 = 0.05373431;
            }
        } else {
            var48 = -0.0050904243;
        }
    } else {
        if (features[2] < 31.25) {
            if (features[5] < 0.008381) {
                var48 = -0.03567634;
            } else {
                var48 = 0.009040759;
            }
        } else {
            if (features[5] < 0.007244) {
                var48 = 0.034480434;
            } else {
                var48 = -0.0013979152;
            }
        }
    }
    double var49;
    if (features[4] < -0.000441) {
        if (features[6] < 0.590591) {
            var49 = 0.007841992;
        } else {
            if (features[2] < 24.14) {
                var49 = -0.008243172;
            } else {
                var49 = -0.043143995;
            }
        }
    } else {
        if (features[4] < 0.003507) {
            if (features[4] < 0.001677) {
                var49 = 0.0026920505;
            } else {
                var49 = 0.037894625;
            }
        } else {
            if (features[2] < 34.92) {
                var49 = -0.012473554;
            } else {
                var49 = 0.0119857555;
            }
        }
    }
    double var50;
    if (features[4] < 0.000401) {
        if (features[4] < -0.004689) {
            if (features[6] < 0.733453) {
                var50 = 0.024791807;
            } else {
                var50 = -0.011792513;
            }
        } else {
            var50 = -0.04892135;
        }
    } else {
        if (features[4] < 0.010312) {
            if (features[0] < 0.008396) {
                var50 = 0.035746656;
            } else {
                var50 = 0.0008263096;
            }
        } else {
            if (features[4] < 0.028529) {
                var50 = -0.013508675;
            } else {
                var50 = 0.026479108;
            }
        }
    }
    double var51;
    if (features[0] < 0.00718) {
        if (features[2] < 22.1) {
            if (features[2] < 19.71) {
                var51 = -0.038156644;
            } else {
                var51 = 0.02270521;
            }
        } else {
            var51 = -0.04326882;
        }
    } else {
        if (features[5] < 0.004266) {
            if (features[1] < 0.176429) {
                var51 = -0.0071659232;
            } else {
                var51 = 0.03255787;
            }
        } else {
            if (features[4] < 0.00565) {
                var51 = -0.020466791;
            } else {
                var51 = 0.003420395;
            }
        }
    }
    double var52;
    if (features[0] < 0.009577) {
        if (features[6] < 0.796758) {
            if (features[3] < -1.5131) {
                var52 = -0.011149366;
            } else {
                var52 = 0.030781478;
            }
        } else {
            if (features[3] < 2.7317) {
                var52 = -0.02625362;
            } else {
                var52 = 0.010753307;
            }
        }
    } else {
        if (features[6] < 0.996399) {
            if (features[5] < 0.004266) {
                var52 = 0.007101728;
            } else {
                var52 = -0.040439393;
            }
        } else {
            if (features[3] < 3.0288) {
                var52 = 0.01386112;
            } else {
                var52 = -0.01837292;
            }
        }
    }
    double var53;
    if (features[1] < 0.218488) {
        if (features[6] < 0.46287) {
            var53 = 0.050433643;
        } else {
            if (features[2] < 26.12) {
                var53 = -0.0064602266;
            } else {
                var53 = 0.018731287;
            }
        }
    } else {
        if (features[2] < 31.25) {
            if (features[3] < 3.1423) {
                var53 = -0.037050635;
            } else {
                var53 = -0.00021230083;
            }
        } else {
            if (features[3] < 2.6006) {
                var53 = -0.0025105004;
            } else {
                var53 = 0.023578865;
            }
        }
    }
    double var54;
    if (features[0] < 0.010128) {
        if (features[0] < 0.00718) {
            if (features[4] < 0.011394) {
                var54 = 0.0035181039;
            } else {
                var54 = -0.03507442;
            }
        } else {
            if (features[0] < 0.008626) {
                var54 = 0.028797915;
            } else {
                var54 = 0.0005669095;
            }
        }
    } else {
        if (features[0] < 0.013446) {
            if (features[5] < 0.010453) {
                var54 = -0.045390915;
            } else {
                var54 = -0.016901249;
            }
        } else {
            if (features[2] < 26.4) {
                var54 = 0.029505363;
            } else {
                var54 = -0.007268382;
            }
        }
    }
    double var55;
    if (features[6] < 1.441825) {
        if (features[2] < 24.14) {
            if (features[2] < 18.83) {
                var55 = -0.020358313;
            } else {
                var55 = 0.016083112;
            }
        } else {
            if (features[6] < 0.176453) {
                var55 = 0.016457064;
            } else {
                var55 = -0.022469362;
            }
        }
    } else {
        if (features[0] < 0.009819) {
            var55 = -0.0045986087;
        } else {
            var55 = 0.039335426;
        }
    }
    double var56;
    if (features[2] < 18.83) {
        var56 = -0.03614011;
    } else {
        if (features[2] < 48.71) {
            if (features[0] < 0.006271) {
                var56 = -0.022095677;
            } else {
                var56 = 0.012979266;
            }
        } else {
            var56 = -0.03554572;
        }
    }
    double var57;
    if (features[0] < 0.010128) {
        if (features[2] < 19.61) {
            if (features[3] < 0.364) {
                var57 = -0.040490653;
            } else {
                var57 = 0.009791818;
            }
        } else {
            if (features[0] < 0.00718) {
                var57 = 0.0021524453;
            } else {
                var57 = 0.035909824;
            }
        }
    } else {
        if (features[0] < 0.015586) {
            if (features[4] < 0.015605) {
                var57 = -0.036117136;
            } else {
                var57 = 0.0037169647;
            }
        } else {
            if (features[2] < 47.91) {
                var57 = 0.0137255965;
            } else {
                var57 = -0.011174341;
            }
        }
    }
    double var58;
    if (features[2] < 19.61) {
        if (features[3] < 0.634) {
            var58 = -0.041869007;
        } else {
            var58 = -0.0061281226;
        }
    } else {
        if (features[0] < 0.012278) {
            if (features[3] < 2.1753) {
                var58 = -0.0069675124;
            } else {
                var58 = 0.028370375;
            }
        } else {
            if (features[4] < 0.000401) {
                var58 = -0.040245224;
            } else {
                var58 = 0.0023657407;
            }
        }
    }
    double var59;
    if (features[0] < 0.009577) {
        if (features[6] < 0.587835) {
            if (features[3] < -1.5131) {
                var59 = -0.0035445676;
            } else {
                var59 = 0.051179774;
            }
        } else {
            if (features[3] < 2.9378) {
                var59 = -0.008854835;
            } else {
                var59 = 0.023803381;
            }
        }
    } else {
        if (features[6] < 0.39992) {
            var59 = -0.036644313;
        } else {
            if (features[0] < 0.016574) {
                var59 = -0.010356366;
            } else {
                var59 = 0.020302674;
            }
        }
    }
    double var60;
    if (features[5] < 0.013123) {
        if (features[5] < 0.011774) {
            if (features[5] < 0.004831) {
                var60 = 0.012330325;
            } else {
                var60 = -0.008753344;
            }
        } else {
            var60 = 0.04021883;
        }
    } else {
        if (features[5] < 0.015231) {
            var60 = -0.042043634;
        } else {
            var60 = -0.008257787;
        }
    }
    double var61;
    if (features[2] < 19.61) {
        if (features[2] < 17.05) {
            var61 = -0.0022577108;
        } else {
            var61 = -0.047560982;
        }
    } else {
        if (features[4] < -0.001421) {
            if (features[2] < 28.4) {
                var61 = 0.008280347;
            } else {
                var61 = -0.03932584;
            }
        } else {
            if (features[4] < 0.007965) {
                var61 = 0.017191797;
            } else {
                var61 = -0.0047206464;
            }
        }
    }
    double var62;
    if (features[2] < 28.54) {
        if (features[1] < 0.177114) {
            if (features[2] < 25.17) {
                var62 = -0.00016043846;
            } else {
                var62 = -0.023337502;
            }
        } else {
            if (features[2] < 18.69) {
                var62 = -0.009609818;
            } else {
                var62 = 0.022794096;
            }
        }
    } else {
        if (features[1] < 0.138931) {
            var62 = 0.019692456;
        } else {
            if (features[2] < 31.25) {
                var62 = -0.041162945;
            } else {
                var62 = -0.004465228;
            }
        }
    }
    double var63;
    if (features[4] < 0.028529) {
        if (features[0] < 0.007607) {
            if (features[4] < 0.001561) {
                var63 = -0.0114310235;
            } else {
                var63 = 0.015359624;
            }
        } else {
            if (features[1] < 0.167113) {
                var63 = 0.00790157;
            } else {
                var63 = -0.020752447;
            }
        }
    } else {
        var63 = 0.026701612;
    }
    double var64;
    if (features[1] < 0.13275) {
        var64 = 0.044925716;
    } else {
        if (features[4] < 0.007965) {
            if (features[4] < -0.000441) {
                var64 = -0.012001808;
            } else {
                var64 = 0.026465258;
            }
        } else {
            if (features[3] < 4.1755) {
                var64 = -0.02120511;
            } else {
                var64 = 0.026027894;
            }
        }
    }
    double var65;
    if (features[2] < 23.79) {
        if (features[6] < 0.398207) {
            var65 = -0.019548548;
        } else {
            if (features[0] < 0.007492) {
                var65 = -0.00450546;
            } else {
                var65 = 0.043696154;
            }
        }
    } else {
        if (features[2] < 31.25) {
            if (features[0] < 0.008396) {
                var65 = 0.0031903244;
            } else {
                var65 = -0.038614243;
            }
        } else {
            if (features[5] < 0.009091) {
                var65 = 0.022378957;
            } else {
                var65 = -0.01158294;
            }
        }
    }
    double var66;
    if (features[2] < 31.25) {
        if (features[2] < 30.28) {
            if (features[2] < 19.61) {
                var66 = -0.03055881;
            } else {
                var66 = 0.005435219;
            }
        } else {
            var66 = -0.0474486;
        }
    } else {
        if (features[3] < 0.72) {
            var66 = 0.002522859;
        } else {
            if (features[1] < 0.175778) {
                var66 = 0.01568278;
            } else {
                var66 = 0.054041125;
            }
        }
    }
    double var67;
    if (features[0] < 0.016574) {
        if (features[5] < 0.005929) {
            if (features[5] < 0.00487) {
                var67 = -0.008187919;
            } else {
                var67 = 0.022460757;
            }
        } else {
            if (features[1] < 0.23735) {
                var67 = -0.025352685;
            } else {
                var67 = -0.00064643985;
            }
        }
    } else {
        if (features[0] < 0.022638) {
            var67 = 0.048995998;
        } else {
            var67 = -0.001776097;
        }
    }
    double var68;
    if (features[0] < 0.00718) {
        if (features[6] < 0.582428) {
            var68 = 0.015902897;
        } else {
            if (features[2] < 21.52) {
                var68 = -0.0021043608;
            } else {
                var68 = -0.0392268;
            }
        }
    } else {
        if (features[2] < 57.8) {
            if (features[2] < 35.44) {
                var68 = 0.004863208;
            } else {
                var68 = 0.038272917;
            }
        } else {
            var68 = -0.02006767;
        }
    }
    double var69;
    if (features[2] < 31.25) {
        if (features[3] < 2.528) {
            if (features[3] < 0.5567) {
                var69 = -0.0146563975;
            } else {
                var69 = 0.018842325;
            }
        } else {
            if (features[2] < 26.4) {
                var69 = -0.059583724;
            } else {
                var69 = -0.0070995106;
            }
        }
    } else {
        if (features[5] < 0.008688) {
            if (features[3] < 2.6874) {
                var69 = 0.0048930584;
            } else {
                var69 = 0.04117341;
            }
        } else {
            if (features[6] < 1.031165) {
                var69 = -0.0271388;
            } else {
                var69 = 0.0040068845;
            }
        }
    }
    double var70;
    if (features[6] < 0.666718) {
        if (features[3] < 3.4283) {
            if (features[1] < 0.177114) {
                var70 = -0.046139065;
            } else {
                var70 = -0.01106471;
            }
        } else {
            var70 = 0.009427421;
        }
    } else {
        if (features[6] < 1.089796) {
            if (features[2] < 29.96) {
                var70 = 0.023449386;
            } else {
                var70 = 0.0042946422;
            }
        } else {
            if (features[6] < 1.441825) {
                var70 = -0.022567935;
            } else {
                var70 = 0.014739436;
            }
        }
    }
    double var71;
    if (features[0] < 0.014606) {
        if (features[3] < 4.7427) {
            if (features[0] < 0.008025) {
                var71 = 0.0024570297;
            } else {
                var71 = -0.022252722;
            }
        } else {
            if (features[0] < 0.008646) {
                var71 = 0.0028396808;
            } else {
                var71 = 0.031497788;
            }
        }
    } else {
        if (features[2] < 47.91) {
            var71 = 0.029692272;
        } else {
            var71 = -0.002022593;
        }
    }
    double var72;
    if (features[1] < 0.177114) {
        if (features[4] < 0.005396) {
            if (features[4] < -0.001011) {
                var72 = -0.011408486;
            } else {
                var72 = 0.021938456;
            }
        } else {
            if (features[2] < 28.83) {
                var72 = -0.03956606;
            } else {
                var72 = -0.0061907344;
            }
        }
    } else {
        if (features[1] < 0.218488) {
            if (features[0] < 0.011255) {
                var72 = 0.042714905;
            } else {
                var72 = 0.008213214;
            }
        } else {
            if (features[6] < 1.15571) {
                var72 = 0.009783538;
            } else {
                var72 = -0.019627718;
            }
        }
    }
    double var73;
    if (features[1] < 0.189921) {
        if (features[4] < -0.004291) {
            var73 = -0.0067035556;
        } else {
            if (features[6] < 0.926761) {
                var73 = 0.025053546;
            } else {
                var73 = 0.0010131317;
            }
        }
    } else {
        if (features[3] < -1.6204) {
            var73 = -0.04057582;
        } else {
            if (features[4] < 0.019644) {
                var73 = 0.0011614169;
            } else {
                var73 = -0.029705647;
            }
        }
    }
    double var74;
    if (features[0] < 0.009577) {
        if (features[2] < 26.12) {
            if (features[4] < 0.005622) {
                var74 = 0.002410693;
            } else {
                var74 = -0.032939207;
            }
        } else {
            if (features[1] < 0.217331) {
                var74 = 0.035776254;
            } else {
                var74 = 0.006511394;
            }
        }
    } else {
        if (features[4] < 0.024898) {
            if (features[5] < 0.007477) {
                var74 = 0.003846831;
            } else {
                var74 = -0.035746694;
            }
        } else {
            var74 = 0.013278181;
        }
    }
    double var75;
    if (features[5] < 0.005929) {
        if (features[1] < 0.176429) {
            if (features[5] < 0.00445) {
                var75 = -0.028956085;
            } else {
                var75 = 0.015475093;
            }
        } else {
            if (features[6] < 0.733453) {
                var75 = 0.03990854;
            } else {
                var75 = 0.004661945;
            }
        }
    } else {
        if (features[5] < 0.006661) {
            var75 = -0.032498267;
        } else {
            if (features[1] < 0.267494) {
                var75 = 0.009608101;
            } else {
                var75 = -0.020462528;
            }
        }
    }
    double var76;
    if (features[0] < 0.008646) {
        if (features[5] < 0.009809) {
            if (features[0] < 0.00837) {
                var76 = -0.0046866275;
            } else {
                var76 = 0.026178673;
            }
        } else {
            var76 = 0.04228684;
        }
    } else {
        if (features[4] < 0.010712) {
            if (features[2] < 21.92) {
                var76 = 0.010945811;
            } else {
                var76 = -0.02010189;
            }
        } else {
            if (features[2] < 49.81) {
                var76 = 0.017049445;
            } else {
                var76 = -0.022141242;
            }
        }
    }
    double var77;
    if (features[2] < 18.69) {
        var77 = -0.034315314;
    } else {
        if (features[1] < 0.15875) {
            if (features[2] < 44.09) {
                var77 = 0.00086020905;
            } else {
                var77 = 0.036886197;
            }
        } else {
            if (features[2] < 20.35) {
                var77 = 0.020737099;
            } else {
                var77 = -0.011127222;
            }
        }
    }
    double var78;
    if (features[5] < 0.015231) {
        if (features[0] < 0.014606) {
            if (features[0] < 0.008626) {
                var78 = 0.0057604033;
            } else {
                var78 = -0.0135837635;
            }
        } else {
            if (features[2] < 47.91) {
                var78 = 0.034730237;
            } else {
                var78 = 0.0033391844;
            }
        }
    } else {
        var78 = -0.025938246;
    }
    double var79;
    if (features[4] < 0.024514) {
        if (features[6] < 0.587835) {
            if (features[1] < 0.174753) {
                var79 = 0.04296625;
            } else {
                var79 = -0.0018548018;
            }
        } else {
            if (features[4] < 0.005622) {
                var79 = -0.01871454;
            } else {
                var79 = 0.0040692175;
            }
        }
    } else {
        var79 = -0.030218208;
    }
    double var80;
    if (features[1] < 0.13275) {
        var80 = 0.030089123;
    } else {
        if (features[0] < 0.016574) {
            if (features[1] < 0.217331) {
                var80 = -0.0010979731;
            } else {
                var80 = -0.02364707;
            }
        } else {
            if (features[2] < 41.52) {
                var80 = 0.03366887;
            } else {
                var80 = -0.004946695;
            }
        }
    }
    double var81;
    if (features[4] < 0.007248) {
        if (features[2] < 28.4) {
            if (features[2] < 19.71) {
                var81 = 0.00021376419;
            } else {
                var81 = 0.026168047;
            }
        } else {
            if (features[2] < 40.22) {
                var81 = -0.020877684;
            } else {
                var81 = 0.01667315;
            }
        }
    } else {
        if (features[5] < 0.006034) {
            if (features[4] < 0.010896) {
                var81 = -0.00791736;
            } else {
                var81 = -0.04587682;
            }
        } else {
            if (features[4] < 0.010712) {
                var81 = -0.017631866;
            } else {
                var81 = 0.01037963;
            }
        }
    }
    double var82;
    if (features[3] < 2.63) {
        if (features[5] < 0.00445) {
            if (features[1] < 0.182098) {
                var82 = -0.03457833;
            } else {
                var82 = 0.0045432234;
            }
        } else {
            if (features[1] < 0.247625) {
                var82 = 0.0098748645;
            } else {
                var82 = -0.015710562;
            }
        }
    } else {
        if (features[3] < 3.1423) {
            if (features[1] < 0.250236) {
                var82 = 0.036345966;
            } else {
                var82 = 0.0068545523;
            }
        } else {
            if (features[3] < 4.1167) {
                var82 = -0.012696825;
            } else {
                var82 = 0.018388031;
            }
        }
    }
    double var83;
    if (features[3] < 0.1065) {
        if (features[2] < 28.12) {
            if (features[2] < 19.71) {
                var83 = -0.03458314;
            } else {
                var83 = 0.009519062;
            }
        } else {
            var83 = -0.040370215;
        }
    } else {
        if (features[2] < 30.73) {
            if (features[2] < 30.28) {
                var83 = 0.0072060274;
            } else {
                var83 = -0.03215907;
            }
        } else {
            if (features[4] < 0.019644) {
                var83 = 0.03381471;
            } else {
                var83 = -0.005948913;
            }
        }
    }
    double var84;
    if (features[3] < 2.955) {
        if (features[5] < 0.004831) {
            if (features[1] < 0.176429) {
                var84 = -0.015882704;
            } else {
                var84 = 0.014500069;
            }
        } else {
            if (features[6] < 1.441825) {
                var84 = -0.02346884;
            } else {
                var84 = -0.00005333214;
            }
        }
    } else {
        if (features[1] < 0.13275) {
            var84 = 0.038857833;
        } else {
            if (features[3] < 3.1423) {
                var84 = 0.037338067;
            } else {
                var84 = -0.0051945667;
            }
        }
    }
    double var85;
    if (features[0] < 0.006271) {
        var85 = -0.021568334;
    } else {
        if (features[3] < 2.6178) {
            if (features[0] < 0.008396) {
                var85 = 0.026302783;
            } else {
                var85 = -0.01842843;
            }
        } else {
            if (features[0] < 0.009819) {
                var85 = 0.043583285;
            } else {
                var85 = 0.010423549;
            }
        }
    }
    double var86;
    if (features[4] < 0.000401) {
        if (features[4] < -0.007209) {
            var86 = 0.011096689;
        } else {
            if (features[0] < 0.009667) {
                var86 = -0.0071957083;
            } else {
                var86 = -0.042322163;
            }
        }
    } else {
        if (features[4] < 0.010312) {
            if (features[0] < 0.008396) {
                var86 = 0.051215947;
            } else {
                var86 = 0.0012935133;
            }
        } else {
            if (features[0] < 0.008038) {
                var86 = -0.016574567;
            } else {
                var86 = 0.0084243;
            }
        }
    }
    double var87;
    if (features[2] < 49.81) {
        if (features[2] < 31.25) {
            if (features[2] < 30.28) {
                var87 = -0.0030148267;
            } else {
                var87 = -0.03525456;
            }
        } else {
            if (features[1] < 0.166937) {
                var87 = -0.011401774;
            } else {
                var87 = 0.016934697;
            }
        }
    } else {
        var87 = -0.031235892;
    }
    double var88;
    if (features[1] < 0.240618) {
        if (features[0] < 0.005807) {
            var88 = -0.025715873;
        } else {
            if (features[1] < 0.174753) {
                var88 = -0.00047756624;
            } else {
                var88 = 0.021259574;
            }
        }
    } else {
        if (features[1] < 0.2956) {
            if (features[4] < -0.00358) {
                var88 = -0.001269325;
            } else {
                var88 = -0.037024714;
            }
        } else {
            var88 = 0.016135156;
        }
    }
    double var89;
    if (features[1] < 0.155455) {
        if (features[1] < 0.138931) {
            if (features[1] < 0.122604) {
                var89 = 0.0103855925;
            } else {
                var89 = -0.0061863377;
            }
        } else {
            var89 = 0.026940364;
        }
    } else {
        if (features[4] < 0.012339) {
            if (features[4] < 0.000401) {
                var89 = -0.012476756;
            } else {
                var89 = 0.014464654;
            }
        } else {
            if (features[6] < 0.936173) {
                var89 = -0.039221384;
            } else {
                var89 = -0.0031449308;
            }
        }
    }
    double var90;
    if (features[4] < 0.001561) {
        if (features[3] < 2.8513) {
            if (features[3] < 0.4884) {
                var90 = -0.01019429;
            } else {
                var90 = -0.04339018;
            }
        } else {
            if (features[0] < 0.011255) {
                var90 = 0.023139028;
            } else {
                var90 = -0.014012846;
            }
        }
    } else {
        if (features[4] < 0.019644) {
            if (features[5] < 0.00445) {
                var90 = -0.0075712833;
            } else {
                var90 = 0.021417525;
            }
        } else {
            if (features[6] < 0.852638) {
                var90 = -0.018590163;
            } else {
                var90 = 0.003208718;
            }
        }
    }
    double var91;
    if (features[2] < 28.54) {
        if (features[2] < 18.83) {
            if (features[2] < 17.05) {
                var91 = 0.008459945;
            } else {
                var91 = -0.025843505;
            }
        } else {
            if (features[6] < 1.239781) {
                var91 = 0.006049702;
            } else {
                var91 = 0.028080517;
            }
        }
    } else {
        if (features[2] < 35.07) {
            if (features[5] < 0.006186) {
                var91 = -0.0122864945;
            } else {
                var91 = -0.04951931;
            }
        } else {
            if (features[5] < 0.008686) {
                var91 = 0.02225782;
            } else {
                var91 = -0.014316732;
            }
        }
    }
    double var92;
    if (features[5] < 0.005929) {
        if (features[4] < 0.003507) {
            if (features[1] < 0.21655) {
                var92 = 0.044313055;
            } else {
                var92 = 0.00090228656;
            }
        } else {
            if (features[3] < 1.8908) {
                var92 = -0.021404753;
            } else {
                var92 = 0.0123444125;
            }
        }
    } else {
        if (features[4] < -0.001421) {
            var92 = -0.03966589;
        } else {
            if (features[2] < 34.92) {
                var92 = -0.013153361;
            } else {
                var92 = 0.007686022;
            }
        }
    }
    double var93;
    if (features[2] < 19.71) {
        if (features[3] < -0.948) {
            var93 = -0.035923768;
        } else {
            var93 = -0.008930038;
        }
    } else {
        if (features[2] < 52.06) {
            if (features[0] < 0.008761) {
                var93 = -0.0026273176;
            } else {
                var93 = 0.025282457;
            }
        } else {
            var93 = -0.023145815;
        }
    }
    double var94;
    if (features[0] < 0.008463) {
        if (features[4] < 0.011394) {
            if (features[4] < 0.001561) {
                var94 = -0.0035360393;
            } else {
                var94 = 0.033775955;
            }
        } else {
            if (features[1] < 0.235512) {
                var94 = -0.024291705;
            } else {
                var94 = 0.0061376877;
            }
        }
    } else {
        if (features[6] < 0.936665) {
            if (features[2] < 20.38) {
                var94 = 0.006226131;
            } else {
                var94 = -0.02753408;
            }
        } else {
            if (features[1] < 0.248994) {
                var94 = -0.0030017484;
            } else {
                var94 = 0.02221541;
            }
        }
    }
    double var95;
    if (features[3] < 2.63) {
        if (features[6] < 0.733453) {
            if (features[3] < -2.0303) {
                var95 = 0.022379715;
            } else {
                var95 = -0.010481141;
            }
        } else {
            if (features[1] < 0.264487) {
                var95 = -0.051039737;
            } else {
                var95 = -0.0013212881;
            }
        }
    } else {
        if (features[6] < 0.936665) {
            if (features[1] < 0.13275) {
                var95 = 0.019065058;
            } else {
                var95 = -0.015932743;
            }
        } else {
            if (features[1] < 0.243594) {
                var95 = 0.017414672;
            } else {
                var95 = -0.002244896;
            }
        }
    }
    double var96;
    if (features[6] < 1.469204) {
        if (features[1] < 0.13275) {
            var96 = 0.02698849;
        } else {
            if (features[2] < 26.8) {
                var96 = 0.007926432;
            } else {
                var96 = -0.014379481;
            }
        }
    } else {
        if (features[0] < 0.010065) {
            var96 = 0.004869833;
        } else {
            var96 = 0.03755426;
        }
    }
    double var97;
    if (features[5] < 0.010853) {
        if (features[3] < 3.1924) {
            if (features[3] < 0.364) {
                var97 = -0.017998172;
            } else {
                var97 = 0.008512191;
            }
        } else {
            if (features[3] < 4.1167) {
                var97 = -0.032838155;
            } else {
                var97 = 0.0028566555;
            }
        }
    } else {
        if (features[3] < 2.8235) {
            if (features[1] < 0.247625) {
                var97 = 0.0063845194;
            } else {
                var97 = -0.016889097;
            }
        } else {
            var97 = 0.0354007;
        }
    }
    double var98;
    if (features[1] < 0.267494) {
        if (features[5] < 0.010453) {
            if (features[6] < 0.582428) {
                var98 = 0.013643946;
            } else {
                var98 = -0.012487632;
            }
        } else {
            if (features[0] < 0.011255) {
                var98 = 0.040660884;
            } else {
                var98 = -0.00206874;
            }
        }
    } else {
        if (features[5] < 0.007533) {
            var98 = -0.004820809;
        } else {
            var98 = -0.038818892;
        }
    }
    double var99;
    if (features[6] < 0.926761) {
        if (features[2] < 26.8) {
            if (features[1] < 0.174753) {
                var99 = -0.014506928;
            } else {
                var99 = 0.023218423;
            }
        } else {
            if (features[1] < 0.139408) {
                var99 = 0.0061433082;
            } else {
                var99 = -0.027405608;
            }
        }
    } else {
        if (features[5] < 0.007712) {
            if (features[2] < 20.9) {
                var99 = 0.003029174;
            } else {
                var99 = 0.03877016;
            }
        } else {
            if (features[5] < 0.009809) {
                var99 = -0.011675907;
            } else {
                var99 = 0.011431335;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
