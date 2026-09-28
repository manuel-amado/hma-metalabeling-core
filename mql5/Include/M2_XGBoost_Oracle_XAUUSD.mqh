//+------------------------------------------------------------------+
//| M2_XGBoost_Oracle_XAUUSD.mqh |
//| REGIMEN: Rolling Window 2024-2026 (LONG ONLY)                    |
//+------------------------------------------------------------------+
double MathExpSafe(double x) { if (x > 100) return MathExp(100); if (x < -100) return MathExp(-100); return MathExp(x); }
double sigmoid(double x) {
    if (x < 0.0) { double z = MathExpSafe(x); return z / (1.0 + z); }
    return 1.0 / (1.0 + MathExpSafe(-x));
}
void GetXGBoostProbability(const double &features[], double &result[]) {
    double var0;
    if (features[1] < 0.173326) {
        if (features[3] < 3.7461) {
            if (features[1] < 0.113256) {
                var0 = 0.020000001;
            } else {
                var0 = 0.08260869;
            }
        } else {
            if (features[3] < 3.9613) {
                var0 = -0.060000002;
            } else {
                var0 = 0.06363636;
            }
        }
    } else {
        if (features[3] < 1.113) {
            if (features[2] < 15.91) {
                var0 = 0.011111111;
            } else {
                var0 = -0.071428575;
            }
        } else {
            if (features[1] < 0.207449) {
                var0 = -0.018518519;
            } else {
                var0 = 0.060869563;
            }
        }
    }
    double var1;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[4] < 0.018382) {
                var1 = 0.069059305;
            } else {
                var1 = -0.012227423;
            }
        } else {
            var1 = 0.07763301;
        }
    } else {
        if (features[1] < 0.234905) {
            if (features[0] < 0.029075) {
                var1 = -0.009682843;
            } else {
                var1 = -0.06603597;
            }
        } else {
            if (features[1] < 0.311264) {
                var1 = 0.054902434;
            } else {
                var1 = -0.016502982;
            }
        }
    }
    double var2;
    if (features[3] < 0.6619) {
        if (features[1] < 0.139201) {
            var2 = 0.056920923;
        } else {
            if (features[3] < -1.8892) {
                var2 = 0.00068911334;
            } else {
                var2 = -0.07228472;
            }
        }
    } else {
        if (features[0] < 0.032832) {
            if (features[3] < 3.522) {
                var2 = 0.066984735;
            } else {
                var2 = 0.01665986;
            }
        } else {
            if (features[5] < 0.027517) {
                var2 = -0.046668064;
            } else {
                var2 = 0.04150062;
            }
        }
    }
    double var3;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[4] < 0.018382) {
                var3 = 0.06380566;
            } else {
                var3 = -0.016697893;
            }
        } else {
            if (features[5] < 0.034514) {
                var3 = 0.07427431;
            } else {
                var3 = 0.007744223;
            }
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[5] < 0.011373) {
                var3 = 0.007425125;
            } else {
                var3 = -0.05382682;
            }
        } else {
            if (features[4] < 0.060488) {
                var3 = 0.049807478;
            } else {
                var3 = -0.0400072;
            }
        }
    }
    double var4;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[3] < -2.153) {
                var4 = 0.06456729;
            } else {
                var4 = -0.031920467;
            }
        } else {
            if (features[0] < 0.033707) {
                var4 = 0.060873955;
            } else {
                var4 = 0.017967245;
            }
        }
    } else {
        if (features[5] < 0.014423) {
            var4 = 0.054096706;
        } else {
            if (features[0] < 0.048898) {
                var4 = -0.06305721;
            } else {
                var4 = 0.015213287;
            }
        }
    }
    double var5;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[3] < -0.933) {
                var5 = 0.066170536;
            } else {
                var5 = -0.0073172445;
            }
        } else {
            if (features[4] < -0.011523) {
                var5 = 0.010692989;
            } else {
                var5 = -0.06408569;
            }
        }
    } else {
        if (features[0] < 0.032832) {
            if (features[6] < 0.071689) {
                var5 = 0.0062850937;
            } else {
                var5 = 0.05672989;
            }
        } else {
            if (features[2] < 43.81) {
                var5 = 0.022789054;
            } else {
                var5 = -0.03335592;
            }
        }
    }
    double var6;
    if (features[3] < 0.6619) {
        if (features[3] < -2.153) {
            var6 = 0.061386276;
        } else {
            if (features[6] < 0.479061) {
                var6 = 0.016819386;
            } else {
                var6 = -0.069788836;
            }
        }
    } else {
        if (features[2] < 44.24) {
            if (features[6] < 0.074475) {
                var6 = -0.0093852645;
            } else {
                var6 = 0.061549116;
            }
        } else {
            if (features[5] < 0.014423) {
                var6 = 0.05591104;
            } else {
                var6 = -0.03852397;
            }
        }
    }
    double var7;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[3] < -0.933) {
                var7 = 0.061449498;
            } else {
                var7 = -0.008445609;
            }
        } else {
            if (features[0] < 0.031292) {
                var7 = -0.054660916;
            } else {
                var7 = 0.019169068;
            }
        }
    } else {
        if (features[0] < 0.036723) {
            if (features[6] < 0.071689) {
                var7 = 0.0117442785;
            } else {
                var7 = 0.055915594;
            }
        } else {
            if (features[5] < 0.027517) {
                var7 = -0.043697193;
            } else {
                var7 = 0.03315701;
            }
        }
    }
    double var8;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[3] < -0.5982) {
                var8 = 0.015988642;
            } else {
                var8 = -0.062124874;
            }
        } else {
            if (features[5] < 0.030824) {
                var8 = 0.050703257;
            } else {
                var8 = -0.009578495;
            }
        }
    } else {
        if (features[5] < 0.012496) {
            var8 = 0.052156925;
        } else {
            if (features[0] < 0.027068) {
                var8 = 0.010947096;
            } else {
                var8 = -0.055252768;
            }
        }
    }
    double var9;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[3] < -0.933) {
                var9 = 0.06316992;
            } else {
                var9 = -0.027670993;
            }
        } else {
            if (features[3] < -1.9023) {
                var9 = -0.017088309;
            } else {
                var9 = -0.062857576;
            }
        }
    } else {
        if (features[5] < 0.016424) {
            if (features[4] < 0.047944) {
                var9 = 0.065965496;
            } else {
                var9 = -0.00703135;
            }
        } else {
            if (features[6] < 0.920198) {
                var9 = -0.0067209788;
            } else {
                var9 = 0.034321826;
            }
        }
    }
    double var10;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[3] < -0.5982) {
                var10 = 0.025738886;
            } else {
                var10 = -0.061414547;
            }
        } else {
            if (features[6] < 0.074475) {
                var10 = -0.019861432;
            } else {
                var10 = 0.04713778;
            }
        }
    } else {
        if (features[6] < 0.690268) {
            if (features[5] < 0.014423) {
                var10 = 0.054532893;
            } else {
                var10 = -0.011580636;
            }
        } else {
            if (features[6] < 1.114548) {
                var10 = -0.070069395;
            } else {
                var10 = 0.012288752;
            }
        }
    }
    double var11;
    if (features[1] < 0.173326) {
        if (features[6] < 0.074475) {
            var11 = -0.018948853;
        } else {
            if (features[0] < 0.015044) {
                var11 = 0.003492647;
            } else {
                var11 = 0.06134473;
            }
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[0] < 0.020463) {
                var11 = 0.0010623801;
            } else {
                var11 = -0.06340975;
            }
        } else {
            if (features[0] < 0.019299) {
                var11 = -0.003293362;
            } else {
                var11 = 0.037523016;
            }
        }
    }
    double var12;
    if (features[1] < 0.173326) {
        if (features[2] < 43.81) {
            if (features[2] < 25.24) {
                var12 = 0.026442533;
            } else {
                var12 = 0.067945816;
            }
        } else {
            if (features[6] < 0.423391) {
                var12 = -0.01631044;
            } else {
                var12 = 0.015038288;
            }
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[2] < 17.75) {
                var12 = 0.026705349;
            } else {
                var12 = -0.032659736;
            }
        } else {
            if (features[1] < 0.275268) {
                var12 = 0.06403191;
            } else {
                var12 = 0.0050799516;
            }
        }
    }
    double var13;
    if (features[1] < 0.173326) {
        if (features[6] < 0.247043) {
            if (features[2] < 23.72) {
                var13 = -0.03581013;
            } else {
                var13 = 0.007661469;
            }
        } else {
            if (features[3] < 3.6854) {
                var13 = 0.057849742;
            } else {
                var13 = 0.009869647;
            }
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[0] < 0.029075) {
                var13 = -0.003426109;
            } else {
                var13 = -0.047396686;
            }
        } else {
            if (features[1] < 0.311264) {
                var13 = 0.054082252;
            } else {
                var13 = -0.016640527;
            }
        }
    }
    double var14;
    if (features[1] < 0.173326) {
        if (features[6] < 0.074475) {
            var14 = -0.018680876;
        } else {
            if (features[2] < 49.1) {
                var14 = 0.060416665;
            } else {
                var14 = 0.016651602;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029075) {
                var14 = -0.015733542;
            } else {
                var14 = -0.06885909;
            }
        } else {
            if (features[0] < 0.01288) {
                var14 = -0.023496592;
            } else {
                var14 = 0.031286657;
            }
        }
    }
    double var15;
    if (features[4] < 0.0606) {
        if (features[3] < 0.6619) {
            if (features[3] < -0.5982) {
                var15 = 0.013728226;
            } else {
                var15 = -0.059321236;
            }
        } else {
            if (features[1] < 0.21151) {
                var15 = 0.014704672;
            } else {
                var15 = 0.054601647;
            }
        }
    } else {
        if (features[4] < 0.074749) {
            if (features[3] < 3.9337) {
                var15 = -0.06929425;
            } else {
                var15 = -0.014870958;
            }
        } else {
            var15 = 0.03153783;
        }
    }
    double var16;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[3] < -0.933) {
                var16 = 0.056087412;
            } else {
                var16 = -0.011840437;
            }
        } else {
            if (features[3] < -1.9766) {
                var16 = 0.0063897423;
            } else {
                var16 = -0.058582854;
            }
        }
    } else {
        if (features[5] < 0.031586) {
            if (features[0] < 0.027068) {
                var16 = 0.0498661;
            } else {
                var16 = 0.011073348;
            }
        } else {
            if (features[3] < 3.7158) {
                var16 = 0.009016822;
            } else {
                var16 = -0.036312707;
            }
        }
    }
    double var17;
    if (features[2] < 44.24) {
        if (features[0] < 0.01548) {
            if (features[2] < 20.21) {
                var17 = -0.046232764;
            } else {
                var17 = 0.015663167;
            }
        } else {
            if (features[4] < 0.049127) {
                var17 = 0.018437557;
            } else {
                var17 = 0.058357783;
            }
        }
    } else {
        if (features[6] < 0.578296) {
            if (features[0] < 0.02928) {
                var17 = 0.043528736;
            } else {
                var17 = -0.0062622535;
            }
        } else {
            if (features[6] < 1.053773) {
                var17 = -0.059862223;
            } else {
                var17 = 0.0018837912;
            }
        }
    }
    double var18;
    if (features[1] < 0.173326) {
        if (features[6] < 0.074475) {
            var18 = -0.017406048;
        } else {
            if (features[0] < 0.015044) {
                var18 = 0.0042108404;
            } else {
                var18 = 0.051237043;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029075) {
                var18 = 0.005817413;
            } else {
                var18 = -0.06514295;
            }
        } else {
            if (features[5] < 0.015815) {
                var18 = 0.048239674;
            } else {
                var18 = -0.005122546;
            }
        }
    }
    double var19;
    if (features[1] < 0.173326) {
        if (features[2] < 43.81) {
            if (features[4] < 0.0606) {
                var19 = 0.052594613;
            } else {
                var19 = -0.0036886365;
            }
        } else {
            if (features[1] < 0.145017) {
                var19 = -0.03381982;
            } else {
                var19 = 0.010032207;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[5] < 0.011373) {
                var19 = 0.016002141;
            } else {
                var19 = -0.052472938;
            }
        } else {
            if (features[0] < 0.01288) {
                var19 = -0.023143696;
            } else {
                var19 = 0.029544175;
            }
        }
    }
    double var20;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var20 = 0.060013574;
        } else {
            var20 = -0.00014983033;
        }
    } else {
        if (features[0] < 0.01548) {
            if (features[6] < 0.766371) {
                var20 = -0.0006031437;
            } else {
                var20 = -0.05946516;
            }
        } else {
            if (features[0] < 0.032832) {
                var20 = 0.025594685;
            } else {
                var20 = -0.014712676;
            }
        }
    }
    double var21;
    if (features[1] < 0.174679) {
        if (features[2] < 43.81) {
            if (features[6] < 0.074475) {
                var21 = -0.01496881;
            } else {
                var21 = 0.045923032;
            }
        } else {
            if (features[2] < 48.67) {
                var21 = -0.03748923;
            } else {
                var21 = 0.0046129418;
            }
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[2] < 15.91) {
                var21 = 0.026091287;
            } else {
                var21 = -0.056392998;
            }
        } else {
            if (features[1] < 0.236536) {
                var21 = -0.013243119;
            } else {
                var21 = 0.052908253;
            }
        }
    }
    double var22;
    if (features[5] < 0.013877) {
        if (features[0] < 0.015044) {
            if (features[4] < 0.027438) {
                var22 = 0.04107185;
            } else {
                var22 = -0.044920962;
            }
        } else {
            if (features[5] < 0.005951) {
                var22 = -0.015672043;
            } else {
                var22 = 0.055803854;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[0] < 0.020905) {
                var22 = 0.010019656;
            } else {
                var22 = -0.053502817;
            }
        } else {
            if (features[6] < 0.907802) {
                var22 = -0.0020131452;
            } else {
                var22 = 0.038995508;
            }
        }
    }
    double var23;
    if (features[2] < 44.24) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.479061) {
                var23 = 0.026258636;
            } else {
                var23 = -0.04517485;
            }
        } else {
            if (features[6] < 0.074475) {
                var23 = -0.009181711;
            } else {
                var23 = 0.040441442;
            }
        }
    } else {
        if (features[5] < 0.016901) {
            if (features[4] < 0.047635) {
                var23 = 0.043586474;
            } else {
                var23 = -0.009823223;
            }
        } else {
            if (features[6] < 1.114548) {
                var23 = -0.0591303;
            } else {
                var23 = -0.008266235;
            }
        }
    }
    double var24;
    if (features[1] < 0.173326) {
        if (features[6] < 0.247043) {
            if (features[4] < 0.02916) {
                var24 = 0.03783211;
            } else {
                var24 = -0.026628552;
            }
        } else {
            if (features[3] < 3.6854) {
                var24 = 0.04815386;
            } else {
                var24 = 0.010338684;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.017395) {
                var24 = 0.008698541;
            } else {
                var24 = -0.051084112;
            }
        } else {
            if (features[4] < 0.060488) {
                var24 = 0.023924908;
            } else {
                var24 = -0.026407823;
            }
        }
    }
    double var25;
    if (features[5] < 0.013877) {
        if (features[5] < 0.005674) {
            var25 = -0.03213337;
        } else {
            if (features[0] < 0.015044) {
                var25 = 0.00082641124;
            } else {
                var25 = 0.054959964;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[0] < 0.022683) {
                var25 = -0.002231348;
            } else {
                var25 = -0.049848028;
            }
        } else {
            if (features[5] < 0.031586) {
                var25 = 0.03312264;
            } else {
                var25 = -0.006963166;
            }
        }
    }
    double var26;
    if (features[1] < 0.166537) {
        if (features[2] < 43.81) {
            if (features[1] < 0.123733) {
                var26 = 0.0034828093;
            } else {
                var26 = 0.0480261;
            }
        } else {
            var26 = -0.009756698;
        }
    } else {
        if (features[3] < 1.113) {
            if (features[3] < -1.2873) {
                var26 = 0.0026816314;
            } else {
                var26 = -0.055138327;
            }
        } else {
            if (features[0] < 0.027068) {
                var26 = 0.038164865;
            } else {
                var26 = -0.013383383;
            }
        }
    }
    double var27;
    if (features[1] < 0.173326) {
        if (features[6] < 0.074475) {
            var27 = -0.02607058;
        } else {
            if (features[1] < 0.146879) {
                var27 = 0.0120476745;
            } else {
                var27 = 0.04603886;
            }
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029075) {
                var27 = -0.0015397347;
            } else {
                var27 = -0.057157815;
            }
        } else {
            if (features[4] < 0.060488) {
                var27 = 0.01984019;
            } else {
                var27 = -0.028359307;
            }
        }
    }
    double var28;
    if (features[3] < 0.6619) {
        if (features[3] < -2.153) {
            var28 = 0.042542174;
        } else {
            if (features[6] < 0.479061) {
                var28 = 0.012726721;
            } else {
                var28 = -0.049325556;
            }
        }
    } else {
        if (features[0] < 0.036723) {
            if (features[5] < 0.016424) {
                var28 = 0.048328817;
            } else {
                var28 = 0.015072547;
            }
        } else {
            if (features[0] < 0.065067) {
                var28 = -0.03086991;
            } else {
                var28 = 0.044635393;
            }
        }
    }
    double var29;
    if (features[1] < 0.166537) {
        if (features[2] < 47.25) {
            if (features[1] < 0.113256) {
                var29 = 0.006302856;
            } else {
                var29 = 0.04965122;
            }
        } else {
            var29 = -0.0060453755;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029165) {
                var29 = -0.009985039;
            } else {
                var29 = -0.05771784;
            }
        } else {
            if (features[0] < 0.019299) {
                var29 = -0.009088469;
            } else {
                var29 = 0.036509108;
            }
        }
    }
    double var30;
    if (features[1] < 0.173326) {
        if (features[3] < 3.7461) {
            if (features[5] < 0.005951) {
                var30 = -0.0002645739;
            } else {
                var30 = 0.044554252;
            }
        } else {
            var30 = -0.01878142;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[5] < 0.014423) {
                var30 = 0.005634017;
            } else {
                var30 = -0.046904523;
            }
        } else {
            if (features[3] < 1.9315) {
                var30 = -0.017780587;
            } else {
                var30 = 0.05365634;
            }
        }
    }
    double var31;
    if (features[3] < 0.6619) {
        if (features[3] < -2.153) {
            var31 = 0.040410414;
        } else {
            if (features[2] < 15.83) {
                var31 = 0.014097924;
            } else {
                var31 = -0.041848946;
            }
        }
    } else {
        if (features[4] < 0.06538) {
            if (features[0] < 0.01548) {
                var31 = -0.00828364;
            } else {
                var31 = 0.030784134;
            }
        } else {
            if (features[4] < 0.074749) {
                var31 = -0.055195957;
            } else {
                var31 = 0.038361266;
            }
        }
    }
    double var32;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[3] < -0.933) {
                var32 = 0.04551124;
            } else {
                var32 = -0.009237056;
            }
        } else {
            if (features[3] < -1.9023) {
                var32 = 0.0007186247;
            } else {
                var32 = -0.061544288;
            }
        }
    } else {
        if (features[0] < 0.036723) {
            if (features[0] < 0.01548) {
                var32 = -0.010607633;
            } else {
                var32 = 0.033485297;
            }
        } else {
            if (features[0] < 0.061653) {
                var32 = -0.03213125;
            } else {
                var32 = 0.02990072;
            }
        }
    }
    double var33;
    if (features[5] < 0.013877) {
        if (features[3] < 0.6064) {
            if (features[6] < 0.479061) {
                var33 = 0.043306943;
            } else {
                var33 = -0.02850684;
            }
        } else {
            var33 = 0.05281496;
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[3] < 3.8461) {
                var33 = -0.031265177;
            } else {
                var33 = 0.031776335;
            }
        } else {
            if (features[3] < 4.4055) {
                var33 = 0.029644465;
            } else {
                var33 = -0.037292667;
            }
        }
    }
    double var34;
    if (features[1] < 0.236536) {
        if (features[1] < 0.173326) {
            if (features[6] < 0.074475) {
                var34 = -0.022403998;
            } else {
                var34 = 0.035572305;
            }
        } else {
            if (features[5] < 0.011552) {
                var34 = 0.011990613;
            } else {
                var34 = -0.030478254;
            }
        }
    } else {
        if (features[1] < 0.311264) {
            var34 = 0.051181067;
        } else {
            var34 = -0.017533835;
        }
    }
    double var35;
    if (features[6] < 0.773166) {
        if (features[6] < 0.41723) {
            if (features[1] < 0.21151) {
                var35 = -0.01425325;
            } else {
                var35 = 0.028636083;
            }
        } else {
            if (features[3] < 0.2856) {
                var35 = 0.00088395906;
            } else {
                var35 = 0.054110713;
            }
        }
    } else {
        if (features[6] < 0.923543) {
            var35 = -0.062367346;
        } else {
            if (features[1] < 0.182103) {
                var35 = 0.045882415;
            } else {
                var35 = -0.003955753;
            }
        }
    }
    double var36;
    if (features[4] < 0.013037) {
        if (features[0] < 0.033707) {
            var36 = 0.049734898;
        } else {
            if (features[1] < 0.156804) {
                var36 = 0.037468925;
            } else {
                var36 = -0.017102063;
            }
        }
    } else {
        if (features[4] < 0.032701) {
            if (features[6] < 0.421998) {
                var36 = 0.006223376;
            } else {
                var36 = -0.052978702;
            }
        } else {
            if (features[4] < 0.06538) {
                var36 = 0.02256699;
            } else {
                var36 = -0.030318815;
            }
        }
    }
    double var37;
    if (features[1] < 0.234905) {
        if (features[1] < 0.166537) {
            if (features[2] < 43.81) {
                var37 = 0.03568555;
            } else {
                var37 = -0.0072707185;
            }
        } else {
            if (features[2] < 17.75) {
                var37 = 0.024317913;
            } else {
                var37 = -0.020342767;
            }
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[1] < 0.259479) {
                var37 = 0.042941537;
            } else {
                var37 = -0.057514466;
            }
        } else {
            var37 = 0.055999737;
        }
    }
    double var38;
    if (features[4] < 0.013681) {
        if (features[6] < 1.197851) {
            if (features[4] < -0.010453) {
                var38 = 0.011182407;
            } else {
                var38 = 0.05103259;
            }
        } else {
            var38 = -0.012677905;
        }
    } else {
        if (features[4] < 0.032701) {
            if (features[6] < 0.421998) {
                var38 = 0.010120103;
            } else {
                var38 = -0.05627213;
            }
        } else {
            if (features[4] < 0.03953) {
                var38 = 0.049463846;
            } else {
                var38 = -0.006330067;
            }
        }
    }
    double var39;
    if (features[6] < 0.773166) {
        if (features[6] < 0.074475) {
            if (features[2] < 46.43) {
                var39 = -0.018872535;
            } else {
                var39 = 0.041231927;
            }
        } else {
            if (features[5] < 0.005674) {
                var39 = -0.02420573;
            } else {
                var39 = 0.043720543;
            }
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[6] < 0.907802) {
                var39 = -0.06549257;
            } else {
                var39 = -0.015417362;
            }
        } else {
            if (features[2] < 42.54) {
                var39 = 0.029997936;
            } else {
                var39 = -0.028323382;
            }
        }
    }
    double var40;
    if (features[3] < 1.9315) {
        if (features[4] < 0.020111) {
            if (features[4] < -0.010453) {
                var40 = -0.000029893918;
            } else {
                var40 = 0.039221533;
            }
        } else {
            if (features[1] < 0.1861) {
                var40 = -0.0039202482;
            } else {
                var40 = -0.040755477;
            }
        }
    } else {
        if (features[5] < 0.031586) {
            if (features[1] < 0.236536) {
                var40 = 0.01727823;
            } else {
                var40 = 0.052188873;
            }
        } else {
            if (features[1] < 0.165671) {
                var40 = 0.03651057;
            } else {
                var40 = -0.051425904;
            }
        }
    }
    double var41;
    if (features[1] < 0.173326) {
        if (features[1] < 0.146879) {
            if (features[4] < 0.024373) {
                var41 = 0.03223805;
            } else {
                var41 = -0.028327066;
            }
        } else {
            var41 = 0.0470554;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[0] < 0.029075) {
                var41 = -0.0024134978;
            } else {
                var41 = -0.05240593;
            }
        } else {
            if (features[4] < 0.058177) {
                var41 = 0.027873356;
            } else {
                var41 = -0.01662926;
            }
        }
    }
    double var42;
    if (features[1] < 0.173326) {
        if (features[3] < 3.7461) {
            if (features[5] < 0.027517) {
                var42 = 0.015666492;
            } else {
                var42 = 0.049322072;
            }
        } else {
            if (features[3] < 3.9613) {
                var42 = -0.058586475;
            } else {
                var42 = 0.033577558;
            }
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[4] < 0.062347) {
                var42 = -0.05044637;
            } else {
                var42 = 0.0067522163;
            }
        } else {
            if (features[4] < 0.060488) {
                var42 = 0.021136863;
            } else {
                var42 = -0.045019764;
            }
        }
    }
    double var43;
    if (features[2] < 38.93) {
        if (features[0] < 0.01548) {
            if (features[0] < 0.013096) {
                var43 = 0.014454032;
            } else {
                var43 = -0.034944735;
            }
        } else {
            if (features[2] < 23.07) {
                var43 = 0.0056577;
            } else {
                var43 = 0.04076514;
            }
        }
    } else {
        if (features[0] < 0.027068) {
            if (features[0] < 0.022567) {
                var43 = 0.005057652;
            } else {
                var43 = 0.036598314;
            }
        } else {
            if (features[4] < 0.040988) {
                var43 = -0.058693208;
            } else {
                var43 = -0.006337137;
            }
        }
    }
    double var44;
    if (features[3] < 1.9315) {
        if (features[3] < -1.2873) {
            if (features[0] < 0.013096) {
                var44 = -0.0027247546;
            } else {
                var44 = 0.025667736;
            }
        } else {
            if (features[2] < 19.73) {
                var44 = -0.00067890395;
            } else {
                var44 = -0.04974764;
            }
        }
    } else {
        if (features[3] < 3.522) {
            if (features[0] < 0.032832) {
                var44 = 0.03956468;
            } else {
                var44 = -0.0014999536;
            }
        } else {
            if (features[5] < 0.030824) {
                var44 = 0.009552676;
            } else {
                var44 = -0.033117678;
            }
        }
    }
    double var45;
    if (features[2] < 44.24) {
        if (features[1] < 0.173326) {
            if (features[2] < 25.24) {
                var45 = 0.008949378;
            } else {
                var45 = 0.050689895;
            }
        } else {
            if (features[3] < 1.113) {
                var45 = -0.017830832;
            } else {
                var45 = 0.017291702;
            }
        }
    } else {
        if (features[6] < 0.690268) {
            if (features[2] < 47.29) {
                var45 = -0.020970585;
            } else {
                var45 = 0.033039194;
            }
        } else {
            if (features[3] < 2.6256) {
                var45 = 0.006285847;
            } else {
                var45 = -0.0539471;
            }
        }
    }
    double var46;
    if (features[3] < 1.9315) {
        if (features[4] < 0.058177) {
            if (features[1] < 0.170443) {
                var46 = 0.028322667;
            } else {
                var46 = -0.011838463;
            }
        } else {
            var46 = -0.049146827;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[1] < 0.197933) {
                var46 = 0.018796718;
            } else {
                var46 = -0.028899172;
            }
        } else {
            var46 = 0.04424076;
        }
    }
    double var47;
    if (features[6] < 0.756389) {
        if (features[0] < 0.027068) {
            if (features[0] < 0.012697) {
                var47 = -0.013052069;
            } else {
                var47 = 0.040763408;
            }
        } else {
            if (features[5] < 0.027517) {
                var47 = -0.014836204;
            } else {
                var47 = 0.03345485;
            }
        }
    } else {
        if (features[6] < 0.994769) {
            if (features[2] < 24.73) {
                var47 = -0.0035608315;
            } else {
                var47 = -0.05347329;
            }
        } else {
            if (features[1] < 0.311264) {
                var47 = 0.024164451;
            } else {
                var47 = -0.038518596;
            }
        }
    }
    double var48;
    if (features[2] < 16.95) {
        var48 = 0.04220095;
    } else {
        if (features[3] < 0.6619) {
            if (features[3] < -1.9766) {
                var48 = 0.01618916;
            } else {
                var48 = -0.049433973;
            }
        } else {
            if (features[0] < 0.032832) {
                var48 = 0.02217266;
            } else {
                var48 = -0.008648771;
            }
        }
    }
    double var49;
    if (features[5] < 0.016067) {
        if (features[4] < 0.026537) {
            if (features[6] < 0.464117) {
                var49 = 0.049913198;
            } else {
                var49 = 0.012616183;
            }
        } else {
            if (features[1] < 0.211673) {
                var49 = -0.019974539;
            } else {
                var49 = 0.025447035;
            }
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[1] < 0.165671) {
                var49 = 0.0044719637;
            } else {
                var49 = -0.03326511;
            }
        } else {
            if (features[1] < 0.311264) {
                var49 = 0.039248485;
            } else {
                var49 = -0.018222466;
            }
        }
    }
    double var50;
    if (features[5] < 0.016424) {
        if (features[0] < 0.015044) {
            if (features[4] < 0.027438) {
                var50 = 0.03663426;
            } else {
                var50 = -0.05017829;
            }
        } else {
            if (features[0] < 0.022883) {
                var50 = 0.053459466;
            } else {
                var50 = 0.00023175306;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[0] < 0.03593) {
                var50 = -0.05337909;
            } else {
                var50 = 0.002783419;
            }
        } else {
            if (features[5] < 0.023569) {
                var50 = 0.037466075;
            } else {
                var50 = -0.007205562;
            }
        }
    }
    double var51;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var51 = 0.04754278;
        } else {
            var51 = -0.016390918;
        }
    } else {
        if (features[4] < 0.032701) {
            if (features[2] < 24.61) {
                var51 = -0.005212177;
            } else {
                var51 = -0.048783217;
            }
        } else {
            if (features[4] < 0.03953) {
                var51 = 0.04520851;
            } else {
                var51 = -0.007681458;
            }
        }
    }
    double var52;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var52 = 0.04805743;
        } else {
            var52 = -0.014547579;
        }
    } else {
        if (features[4] < 0.032701) {
            if (features[6] < 0.421998) {
                var52 = -0.0038714434;
            } else {
                var52 = -0.049549103;
            }
        } else {
            if (features[4] < 0.0606) {
                var52 = 0.019634327;
            } else {
                var52 = -0.025436608;
            }
        }
    }
    double var53;
    if (features[2] < 44.24) {
        if (features[3] < 3.9613) {
            if (features[3] < 3.7988) {
                var53 = 0.014820359;
            } else {
                var53 = -0.056424763;
            }
        } else {
            var53 = 0.054665226;
        }
    } else {
        if (features[3] < 3.4979) {
            if (features[3] < 1.8293) {
                var53 = -0.038146786;
            } else {
                var53 = 0.027576888;
            }
        } else {
            var53 = -0.042204265;
        }
    }
    double var54;
    if (features[0] < 0.01548) {
        if (features[4] < 0.027438) {
            var54 = 0.011617959;
        } else {
            if (features[2] < 20.21) {
                var54 = -0.0430681;
            } else {
                var54 = -0.0051063704;
            }
        }
    } else {
        if (features[0] < 0.017395) {
            var54 = 0.05020187;
        } else {
            if (features[0] < 0.018792) {
                var54 = -0.04423288;
            } else {
                var54 = 0.010834641;
            }
        }
    }
    double var55;
    if (features[3] < 0.6619) {
        if (features[6] < 0.464117) {
            var55 = 0.024100935;
        } else {
            if (features[6] < 0.994769) {
                var55 = -0.051235266;
            } else {
                var55 = -0.016108109;
            }
        }
    } else {
        if (features[0] < 0.032832) {
            if (features[0] < 0.01548) {
                var55 = -0.014845473;
            } else {
                var55 = 0.03005347;
            }
        } else {
            if (features[0] < 0.065067) {
                var55 = -0.021674123;
            } else {
                var55 = 0.03849495;
            }
        }
    }
    double var56;
    if (features[1] < 0.236536) {
        if (features[2] < 38.93) {
            if (features[1] < 0.2333) {
                var56 = 0.019686973;
            } else {
                var56 = -0.039573994;
            }
        } else {
            if (features[5] < 0.012496) {
                var56 = 0.030996267;
            } else {
                var56 = -0.03814288;
            }
        }
    } else {
        if (features[1] < 0.275268) {
            var56 = 0.04505172;
        } else {
            if (features[3] < 3.1043) {
                var56 = -0.0027500654;
            } else {
                var56 = 0.018807266;
            }
        }
    }
    double var57;
    if (features[0] < 0.01548) {
        if (features[4] < 0.027438) {
            var57 = 0.017454186;
        } else {
            if (features[2] < 20.21) {
                var57 = -0.04712558;
            } else {
                var57 = -0.011647791;
            }
        }
    } else {
        if (features[2] < 44.24) {
            if (features[6] < 0.074475) {
                var57 = -0.024328308;
            } else {
                var57 = 0.031657994;
            }
        } else {
            if (features[6] < 0.690268) {
                var57 = 0.010756832;
            } else {
                var57 = -0.034628883;
            }
        }
    }
    double var58;
    if (features[4] < 0.074749) {
        if (features[4] < 0.06538) {
            if (features[4] < 0.032701) {
                var58 = -0.007415735;
            } else {
                var58 = 0.017761176;
            }
        } else {
            var58 = -0.045239065;
        }
    } else {
        var58 = 0.040872093;
    }
    double var59;
    if (features[1] < 0.236536) {
        if (features[1] < 0.166537) {
            if (features[5] < 0.027517) {
                var59 = -0.008844462;
            } else {
                var59 = 0.048125673;
            }
        } else {
            if (features[5] < 0.013877) {
                var59 = 0.01586227;
            } else {
                var59 = -0.030031145;
            }
        }
    } else {
        if (features[1] < 0.275268) {
            var59 = 0.045330703;
        } else {
            if (features[0] < 0.02844) {
                var59 = -0.031646162;
            } else {
                var59 = 0.02487837;
            }
        }
    }
    double var60;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var60 = 0.045301013;
        } else {
            var60 = -0.008206079;
        }
    } else {
        if (features[5] < 0.020334) {
            if (features[5] < 0.016424) {
                var60 = -0.00095818593;
            } else {
                var60 = -0.047590416;
            }
        } else {
            if (features[1] < 0.145017) {
                var60 = -0.016326612;
            } else {
                var60 = 0.02686338;
            }
        }
    }
    double var61;
    if (features[1] < 0.173326) {
        if (features[6] < 0.247043) {
            if (features[4] < 0.031621) {
                var61 = 0.009448671;
            } else {
                var61 = -0.032972123;
            }
        } else {
            if (features[2] < 47.25) {
                var61 = 0.037359875;
            } else {
                var61 = -0.0016148736;
            }
        }
    } else {
        if (features[1] < 0.211673) {
            if (features[4] < 0.062347) {
                var61 = -0.03393508;
            } else {
                var61 = 0.012178054;
            }
        } else {
            if (features[4] < 0.060488) {
                var61 = 0.020689838;
            } else {
                var61 = -0.037611376;
            }
        }
    }
    double var62;
    if (features[3] < 1.9315) {
        if (features[1] < 0.259479) {
            if (features[1] < 0.234905) {
                var62 = -0.018382883;
            } else {
                var62 = 0.033832684;
            }
        } else {
            var62 = -0.051200937;
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[5] < 0.023757) {
                var62 = 0.010420417;
            } else {
                var62 = 0.04586748;
            }
        } else {
            if (features[5] < 0.030824) {
                var62 = 0.016381046;
            } else {
                var62 = -0.038659822;
            }
        }
    }
    double var63;
    if (features[1] < 0.236536) {
        if (features[0] < 0.017479) {
            if (features[0] < 0.01548) {
                var63 = -0.0034640196;
            } else {
                var63 = 0.048256293;
            }
        } else {
            if (features[1] < 0.165671) {
                var63 = 0.011467229;
            } else {
                var63 = -0.035255898;
            }
        }
    } else {
        if (features[3] < 1.9315) {
            var63 = -0.0075219707;
        } else {
            var63 = 0.041014973;
        }
    }
    double var64;
    if (features[2] < 44.24) {
        if (features[4] < 0.049314) {
            if (features[1] < 0.173326) {
                var64 = 0.015608817;
            } else {
                var64 = -0.01745822;
            }
        } else {
            if (features[0] < 0.021319) {
                var64 = 0.0085606165;
            } else {
                var64 = 0.04735751;
            }
        }
    } else {
        if (features[4] < 0.056881) {
            if (features[1] < 0.179458) {
                var64 = -0.020808898;
            } else {
                var64 = 0.026008619;
            }
        } else {
            var64 = -0.04188272;
        }
    }
    double var65;
    if (features[6] < 0.756389) {
        if (features[6] < 0.41723) {
            if (features[2] < 38.06) {
                var65 = 0.016295752;
            } else {
                var65 = -0.023902208;
            }
        } else {
            if (features[2] < 22.07) {
                var65 = 0.01057393;
            } else {
                var65 = 0.04440711;
            }
        }
    } else {
        if (features[6] < 0.923543) {
            if (features[2] < 23.75) {
                var65 = -0.010201974;
            } else {
                var65 = -0.050902374;
            }
        } else {
            if (features[3] < 4.4055) {
                var65 = 0.017837817;
            } else {
                var65 = -0.03752609;
            }
        }
    }
    double var66;
    if (features[2] < 16.95) {
        var66 = 0.035054646;
    } else {
        if (features[3] < 1.9315) {
            if (features[4] < 0.020111) {
                var66 = 0.008420506;
            } else {
                var66 = -0.035917237;
            }
        } else {
            if (features[6] < 0.766371) {
                var66 = 0.020728603;
            } else {
                var66 = -0.009337421;
            }
        }
    }
    double var67;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var67 = 0.04405595;
        } else {
            var67 = -0.017147304;
        }
    } else {
        if (features[4] < 0.032701) {
            if (features[1] < 0.189594) {
                var67 = -0.0075678094;
            } else {
                var67 = -0.04258622;
            }
        } else {
            if (features[4] < 0.03953) {
                var67 = 0.039407108;
            } else {
                var67 = -0.0045023183;
            }
        }
    }
    double var68;
    if (features[6] < 0.773166) {
        if (features[1] < 0.211673) {
            if (features[6] < 0.074475) {
                var68 = -0.030103145;
            } else {
                var68 = 0.020138767;
            }
        } else {
            if (features[2] < 19.64) {
                var68 = 0.009316578;
            } else {
                var68 = 0.038666457;
            }
        }
    } else {
        if (features[6] < 0.923543) {
            var68 = -0.047934376;
        } else {
            if (features[1] < 0.182103) {
                var68 = 0.039343607;
            } else {
                var68 = -0.0130620245;
            }
        }
    }
    double var69;
    if (features[3] < 0.6619) {
        if (features[6] < 0.479061) {
            if (features[6] < 0.41723) {
                var69 = -0.00084419356;
            } else {
                var69 = 0.03375369;
            }
        } else {
            if (features[0] < 0.028314) {
                var69 = -0.052057207;
            } else {
                var69 = 0.0015261618;
            }
        }
    } else {
        if (features[5] < 0.016424) {
            if (features[0] < 0.015044) {
                var69 = -0.01013768;
            } else {
                var69 = 0.039907422;
            }
        } else {
            if (features[5] < 0.019235) {
                var69 = -0.034784485;
            } else {
                var69 = 0.006303735;
            }
        }
    }
    double var70;
    if (features[2] < 17.75) {
        var70 = 0.038314532;
    } else {
        if (features[6] < 0.773166) {
            if (features[3] < 2.4056) {
                var70 = -0.012592931;
            } else {
                var70 = 0.031731978;
            }
        } else {
            if (features[6] < 0.907802) {
                var70 = -0.052114405;
            } else {
                var70 = -0.0040544015;
            }
        }
    }
    double var71;
    if (features[2] < 44.24) {
        if (features[0] < 0.041016) {
            if (features[2] < 16.95) {
                var71 = 0.036837958;
            } else {
                var71 = -0.007997072;
            }
        } else {
            var71 = 0.035708733;
        }
    } else {
        if (features[5] < 0.016901) {
            var71 = 0.0056358776;
        } else {
            var71 = -0.040955227;
        }
    }
    double var72;
    if (features[1] < 0.166537) {
        if (features[1] < 0.146879) {
            if (features[2] < 25.24) {
                var72 = -0.03415687;
            } else {
                var72 = 0.017855844;
            }
        } else {
            var72 = 0.03821367;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[0] < 0.017395) {
                var72 = 0.00676317;
            } else {
                var72 = -0.029352624;
            }
        } else {
            if (features[1] < 0.273085) {
                var72 = 0.039684445;
            } else {
                var72 = -0.010052096;
            }
        }
    }
    double var73;
    if (features[2] < 44.24) {
        if (features[4] < 0.044077) {
            if (features[4] < 0.03953) {
                var73 = 0.008502558;
            } else {
                var73 = -0.035681866;
            }
        } else {
            if (features[6] < 0.036636) {
                var73 = 0.0018806172;
            } else {
                var73 = 0.040120333;
            }
        }
    } else {
        if (features[2] < 48.67) {
            var73 = -0.040631603;
        } else {
            if (features[6] < 0.690268) {
                var73 = 0.027895784;
            } else {
                var73 = -0.017105171;
            }
        }
    }
    double var74;
    if (features[4] < 0.074749) {
        if (features[4] < 0.0606) {
            if (features[1] < 0.211673) {
                var74 = -0.008281656;
            } else {
                var74 = 0.023375824;
            }
        } else {
            var74 = -0.04233561;
        }
    } else {
        var74 = 0.033249125;
    }
    double var75;
    if (features[5] < 0.016067) {
        if (features[5] < 0.005951) {
            var75 = -0.020917132;
        } else {
            if (features[0] < 0.015044) {
                var75 = -0.011210161;
            } else {
                var75 = 0.03442459;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[1] < 0.182103) {
                var75 = 0.004313036;
            } else {
                var75 = -0.04287259;
            }
        } else {
            if (features[1] < 0.21151) {
                var75 = -0.006998822;
            } else {
                var75 = 0.029263426;
            }
        }
    }
    double var76;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var76 = 0.043030187;
        } else {
            var76 = -0.0039315457;
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[2] < 15.84) {
                var76 = 0.024564799;
            } else {
                var76 = -0.034240022;
            }
        } else {
            if (features[5] < 0.031586) {
                var76 = 0.017624168;
            } else {
                var76 = -0.026760677;
            }
        }
    }
    double var77;
    if (features[1] < 0.166537) {
        if (features[5] < 0.027517) {
            if (features[5] < 0.018909) {
                var77 = 0.014109745;
            } else {
                var77 = -0.040420245;
            }
        } else {
            var77 = 0.045536894;
        }
    } else {
        if (features[1] < 0.207449) {
            if (features[5] < 0.011373) {
                var77 = 0.008986762;
            } else {
                var77 = -0.036508523;
            }
        } else {
            if (features[0] < 0.012697) {
                var77 = -0.021922024;
            } else {
                var77 = 0.013723545;
            }
        }
    }
    double var78;
    if (features[2] < 16.95) {
        var78 = 0.03287609;
    } else {
        if (features[3] < 3.9613) {
            if (features[3] < 3.6854) {
                var78 = -0.0020692975;
            } else {
                var78 = -0.047805116;
            }
        } else {
            if (features[4] < 0.02804) {
                var78 = -0.020515637;
            } else {
                var78 = 0.038426418;
            }
        }
    }
    double var79;
    if (features[4] < 0.013037) {
        if (features[4] < -0.028531) {
            var79 = -0.006248126;
        } else {
            var79 = 0.03363114;
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[1] < 0.1861) {
                var79 = 0.0041230344;
            } else {
                var79 = -0.0348771;
            }
        } else {
            if (features[3] < 3.0209) {
                var79 = 0.03051113;
            } else {
                var79 = -0.0076697865;
            }
        }
    }
    double var80;
    if (features[1] < 0.236536) {
        if (features[3] < -0.5982) {
            if (features[6] < 0.479061) {
                var80 = 0.044553526;
            } else {
                var80 = -0.005632139;
            }
        } else {
            if (features[3] < 0.6619) {
                var80 = -0.04212178;
            } else {
                var80 = -0.0048249825;
            }
        }
    } else {
        if (features[1] < 0.311264) {
            var80 = 0.04418419;
        } else {
            var80 = -0.012835686;
        }
    }
    double var81;
    if (features[5] < 0.016424) {
        if (features[3] < 0.6619) {
            if (features[6] < 0.4964) {
                var81 = 0.013480179;
            } else {
                var81 = -0.032385286;
            }
        } else {
            if (features[4] < 0.047944) {
                var81 = 0.043000367;
            } else {
                var81 = -0.02350485;
            }
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[6] < 1.147066) {
                var81 = -0.0057139504;
            } else {
                var81 = -0.05885746;
            }
        } else {
            if (features[5] < 0.023569) {
                var81 = 0.03630895;
            } else {
                var81 = -0.008685767;
            }
        }
    }
    double var82;
    if (features[0] < 0.027068) {
        if (features[6] < 1.144717) {
            if (features[5] < 0.007855) {
                var82 = -0.010125055;
            } else {
                var82 = 0.033625923;
            }
        } else {
            var82 = -0.032986786;
        }
    } else {
        if (features[6] < 1.114548) {
            if (features[1] < 0.156573) {
                var82 = 0.0019150184;
            } else {
                var82 = -0.03953076;
            }
        } else {
            if (features[6] < 1.297501) {
                var82 = 0.04077233;
            } else {
                var82 = -0.009332657;
            }
        }
    }
    double var83;
    if (features[5] < 0.016067) {
        if (features[0] < 0.015044) {
            var83 = -0.021366308;
        } else {
            if (features[0] < 0.032781) {
                var83 = 0.03433926;
            } else {
                var83 = -0.008146777;
            }
        }
    } else {
        if (features[4] < 0.049573) {
            if (features[2] < 23.81) {
                var83 = 0.0018846722;
            } else {
                var83 = -0.037456825;
            }
        } else {
            if (features[4] < 0.0606) {
                var83 = 0.041740887;
            } else {
                var83 = -0.009654636;
            }
        }
    }
    double var84;
    if (features[1] < 0.139201) {
        var84 = 0.02588757;
    } else {
        if (features[1] < 0.146879) {
            var84 = -0.031194065;
        } else {
            if (features[1] < 0.173326) {
                var84 = 0.023508623;
            } else {
                var84 = -0.00705504;
            }
        }
    }
    double var85;
    if (features[4] < 0.013681) {
        if (features[5] < 0.018909) {
            var85 = 0.04062569;
        } else {
            var85 = 0.0006010697;
        }
    } else {
        if (features[3] < 1.9315) {
            if (features[2] < 19.73) {
                var85 = 0.0023092248;
            } else {
                var85 = -0.03498325;
            }
        } else {
            if (features[3] < 3.7988) {
                var85 = 0.021259788;
            } else {
                var85 = -0.012202737;
            }
        }
    }
    double var86;
    if (features[1] < 0.211673) {
        if (features[1] < 0.173326) {
            if (features[1] < 0.146879) {
                var86 = -0.006074175;
            } else {
                var86 = 0.032620177;
            }
        } else {
            if (features[3] < 3.2613) {
                var86 = -0.03850561;
            } else {
                var86 = -0.0011308645;
            }
        }
    } else {
        if (features[4] < 0.060488) {
            if (features[4] < 0.031117) {
                var86 = 0.0065710978;
            } else {
                var86 = 0.036012392;
            }
        } else {
            var86 = -0.023319645;
        }
    }
    double var87;
    if (features[2] < 44.24) {
        if (features[2] < 40.4) {
            if (features[1] < 0.173326) {
                var87 = 0.023057586;
            } else {
                var87 = -0.0054512;
            }
        } else {
            var87 = 0.04021656;
        }
    } else {
        if (features[5] < 0.016901) {
            if (features[4] < 0.047635) {
                var87 = 0.031369198;
            } else {
                var87 = -0.009162752;
            }
        } else {
            if (features[5] < 0.019221) {
                var87 = -0.038013306;
            } else {
                var87 = -0.013336238;
            }
        }
    }
    double var88;
    if (features[3] < 3.9613) {
        if (features[3] < 3.7988) {
            if (features[0] < 0.017479) {
                var88 = 0.024133472;
            } else {
                var88 = -0.0025454478;
            }
        } else {
            var88 = -0.04509067;
        }
    } else {
        if (features[0] < 0.029097) {
            var88 = 0.043028772;
        } else {
            var88 = 0.0033248179;
        }
    }
    double var89;
    if (features[1] < 0.173326) {
        if (features[5] < 0.027517) {
            if (features[5] < 0.018909) {
                var89 = 0.02005914;
            } else {
                var89 = -0.03959943;
            }
        } else {
            var89 = 0.042879168;
        }
    } else {
        if (features[1] < 0.236536) {
            if (features[5] < 0.013877) {
                var89 = 0.007961042;
            } else {
                var89 = -0.03148505;
            }
        } else {
            if (features[1] < 0.311264) {
                var89 = 0.03360743;
            } else {
                var89 = -0.011835038;
            }
        }
    }
    double var90;
    if (features[6] < 0.994769) {
        if (features[4] < 0.020107) {
            if (features[5] < 0.018909) {
                var90 = 0.038564857;
            } else {
                var90 = -0.017846938;
            }
        } else {
            if (features[6] < 0.773166) {
                var90 = -0.009318172;
            } else {
                var90 = -0.03876947;
            }
        }
    } else {
        if (features[6] < 1.147066) {
            var90 = 0.039329346;
        } else {
            if (features[0] < 0.020623) {
                var90 = -0.039079078;
            } else {
                var90 = 0.018502591;
            }
        }
    }
    double var91;
    if (features[6] < 0.773166) {
        if (features[3] < 3.2613) {
            if (features[3] < -0.6789) {
                var91 = 0.02733906;
            } else {
                var91 = -0.01467594;
            }
        } else {
            if (features[5] < 0.029379) {
                var91 = 0.033008095;
            } else {
                var91 = 0.0033906326;
            }
        }
    } else {
        if (features[6] < 0.994769) {
            var91 = -0.03618542;
        } else {
            if (features[3] < 4.4055) {
                var91 = 0.019988937;
            } else {
                var91 = -0.025785094;
            }
        }
    }
    double var92;
    if (features[4] < 0.018382) {
        if (features[5] < 0.018909) {
            var92 = 0.039613724;
        } else {
            var92 = -0.014480533;
        }
    } else {
        if (features[5] < 0.019235) {
            if (features[5] < 0.016424) {
                var92 = -0.011120134;
            } else {
                var92 = -0.04220528;
            }
        } else {
            if (features[5] < 0.023569) {
                var92 = 0.038262364;
            } else {
                var92 = -0.0031294022;
            }
        }
    }
    double var93;
    if (features[1] < 0.211673) {
        if (features[0] < 0.021051) {
            if (features[1] < 0.195945) {
                var93 = 0.026554143;
            } else {
                var93 = -0.028212601;
            }
        } else {
            if (features[1] < 0.165671) {
                var93 = -0.0012212613;
            } else {
                var93 = -0.038097948;
            }
        }
    } else {
        if (features[2] < 27.52) {
            if (features[0] < 0.015289) {
                var93 = 0.006908346;
            } else {
                var93 = 0.040114805;
            }
        } else {
            if (features[0] < 0.021132) {
                var93 = -0.021431478;
            } else {
                var93 = 0.015018205;
            }
        }
    }
    double var94;
    if (features[4] < 0.0606) {
        if (features[6] < 1.147066) {
            if (features[0] < 0.027068) {
                var94 = 0.028299663;
            } else {
                var94 = -0.0029039942;
            }
        } else {
            if (features[0] < 0.021132) {
                var94 = -0.04848857;
            } else {
                var94 = 0.013806011;
            }
        }
    } else {
        if (features[4] < 0.074749) {
            var94 = -0.04012295;
        } else {
            var94 = 0.018136261;
        }
    }
    double var95;
    if (features[3] < 1.9315) {
        if (features[4] < 0.024373) {
            if (features[6] < 0.479061) {
                var95 = 0.025478108;
            } else {
                var95 = 0.0018289626;
            }
        } else {
            if (features[5] < 0.011552) {
                var95 = -0.0009507268;
            } else {
                var95 = -0.033988085;
            }
        }
    } else {
        if (features[3] < 3.6854) {
            if (features[1] < 0.156657) {
                var95 = -0.0017539129;
            } else {
                var95 = 0.041812535;
            }
        } else {
            if (features[5] < 0.030824) {
                var95 = 0.0104718525;
            } else {
                var95 = -0.03364818;
            }
        }
    }
    double var96;
    if (features[2] < 17.75) {
        var96 = 0.020062929;
    } else {
        if (features[2] < 20.4) {
            var96 = -0.03241484;
        } else {
            if (features[0] < 0.014185) {
                var96 = 0.026572693;
            } else {
                var96 = -0.0058260527;
            }
        }
    }
    double var97;
    if (features[2] < 27.53) {
        if (features[4] < 0.013681) {
            var97 = 0.02659954;
        } else {
            if (features[2] < 15.99) {
                var97 = 0.014321312;
            } else {
                var97 = -0.036410876;
            }
        }
    } else {
        if (features[2] < 44.24) {
            if (features[5] < 0.030824) {
                var97 = 0.035630304;
            } else {
                var97 = -0.009755996;
            }
        } else {
            if (features[5] < 0.014423) {
                var97 = 0.024708403;
            } else {
                var97 = -0.022061137;
            }
        }
    }
    double var98;
    if (features[1] < 0.211673) {
        if (features[6] < 0.923543) {
            if (features[6] < 0.741746) {
                var98 = -0.004739483;
            } else {
                var98 = -0.0440451;
            }
        } else {
            if (features[6] < 1.297501) {
                var98 = 0.03856831;
            } else {
                var98 = -0.034473058;
            }
        }
    } else {
        if (features[5] < 0.019235) {
            if (features[5] < 0.016424) {
                var98 = 0.021381252;
            } else {
                var98 = -0.025343135;
            }
        } else {
            if (features[1] < 0.288725) {
                var98 = 0.04600913;
            } else {
                var98 = 0.005400825;
            }
        }
    }
    double var99;
    if (features[5] < 0.016067) {
        if (features[4] < 0.051639) {
            if (features[5] < 0.007855) {
                var99 = -0.0023822866;
            } else {
                var99 = 0.035284664;
            }
        } else {
            var99 = -0.018898638;
        }
    } else {
        if (features[5] < 0.019349) {
            if (features[4] < 0.041939) {
                var99 = -0.04240337;
            } else {
                var99 = 0.0068092193;
            }
        } else {
            if (features[5] < 0.031586) {
                var99 = 0.023352765;
            } else {
                var99 = -0.015632866;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
