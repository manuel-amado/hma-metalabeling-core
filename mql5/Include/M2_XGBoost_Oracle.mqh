//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| Generated automatically by m2cgen for MetaTrader 5            |
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
    if (features[2] < 35.66) {
        if (features[3] < -4.2129) {
            var0 = 0.06363636;
        } else {
            if (features[5] < 0.015827) {
                var0 = 0.015032681;
            } else {
                var0 = -0.019402986;
            }
        }
    } else {
        if (features[1] < 0.384485) {
            if (features[1] < 0.200108) {
                var0 = -0.0024390244;
            } else {
                var0 = -0.046031747;
            }
        } else {
            var0 = 0.05;
        }
    }
    double var1;
    if (features[0] < 0.011652) {
        if (features[4] < -0.004969) {
            if (features[0] < 0.008986) {
                var1 = 0.037942674;
            } else {
                var1 = -0.050359655;
            }
        } else {
            if (features[5] < 0.005737) {
                var1 = -0.020364191;
            } else {
                var1 = 0.05866;
            }
        }
    } else {
        if (features[1] < 0.307668) {
            if (features[2] < 35.28) {
                var1 = 0.00087156316;
            } else {
                var1 = -0.03868121;
            }
        } else {
            if (features[5] < 0.049507) {
                var1 = 0.038051482;
            } else {
                var1 = -0.05526304;
            }
        }
    }
    double var2;
    if (features[0] < 0.028538) {
        if (features[4] < -0.00325) {
            if (features[3] < 1.2317) {
                var2 = -0.044595182;
            } else {
                var2 = 0.012591732;
            }
        } else {
            if (features[0] < 0.008352) {
                var2 = 0.057320274;
            } else {
                var2 = 0.0052955383;
            }
        }
    } else {
        if (features[4] < 0.044417) {
            if (features[3] < -3.6468) {
                var2 = -0.007168071;
            } else {
                var2 = -0.063451104;
            }
        } else {
            var2 = 0.008051696;
        }
    }
    double var3;
    if (features[3] < -4.2129) {
        if (features[2] < 39.36) {
            var3 = 0.06907052;
        } else {
            if (features[2] < 44.6) {
                var3 = -0.03167872;
            } else {
                var3 = -0.009395774;
            }
        }
    } else {
        if (features[4] < -0.001097) {
            if (features[1] < 0.295803) {
                var3 = -0.040371176;
            } else {
                var3 = 0.029362574;
            }
        } else {
            if (features[2] < 22.86) {
                var3 = 0.024696011;
            } else {
                var3 = -0.006009003;
            }
        }
    }
    double var4;
    if (features[3] < -2.4022) {
        if (features[5] < 0.008746) {
            if (features[2] < 36.27) {
                var4 = -0.00021605993;
            } else {
                var4 = -0.058235716;
            }
        } else {
            if (features[0] < 0.028447) {
                var4 = 0.031497654;
            } else {
                var4 = -0.0031860366;
            }
        }
    } else {
        if (features[0] < 0.008352) {
            if (features[5] < 0.005737) {
                var4 = -0.010503506;
            } else {
                var4 = 0.060005546;
            }
        } else {
            if (features[3] < -0.1477) {
                var4 = -0.037908744;
            } else {
                var4 = -0.00175675;
            }
        }
    }
    double var5;
    if (features[4] < 0.000219) {
        if (features[3] < 1.2317) {
            if (features[3] < -4.2129) {
                var5 = 0.05262929;
            } else {
                var5 = -0.050639965;
            }
        } else {
            if (features[2] < 34.76) {
                var5 = 0.02976254;
            } else {
                var5 = -0.031068448;
            }
        }
    } else {
        if (features[0] < 0.028279) {
            if (features[6] < 0.860503) {
                var5 = -0.0096262125;
            } else {
                var5 = 0.02912873;
            }
        } else {
            if (features[6] < 0.532431) {
                var5 = 0.05874539;
            } else {
                var5 = -0.04298746;
            }
        }
    }
    double var6;
    if (features[2] < 49.15) {
        if (features[5] < 0.008942) {
            if (features[6] < 0.58362) {
                var6 = 0.020819401;
            } else {
                var6 = -0.036065754;
            }
        } else {
            if (features[0] < 0.011789) {
                var6 = 0.049057517;
            } else {
                var6 = 0.0024545786;
            }
        }
    } else {
        if (features[5] < 0.021535) {
            if (features[0] < 0.02147) {
                var6 = -0.02057548;
            } else {
                var6 = -0.06564185;
            }
        } else {
            var6 = 0.0029606856;
        }
    }
    double var7;
    if (features[3] < -4.2838) {
        if (features[6] < 1.122529) {
            var7 = 0.07050167;
        } else {
            if (features[6] < 1.67145) {
                var7 = -0.0195922;
            } else {
                var7 = 0.037353363;
            }
        }
    } else {
        if (features[6] < 0.952252) {
            if (features[5] < 0.007216) {
                var7 = -0.0022847333;
            } else {
                var7 = -0.035605133;
            }
        } else {
            if (features[0] < 0.02363) {
                var7 = 0.017444305;
            } else {
                var7 = -0.020326613;
            }
        }
    }
    double var8;
    if (features[3] < -2.3163) {
        if (features[3] < -2.6481) {
            if (features[2] < 36.27) {
                var8 = 0.025951212;
            } else {
                var8 = -0.006787181;
            }
        } else {
            if (features[3] < -2.4638) {
                var8 = 0.069535784;
            } else {
                var8 = 0.023863481;
            }
        }
    } else {
        if (features[0] < 0.008352) {
            if (features[4] < -0.004352) {
                var8 = 0.0076381653;
            } else {
                var8 = 0.06654429;
            }
        } else {
            if (features[5] < 0.015827) {
                var8 = -0.002939373;
            } else {
                var8 = -0.043166194;
            }
        }
    }
    double var9;
    if (features[4] < 0.00047) {
        if (features[6] < 1.925583) {
            if (features[3] < -4.2129) {
                var9 = 0.03340968;
            } else {
                var9 = -0.034159105;
            }
        } else {
            var9 = 0.04062586;
        }
    } else {
        if (features[5] < 0.015827) {
            if (features[6] < 0.952252) {
                var9 = -0.007912885;
            } else {
                var9 = 0.048061114;
            }
        } else {
            if (features[3] < -2.6446) {
                var9 = 0.017056582;
            } else {
                var9 = -0.05017906;
            }
        }
    }
    double var10;
    if (features[4] < -0.000798) {
        if (features[3] < 1.8437) {
            if (features[3] < -4.462) {
                var10 = 0.047931448;
            } else {
                var10 = -0.03462712;
            }
        } else {
            if (features[5] < 0.008942) {
                var10 = -0.013560939;
            } else {
                var10 = 0.047272332;
            }
        }
    } else {
        if (features[6] < 1.152675) {
            if (features[6] < 0.651915) {
                var10 = 0.027744701;
            } else {
                var10 = -0.01600709;
            }
        } else {
            if (features[5] < 0.017112) {
                var10 = 0.0396084;
            } else {
                var10 = 0.005615263;
            }
        }
    }
    double var11;
    if (features[0] < 0.028369) {
        if (features[1] < 0.297443) {
            if (features[3] < -2.4022) {
                var11 = 0.014261194;
            } else {
                var11 = -0.014032023;
            }
        } else {
            if (features[3] < 2.6263) {
                var11 = 0.036729258;
            } else {
                var11 = -0.0131915035;
            }
        }
    } else {
        if (features[5] < 0.030022) {
            if (features[1] < 0.340441) {
                var11 = -0.046355966;
            } else {
                var11 = 0.012439835;
            }
        } else {
            if (features[1] < 0.251001) {
                var11 = 0.053373028;
            } else {
                var11 = -0.016045725;
            }
        }
    }
    double var12;
    if (features[1] < 0.385067) {
        if (features[3] < -4.5754) {
            if (features[4] < 0.035993) {
                var12 = 0.05714211;
            } else {
                var12 = 0.003801727;
            }
        } else {
            if (features[4] < 0.003212) {
                var12 = -0.020486;
            } else {
                var12 = 0.0035769038;
            }
        }
    } else {
        if (features[3] < 1.9529) {
            if (features[2] < 48.54) {
                var12 = 0.066683136;
            } else {
                var12 = 0.019529691;
            }
        } else {
            var12 = -0.008047226;
        }
    }
    double var13;
    if (features[6] < 0.952252) {
        if (features[6] < 0.544385) {
            if (features[1] < 0.126393) {
                var13 = -0.027889082;
            } else {
                var13 = 0.029261773;
            }
        } else {
            if (features[2] < 23.73) {
                var13 = -0.008231087;
            } else {
                var13 = -0.05088231;
            }
        }
    } else {
        if (features[0] < 0.028447) {
            if (features[1] < 0.385067) {
                var13 = 0.013623585;
            } else {
                var13 = 0.06489384;
            }
        } else {
            if (features[2] < 52.02) {
                var13 = -0.044721067;
            } else {
                var13 = -0.005336258;
            }
        }
    }
    double var14;
    if (features[6] < 1.978757) {
        if (features[4] < -0.00069) {
            if (features[0] < 0.011401) {
                var14 = 0.017881013;
            } else {
                var14 = -0.040333424;
            }
        } else {
            if (features[4] < 0.007611) {
                var14 = 0.027411604;
            } else {
                var14 = -0.005071724;
            }
        }
    } else {
        if (features[0] < 0.026209) {
            if (features[1] < 0.264532) {
                var14 = 0.010241647;
            } else {
                var14 = 0.06193459;
            }
        } else {
            var14 = -0.012284041;
        }
    }
    double var15;
    if (features[3] < -4.2129) {
        if (features[5] < 0.016503) {
            var15 = 0.05528903;
        } else {
            if (features[2] < 33.76) {
                var15 = 0.035458848;
            } else {
                var15 = -0.03946582;
            }
        }
    } else {
        if (features[4] < -0.003173) {
            if (features[1] < 0.340441) {
                var15 = -0.03462657;
            } else {
                var15 = 0.052940883;
            }
        } else {
            if (features[4] < 0.008189) {
                var15 = 0.018074108;
            } else {
                var15 = -0.00995122;
            }
        }
    }
    double var16;
    if (features[6] < 1.492943) {
        if (features[0] < 0.011401) {
            if (features[2] < 22.01) {
                var16 = -0.00912253;
            } else {
                var16 = 0.053008445;
            }
        } else {
            if (features[3] < -2.4022) {
                var16 = 0.008536184;
            } else {
                var16 = -0.020163938;
            }
        }
    } else {
        if (features[0] < 0.02147) {
            if (features[2] < 35.66) {
                var16 = 0.054663956;
            } else {
                var16 = 0.018236583;
            }
        } else {
            if (features[3] < -0.599) {
                var16 = 0.025543852;
            } else {
                var16 = -0.042701293;
            }
        }
    }
    double var17;
    if (features[6] < 0.700587) {
        if (features[3] < -4.462) {
            var17 = 0.04421058;
        } else {
            if (features[2] < 18.49) {
                var17 = 0.022257363;
            } else {
                var17 = -0.04132316;
            }
        }
    } else {
        if (features[0] < 0.028279) {
            if (features[6] < 1.978757) {
                var17 = 0.008509183;
            } else {
                var17 = 0.03978735;
            }
        } else {
            if (features[6] < 1.461778) {
                var17 = -0.04381998;
            } else {
                var17 = 0.00077897654;
            }
        }
    }
    double var18;
    if (features[0] < 0.008986) {
        if (features[1] < 0.215938) {
            if (features[6] < 0.859194) {
                var18 = -0.014562446;
            } else {
                var18 = 0.012433576;
            }
        } else {
            var18 = 0.06266386;
        }
    } else {
        if (features[4] < -0.001097) {
            if (features[1] < 0.340441) {
                var18 = -0.03417902;
            } else {
                var18 = 0.030310756;
            }
        } else {
            if (features[6] < 0.551433) {
                var18 = 0.03881612;
            } else {
                var18 = -0.0010391488;
            }
        }
    }
    double var19;
    if (features[4] < 0.034375) {
        if (features[4] < -0.000798) {
            if (features[4] < -0.015176) {
                var19 = 0.011679155;
            } else {
                var19 = -0.023619387;
            }
        } else {
            if (features[2] < 49.15) {
                var19 = 0.018770035;
            } else {
                var19 = -0.026058877;
            }
        }
    } else {
        if (features[5] < 0.031009) {
            if (features[5] < 0.014633) {
                var19 = 0.011299433;
            } else {
                var19 = -0.059230257;
            }
        } else {
            var19 = 0.028999744;
        }
    }
    double var20;
    if (features[4] < -0.00081) {
        if (features[6] < 0.859194) {
            if (features[0] < 0.025186) {
                var20 = -0.057342865;
            } else {
                var20 = -0.004001222;
            }
        } else {
            if (features[6] < 1.002327) {
                var20 = 0.02683343;
            } else {
                var20 = -0.02786222;
            }
        }
    } else {
        if (features[6] < 0.551433) {
            if (features[1] < 0.251001) {
                var20 = 0.059283346;
            } else {
                var20 = -0.00024138438;
            }
        } else {
            if (features[0] < 0.017942) {
                var20 = 0.010089624;
            } else {
                var20 = -0.018655516;
            }
        }
    }
    double var21;
    if (features[1] < 0.242188) {
        if (features[2] < 35.14) {
            if (features[3] < -4.2129) {
                var21 = 0.043105103;
            } else {
                var21 = -0.009180172;
            }
        } else {
            if (features[6] < 1.336687) {
                var21 = -0.047224168;
            } else {
                var21 = 0.0071406066;
            }
        }
    } else {
        if (features[5] < 0.015352) {
            if (features[3] < 1.4587) {
                var21 = 0.056641288;
            } else {
                var21 = -0.006926644;
            }
        } else {
            if (features[6] < 1.545563) {
                var21 = -0.030463746;
            } else {
                var21 = 0.027734712;
            }
        }
    }
    double var22;
    if (features[4] < 0.000219) {
        if (features[0] < 0.008986) {
            if (features[2] < 20.1) {
                var22 = -0.020803073;
            } else {
                var22 = 0.033477318;
            }
        } else {
            if (features[2] < 53.98) {
                var22 = -0.031463396;
            } else {
                var22 = 0.03954669;
            }
        }
    } else {
        if (features[0] < 0.014553) {
            if (features[5] < 0.009813) {
                var22 = -0.00289036;
            } else {
                var22 = 0.037761077;
            }
        } else {
            if (features[4] < 0.008189) {
                var22 = 0.026801346;
            } else {
                var22 = -0.010791122;
            }
        }
    }
    double var23;
    if (features[4] < -0.003173) {
        if (features[6] < 1.492443) {
            if (features[3] < -4.2129) {
                var23 = 0.027782505;
            } else {
                var23 = -0.036116883;
            }
        } else {
            var23 = 0.04272825;
        }
    } else {
        if (features[2] < 22.67) {
            if (features[3] < -0.599) {
                var23 = 0.0073036;
            } else {
                var23 = 0.06583061;
            }
        } else {
            if (features[3] < -2.9314) {
                var23 = 0.016257137;
            } else {
                var23 = -0.014441197;
            }
        }
    }
    double var24;
    if (features[1] < 0.232324) {
        if (features[1] < 0.177718) {
            if (features[1] < 0.118119) {
                var24 = -0.051684972;
            } else {
                var24 = 0.023743387;
            }
        } else {
            if (features[6] < 1.492943) {
                var24 = -0.03006648;
            } else {
                var24 = 0.025742574;
            }
        }
    } else {
        if (features[4] < 0.033802) {
            if (features[4] < 0.000846) {
                var24 = -0.008577908;
            } else {
                var24 = 0.040879097;
            }
        } else {
            if (features[4] < 0.038112) {
                var24 = -0.041927576;
            } else {
                var24 = 0.0028237938;
            }
        }
    }
    double var25;
    if (features[6] < 1.492943) {
        if (features[3] < -4.2838) {
            if (features[2] < 36.21) {
                var25 = 0.047961023;
            } else {
                var25 = -0.000008519534;
            }
        } else {
            if (features[0] < 0.011652) {
                var25 = 0.0033711118;
            } else {
                var25 = -0.022085268;
            }
        }
    } else {
        if (features[0] < 0.017942) {
            if (features[6] < 1.830422) {
                var25 = 0.06087148;
            } else {
                var25 = 0.008126406;
            }
        } else {
            if (features[2] < 56.72) {
                var25 = -0.015302509;
            } else {
                var25 = 0.030618707;
            }
        }
    }
    double var26;
    if (features[1] < 0.37751) {
        if (features[3] < -4.2129) {
            if (features[2] < 40.42) {
                var26 = 0.040365163;
            } else {
                var26 = -0.026631495;
            }
        } else {
            if (features[2] < 22.41) {
                var26 = 0.011975177;
            } else {
                var26 = -0.014107919;
            }
        }
    } else {
        if (features[0] < 0.031506) {
            if (features[3] < 0.1169) {
                var26 = 0.06397513;
            } else {
                var26 = 0.013567181;
            }
        } else {
            var26 = -0.014292768;
        }
    }
    double var27;
    if (features[1] < 0.385067) {
        if (features[0] < 0.008986) {
            if (features[1] < 0.215938) {
                var27 = -0.00042013638;
            } else {
                var27 = 0.057351;
            }
        } else {
            if (features[4] < 0.004088) {
                var27 = -0.026655233;
            } else {
                var27 = -0.0011774042;
            }
        }
    } else {
        if (features[0] < 0.031506) {
            var27 = 0.06336865;
        } else {
            var27 = -0.0070631313;
        }
    }
    double var28;
    if (features[2] < 35.66) {
        if (features[3] < -4.2397) {
            var28 = 0.045639057;
        } else {
            if (features[0] < 0.008986) {
                var28 = 0.03268547;
            } else {
                var28 = -0.0011071576;
            }
        }
    } else {
        if (features[6] < 0.894843) {
            if (features[2] < 44.96) {
                var28 = -0.06679432;
            } else {
                var28 = -0.02185064;
            }
        } else {
            if (features[6] < 1.125862) {
                var28 = 0.032717004;
            } else {
                var28 = -0.012852237;
            }
        }
    }
    double var29;
    if (features[6] < 1.978757) {
        if (features[6] < 1.667741) {
            if (features[6] < 1.492943) {
                var29 = -0.005291428;
            } else {
                var29 = 0.038356304;
            }
        } else {
            if (features[2] < 32.76) {
                var29 = -0.0009189349;
            } else {
                var29 = -0.05492824;
            }
        }
    } else {
        if (features[1] < 0.516566) {
            if (features[1] < 0.235049) {
                var29 = 0.0031208869;
            } else {
                var29 = 0.048041582;
            }
        } else {
            var29 = -0.026405487;
        }
    }
    double var30;
    if (features[3] < -4.5754) {
        if (features[2] < 34.96) {
            var30 = 0.055157956;
        } else {
            if (features[2] < 39.9) {
                var30 = -0.015616362;
            } else {
                var30 = 0.02787734;
            }
        }
    } else {
        if (features[1] < 0.308387) {
            if (features[5] < 0.02847) {
                var30 = -0.010258528;
            } else {
                var30 = 0.045852315;
            }
        } else {
            if (features[5] < 0.049507) {
                var30 = 0.027688533;
            } else {
                var30 = -0.0488051;
            }
        }
    }
    double var31;
    if (features[5] < 0.008942) {
        if (features[5] < 0.006092) {
            if (features[2] < 35.14) {
                var31 = 0.04189191;
            } else {
                var31 = -0.022124128;
            }
        } else {
            if (features[3] < -1.8133) {
                var31 = -0.0014433294;
            } else {
                var31 = -0.04130585;
            }
        }
    } else {
        if (features[0] < 0.014553) {
            if (features[3] < -1.7072) {
                var31 = 0.015187508;
            } else {
                var31 = 0.052121677;
            }
        } else {
            if (features[5] < 0.013228) {
                var31 = 0.029570729;
            } else {
                var31 = -0.01077179;
            }
        }
    }
    double var32;
    if (features[3] < -4.5214) {
        if (features[6] < 1.295657) {
            var32 = 0.04625579;
        } else {
            if (features[6] < 1.67145) {
                var32 = -0.025770376;
            } else {
                var32 = 0.041457918;
            }
        }
    } else {
        if (features[1] < 0.308387) {
            if (features[4] < -0.000798) {
                var32 = -0.024039138;
            } else {
                var32 = -0.0019803843;
            }
        } else {
            if (features[6] < 2.381062) {
                var32 = 0.027858077;
            } else {
                var32 = -0.036296245;
            }
        }
    }
    double var33;
    if (features[0] < 0.028369) {
        if (features[5] < 0.008879) {
            if (features[6] < 0.58362) {
                var33 = 0.030608285;
            } else {
                var33 = -0.029373014;
            }
        } else {
            if (features[0] < 0.011652) {
                var33 = 0.039134737;
            } else {
                var33 = 0.0023058013;
            }
        }
    } else {
        if (features[5] < 0.019165) {
            if (features[3] < 1.798) {
                var33 = -0.055068433;
            } else {
                var33 = 0.003376133;
            }
        } else {
            if (features[3] < -3.6468) {
                var33 = 0.039006595;
            } else {
                var33 = -0.02518338;
            }
        }
    }
    double var34;
    if (features[1] < 0.232324) {
        if (features[1] < 0.179792) {
            if (features[6] < 0.952252) {
                var34 = -0.008833796;
            } else {
                var34 = 0.040302332;
            }
        } else {
            if (features[5] < 0.009222) {
                var34 = -0.04338503;
            } else {
                var34 = -0.008292174;
            }
        }
    } else {
        if (features[5] < 0.015726) {
            if (features[3] < -2.3828) {
                var34 = 0.065708466;
            } else {
                var34 = 0.014743792;
            }
        } else {
            if (features[1] < 0.37751) {
                var34 = -0.01228598;
            } else {
                var34 = 0.03765778;
            }
        }
    }
    double var35;
    if (features[3] < -2.3163) {
        if (features[3] < -2.7231) {
            if (features[4] < 0.003968) {
                var35 = -0.025533542;
            } else {
                var35 = 0.011968336;
            }
        } else {
            if (features[4] < 0.024312) {
                var35 = 0.043321103;
            } else {
                var35 = 0.013984667;
            }
        }
    } else {
        if (features[5] < 0.018174) {
            if (features[3] < -2.058) {
                var35 = -0.048041016;
            } else {
                var35 = 0.007531069;
            }
        } else {
            if (features[6] < 1.568961) {
                var35 = -0.057989072;
            } else {
                var35 = 0.00020650975;
            }
        }
    }
    double var36;
    if (features[0] < 0.028369) {
        if (features[1] < 0.37751) {
            if (features[1] < 0.352164) {
                var36 = 0.0028022286;
            } else {
                var36 = -0.064451225;
            }
        } else {
            var36 = 0.041983243;
        }
    } else {
        if (features[2] < 62.95) {
            if (features[6] < 0.532431) {
                var36 = 0.018875718;
            } else {
                var36 = -0.039220527;
            }
        } else {
            var36 = 0.016399298;
        }
    }
    double var37;
    if (features[2] < 36.27) {
        if (features[1] < 0.21844) {
            if (features[1] < 0.207335) {
                var37 = 0.00079743343;
            } else {
                var37 = -0.05393262;
            }
        } else {
            if (features[4] < -0.002848) {
                var37 = -0.010459232;
            } else {
                var37 = 0.029685238;
            }
        }
    } else {
        if (features[2] < 38.14) {
            var37 = -0.05984332;
        } else {
            if (features[1] < 0.170333) {
                var37 = 0.029831473;
            } else {
                var37 = -0.020497669;
            }
        }
    }
    double var38;
    if (features[0] < 0.008352) {
        if (features[0] < 0.005664) {
            var38 = -0.030110782;
        } else {
            if (features[1] < 0.264638) {
                var38 = 0.053715605;
            } else {
                var38 = -0.007095755;
            }
        }
    } else {
        if (features[4] < 0.004088) {
            if (features[4] < -0.015176) {
                var38 = 0.009328078;
            } else {
                var38 = -0.027375672;
            }
        } else {
            if (features[4] < 0.008348) {
                var38 = 0.035312828;
            } else {
                var38 = -0.0059334873;
            }
        }
    }
    double var39;
    if (features[1] < 0.242188) {
        if (features[1] < 0.206642) {
            if (features[2] < 22.86) {
                var39 = 0.02410592;
            } else {
                var39 = -0.003215395;
            }
        } else {
            if (features[3] < 0.6508) {
                var39 = -0.04990385;
            } else {
                var39 = 0.0283732;
            }
        }
    } else {
        if (features[1] < 0.252969) {
            var39 = 0.057189353;
        } else {
            if (features[6] < 0.688392) {
                var39 = -0.025679592;
            } else {
                var39 = 0.01499013;
            }
        }
    }
    double var40;
    if (features[3] < -2.4022) {
        if (features[3] < -2.7231) {
            if (features[2] < 20.1) {
                var40 = -0.05980124;
            } else {
                var40 = 0.009607239;
            }
        } else {
            if (features[5] < 0.012362) {
                var40 = 0.007028784;
            } else {
                var40 = 0.06256871;
            }
        }
    } else {
        if (features[5] < 0.015744) {
            if (features[1] < 0.300731) {
                var40 = -0.0015735785;
            } else {
                var40 = 0.04161237;
            }
        } else {
            if (features[1] < 0.355184) {
                var40 = -0.048668507;
            } else {
                var40 = 0.00519224;
            }
        }
    }
    double var41;
    if (features[3] < 3.8529) {
        if (features[1] < 0.242188) {
            if (features[3] < 2.177) {
                var41 = -0.009194167;
            } else {
                var41 = 0.037371047;
            }
        } else {
            if (features[1] < 0.260367) {
                var41 = 0.047086537;
            } else {
                var41 = 0.0054069078;
            }
        }
    } else {
        var41 = -0.04154877;
    }
    double var42;
    if (features[0] < 0.008986) {
        if (features[0] < 0.005664) {
            var42 = -0.029245427;
        } else {
            if (features[1] < 0.264638) {
                var42 = 0.044016477;
            } else {
                var42 = -0.00375438;
            }
        }
    } else {
        if (features[3] < -2.9314) {
            if (features[0] < 0.044523) {
                var42 = 0.01791779;
            } else {
                var42 = -0.050624337;
            }
        } else {
            if (features[3] < -1.4951) {
                var42 = -0.025847053;
            } else {
                var42 = 0.0055188504;
            }
        }
    }
    double var43;
    if (features[1] < 0.37751) {
        if (features[4] < -0.003173) {
            if (features[5] < 0.011004) {
                var43 = -0.033798937;
            } else {
                var43 = 0.0012756346;
            }
        } else {
            if (features[1] < 0.34353) {
                var43 = 0.0026161622;
            } else {
                var43 = -0.04627857;
            }
        }
    } else {
        if (features[5] < 0.027152) {
            var43 = 0.04899096;
        } else {
            var43 = -0.008756375;
        }
    }
    double var44;
    if (features[2] < 35.66) {
        if (features[3] < -4.2397) {
            if (features[0] < 0.013989) {
                var44 = 0.012869283;
            } else {
                var44 = 0.045401443;
            }
        } else {
            if (features[5] < 0.017607) {
                var44 = 0.010146046;
            } else {
                var44 = -0.012382853;
            }
        }
    } else {
        if (features[1] < 0.308387) {
            if (features[1] < 0.216958) {
                var44 = -0.0028738042;
            } else {
                var44 = -0.04300772;
            }
        } else {
            if (features[5] < 0.023507) {
                var44 = 0.03533126;
            } else {
                var44 = -0.018869497;
            }
        }
    }
    double var45;
    if (features[0] < 0.007313) {
        var45 = 0.040252008;
    } else {
        if (features[3] < -2.4749) {
            if (features[3] < -2.6878) {
                var45 = -0.001326064;
            } else {
                var45 = 0.050805815;
            }
        } else {
            if (features[2] < 21.19) {
                var45 = 0.013037671;
            } else {
                var45 = -0.024855668;
            }
        }
    }
    double var46;
    if (features[3] < -2.3163) {
        if (features[3] < -3.6043) {
            if (features[3] < -4.2129) {
                var46 = 0.014014879;
            } else {
                var46 = -0.020480534;
            }
        } else {
            if (features[4] < 0.00047) {
                var46 = -0.0031826887;
            } else {
                var46 = 0.037102815;
            }
        }
    } else {
        if (features[0] < 0.011789) {
            if (features[4] < 0.017068) {
                var46 = 0.02795134;
            } else {
                var46 = -0.017014803;
            }
        } else {
            if (features[0] < 0.013146) {
                var46 = -0.060020324;
            } else {
                var46 = -0.0090305945;
            }
        }
    }
    double var47;
    if (features[6] < 0.58362) {
        if (features[1] < 0.118119) {
            var47 = -0.02057304;
        } else {
            if (features[2] < 35.66) {
                var47 = 0.0489567;
            } else {
                var47 = -0.017338052;
            }
        }
    } else {
        if (features[6] < 0.726599) {
            if (features[0] < 0.014296) {
                var47 = 0.0051525766;
            } else {
                var47 = -0.048896175;
            }
        } else {
            if (features[0] < 0.023665) {
                var47 = 0.011222739;
            } else {
                var47 = -0.015054392;
            }
        }
    }
    double var48;
    if (features[0] < 0.011652) {
        if (features[5] < 0.013002) {
            if (features[0] < 0.01031) {
                var48 = -0.02418691;
            } else {
                var48 = 0.028822387;
            }
        } else {
            if (features[0] < 0.011401) {
                var48 = 0.06288057;
            } else {
                var48 = 0.00891546;
            }
        }
    } else {
        if (features[2] < 21.91) {
            if (features[0] < 0.018155) {
                var48 = -0.00708502;
            } else {
                var48 = 0.039203707;
            }
        } else {
            if (features[0] < 0.01541) {
                var48 = -0.036324378;
            } else {
                var48 = -0.004635438;
            }
        }
    }
    double var49;
    if (features[6] < 2.075328) {
        if (features[6] < 1.831135) {
            if (features[6] < 0.952252) {
                var49 = -0.01121436;
            } else {
                var49 = 0.005713301;
            }
        } else {
            if (features[6] < 1.978757) {
                var49 = -0.058570392;
            } else {
                var49 = 0.0011522928;
            }
        }
    } else {
        if (features[6] < 2.776231) {
            if (features[1] < 0.323353) {
                var49 = 0.012853505;
            } else {
                var49 = 0.054209877;
            }
        } else {
            var49 = -0.017834445;
        }
    }
    double var50;
    if (features[6] < 2.075328) {
        if (features[6] < 1.831135) {
            if (features[6] < 1.492943) {
                var50 = -0.004187153;
            } else {
                var50 = 0.033070482;
            }
        } else {
            if (features[0] < 0.015924) {
                var50 = -0.068922475;
            } else {
                var50 = 0.002632079;
            }
        }
    } else {
        if (features[6] < 2.381062) {
            var50 = 0.06218482;
        } else {
            if (features[4] < 0.020997) {
                var50 = 0.02815991;
            } else {
                var50 = -0.05105883;
            }
        }
    }
    double var51;
    if (features[5] < 0.017607) {
        if (features[4] < 0.004088) {
            if (features[2] < 36.04) {
                var51 = 0.002477829;
            } else {
                var51 = -0.042255793;
            }
        } else {
            if (features[1] < 0.232324) {
                var51 = 0.008771286;
            } else {
                var51 = 0.044091802;
            }
        }
    } else {
        if (features[5] < 0.019977) {
            if (features[1] < 0.330172) {
                var51 = -0.059032213;
            } else {
                var51 = 0.0066610137;
            }
        } else {
            if (features[2] < 39.9) {
                var51 = -0.008360766;
            } else {
                var51 = 0.02428982;
            }
        }
    }
    double var52;
    if (features[3] < -4.5214) {
        if (features[6] < 1.341392) {
            var52 = 0.05351918;
        } else {
            var52 = 0.01966488;
        }
    } else {
        if (features[0] < 0.008986) {
            if (features[5] < 0.006346) {
                var52 = -0.014757228;
            } else {
                var52 = 0.03581995;
            }
        } else {
            if (features[4] < -0.000798) {
                var52 = -0.023124052;
            } else {
                var52 = 0.0014835896;
            }
        }
    }
    double var53;
    if (features[1] < 0.177718) {
        if (features[6] < 1.06181) {
            if (features[6] < 0.58362) {
                var53 = 0.037532326;
            } else {
                var53 = -0.023677537;
            }
        } else {
            if (features[2] < 22.86) {
                var53 = 0.0026220817;
            } else {
                var53 = 0.066542275;
            }
        }
    } else {
        if (features[1] < 0.23301) {
            if (features[4] < -0.017635) {
                var53 = 0.02670736;
            } else {
                var53 = -0.02094009;
            }
        } else {
            if (features[4] < 0.033802) {
                var53 = 0.016764706;
            } else {
                var53 = -0.030376112;
            }
        }
    }
    double var54;
    if (features[5] < 0.030022) {
        if (features[0] < 0.032479) {
            if (features[0] < 0.008352) {
                var54 = 0.026757319;
            } else {
                var54 = -0.0052597397;
            }
        } else {
            if (features[2] < 41.23) {
                var54 = -0.017013287;
            } else {
                var54 = -0.05419171;
            }
        }
    } else {
        if (features[4] < 0.010458) {
            var54 = -0.0051511168;
        } else {
            if (features[6] < 2.110347) {
                var54 = 0.045554828;
            } else {
                var54 = 0.004780268;
            }
        }
    }
    double var55;
    if (features[6] < 1.978757) {
        if (features[6] < 1.803363) {
            if (features[0] < 0.035537) {
                var55 = 0.010299157;
            } else {
                var55 = -0.027609913;
            }
        } else {
            if (features[0] < 0.015371) {
                var55 = -0.06505648;
            } else {
                var55 = -0.016764203;
            }
        }
    } else {
        if (features[3] < 1.9529) {
            var55 = 0.05066926;
        } else {
            var55 = -0.017275821;
        }
    }
    double var56;
    if (features[1] < 0.232324) {
        if (features[1] < 0.177718) {
            if (features[1] < 0.151153) {
                var56 = -0.014403673;
            } else {
                var56 = 0.021940835;
            }
        } else {
            if (features[2] < 16.81) {
                var56 = 0.017834177;
            } else {
                var56 = -0.021269713;
            }
        }
    } else {
        if (features[5] < 0.015726) {
            if (features[0] < 0.013592) {
                var56 = 0.00036240832;
            } else {
                var56 = 0.061308067;
            }
        } else {
            if (features[0] < 0.014518) {
                var56 = 0.039531287;
            } else {
                var56 = -0.01613961;
            }
        }
    }
    double var57;
    if (features[2] < 16.35) {
        var57 = 0.043532297;
    } else {
        if (features[3] < -2.3163) {
            if (features[3] < -3.5228) {
                var57 = -0.0049725226;
            } else {
                var57 = 0.026388345;
            }
        } else {
            if (features[3] < -1.658) {
                var57 = -0.039140385;
            } else {
                var57 = -0.0009580354;
            }
        }
    }
    double var58;
    if (features[0] < 0.008986) {
        if (features[2] < 19.78) {
            var58 = 0.00023162003;
        } else {
            var58 = 0.044609476;
        }
    } else {
        if (features[0] < 0.009623) {
            var58 = -0.04179282;
        } else {
            if (features[0] < 0.011652) {
                var58 = 0.025860785;
            } else {
                var58 = -0.00094298675;
            }
        }
    }
    double var59;
    if (features[5] < 0.008942) {
        if (features[6] < 0.532431) {
            if (features[5] < 0.004861) {
                var59 = 0.049643703;
            } else {
                var59 = -0.00087946263;
            }
        } else {
            if (features[1] < 0.209709) {
                var59 = -0.04319504;
            } else {
                var59 = 0.013081001;
            }
        }
    } else {
        if (features[0] < 0.011789) {
            if (features[3] < -1.947) {
                var59 = -0.0027476107;
            } else {
                var59 = 0.049755033;
            }
        } else {
            if (features[3] < -2.4749) {
                var59 = 0.012004065;
            } else {
                var59 = -0.01707643;
            }
        }
    }
    double var60;
    if (features[3] < -4.2397) {
        if (features[5] < 0.016969) {
            var60 = 0.059757423;
        } else {
            if (features[5] < 0.019437) {
                var60 = -0.051900722;
            } else {
                var60 = 0.017623914;
            }
        }
    } else {
        if (features[1] < 0.385067) {
            if (features[0] < 0.008986) {
                var60 = 0.018062823;
            } else {
                var60 = -0.009815148;
            }
        } else {
            if (features[5] < 0.023507) {
                var60 = 0.04678439;
            } else {
                var60 = 0.006065789;
            }
        }
    }
    double var61;
    if (features[6] < 0.58362) {
        if (features[4] < -0.004376) {
            if (features[6] < 0.239841) {
                var61 = -0.006177149;
            } else {
                var61 = -0.037316058;
            }
        } else {
            if (features[3] < 0.0732) {
                var61 = 0.059508193;
            } else {
                var61 = 0.008963957;
            }
        }
    } else {
        if (features[6] < 0.728566) {
            if (features[2] < 19.04) {
                var61 = 0.020134283;
            } else {
                var61 = -0.042514153;
            }
        } else {
            if (features[3] < -2.4749) {
                var61 = 0.009438521;
            } else {
                var61 = -0.009807557;
            }
        }
    }
    double var62;
    if (features[3] < -4.5754) {
        if (features[2] < 34.96) {
            var62 = 0.04901802;
        } else {
            var62 = 0.00408317;
        }
    } else {
        if (features[1] < 0.308387) {
            if (features[5] < 0.02847) {
                var62 = -0.0068351733;
            } else {
                var62 = 0.042709444;
            }
        } else {
            if (features[5] < 0.037162) {
                var62 = 0.024046246;
            } else {
                var62 = -0.026898323;
            }
        }
    }
    double var63;
    if (features[3] < -2.3163) {
        if (features[0] < 0.011046) {
            if (features[0] < 0.008874) {
                var63 = -0.002971106;
            } else {
                var63 = -0.044479556;
            }
        } else {
            if (features[3] < -3.6844) {
                var63 = -0.006356238;
            } else {
                var63 = 0.023643428;
            }
        }
    } else {
        if (features[3] < -0.599) {
            if (features[0] < 0.008986) {
                var63 = 0.031595435;
            } else {
                var63 = -0.042735368;
            }
        } else {
            if (features[6] < 0.426649) {
                var63 = -0.042796288;
            } else {
                var63 = 0.009665827;
            }
        }
    }
    double var64;
    if (features[1] < 0.385067) {
        if (features[2] < 36.27) {
            if (features[3] < -4.2129) {
                var64 = 0.04415844;
            } else {
                var64 = 0.0012074491;
            }
        } else {
            if (features[1] < 0.138293) {
                var64 = 0.047695182;
            } else {
                var64 = -0.021811131;
            }
        }
    } else {
        if (features[3] < 0.1169) {
            var64 = 0.0454984;
        } else {
            var64 = -0.0039139325;
        }
    }
    double var65;
    if (features[3] < -4.2129) {
        if (features[5] < 0.016503) {
            if (features[6] < 0.847104) {
                var65 = 0.011958216;
            } else {
                var65 = 0.053968687;
            }
        } else {
            if (features[3] < -4.7008) {
                var65 = -0.025749465;
            } else {
                var65 = 0.020630505;
            }
        }
    } else {
        if (features[0] < 0.008986) {
            if (features[3] < -2.4638) {
                var65 = -0.019946827;
            } else {
                var65 = 0.0360356;
            }
        } else {
            if (features[0] < 0.010386) {
                var65 = -0.057402153;
            } else {
                var65 = -0.0038551688;
            }
        }
    }
    double var66;
    if (features[1] < 0.384485) {
        if (features[2] < 35.28) {
            if (features[1] < 0.260367) {
                var66 = 0.010529887;
            } else {
                var66 = -0.018205812;
            }
        } else {
            if (features[1] < 0.138293) {
                var66 = 0.037455715;
            } else {
                var66 = -0.021845791;
            }
        }
    } else {
        if (features[4] < 0.031999) {
            var66 = 0.049778216;
        } else {
            var66 = 0.0031430942;
        }
    }
    double var67;
    if (features[2] < 49.15) {
        if (features[2] < 46.79) {
            if (features[1] < 0.23301) {
                var67 = -0.0053870226;
            } else {
                var67 = 0.012518786;
            }
        } else {
            var67 = 0.04442268;
        }
    } else {
        if (features[2] < 52.42) {
            if (features[1] < 0.284483) {
                var67 = -0.0029712569;
            } else {
                var67 = -0.055234767;
            }
        } else {
            if (features[1] < 0.281673) {
                var67 = -0.021391086;
            } else {
                var67 = 0.020404771;
            }
        }
    }
    double var68;
    if (features[1] < 0.120463) {
        var68 = -0.045480996;
    } else {
        if (features[1] < 0.179792) {
            if (features[6] < 0.952252) {
                var68 = -0.0039516483;
            } else {
                var68 = 0.04781672;
            }
        } else {
            if (features[1] < 0.297443) {
                var68 = -0.008171121;
            } else {
                var68 = 0.011988047;
            }
        }
    }
    double var69;
    if (features[6] < 0.859194) {
        if (features[0] < 0.024438) {
            if (features[2] < 25.08) {
                var69 = -0.00046179187;
            } else {
                var69 = -0.039065715;
            }
        } else {
            if (features[5] < 0.013192) {
                var69 = 0.052117407;
            } else {
                var69 = 0.005283296;
            }
        }
    } else {
        if (features[0] < 0.028279) {
            if (features[6] < 0.99552) {
                var69 = 0.037344422;
            } else {
                var69 = 0.008187134;
            }
        } else {
            if (features[6] < 1.461778) {
                var69 = -0.050855357;
            } else {
                var69 = 0.009814623;
            }
        }
    }
    double var70;
    if (features[3] < 0.9665) {
        if (features[3] < -2.3163) {
            if (features[3] < -3.5228) {
                var70 = -0.0067195334;
            } else {
                var70 = 0.021310506;
            }
        } else {
            if (features[1] < 0.177011) {
                var70 = 0.015897619;
            } else {
                var70 = -0.02507013;
            }
        }
    } else {
        if (features[4] < 0.022494) {
            if (features[3] < 3.8529) {
                var70 = 0.035798896;
            } else {
                var70 = -0.01364633;
            }
        } else {
            if (features[6] < 0.610426) {
                var70 = 0.006216387;
            } else {
                var70 = -0.04750921;
            }
        }
    }
    double var71;
    if (features[3] < 2.3895) {
        if (features[3] < -2.2843) {
            if (features[5] < 0.02048) {
                var71 = 0.0030421233;
            } else {
                var71 = 0.030238077;
            }
        } else {
            if (features[5] < 0.018174) {
                var71 = 0.0018890415;
            } else {
                var71 = -0.032328352;
            }
        }
    } else {
        if (features[5] < 0.007216) {
            var71 = -0.015789412;
        } else {
            if (features[6] < 1.347552) {
                var71 = 0.060678452;
            } else {
                var71 = 0.0043791006;
            }
        }
    }
    double var72;
    if (features[6] < 0.58362) {
        if (features[4] < -0.001097) {
            if (features[1] < 0.162863) {
                var72 = 0.013009015;
            } else {
                var72 = -0.04018925;
            }
        } else {
            if (features[1] < 0.251001) {
                var72 = 0.06976917;
            } else {
                var72 = 0.0005940708;
            }
        }
    } else {
        if (features[0] < 0.028279) {
            if (features[6] < 0.952252) {
                var72 = -0.01239838;
            } else {
                var72 = 0.010313234;
            }
        } else {
            if (features[6] < 1.461778) {
                var72 = -0.044382107;
            } else {
                var72 = 0.012689993;
            }
        }
    }
    double var73;
    if (features[6] < 0.58362) {
        if (features[4] < -0.001097) {
            if (features[2] < 20.66) {
                var73 = 0.01115009;
            } else {
                var73 = -0.029481262;
            }
        } else {
            if (features[3] < 0.714) {
                var73 = 0.049203034;
            } else {
                var73 = 0.0036792455;
            }
        }
    } else {
        if (features[4] < 0.008348) {
            if (features[2] < 21.08) {
                var73 = -0.019468188;
            } else {
                var73 = 0.019299218;
            }
        } else {
            if (features[1] < 0.230185) {
                var73 = -0.022729669;
            } else {
                var73 = 0.0010298978;
            }
        }
    }
    double var74;
    if (features[2] < 35.66) {
        if (features[2] < 30.75) {
            if (features[4] < -0.004352) {
                var74 = -0.017983338;
            } else {
                var74 = 0.01069719;
            }
        } else {
            if (features[4] < 0.003659) {
                var74 = 0.06159958;
            } else {
                var74 = 0.018361123;
            }
        }
    } else {
        if (features[1] < 0.308387) {
            if (features[2] < 46.79) {
                var74 = -0.030492935;
            } else {
                var74 = 0.005712655;
            }
        } else {
            if (features[1] < 0.318976) {
                var74 = 0.05105443;
            } else {
                var74 = 0.008324224;
            }
        }
    }
    double var75;
    if (features[4] < 0.005233) {
        if (features[1] < 0.259212) {
            if (features[1] < 0.212977) {
                var75 = -0.011999104;
            } else {
                var75 = 0.03433096;
            }
        } else {
            if (features[1] < 0.281673) {
                var75 = -0.06846943;
            } else {
                var75 = -0.0073612235;
            }
        }
    } else {
        if (features[4] < 0.007611) {
            var75 = 0.05282153;
        } else {
            if (features[4] < 0.013858) {
                var75 = -0.027932266;
            } else {
                var75 = 0.0061645494;
            }
        }
    }
    double var76;
    if (features[2] < 49.95) {
        if (features[2] < 44.96) {
            if (features[2] < 36.27) {
                var76 = 0.0057882783;
            } else {
                var76 = -0.02278068;
            }
        } else {
            if (features[5] < 0.0111) {
                var76 = -0.009261337;
            } else {
                var76 = 0.054050293;
            }
        }
    } else {
        if (features[2] < 62.95) {
            if (features[3] < -2.3026) {
                var76 = -0.04919981;
            } else {
                var76 = 0.002847218;
            }
        } else {
            var76 = 0.010080696;
        }
    }
    double var77;
    if (features[6] < 0.58362) {
        if (features[1] < 0.190216) {
            if (features[1] < 0.126393) {
                var77 = 0.0026187405;
            } else {
                var77 = 0.052387733;
            }
        } else {
            if (features[1] < 0.225582) {
                var77 = -0.02594979;
            } else {
                var77 = 0.01883685;
            }
        }
    } else {
        if (features[6] < 0.692517) {
            if (features[5] < 0.008879) {
                var77 = -0.049168017;
            } else {
                var77 = -0.009231179;
            }
        } else {
            if (features[0] < 0.028279) {
                var77 = 0.006285167;
            } else {
                var77 = -0.024533415;
            }
        }
    }
    double var78;
    if (features[2] < 67.47) {
        if (features[2] < 61.55) {
            if (features[2] < 49.95) {
                var78 = 0.005122247;
            } else {
                var78 = -0.018970914;
            }
        } else {
            var78 = 0.047015384;
        }
    } else {
        var78 = -0.035017915;
    }
    double var79;
    if (features[6] < 0.58362) {
        if (features[3] < 0.0732) {
            var79 = 0.057146456;
        } else {
            if (features[1] < 0.186529) {
                var79 = 0.04498632;
            } else {
                var79 = -0.04508219;
            }
        }
    } else {
        if (features[4] < 0.017565) {
            if (features[1] < 0.295803) {
                var79 = -0.006279606;
            } else {
                var79 = 0.041025188;
            }
        } else {
            if (features[3] < -2.1174) {
                var79 = -0.0043622586;
            } else {
                var79 = -0.03218916;
            }
        }
    }
    double var80;
    if (features[6] < 0.651915) {
        if (features[2] < 26.12) {
            if (features[3] < -2.6878) {
                var80 = 0.00543928;
            } else {
                var80 = 0.053181063;
            }
        } else {
            if (features[1] < 0.186529) {
                var80 = 0.021479946;
            } else {
                var80 = -0.025795434;
            }
        }
    } else {
        if (features[6] < 0.726599) {
            if (features[2] < 20.17) {
                var80 = -0.0017020938;
            } else {
                var80 = -0.05766315;
            }
        } else {
            if (features[6] < 0.78691) {
                var80 = 0.031776212;
            } else {
                var80 = -0.002329422;
            }
        }
    }
    double var81;
    if (features[3] < -4.2129) {
        if (features[5] < 0.016969) {
            if (features[6] < 0.767066) {
                var81 = 0.0056889975;
            } else {
                var81 = 0.054104973;
            }
        } else {
            if (features[6] < 1.295657) {
                var81 = 0.027836958;
            } else {
                var81 = -0.032378945;
            }
        }
    } else {
        if (features[5] < 0.030022) {
            if (features[4] < 0.030409) {
                var81 = -0.0021349008;
            } else {
                var81 = -0.027071342;
            }
        } else {
            if (features[3] < -2.4022) {
                var81 = 0.04597612;
            } else {
                var81 = -0.03360398;
            }
        }
    }
    double var82;
    if (features[3] < -3.8758) {
        if (features[5] < 0.020776) {
            if (features[1] < 0.208608) {
                var82 = 0.02448818;
            } else {
                var82 = -0.030389732;
            }
        } else {
            var82 = 0.05628215;
        }
    } else {
        if (features[6] < 1.978757) {
            if (features[6] < 1.831135) {
                var82 = -0.0019857427;
            } else {
                var82 = -0.045905937;
            }
        } else {
            if (features[3] < -0.4414) {
                var82 = 0.046401225;
            } else {
                var82 = -0.024611864;
            }
        }
    }
    double var83;
    if (features[4] < 0.004667) {
        if (features[3] < 0.6508) {
            if (features[0] < 0.008569) {
                var83 = 0.010950008;
            } else {
                var83 = -0.026828934;
            }
        } else {
            if (features[5] < 0.008942) {
                var83 = -0.017467197;
            } else {
                var83 = 0.036145467;
            }
        }
    } else {
        if (features[2] < 22.93) {
            if (features[5] < 0.014633) {
                var83 = 0.04658301;
            } else {
                var83 = 0.0056162137;
            }
        } else {
            if (features[3] < -2.9314) {
                var83 = 0.012544693;
            } else {
                var83 = -0.015732516;
            }
        }
    }
    double var84;
    if (features[5] < 0.004861) {
        if (features[5] < 0.004118) {
            var84 = 0.014557162;
        } else {
            var84 = 0.05575737;
        }
    } else {
        if (features[5] < 0.006881) {
            if (features[2] < 27.9) {
                var84 = 0.0020734582;
            } else {
                var84 = -0.050297447;
            }
        } else {
            if (features[5] < 0.015827) {
                var84 = 0.011438015;
            } else {
                var84 = -0.004340994;
            }
        }
    }
    double var85;
    if (features[4] < -0.015176) {
        if (features[5] < 0.008746) {
            var85 = -0.022008825;
        } else {
            if (features[3] < -0.3345) {
                var85 = 0.0035096114;
            } else {
                var85 = 0.06625208;
            }
        }
    } else {
        if (features[3] < 3.3342) {
            if (features[5] < 0.030022) {
                var85 = -0.007822133;
            } else {
                var85 = 0.018963559;
            }
        } else {
            var85 = -0.0426859;
        }
    }
    double var86;
    if (features[4] < -0.003173) {
        if (features[2] < 30.36) {
            if (features[0] < 0.024755) {
                var86 = -0.029794483;
            } else {
                var86 = 0.010937498;
            }
        } else {
            if (features[2] < 34.76) {
                var86 = 0.038587116;
            } else {
                var86 = -0.0069261426;
            }
        }
    } else {
        if (features[1] < 0.242188) {
            if (features[3] < -1.4951) {
                var86 = -0.012656182;
            } else {
                var86 = 0.015829144;
            }
        } else {
            if (features[4] < 0.034964) {
                var86 = 0.025791643;
            } else {
                var86 = -0.02234709;
            }
        }
    }
    double var87;
    if (features[5] < 0.015827) {
        if (features[1] < 0.23301) {
            if (features[5] < 0.015489) {
                var87 = -0.0060145156;
            } else {
                var87 = 0.048111256;
            }
        } else {
            if (features[1] < 0.260367) {
                var87 = 0.054381706;
            } else {
                var87 = 0.0054787328;
            }
        }
    } else {
        if (features[5] < 0.021535) {
            if (features[3] < 0.8469) {
                var87 = -0.02598508;
            } else {
                var87 = 0.021235766;
            }
        } else {
            if (features[3] < -2.1174) {
                var87 = 0.019404586;
            } else {
                var87 = -0.021281095;
            }
        }
    }
    double var88;
    if (features[1] < 0.177718) {
        if (features[3] < 1.3756) {
            if (features[1] < 0.126393) {
                var88 = -0.035989154;
            } else {
                var88 = 0.035632696;
            }
        } else {
            if (features[3] < 2.2237) {
                var88 = -0.051612895;
            } else {
                var88 = -0.0031789837;
            }
        }
    } else {
        if (features[1] < 0.182675) {
            if (features[4] < 0.006446) {
                var88 = -0.0093651125;
            } else {
                var88 = -0.051057365;
            }
        } else {
            if (features[1] < 0.18888) {
                var88 = 0.041076973;
            } else {
                var88 = -0.008004057;
            }
        }
    }
    double var89;
    if (features[3] < -2.4749) {
        if (features[1] < 0.194857) {
            if (features[3] < -4.2838) {
                var89 = 0.025807044;
            } else {
                var89 = -0.01929416;
            }
        } else {
            if (features[4] < 0.017153) {
                var89 = 0.032834392;
            } else {
                var89 = 0.0033719332;
            }
        }
    } else {
        if (features[5] < 0.005149) {
            var89 = 0.040683977;
        } else {
            if (features[5] < 0.015744) {
                var89 = -0.004890791;
            } else {
                var89 = -0.031000689;
            }
        }
    }
    double var90;
    if (features[4] < -0.013023) {
        if (features[6] < 1.259631) {
            if (features[3] < -0.3345) {
                var90 = -0.052357584;
            } else {
                var90 = -0.013362035;
            }
        } else {
            var90 = 0.016945262;
        }
    } else {
        if (features[3] < 3.1127) {
            if (features[3] < 1.0464) {
                var90 = 0.001837104;
            } else {
                var90 = 0.027964765;
            }
        } else {
            if (features[5] < 0.011595) {
                var90 = -0.04196902;
            } else {
                var90 = -0.005921071;
            }
        }
    }
    double var91;
    if (features[5] < 0.004861) {
        if (features[6] < 0.487791) {
            var91 = 0.042224284;
        } else {
            var91 = 0.005688579;
        }
    } else {
        if (features[4] < 0.034375) {
            if (features[3] < -4.5754) {
                var91 = 0.029191315;
            } else {
                var91 = -0.0025050507;
            }
        } else {
            if (features[5] < 0.027807) {
                var91 = -0.03364162;
            } else {
                var91 = 0.02049408;
            }
        }
    }
    double var92;
    if (features[1] < 0.151153) {
        if (features[5] < 0.013002) {
            if (features[4] < 0.003968) {
                var92 = -0.009685497;
            } else {
                var92 = -0.048932742;
            }
        } else {
            var92 = 0.011023522;
        }
    } else {
        if (features[3] < 3.1127) {
            if (features[5] < 0.015827) {
                var92 = 0.017716752;
            } else {
                var92 = -0.0026277767;
            }
        } else {
            if (features[2] < 35.66) {
                var92 = 0.00033368208;
            } else {
                var92 = -0.040441755;
            }
        }
    }
    double var93;
    if (features[6] < 0.58362) {
        if (features[1] < 0.118119) {
            var93 = -0.01886016;
        } else {
            if (features[3] < -0.4414) {
                var93 = 0.05265641;
            } else {
                var93 = 0.0028133513;
            }
        }
    } else {
        if (features[1] < 0.151153) {
            if (features[6] < 0.75632) {
                var93 = -0.05574125;
            } else {
                var93 = -0.0020025324;
            }
        } else {
            if (features[3] < -0.1477) {
                var93 = -0.0043065907;
            } else {
                var93 = 0.021058304;
            }
        }
    }
    double var94;
    if (features[1] < 0.179792) {
        if (features[1] < 0.151153) {
            if (features[1] < 0.144938) {
                var94 = 0.0031509567;
            } else {
                var94 = -0.05247407;
            }
        } else {
            if (features[4] < 0.019389) {
                var94 = 0.048535638;
            } else {
                var94 = -0.009533162;
            }
        }
    } else {
        if (features[2] < 22.58) {
            if (features[4] < 0.002743) {
                var94 = -0.012103406;
            } else {
                var94 = 0.02199859;
            }
        } else {
            if (features[2] < 27.33) {
                var94 = -0.033872347;
            } else {
                var94 = -0.0014557004;
            }
        }
    }
    double var95;
    if (features[4] < 0.004088) {
        if (features[3] < 0.6508) {
            if (features[4] < -0.017039) {
                var95 = 0.0126185585;
            } else {
                var95 = -0.031025574;
            }
        } else {
            if (features[3] < 3.8529) {
                var95 = 0.0303266;
            } else {
                var95 = -0.030343855;
            }
        }
    } else {
        if (features[4] < 0.007611) {
            if (features[4] < 0.005233) {
                var95 = 0.0036330782;
            } else {
                var95 = 0.048944145;
            }
        } else {
            if (features[6] < 0.651915) {
                var95 = 0.038560044;
            } else {
                var95 = 0.0000050793606;
            }
        }
    }
    double var96;
    if (features[5] < 0.02847) {
        if (features[5] < 0.015827) {
            if (features[5] < 0.008879) {
                var96 = -0.011053232;
            } else {
                var96 = 0.013111255;
            }
        } else {
            if (features[2] < 21.04) {
                var96 = -0.05783527;
            } else {
                var96 = -0.004908282;
            }
        }
    } else {
        if (features[1] < 0.315101) {
            var96 = 0.04769092;
        } else {
            if (features[1] < 0.384485) {
                var96 = -0.033770777;
            } else {
                var96 = 0.0038280257;
            }
        }
    }
    double var97;
    if (features[5] < 0.017607) {
        if (features[5] < 0.008942) {
            if (features[5] < 0.008531) {
                var97 = 0.0044720303;
            } else {
                var97 = -0.049983513;
            }
        } else {
            if (features[3] < 2.1304) {
                var97 = 0.010891165;
            } else {
                var97 = 0.0471444;
            }
        }
    } else {
        if (features[5] < 0.018673) {
            if (features[4] < 0.00712) {
                var97 = -0.00603355;
            } else {
                var97 = -0.06025784;
            }
        } else {
            if (features[2] < 32.45) {
                var97 = -0.015689049;
            } else {
                var97 = 0.019949455;
            }
        }
    }
    double var98;
    if (features[1] < 0.385067) {
        if (features[6] < 1.125862) {
            if (features[1] < 0.299143) {
                var98 = 0.0017093184;
            } else {
                var98 = 0.043252084;
            }
        } else {
            if (features[1] < 0.179792) {
                var98 = 0.022325175;
            } else {
                var98 = -0.01915768;
            }
        }
    } else {
        if (features[5] < 0.031009) {
            if (features[0] < 0.025782) {
                var98 = 0.04552368;
            } else {
                var98 = 0.012287183;
            }
        } else {
            var98 = -0.017208248;
        }
    }
    double var99;
    if (features[1] < 0.120463) {
        var99 = -0.046013486;
    } else {
        if (features[1] < 0.179792) {
            if (features[6] < 1.152675) {
                var99 = 0.007353738;
            } else {
                var99 = 0.05399085;
            }
        } else {
            if (features[1] < 0.232324) {
                var99 = -0.0117361685;
            } else {
                var99 = 0.0072327317;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = var100;
}
