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
    if (features[2] < 38.59) {
        if (features[1] < 0.000008) {
            var0 = -0.06363636;
        } else {
            if (features[2] < 23.07) {
                var0 = -0.02857143;
            } else {
                var0 = 0.037142858;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var0 = -0.06923077;
        } else {
            var0 = 0.0;
        }
    }
    double var1;
    if (features[2] < 38.59) {
        if (features[1] < 0.000008) {
            var1 = -0.051680297;
        } else {
            if (features[1] < 0.000018) {
                var1 = 0.074445285;
            } else {
                var1 = 0.0021389758;
            }
        }
    } else {
        var1 = -0.06949889;
    }
    double var2;
    if (features[4] < -0.99973) {
        if (features[1] < 0.000014) {
            if (features[1] < 0.000008) {
                var2 = -0.046262674;
            } else {
                var2 = 0.044538643;
            }
        } else {
            var2 = -0.05363084;
        }
    } else {
        if (features[3] < 1.2772) {
            if (features[0] < 62.278816) {
                var2 = 0.010353951;
            } else {
                var2 = 0.060260277;
            }
        } else {
            var2 = -0.032487776;
        }
    }
    double var3;
    if (features[4] < -0.999727) {
        if (features[3] < -2.9023) {
            var3 = 0.02656884;
        } else {
            if (features[3] < -0.0737) {
                var3 = -0.06909012;
            } else {
                var3 = -0.0134747;
            }
        }
    } else {
        if (features[3] < -1.1427) {
            var3 = 0.06175238;
        } else {
            var3 = 0.000045473556;
        }
    }
    double var4;
    if (features[4] < -0.99973) {
        if (features[3] < -3.2219) {
            var4 = 0.032176252;
        } else {
            if (features[3] < -0.0737) {
                var4 = -0.05953304;
            } else {
                var4 = -0.0015542815;
            }
        }
    } else {
        if (features[3] < -1.0619) {
            var4 = 0.06358483;
        } else {
            var4 = -0.006935995;
        }
    }
    double var5;
    if (features[2] < 38.59) {
        if (features[6] < 0.000015) {
            var5 = 0.05059394;
        } else {
            if (features[0] < 65.95301) {
                var5 = -0.036907878;
            } else {
                var5 = 0.009769832;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var5 = -0.06753222;
        } else {
            var5 = -0.007905653;
        }
    }
    double var6;
    if (features[2] < 38.59) {
        if (features[0] < 54.69221) {
            var6 = -0.025754496;
        } else {
            if (features[3] < -0.5068) {
                var6 = 0.0005256605;
            } else {
                var6 = 0.046945363;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var6 = -0.061627682;
        } else {
            var6 = -0.009034993;
        }
    }
    double var7;
    if (features[6] < 0.00008) {
        if (features[0] < 152.01608) {
            var7 = 0.059211027;
        } else {
            if (features[6] < 0.000027) {
                var7 = 0.008670741;
            } else {
                var7 = -0.04018062;
            }
        }
    } else {
        if (features[3] < -2.2161) {
            var7 = 0.011927678;
        } else {
            var7 = -0.052719336;
        }
    }
    double var8;
    if (features[2] < 38.59) {
        if (features[3] < -0.4071) {
            if (features[3] < -3.2219) {
                var8 = 0.051161345;
            } else {
                var8 = -0.04167915;
            }
        } else {
            if (features[0] < 79.21245) {
                var8 = -0.009649439;
            } else {
                var8 = 0.052090384;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var8 = -0.058829047;
        } else {
            var8 = -0.0065434226;
        }
    }
    double var9;
    if (features[6] < 0.000015) {
        if (features[2] < 29.59) {
            var9 = 0.053536206;
        } else {
            var9 = 0.008891016;
        }
    } else {
        if (features[4] < -0.999729) {
            if (features[6] < 0.000062) {
                var9 = -0.00082715537;
            } else {
                var9 = -0.04849583;
            }
        } else {
            if (features[6] < 0.000115) {
                var9 = 0.039373636;
            } else {
                var9 = -0.0110856285;
            }
        }
    }
    double var10;
    if (features[4] < -0.99973) {
        if (features[6] < 0.000062) {
            if (features[5] < 0.004968) {
                var10 = 0.02515359;
            } else {
                var10 = -0.026906444;
            }
        } else {
            if (features[4] < -0.999756) {
                var10 = -0.050915875;
            } else {
                var10 = -0.012916679;
            }
        }
    } else {
        if (features[6] < 0.000071) {
            var10 = 0.05870988;
        } else {
            if (features[5] < 0.007383) {
                var10 = -0.034173515;
            } else {
                var10 = 0.019474763;
            }
        }
    }
    double var11;
    if (features[6] < 0.000027) {
        if (features[5] < 0.005179) {
            var11 = 0.04891274;
        } else {
            var11 = 0.006748624;
        }
    } else {
        if (features[3] < -2.2161) {
            var11 = 0.02777733;
        } else {
            if (features[3] < -0.0737) {
                var11 = -0.05379122;
            } else {
                var11 = -0.023109557;
            }
        }
    }
    double var12;
    if (features[2] < 35.87) {
        if (features[1] < 0.000008) {
            var12 = -0.043666;
        } else {
            if (features[6] < 0.000115) {
                var12 = 0.03582708;
            } else {
                var12 = -0.021523034;
            }
        }
    } else {
        if (features[2] < 47.96) {
            var12 = -0.05226908;
        } else {
            var12 = -0.00508721;
        }
    }
    double var13;
    if (features[1] < 0.000026) {
        if (features[1] < 0.00001) {
            var13 = -0.051559784;
        } else {
            if (features[6] < 0.000067) {
                var13 = 0.049073365;
            } else {
                var13 = -0.00054150814;
            }
        }
    } else {
        if (features[6] < 0.00008) {
            var13 = 0.0024375913;
        } else {
            var13 = -0.05197617;
        }
    }
    double var14;
    if (features[6] < 0.000015) {
        if (features[2] < 29.59) {
            var14 = 0.04976851;
        } else {
            var14 = 0.007959483;
        }
    } else {
        if (features[1] < 0.000008) {
            var14 = -0.05647401;
        } else {
            if (features[1] < 0.000014) {
                var14 = 0.040649127;
            } else {
                var14 = -0.022463402;
            }
        }
    }
    double var15;
    if (features[1] < 0.000008) {
        var15 = -0.055369835;
    } else {
        if (features[2] < 38.59) {
            if (features[1] < 0.000035) {
                var15 = 0.038534414;
            } else {
                var15 = -0.023037167;
            }
        } else {
            if (features[2] < 47.01) {
                var15 = -0.0570137;
            } else {
                var15 = 0.0054914807;
            }
        }
    }
    double var16;
    if (features[6] < 0.000015) {
        var16 = 0.04525214;
    } else {
        if (features[3] < -2.8558) {
            var16 = 0.016252724;
        } else {
            if (features[3] < -0.0737) {
                var16 = -0.043703225;
            } else {
                var16 = -0.001848751;
            }
        }
    }
    double var17;
    if (features[6] < 0.000015) {
        var17 = 0.043652397;
    } else {
        if (features[3] < -3.2219) {
            var17 = 0.03195707;
        } else {
            if (features[4] < -0.999727) {
                var17 = -0.034129035;
            } else {
                var17 = 0.011088554;
            }
        }
    }
    double var18;
    if (features[4] < -0.999727) {
        if (features[0] < 90.924515) {
            var18 = -0.04800212;
        } else {
            if (features[1] < 0.00001) {
                var18 = -0.037144266;
            } else {
                var18 = 0.014434575;
            }
        }
    } else {
        if (features[6] < 0.000115) {
            var18 = 0.045488432;
        } else {
            var18 = -0.00891317;
        }
    }
    double var19;
    if (features[4] < -0.999753) {
        if (features[4] < -0.999838) {
            if (features[1] < 0.00001) {
                var19 = -0.025348073;
            } else {
                var19 = 0.03942169;
            }
        } else {
            if (features[0] < 198.30162) {
                var19 = -0.04850465;
            } else {
                var19 = -0.013267604;
            }
        }
    } else {
        if (features[0] < 59.650723) {
            var19 = -0.0065741213;
        } else {
            if (features[2] < 37.19) {
                var19 = 0.06326876;
            } else {
                var19 = -0.0038189925;
            }
        }
    }
    double var20;
    if (features[6] < 0.000027) {
        if (features[1] < 0.00001) {
            var20 = 0.0029505834;
        } else {
            var20 = 0.042049084;
        }
    } else {
        if (features[4] < -0.999727) {
            if (features[5] < 0.012746) {
                var20 = -0.032440614;
            } else {
                var20 = 0.015088799;
            }
        } else {
            if (features[1] < 0.000026) {
                var20 = 0.045099434;
            } else {
                var20 = -0.013419777;
            }
        }
    }
    double var21;
    if (features[6] < 0.000062) {
        if (features[1] < 0.000008) {
            var21 = -0.02940884;
        } else {
            if (features[2] < 31.06) {
                var21 = 0.05481137;
            } else {
                var21 = 0.0023607442;
            }
        }
    } else {
        if (features[3] < -2.499) {
            var21 = 0.010194381;
        } else {
            if (features[2] < 23.72) {
                var21 = -0.0020281426;
            } else {
                var21 = -0.057263393;
            }
        }
    }
    double var22;
    if (features[0] < 72.62282) {
        if (features[6] < 0.000108) {
            var22 = -0.014758457;
        } else {
            var22 = -0.04839113;
        }
    } else {
        if (features[2] < 38.59) {
            if (features[4] < -0.999845) {
                var22 = -0.028080523;
            } else {
                var22 = 0.032872923;
            }
        } else {
            if (features[2] < 47.01) {
                var22 = -0.051541507;
            } else {
                var22 = 0.0067127696;
            }
        }
    }
    double var23;
    if (features[4] < -0.99973) {
        if (features[4] < -0.999838) {
            if (features[4] < -0.999842) {
                var23 = -0.012020675;
            } else {
                var23 = 0.033091396;
            }
        } else {
            if (features[3] < -3.0257) {
                var23 = -0.0050102193;
            } else {
                var23 = -0.045878403;
            }
        }
    } else {
        if (features[3] < -1.0619) {
            var23 = 0.04606281;
        } else {
            var23 = -0.0111450255;
        }
    }
    double var24;
    if (features[6] < 0.000027) {
        if (features[1] < 0.00001) {
            var24 = 0.0035312392;
        } else {
            var24 = 0.037047226;
        }
    } else {
        if (features[4] < -0.999729) {
            if (features[6] < 0.000092) {
                var24 = -0.04450816;
            } else {
                var24 = -0.009816474;
            }
        } else {
            if (features[1] < 0.000026) {
                var24 = 0.039909523;
            } else {
                var24 = -0.023882011;
            }
        }
    }
    double var25;
    if (features[6] < 0.000062) {
        if (features[5] < 0.006921) {
            if (features[2] < 26.36) {
                var25 = 0.008408865;
            } else {
                var25 = 0.0510507;
            }
        } else {
            if (features[5] < 0.010742) {
                var25 = -0.031652015;
            } else {
                var25 = 0.034870338;
            }
        }
    } else {
        if (features[2] < 37.19) {
            if (features[0] < 65.95301) {
                var25 = -0.03282833;
            } else {
                var25 = 0.022948002;
            }
        } else {
            var25 = -0.03989702;
        }
    }
    double var26;
    if (features[6] < 0.000027) {
        if (features[2] < 25.29) {
            var26 = 0.0057004285;
        } else {
            var26 = 0.044990964;
        }
    } else {
        if (features[3] < -3.2219) {
            var26 = 0.030196432;
        } else {
            if (features[1] < 0.000025) {
                var26 = -0.003211429;
            } else {
                var26 = -0.039761122;
            }
        }
    }
    double var27;
    if (features[4] < -0.999729) {
        if (features[6] < 0.000062) {
            if (features[1] < 0.00001) {
                var27 = -0.0391798;
            } else {
                var27 = 0.03549751;
            }
        } else {
            if (features[6] < 0.000134) {
                var27 = -0.048756476;
            } else {
                var27 = -0.011865014;
            }
        }
    } else {
        if (features[1] < 0.000026) {
            var27 = 0.054017354;
        } else {
            var27 = -0.005364929;
        }
    }
    double var28;
    if (features[6] < 0.000115) {
        if (features[2] < 32.51) {
            if (features[5] < 0.003935) {
                var28 = -0.022076583;
            } else {
                var28 = 0.036419984;
            }
        } else {
            if (features[5] < 0.004529) {
                var28 = 0.03709453;
            } else {
                var28 = -0.035664678;
            }
        }
    } else {
        if (features[0] < 72.62282) {
            var28 = -0.045179863;
        } else {
            var28 = -0.0034847178;
        }
    }
    double var29;
    if (features[1] < 0.000008) {
        var29 = -0.03755377;
    } else {
        if (features[6] < 0.00006) {
            if (features[2] < 31.06) {
                var29 = 0.051407255;
            } else {
                var29 = -0.0009361702;
            }
        } else {
            if (features[4] < -0.999727) {
                var29 = -0.028932676;
            } else {
                var29 = 0.026003022;
            }
        }
    }
    double var30;
    if (features[2] < 38.59) {
        if (features[1] < 0.000008) {
            var30 = -0.030588811;
        } else {
            if (features[0] < 65.95301) {
                var30 = -0.01857543;
            } else {
                var30 = 0.030070681;
            }
        }
    } else {
        if (features[1] < 0.00002) {
            var30 = 0.0004041878;
        } else {
            var30 = -0.04698623;
        }
    }
    double var31;
    if (features[4] < -0.999729) {
        if (features[3] < -0.4071) {
            if (features[2] < 25.24) {
                var31 = -0.057169687;
            } else {
                var31 = 0.004716078;
            }
        } else {
            if (features[2] < 25.29) {
                var31 = 0.032737575;
            } else {
                var31 = -0.023115596;
            }
        }
    } else {
        if (features[3] < -1.0619) {
            var31 = 0.051348276;
        } else {
            var31 = -0.020603796;
        }
    }
    double var32;
    if (features[1] < 0.000008) {
        var32 = -0.03141913;
    } else {
        if (features[6] < 0.000062) {
            if (features[0] < 290.8009) {
                var32 = 0.048006922;
            } else {
                var32 = -0.014167653;
            }
        } else {
            if (features[4] < -0.999753) {
                var32 = -0.036178898;
            } else {
                var32 = 0.012382072;
            }
        }
    }
    double var33;
    if (features[4] < -0.999729) {
        if (features[3] < -0.0737) {
            if (features[3] < -3.0325) {
                var33 = 0.0094696805;
            } else {
                var33 = -0.058295544;
            }
        } else {
            if (features[4] < -0.999791) {
                var33 = 0.020582905;
            } else {
                var33 = -0.019767722;
            }
        }
    } else {
        if (features[3] < -1.0619) {
            var33 = 0.051576287;
        } else {
            if (features[6] < 0.000114) {
                var33 = 0.0146963075;
            } else {
                var33 = -0.022268608;
            }
        }
    }
    double var34;
    if (features[6] < 0.000027) {
        if (features[1] < 0.000008) {
            var34 = -0.015075495;
        } else {
            if (features[5] < 0.006921) {
                var34 = 0.04668794;
            } else {
                var34 = 0.0067329197;
            }
        }
    } else {
        if (features[3] < -2.2161) {
            if (features[4] < -0.999791) {
                var34 = -0.0057407985;
            } else {
                var34 = 0.02830553;
            }
        } else {
            if (features[3] < 2.4052) {
                var34 = -0.04853664;
            } else {
                var34 = -0.0037758488;
            }
        }
    }
    double var35;
    if (features[1] < 0.000026) {
        if (features[1] < 0.00001) {
            var35 = -0.02950096;
        } else {
            if (features[6] < 0.000067) {
                var35 = 0.038577817;
            } else {
                var35 = 0.0038575113;
            }
        }
    } else {
        if (features[4] < -0.999763) {
            var35 = 0.0019518556;
        } else {
            var35 = -0.044432368;
        }
    }
    double var36;
    if (features[2] < 38.59) {
        if (features[1] < 0.000008) {
            var36 = -0.029147191;
        } else {
            if (features[0] < 108.21798) {
                var36 = -0.004369806;
            } else {
                var36 = 0.05447315;
            }
        }
    } else {
        if (features[2] < 46.68) {
            var36 = -0.03839019;
        } else {
            var36 = -0.0012422398;
        }
    }
    double var37;
    if (features[2] < 35.87) {
        if (features[4] < -0.999729) {
            if (features[0] < 108.21798) {
                var37 = -0.036337484;
            } else {
                var37 = 0.012691513;
            }
        } else {
            if (features[0] < 62.278816) {
                var37 = 0.008456385;
            } else {
                var37 = 0.038728558;
            }
        }
    } else {
        if (features[3] < -1.0619) {
            var37 = 0.013073373;
        } else {
            var37 = -0.050070394;
        }
    }
    double var38;
    if (features[6] < 0.000218) {
        if (features[1] < 0.00001) {
            if (features[0] < 240.37965) {
                var38 = -0.03526394;
            } else {
                var38 = -0.004602287;
            }
        } else {
            if (features[6] < 0.000062) {
                var38 = 0.038834494;
            } else {
                var38 = -0.0032037017;
            }
        }
    } else {
        var38 = -0.03658761;
    }
    double var39;
    if (features[6] < 0.000027) {
        if (features[5] < 0.006921) {
            var39 = 0.04460696;
        } else {
            var39 = 0.005024113;
        }
    } else {
        if (features[3] < 3.5898) {
            if (features[3] < 0.9524) {
                var39 = -0.017890086;
            } else {
                var39 = 0.029530784;
            }
        } else {
            var39 = -0.033850607;
        }
    }
    double var40;
    if (features[1] < 0.00001) {
        var40 = -0.043678354;
    } else {
        if (features[1] < 0.000026) {
            if (features[2] < 23.07) {
                var40 = 0.0051750178;
            } else {
                var40 = 0.041673064;
            }
        } else {
            if (features[1] < 0.00003) {
                var40 = -0.04041594;
            } else {
                var40 = 0.0051738;
            }
        }
    }
    double var41;
    if (features[1] < 0.000008) {
        var41 = -0.040206663;
    } else {
        if (features[3] < -2.2161) {
            var41 = 0.033393957;
        } else {
            if (features[0] < 65.95301) {
                var41 = -0.034341406;
            } else {
                var41 = 0.008179566;
            }
        }
    }
    double var42;
    if (features[5] < 0.013178) {
        if (features[4] < -0.999723) {
            if (features[0] < 72.62282) {
                var42 = -0.0373596;
            } else {
                var42 = 0.00208431;
            }
        } else {
            var42 = 0.029682508;
        }
    } else {
        var42 = -0.04017856;
    }
    double var43;
    if (features[2] < 35.87) {
        if (features[2] < 23.07) {
            if (features[2] < 20.73) {
                var43 = -0.0027748176;
            } else {
                var43 = -0.03643752;
            }
        } else {
            if (features[5] < 0.010291) {
                var43 = 0.031084692;
            } else {
                var43 = -0.013048619;
            }
        }
    } else {
        if (features[4] < -0.999731) {
            var43 = -0.04588142;
        } else {
            var43 = -0.0059570647;
        }
    }
    double var44;
    if (features[1] < 0.000008) {
        var44 = -0.03950105;
    } else {
        if (features[1] < 0.000018) {
            if (features[2] < 32.51) {
                var44 = 0.048931416;
            } else {
                var44 = 0.000506723;
            }
        } else {
            if (features[5] < 0.004837) {
                var44 = -0.027453443;
            } else {
                var44 = 0.009488696;
            }
        }
    }
    double var45;
    if (features[1] < 0.000026) {
        if (features[1] < 0.00001) {
            if (features[6] < 0.000026) {
                var45 = -0.028560633;
            } else {
                var45 = -0.0011107612;
            }
        } else {
            if (features[0] < 65.68104) {
                var45 = -0.003826099;
            } else {
                var45 = 0.034983266;
            }
        }
    } else {
        if (features[0] < 108.21798) {
            if (features[1] < 0.000035) {
                var45 = -0.01082916;
            } else {
                var45 = -0.045112163;
            }
        } else {
            var45 = 0.012349876;
        }
    }
    double var46;
    if (features[1] < 0.00001) {
        var46 = -0.040717788;
    } else {
        if (features[6] < 0.000062) {
            if (features[4] < -0.999791) {
                var46 = 0.04380381;
            } else {
                var46 = 0.009204354;
            }
        } else {
            if (features[0] < 108.21798) {
                var46 = -0.03361591;
            } else {
                var46 = 0.012128084;
            }
        }
    }
    double var47;
    if (features[0] < 152.01608) {
        if (features[6] < 0.000071) {
            if (features[2] < 27.71) {
                var47 = 0.010087985;
            } else {
                var47 = 0.03911847;
            }
        } else {
            if (features[5] < 0.007631) {
                var47 = -0.020490518;
            } else {
                var47 = 0.018936811;
            }
        }
    } else {
        if (features[5] < 0.011074) {
            if (features[5] < 0.005179) {
                var47 = -0.0020463106;
            } else {
                var47 = -0.041865144;
            }
        } else {
            var47 = 0.026791647;
        }
    }
    double var48;
    if (features[5] < 0.008285) {
        if (features[2] < 23.18) {
            if (features[0] < 97.7665) {
                var48 = 0.007076738;
            } else {
                var48 = -0.027454967;
            }
        } else {
            if (features[2] < 37.19) {
                var48 = 0.044095367;
            } else {
                var48 = -0.010956665;
            }
        }
    } else {
        if (features[2] < 25.94) {
            var48 = 0.012360689;
        } else {
            var48 = -0.03271133;
        }
    }
    double var49;
    if (features[2] < 38.59) {
        if (features[4] < -0.999759) {
            if (features[2] < 26.98) {
                var49 = -0.026060656;
            } else {
                var49 = 0.014862527;
            }
        } else {
            if (features[5] < 0.006304) {
                var49 = -0.014469757;
            } else {
                var49 = 0.050682258;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var49 = -0.04530285;
        } else {
            var49 = 0.009606612;
        }
    }
    double var50;
    if (features[4] < -0.99973) {
        if (features[0] < 90.924515) {
            var50 = -0.046180986;
        } else {
            if (features[3] < -0.0737) {
                var50 = -0.023829963;
            } else {
                var50 = 0.014348991;
            }
        }
    } else {
        if (features[6] < 0.000071) {
            var50 = 0.04458111;
        } else {
            if (features[3] < -1.8971) {
                var50 = 0.02653918;
            } else {
                var50 = -0.008627996;
            }
        }
    }
    double var51;
    if (features[4] < -0.999729) {
        if (features[2] < 38.59) {
            if (features[2] < 30.01) {
                var51 = -0.015210054;
            } else {
                var51 = 0.04333792;
            }
        } else {
            var51 = -0.03417262;
        }
    } else {
        if (features[2] < 29.59) {
            var51 = 0.046983726;
        } else {
            var51 = 0.0015592119;
        }
    }
    double var52;
    if (features[6] < 0.000027) {
        if (features[5] < 0.006921) {
            var52 = 0.035612278;
        } else {
            var52 = 0.0044878;
        }
    } else {
        if (features[4] < -0.999756) {
            if (features[5] < 0.012746) {
                var52 = -0.03920099;
            } else {
                var52 = 0.0015853358;
            }
        } else {
            if (features[5] < 0.006447) {
                var52 = -0.017729577;
            } else {
                var52 = 0.028718174;
            }
        }
    }
    double var53;
    if (features[1] < 0.000008) {
        var53 = -0.038385436;
    } else {
        if (features[6] < 0.00008) {
            if (features[4] < -0.999839) {
                var53 = 0.0034306855;
            } else {
                var53 = 0.039625984;
            }
        } else {
            if (features[1] < 0.000035) {
                var53 = 0.004533814;
            } else {
                var53 = -0.03743566;
            }
        }
    }
    double var54;
    if (features[6] < 0.000027) {
        if (features[2] < 25.29) {
            var54 = 0.0019051603;
        } else {
            var54 = 0.03467638;
        }
    } else {
        if (features[4] < -0.999727) {
            if (features[0] < 90.924515) {
                var54 = -0.044078607;
            } else {
                var54 = -0.010734407;
            }
        } else {
            if (features[2] < 32.51) {
                var54 = 0.030911913;
            } else {
                var54 = -0.011319789;
            }
        }
    }
    double var55;
    if (features[6] < 0.000027) {
        if (features[0] < 198.30162) {
            var55 = 0.0048796223;
        } else {
            var55 = 0.036881626;
        }
    } else {
        if (features[2] < 37.19) {
            if (features[4] < -0.999753) {
                var55 = -0.014127252;
            } else {
                var55 = 0.023518087;
            }
        } else {
            var55 = -0.03118386;
        }
    }
    double var56;
    if (features[1] < 0.000018) {
        if (features[5] < 0.005129) {
            var56 = 0.03743176;
        } else {
            if (features[3] < 0.0038) {
                var56 = 0.008202485;
            } else {
                var56 = -0.029825702;
            }
        }
    } else {
        if (features[0] < 134.79712) {
            if (features[1] < 0.000026) {
                var56 = 0.00430428;
            } else {
                var56 = -0.038996827;
            }
        } else {
            if (features[1] < 0.00003) {
                var56 = -0.026208986;
            } else {
                var56 = 0.02859051;
            }
        }
    }
    double var57;
    if (features[2] < 38.59) {
        if (features[3] < -0.4071) {
            if (features[3] < -2.2161) {
                var57 = 0.020777984;
            } else {
                var57 = -0.039493483;
            }
        } else {
            if (features[0] < 59.650723) {
                var57 = -0.0193059;
            } else {
                var57 = 0.033990927;
            }
        }
    } else {
        if (features[6] < 0.000041) {
            var57 = -0.0007633755;
        } else {
            var57 = -0.04227072;
        }
    }
    double var58;
    if (features[4] < -0.99973) {
        if (features[6] < 0.000027) {
            if (features[0] < 225.96051) {
                var58 = -0.0053565307;
            } else {
                var58 = 0.01897312;
            }
        } else {
            if (features[3] < -2.9023) {
                var58 = 0.010980142;
            } else {
                var58 = -0.0322068;
            }
        }
    } else {
        if (features[2] < 29.59) {
            var58 = 0.0393128;
        } else {
            var58 = -0.008447503;
        }
    }
    double var59;
    if (features[6] < 0.00008) {
        if (features[1] < 0.00001) {
            if (features[5] < 0.004458) {
                var59 = 0.008999703;
            } else {
                var59 = -0.04221154;
            }
        } else {
            if (features[1] < 0.000018) {
                var59 = 0.047409784;
            } else {
                var59 = 0.006588099;
            }
        }
    } else {
        if (features[3] < -2.499) {
            var59 = 0.008618515;
        } else {
            if (features[1] < 0.000026) {
                var59 = -0.002415697;
            } else {
                var59 = -0.045131084;
            }
        }
    }
    double var60;
    if (features[4] < -0.999753) {
        if (features[3] < -3.2219) {
            var60 = 0.026387874;
        } else {
            if (features[0] < 258.65457) {
                var60 = -0.042282972;
            } else {
                var60 = -0.0049145403;
            }
        }
    } else {
        if (features[3] < 1.2772) {
            var60 = 0.03535858;
        } else {
            var60 = -0.010487728;
        }
    }
    double var61;
    if (features[6] < 0.000027) {
        if (features[1] < 0.00001) {
            var61 = 0.0039541037;
        } else {
            var61 = 0.030249078;
        }
    } else {
        if (features[2] < 37.19) {
            if (features[6] < 0.000039) {
                var61 = -0.027097588;
            } else {
                var61 = 0.0058379886;
            }
        } else {
            var61 = -0.031632226;
        }
    }
    double var62;
    if (features[1] < 0.000008) {
        var62 = -0.034895357;
    } else {
        if (features[2] < 38.59) {
            if (features[3] < -0.4071) {
                var62 = -0.012139685;
            } else {
                var62 = 0.031826537;
            }
        } else {
            if (features[2] < 46.68) {
                var62 = -0.038041357;
            } else {
                var62 = 0.0071352036;
            }
        }
    }
    double var63;
    if (features[6] < 0.000027) {
        if (features[1] < 0.00001) {
            var63 = 0.010034301;
        } else {
            var63 = 0.035621464;
        }
    } else {
        if (features[4] < -0.999727) {
            if (features[0] < 108.21798) {
                var63 = -0.037248027;
            } else {
                var63 = -0.0022524998;
            }
        } else {
            if (features[6] < 0.000114) {
                var63 = 0.03425802;
            } else {
                var63 = -0.0104114935;
            }
        }
    }
    double var64;
    if (features[3] < -3.2219) {
        var64 = 0.03841619;
    } else {
        if (features[3] < 2.4052) {
            if (features[4] < -0.999729) {
                var64 = -0.038418964;
            } else {
                var64 = 0.013899843;
            }
        } else {
            if (features[2] < 37.19) {
                var64 = 0.031361118;
            } else {
                var64 = -0.018550975;
            }
        }
    }
    double var65;
    if (features[6] < 0.00008) {
        if (features[0] < 152.01608) {
            var65 = 0.043531418;
        } else {
            if (features[6] < 0.000027) {
                var65 = 0.017745456;
            } else {
                var65 = -0.018161928;
            }
        }
    } else {
        if (features[3] < -2.2161) {
            var65 = 0.02115552;
        } else {
            if (features[3] < 1.3129) {
                var65 = -0.042436626;
            } else {
                var65 = -0.0062912824;
            }
        }
    }
    double var66;
    if (features[4] < -0.999753) {
        if (features[3] < -3.2219) {
            var66 = 0.024622029;
        } else {
            if (features[3] < -0.0737) {
                var66 = -0.039002623;
            } else {
                var66 = 0.0010987598;
            }
        }
    } else {
        if (features[1] < 0.000026) {
            var66 = 0.04484592;
        } else {
            var66 = 0.004909384;
        }
    }
    double var67;
    if (features[2] < 37.19) {
        if (features[0] < 65.95301) {
            if (features[4] < -0.999723) {
                var67 = -0.036786884;
            } else {
                var67 = 0.011715279;
            }
        } else {
            if (features[1] < 0.000008) {
                var67 = -0.0178207;
            } else {
                var67 = 0.03723421;
            }
        }
    } else {
        if (features[2] < 47.01) {
            var67 = -0.040389474;
        } else {
            var67 = 0.0069645545;
        }
    }
    double var68;
    if (features[1] < 0.000008) {
        var68 = -0.032393124;
    } else {
        if (features[1] < 0.000026) {
            if (features[0] < 290.8009) {
                var68 = 0.022068433;
            } else {
                var68 = -0.018860871;
            }
        } else {
            if (features[3] < -2.499) {
                var68 = 0.01906949;
            } else {
                var68 = -0.03025258;
            }
        }
    }
    double var69;
    if (features[0] < 290.8009) {
        if (features[0] < 72.62282) {
            if (features[6] < 0.000071) {
                var69 = 0.010728884;
            } else {
                var69 = -0.033728477;
            }
        } else {
            if (features[3] < -0.5068) {
                var69 = -0.0059638117;
            } else {
                var69 = 0.038616832;
            }
        }
    } else {
        var69 = -0.026067575;
    }
    double var70;
    if (features[2] < 38.59) {
        if (features[3] < -2.8558) {
            var70 = 0.041267764;
        } else {
            if (features[3] < -0.4071) {
                var70 = -0.019029103;
            } else {
                var70 = 0.023691935;
            }
        }
    } else {
        if (features[2] < 46.68) {
            var70 = -0.034062013;
        } else {
            var70 = -0.00022177506;
        }
    }
    double var71;
    if (features[2] < 38.59) {
        if (features[3] < -0.4071) {
            if (features[2] < 25.24) {
                var71 = -0.028138492;
            } else {
                var71 = 0.016933406;
            }
        } else {
            if (features[0] < 65.95301) {
                var71 = -0.014241211;
            } else {
                var71 = 0.037455913;
            }
        }
    } else {
        var71 = -0.028631378;
    }
    double var72;
    if (features[4] < -0.999729) {
        if (features[1] < 0.000018) {
            if (features[1] < 0.000008) {
                var72 = -0.031182615;
            } else {
                var72 = 0.032984514;
            }
        } else {
            if (features[1] < 0.000033) {
                var72 = -0.037767388;
            } else {
                var72 = -0.00024384155;
            }
        }
    } else {
        if (features[6] < 0.000115) {
            var72 = 0.04536198;
        } else {
            var72 = 0.0048820972;
        }
    }
    double var73;
    if (features[6] < 0.000015) {
        var73 = 0.03647654;
    } else {
        if (features[3] < -0.2616) {
            if (features[4] < -0.999753) {
                var73 = -0.03523175;
            } else {
                var73 = 0.014985591;
            }
        } else {
            if (features[3] < 3.5898) {
                var73 = 0.020702573;
            } else {
                var73 = -0.01615778;
            }
        }
    }
    double var74;
    if (features[5] < 0.00814) {
        if (features[2] < 30.01) {
            if (features[5] < 0.004837) {
                var74 = -0.027813157;
            } else {
                var74 = 0.0181463;
            }
        } else {
            if (features[1] < 0.000024) {
                var74 = 0.043796908;
            } else {
                var74 = -0.0028785206;
            }
        }
    } else {
        if (features[5] < 0.011074) {
            var74 = -0.04333171;
        } else {
            if (features[4] < -0.999778) {
                var74 = 0.021661751;
            } else {
                var74 = -0.02137697;
            }
        }
    }
    double var75;
    if (features[6] < 0.000027) {
        if (features[1] < 0.00001) {
            var75 = -0.00027641907;
        } else {
            var75 = 0.035768315;
        }
    } else {
        if (features[4] < -0.999727) {
            if (features[0] < 108.21798) {
                var75 = -0.034232892;
            } else {
                var75 = -0.008460785;
            }
        } else {
            if (features[1] < 0.000025) {
                var75 = 0.023887312;
            } else {
                var75 = -0.007385142;
            }
        }
    }
    double var76;
    if (features[2] < 38.59) {
        if (features[3] < -0.5068) {
            if (features[2] < 28.57) {
                var76 = -0.03662851;
            } else {
                var76 = 0.01372832;
            }
        } else {
            if (features[0] < 65.95301) {
                var76 = -0.024972307;
            } else {
                var76 = 0.03755813;
            }
        }
    } else {
        var76 = -0.029926628;
    }
    double var77;
    if (features[5] < 0.007794) {
        if (features[6] < 0.00004) {
            if (features[2] < 30.01) {
                var77 = 0.005309479;
            } else {
                var77 = 0.042030644;
            }
        } else {
            if (features[5] < 0.006447) {
                var77 = -0.022510258;
            } else {
                var77 = 0.024193278;
            }
        }
    } else {
        if (features[2] < 27.03) {
            var77 = 0.0047367685;
        } else {
            var77 = -0.037584413;
        }
    }
    double var78;
    if (features[4] < -0.999753) {
        if (features[3] < 2.4052) {
            if (features[3] < -3.0325) {
                var78 = 0.015369909;
            } else {
                var78 = -0.032738693;
            }
        } else {
            var78 = 0.022907434;
        }
    } else {
        if (features[2] < 29.59) {
            var78 = 0.046703856;
        } else {
            if (features[3] < -0.2616) {
                var78 = 0.012921566;
            } else {
                var78 = -0.014025174;
            }
        }
    }
    double var79;
    if (features[4] < -0.999753) {
        if (features[2] < 31.06) {
            if (features[3] < -0.4071) {
                var79 = -0.0208647;
            } else {
                var79 = 0.02134434;
            }
        } else {
            var79 = -0.030073097;
        }
    } else {
        if (features[3] < 1.2772) {
            var79 = 0.036818802;
        } else {
            var79 = -0.011011959;
        }
    }
    double var80;
    if (features[6] < 0.000027) {
        var80 = 0.030865747;
    } else {
        if (features[1] < 0.000033) {
            if (features[1] < 0.000025) {
                var80 = -0.0046944604;
            } else {
                var80 = -0.03778095;
            }
        } else {
            if (features[0] < 108.21798) {
                var80 = -0.0084080305;
            } else {
                var80 = 0.024632636;
            }
        }
    }
    double var81;
    if (features[4] < -0.999753) {
        if (features[3] < -0.0737) {
            if (features[2] < 26.98) {
                var81 = -0.03884587;
            } else {
                var81 = -0.0094064735;
            }
        } else {
            if (features[2] < 27.82) {
                var81 = 0.031941753;
            } else {
                var81 = -0.01766704;
            }
        }
    } else {
        if (features[5] < 0.006447) {
            if (features[3] < 1.2772) {
                var81 = 0.024333997;
            } else {
                var81 = -0.01916715;
            }
        } else {
            var81 = 0.039103355;
        }
    }
    double var82;
    if (features[5] < 0.00571) {
        if (features[5] < 0.003559) {
            var82 = -0.012117944;
        } else {
            if (features[3] < 2.8958) {
                var82 = 0.04213819;
            } else {
                var82 = 0.0072603147;
            }
        }
    } else {
        if (features[3] < 2.9169) {
            if (features[5] < 0.011074) {
                var82 = -0.033235006;
            } else {
                var82 = 0.011929425;
            }
        } else {
            var82 = 0.011843319;
        }
    }
    double var83;
    if (features[0] < 72.62282) {
        if (features[3] < -0.8758) {
            var83 = 0.0036426687;
        } else {
            var83 = -0.026048202;
        }
    } else {
        if (features[2] < 38.59) {
            if (features[3] < -0.5068) {
                var83 = -0.0032305678;
            } else {
                var83 = 0.04594169;
            }
        } else {
            if (features[2] < 46.68) {
                var83 = -0.033087503;
            } else {
                var83 = 0.009044661;
            }
        }
    }
    double var84;
    if (features[6] < 0.00008) {
        if (features[1] < 0.000008) {
            var84 = -0.017116217;
        } else {
            if (features[2] < 38.59) {
                var84 = 0.033047542;
            } else {
                var84 = 0.00055383425;
            }
        }
    } else {
        if (features[3] < -2.2161) {
            var84 = 0.013585723;
        } else {
            if (features[3] < 2.3801) {
                var84 = -0.042392775;
            } else {
                var84 = -0.005925118;
            }
        }
    }
    double var85;
    if (features[5] < 0.00571) {
        if (features[2] < 28.57) {
            var85 = -0.009313482;
        } else {
            if (features[5] < 0.004529) {
                var85 = 0.044584382;
            } else {
                var85 = -0.00013714762;
            }
        }
    } else {
        if (features[4] < -0.999743) {
            if (features[5] < 0.010742) {
                var85 = -0.04208648;
            } else {
                var85 = -0.0015627692;
            }
        } else {
            if (features[5] < 0.007633) {
                var85 = -0.006011656;
            } else {
                var85 = 0.021243555;
            }
        }
    }
    double var86;
    if (features[4] < -0.999753) {
        if (features[1] < 0.000014) {
            if (features[1] < 0.00001) {
                var86 = -0.020120418;
            } else {
                var86 = 0.032957874;
            }
        } else {
            if (features[3] < -2.955) {
                var86 = 0.0010739816;
            } else {
                var86 = -0.03423268;
            }
        }
    } else {
        if (features[2] < 29.59) {
            var86 = 0.039003145;
        } else {
            if (features[4] < -0.999724) {
                var86 = 0.021093741;
            } else {
                var86 = -0.022169834;
            }
        }
    }
    double var87;
    if (features[1] < 0.00001) {
        var87 = -0.024609;
    } else {
        if (features[1] < 0.000026) {
            if (features[2] < 23.07) {
                var87 = 0.00012043617;
            } else {
                var87 = 0.039039455;
            }
        } else {
            if (features[1] < 0.00003) {
                var87 = -0.035928164;
            } else {
                var87 = 0.009881149;
            }
        }
    }
    double var88;
    if (features[4] < -0.99973) {
        if (features[6] < 0.000062) {
            if (features[4] < -0.999844) {
                var88 = -0.022853656;
            } else {
                var88 = 0.014602335;
            }
        } else {
            var88 = -0.03968582;
        }
    } else {
        if (features[1] < 0.000025) {
            var88 = 0.035455566;
        } else {
            var88 = -0.0059566847;
        }
    }
    double var89;
    if (features[4] < -0.999845) {
        var89 = -0.017820619;
    } else {
        if (features[6] < 0.000062) {
            if (features[3] < -0.0737) {
                var89 = 0.0032485747;
            } else {
                var89 = 0.038314655;
            }
        } else {
            if (features[3] < 1.3889) {
                var89 = 0.007491375;
            } else {
                var89 = -0.02093251;
            }
        }
    }
    double var90;
    if (features[6] < 0.000114) {
        if (features[0] < 152.01608) {
            if (features[0] < 100.3848) {
                var90 = 0.006166866;
            } else {
                var90 = 0.038962554;
            }
        } else {
            if (features[0] < 258.65457) {
                var90 = -0.019587116;
            } else {
                var90 = 0.022163227;
            }
        }
    } else {
        if (features[3] < -1.5997) {
            var90 = -0.0056309286;
        } else {
            var90 = -0.027769983;
        }
    }
    double var91;
    if (features[6] < 0.00008) {
        if (features[4] < -0.99985) {
            var91 = -0.020631546;
        } else {
            if (features[2] < 27.07) {
                var91 = 0.003481311;
            } else {
                var91 = 0.03424449;
            }
        }
    } else {
        if (features[6] < 0.000103) {
            var91 = -0.033146452;
        } else {
            if (features[3] < -2.499) {
                var91 = 0.018672682;
            } else {
                var91 = -0.0086093955;
            }
        }
    }
    double var92;
    if (features[3] < -0.0737) {
        if (features[4] < -0.999753) {
            if (features[3] < -2.9023) {
                var92 = 0.0049324404;
            } else {
                var92 = -0.042370748;
            }
        } else {
            var92 = 0.017547973;
        }
    } else {
        if (features[2] < 37.19) {
            if (features[4] < -0.999742) {
                var92 = 0.042213395;
            } else {
                var92 = 0.0042815553;
            }
        } else {
            var92 = -0.017439937;
        }
    }
    double var93;
    if (features[2] < 38.59) {
        if (features[2] < 23.18) {
            if (features[0] < 97.7665) {
                var93 = -0.0028922462;
            } else {
                var93 = -0.014249346;
            }
        } else {
            if (features[1] < 0.000035) {
                var93 = 0.031625476;
            } else {
                var93 = -0.0051975637;
            }
        }
    } else {
        var93 = -0.019481206;
    }
    double var94;
    if (features[0] < 72.62282) {
        var94 = -0.027867535;
    } else {
        if (features[4] < -0.999753) {
            if (features[2] < 27.82) {
                var94 = 0.008357799;
            } else {
                var94 = -0.021408528;
            }
        } else {
            var94 = 0.027951032;
        }
    }
    double var95;
    if (features[1] < 0.00001) {
        var95 = -0.028576553;
    } else {
        if (features[3] < -2.2161) {
            var95 = 0.029337574;
        } else {
            if (features[3] < 0.9524) {
                var95 = -0.015802275;
            } else {
                var95 = 0.01750028;
            }
        }
    }
    double var96;
    if (features[2] < 38.59) {
        if (features[0] < 65.95301) {
            if (features[2] < 26.36) {
                var96 = 0.0011482041;
            } else {
                var96 = -0.02398211;
            }
        } else {
            if (features[6] < 0.000074) {
                var96 = -0.00008231407;
            } else {
                var96 = 0.037836976;
            }
        }
    } else {
        if (features[5] < 0.006447) {
            var96 = -0.0023325484;
        } else {
            var96 = -0.032220248;
        }
    }
    double var97;
    if (features[4] < -0.999753) {
        if (features[5] < 0.004529) {
            var97 = 0.010269203;
        } else {
            if (features[2] < 30.56) {
                var97 = -0.00008712;
            } else {
                var97 = -0.040989418;
            }
        }
    } else {
        if (features[3] < 1.2772) {
            var97 = 0.034043588;
        } else {
            var97 = -0.0013781546;
        }
    }
    double var98;
    if (features[5] < 0.004529) {
        if (features[5] < 0.003935) {
            var98 = -0.006092875;
        } else {
            var98 = 0.03752722;
        }
    } else {
        if (features[4] < -0.999753) {
            if (features[5] < 0.010742) {
                var98 = -0.029504208;
            } else {
                var98 = 0.0020590571;
            }
        } else {
            if (features[0] < 54.69221) {
                var98 = -0.005264833;
            } else {
                var98 = 0.027685313;
            }
        }
    }
    double var99;
    if (features[2] < 38.59) {
        if (features[1] < 0.00001) {
            var99 = -0.0116810305;
        } else {
            if (features[6] < 0.000115) {
                var99 = 0.028185785;
            } else {
                var99 = -0.0087306835;
            }
        }
    } else {
        var99 = -0.03821359;
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
