//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| Generated automatically by m2cgen for MetaTrader 5            |
//| Model: XGBoost (Longs Only Specialized)                       |
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
    if (features[3] < 2.4022) {
        if (features[1] < 0.179458) {
            if (features[3] < -2.918) {
                var0 = -0.040000003;
            } else {
                var0 = 0.036842104;
            }
        } else {
            if (features[2] < 18.2) {
                var0 = 0.020000001;
            } else {
                var0 = -0.034653466;
            }
        }
    } else {
        if (features[4] < 0.009965) {
            if (features[3] < 3.5708) {
                var0 = 0.016666668;
            } else {
                var0 = -0.033333335;
            }
        } else {
            if (features[1] < 0.145358) {
                var0 = 0.0;
            } else {
                var0 = 0.061538465;
            }
        }
    }
    double var1;
    if (features[4] < 0.002672) {
        if (features[2] < 31.6) {
            if (features[2] < 28.62) {
                var1 = -0.0064262175;
            } else {
                var1 = 0.06353613;
            }
        } else {
            if (features[5] < 0.011861) {
                var1 = -0.059363384;
            } else {
                var1 = 0.00051320344;
            }
        }
    } else {
        if (features[5] < 0.047904) {
            if (features[4] < 0.041695) {
                var1 = 0.017094016;
            } else {
                var1 = 0.049031805;
            }
        } else {
            var1 = -0.03344976;
        }
    }
    double var2;
    if (features[3] < 2.6256) {
        if (features[5] < 0.015746) {
            if (features[3] < -3.0902) {
                var2 = -0.05828766;
            } else {
                var2 = 0.01717275;
            }
        } else {
            if (features[0] < 0.013556) {
                var2 = 0.0073563964;
            } else {
                var2 = -0.057078697;
            }
        }
    } else {
        if (features[0] < 0.010643) {
            var2 = -0.040136233;
        } else {
            if (features[1] < 0.146961) {
                var2 = -0.005908585;
            } else {
                var2 = 0.048209265;
            }
        }
    }
    double var3;
    if (features[3] < -3.0902) {
        if (features[5] < 0.008459) {
            var3 = -0.060243357;
        } else {
            var3 = -0.017028905;
        }
    } else {
        if (features[1] < 0.145358) {
            if (features[1] < 0.105091) {
                var3 = 0.031380937;
            } else {
                var3 = -0.030723399;
            }
        } else {
            if (features[1] < 0.179458) {
                var3 = 0.05653375;
            } else {
                var3 = 0.009462818;
            }
        }
    }
    double var4;
    if (features[3] < 2.6468) {
        if (features[0] < 0.01189) {
            if (features[5] < 0.007314) {
                var4 = -0.020611476;
            } else {
                var4 = 0.052266818;
            }
        } else {
            if (features[2] < 17.71) {
                var4 = 0.031087974;
            } else {
                var4 = -0.019337319;
            }
        }
    } else {
        if (features[0] < 0.01086) {
            var4 = -0.027838582;
        } else {
            if (features[2] < 39.27) {
                var4 = 0.047462527;
            } else {
                var4 = 0.012816921;
            }
        }
    }
    double var5;
    if (features[3] < 2.5377) {
        if (features[2] < 17.71) {
            if (features[2] < 15.84) {
                var5 = -0.0026062715;
            } else {
                var5 = 0.0682924;
            }
        } else {
            if (features[0] < 0.011724) {
                var5 = 0.020216886;
            } else {
                var5 = -0.02245842;
            }
        }
    } else {
        if (features[4] < 0.002661) {
            if (features[0] < 0.018155) {
                var5 = -0.038684875;
            } else {
                var5 = 0.014172214;
            }
        } else {
            if (features[6] < 0.36583) {
                var5 = -0.02007788;
            } else {
                var5 = 0.047390867;
            }
        }
    }
    double var6;
    if (features[3] < -3.0902) {
        var6 = -0.053270597;
    } else {
        if (features[3] < 2.6256) {
            if (features[3] < 1.9409) {
                var6 = 0.01565364;
            } else {
                var6 = -0.03519967;
            }
        } else {
            if (features[0] < 0.010643) {
                var6 = -0.038347963;
            } else {
                var6 = 0.03274514;
            }
        }
    }
    double var7;
    if (features[3] < -2.918) {
        var7 = -0.059002377;
    } else {
        if (features[3] < 2.5377) {
            if (features[5] < 0.015644) {
                var7 = 0.025174825;
            } else {
                var7 = -0.029343134;
            }
        } else {
            if (features[5] < 0.009407) {
                var7 = -0.026041603;
            } else {
                var7 = 0.039477352;
            }
        }
    }
    double var8;
    if (features[3] < 0.4414) {
        if (features[2] < 31.75) {
            if (features[4] < 0.020727) {
                var8 = 0.024851743;
            } else {
                var8 = -0.03395548;
            }
        } else {
            if (features[0] < 0.019694) {
                var8 = -0.06718153;
            } else {
                var8 = -0.0034275816;
            }
        }
    } else {
        if (features[4] < 0.002661) {
            if (features[4] < -0.010343) {
                var8 = 0.02064097;
            } else {
                var8 = -0.040644426;
            }
        } else {
            if (features[4] < 0.008124) {
                var8 = 0.060238954;
            } else {
                var8 = 0.018722719;
            }
        }
    }
    double var9;
    if (features[3] < 2.6228) {
        if (features[5] < 0.015746) {
            if (features[6] < 1.091543) {
                var9 = -0.006986832;
            } else {
                var9 = 0.036795374;
            }
        } else {
            if (features[4] < 0.019337) {
                var9 = -0.059337366;
            } else {
                var9 = -0.00401693;
            }
        }
    } else {
        if (features[5] < 0.009407) {
            if (features[5] < 0.00853) {
                var9 = 0.016267283;
            } else {
                var9 = -0.046621364;
            }
        } else {
            if (features[6] < 0.091561) {
                var9 = -0.0073109167;
            } else {
                var9 = 0.037802696;
            }
        }
    }
    double var10;
    if (features[3] < -3.0902) {
        var10 = -0.054948308;
    } else {
        if (features[3] < 4.2217) {
            if (features[3] < -2.2761) {
                var10 = 0.05262633;
            } else {
                var10 = 0.0014379298;
            }
        } else {
            if (features[6] < 1.442261) {
                var10 = 0.06649171;
            } else {
                var10 = 0.0099366335;
            }
        }
    }
    double var11;
    if (features[3] < 0.4281) {
        if (features[5] < 0.021535) {
            if (features[6] < 0.47591) {
                var11 = 0.035925914;
            } else {
                var11 = -0.018498547;
            }
        } else {
            var11 = -0.065947935;
        }
    } else {
        if (features[1] < 0.123733) {
            var11 = -0.0516829;
        } else {
            if (features[1] < 0.176351) {
                var11 = 0.04724207;
            } else {
                var11 = 0.010411943;
            }
        }
    }
    double var12;
    if (features[3] < -3.0902) {
        var12 = -0.054719474;
    } else {
        if (features[2] < 28.9) {
            if (features[6] < 0.515955) {
                var12 = 0.038472366;
            } else {
                var12 = -0.014565371;
            }
        } else {
            if (features[6] < 0.944395) {
                var12 = 0.00594216;
            } else {
                var12 = 0.045473594;
            }
        }
    }
    double var13;
    if (features[3] < 2.6256) {
        if (features[0] < 0.011724) {
            if (features[1] < 0.217756) {
                var13 = -0.0002816313;
            } else {
                var13 = 0.043031804;
            }
        } else {
            if (features[1] < 0.174615) {
                var13 = 0.019085675;
            } else {
                var13 = -0.028086647;
            }
        }
    } else {
        if (features[0] < 0.010643) {
            var13 = -0.043823592;
        } else {
            if (features[1] < 0.146961) {
                var13 = -0.011082012;
            } else {
                var13 = 0.042443622;
            }
        }
    }
    double var14;
    if (features[1] < 0.142891) {
        if (features[1] < 0.108243) {
            var14 = 0.03217662;
        } else {
            if (features[0] < 0.011498) {
                var14 = -0.0028399215;
            } else {
                var14 = -0.053723205;
            }
        }
    } else {
        if (features[1] < 0.173326) {
            if (features[4] < 0.009792) {
                var14 = 0.01807903;
            } else {
                var14 = 0.056165732;
            }
        } else {
            if (features[1] < 0.224159) {
                var14 = -0.016997047;
            } else {
                var14 = 0.015872868;
            }
        }
    }
    double var15;
    if (features[3] < 2.6228) {
        if (features[1] < 0.189323) {
            if (features[1] < 0.14252) {
                var15 = -0.018386694;
            } else {
                var15 = 0.039134774;
            }
        } else {
            if (features[5] < 0.018248) {
                var15 = -0.0012992834;
            } else {
                var15 = -0.049189147;
            }
        }
    } else {
        if (features[4] < 0.002661) {
            if (features[3] < 3.4124) {
                var15 = 0.03915846;
            } else {
                var15 = -0.049075242;
            }
        } else {
            if (features[1] < 0.146961) {
                var15 = 0.0004427412;
            } else {
                var15 = 0.047194883;
            }
        }
    }
    double var16;
    if (features[3] < -3.0902) {
        var16 = -0.0457468;
    } else {
        if (features[6] < 0.651915) {
            if (features[5] < 0.014896) {
                var16 = 0.035519786;
            } else {
                var16 = -0.010004333;
            }
        } else {
            if (features[6] < 0.692197) {
                var16 = -0.06724006;
            } else {
                var16 = 0.008340387;
            }
        }
    }
    double var17;
    if (features[3] < 2.6256) {
        if (features[3] < 1.7916) {
            if (features[6] < 0.529138) {
                var17 = 0.037422057;
            } else {
                var17 = -0.0076959985;
            }
        } else {
            if (features[2] < 21.03) {
                var17 = 0.006186578;
            } else {
                var17 = -0.07122083;
            }
        }
    } else {
        if (features[0] < 0.010643) {
            var17 = -0.0374969;
        } else {
            if (features[0] < 0.025795) {
                var17 = 0.033504136;
            } else {
                var17 = 0.0049342103;
            }
        }
    }
    double var18;
    if (features[4] < -0.002464) {
        if (features[0] < 0.017088) {
            if (features[5] < 0.007966) {
                var18 = -0.061570432;
            } else {
                var18 = -0.018302849;
            }
        } else {
            if (features[5] < 0.014429) {
                var18 = 0.021839153;
            } else {
                var18 = -0.031959567;
            }
        }
    } else {
        if (features[1] < 0.173326) {
            if (features[0] < 0.017066) {
                var18 = 0.0017428262;
            } else {
                var18 = 0.052471813;
            }
        } else {
            if (features[0] < 0.007863) {
                var18 = 0.05000289;
            } else {
                var18 = -0.0033753437;
            }
        }
    }
    double var19;
    if (features[0] < 0.037544) {
        if (features[2] < 17.71) {
            if (features[4] < -0.000775) {
                var19 = -0.00438766;
            } else {
                var19 = 0.044840947;
            }
        } else {
            if (features[5] < 0.006881) {
                var19 = -0.037434455;
            } else {
                var19 = 0.004925652;
            }
        }
    } else {
        var19 = 0.049811114;
    }
    double var20;
    if (features[5] < 0.015746) {
        if (features[5] < 0.012512) {
            if (features[6] < 0.545508) {
                var20 = 0.0337954;
            } else {
                var20 = -0.009566074;
            }
        } else {
            if (features[0] < 0.028006) {
                var20 = 0.041627303;
            } else {
                var20 = -0.032361355;
            }
        }
    } else {
        if (features[4] < 0.010458) {
            if (features[1] < 0.244944) {
                var20 = -0.06457392;
            } else {
                var20 = -0.0067453496;
            }
        } else {
            if (features[6] < 1.418829) {
                var20 = 0.021002227;
            } else {
                var20 = -0.020356888;
            }
        }
    }
    double var21;
    if (features[3] < 0.4414) {
        if (features[6] < 0.526408) {
            if (features[1] < 0.168867) {
                var21 = 0.03461003;
            } else {
                var21 = -0.02790757;
            }
        } else {
            if (features[6] < 1.040147) {
                var21 = -0.05962501;
            } else {
                var21 = -0.006071422;
            }
        }
    } else {
        if (features[1] < 0.123733) {
            var21 = -0.03616856;
        } else {
            if (features[1] < 0.176351) {
                var21 = 0.05239835;
            } else {
                var21 = 0.007775496;
            }
        }
    }
    double var22;
    if (features[2] < 49.1) {
        if (features[4] < 0.02452) {
            if (features[4] < -0.0019) {
                var22 = -0.020905105;
            } else {
                var22 = 0.0115006715;
            }
        } else {
            if (features[0] < 0.029132) {
                var22 = -0.026185269;
            } else {
                var22 = 0.043659475;
            }
        }
    } else {
        if (features[4] < 0.020933) {
            if (features[0] < 0.018123) {
                var22 = 0.0076557407;
            } else {
                var22 = -0.028361237;
            }
        } else {
            var22 = 0.06436465;
        }
    }
    double var23;
    if (features[3] < -2.918) {
        if (features[5] < 0.008561) {
            var23 = -0.050526656;
        } else {
            var23 = -0.012876651;
        }
    } else {
        if (features[3] < -2.2891) {
            if (features[4] < 0.000719) {
                var23 = 0.052630406;
            } else {
                var23 = 0.00936135;
            }
        } else {
            if (features[5] < 0.005564) {
                var23 = -0.039329764;
            } else {
                var23 = 0.0029738245;
            }
        }
    }
    double var24;
    if (features[3] < 0.4414) {
        if (features[1] < 0.126393) {
            var24 = 0.04040331;
        } else {
            if (features[4] < 0.001844) {
                var24 = 0.010577652;
            } else {
                var24 = -0.039028134;
            }
        }
    } else {
        if (features[1] < 0.142491) {
            if (features[4] < 0.009299) {
                var24 = -0.052108746;
            } else {
                var24 = -0.008378769;
            }
        } else {
            if (features[6] < 0.768912) {
                var24 = 0.04599609;
            } else {
                var24 = 0.006090094;
            }
        }
    }
    double var25;
    if (features[3] < -2.918) {
        if (features[5] < 0.008561) {
            var25 = -0.04921795;
        } else {
            var25 = -0.017986413;
        }
    } else {
        if (features[2] < 26.82) {
            if (features[2] < 21.95) {
                var25 = 0.013857216;
            } else {
                var25 = -0.023161529;
            }
        } else {
            if (features[6] < 0.095114) {
                var25 = -0.015559954;
            } else {
                var25 = 0.022925867;
            }
        }
    }
    double var26;
    if (features[1] < 0.245359) {
        if (features[1] < 0.205013) {
            if (features[1] < 0.145358) {
                var26 = -0.024930729;
            } else {
                var26 = 0.013984307;
            }
        } else {
            if (features[6] < 1.081635) {
                var26 = -0.012301386;
            } else {
                var26 = -0.061707217;
            }
        }
    } else {
        if (features[1] < 0.260367) {
            var26 = 0.05946354;
        } else {
            if (features[3] < -0.2718) {
                var26 = -0.024432095;
            } else {
                var26 = 0.017262613;
            }
        }
    }
    double var27;
    if (features[6] < 0.952252) {
        if (features[6] < 0.773166) {
            if (features[6] < 0.700587) {
                var27 = -0.0013017798;
            } else {
                var27 = 0.033809334;
            }
        } else {
            if (features[6] < 0.822996) {
                var27 = -0.07428317;
            } else {
                var27 = -0.018366696;
            }
        }
    } else {
        if (features[1] < 0.179458) {
            var27 = 0.0537644;
        } else {
            if (features[0] < 0.025795) {
                var27 = 0.014195657;
            } else {
                var27 = -0.031826597;
            }
        }
    }
    double var28;
    if (features[3] < -2.918) {
        if (features[5] < 0.008561) {
            var28 = -0.05199934;
        } else {
            var28 = -0.017351609;
        }
    } else {
        if (features[3] < 2.5037) {
            if (features[3] < 1.7916) {
                var28 = 0.010569974;
            } else {
                var28 = -0.03371622;
            }
        } else {
            if (features[2] < 31.64) {
                var28 = 0.03664857;
            } else {
                var28 = 0.0014879315;
            }
        }
    }
    double var29;
    if (features[6] < 0.108291) {
        if (features[2] < 28.96) {
            if (features[1] < 0.246939) {
                var29 = 0.004957214;
            } else {
                var29 = 0.029453216;
            }
        } else {
            var29 = -0.07306763;
        }
    } else {
        if (features[6] < 0.529138) {
            if (features[4] < -0.004415) {
                var29 = -0.027093416;
            } else {
                var29 = 0.047920007;
            }
        } else {
            if (features[1] < 0.145358) {
                var29 = -0.06199339;
            } else {
                var29 = 0.0061054593;
            }
        }
    }
    double var30;
    if (features[3] < 2.5037) {
        if (features[3] < 1.9409) {
            if (features[5] < 0.021535) {
                var30 = 0.01387613;
            } else {
                var30 = -0.041797172;
            }
        } else {
            if (features[5] < 0.012512) {
                var30 = -0.07027286;
            } else {
                var30 = -0.018077867;
            }
        }
    } else {
        if (features[0] < 0.011046) {
            var30 = -0.037128177;
        } else {
            if (features[1] < 0.145358) {
                var30 = -0.016267948;
            } else {
                var30 = 0.033165764;
            }
        }
    }
    double var31;
    if (features[3] < 0.6486) {
        if (features[4] < 0.007987) {
            if (features[3] < -3.0902) {
                var31 = -0.04646292;
            } else {
                var31 = 0.030592624;
            }
        } else {
            if (features[2] < 29.82) {
                var31 = -0.06039986;
            } else {
                var31 = 0.01241023;
            }
        }
    } else {
        if (features[4] < 0.002672) {
            if (features[4] < -0.011305) {
                var31 = 0.02114825;
            } else {
                var31 = -0.047515016;
            }
        } else {
            if (features[2] < 23.23) {
                var31 = 0.046106536;
            } else {
                var31 = 0.008546057;
            }
        }
    }
    double var32;
    if (features[1] < 0.224159) {
        if (features[1] < 0.204426) {
            if (features[6] < 1.217286) {
                var32 = -0.004417078;
            } else {
                var32 = 0.03467385;
            }
        } else {
            if (features[3] < -0.6508) {
                var32 = 0.014355649;
            } else {
                var32 = -0.055850722;
            }
        }
    } else {
        if (features[6] < 1.341072) {
            if (features[1] < 0.256474) {
                var32 = 0.048778947;
            } else {
                var32 = 0.012948825;
            }
        } else {
            if (features[1] < 0.384663) {
                var32 = -0.02531579;
            } else {
                var32 = 0.034088206;
            }
        }
    }
    double var33;
    if (features[3] < 2.4022) {
        if (features[0] < 0.01189) {
            if (features[4] < 0.016074) {
                var33 = 0.041172065;
            } else {
                var33 = -0.035198234;
            }
        } else {
            if (features[6] < 0.529138) {
                var33 = 0.007671967;
            } else {
                var33 = -0.03092404;
            }
        }
    } else {
        if (features[0] < 0.011046) {
            var33 = -0.046731822;
        } else {
            if (features[5] < 0.008962) {
                var33 = -0.016615652;
            } else {
                var33 = 0.026513407;
            }
        }
    }
    double var34;
    if (features[1] < 0.150823) {
        if (features[6] < 0.526408) {
            if (features[3] < 3.2614) {
                var34 = 0.021063467;
            } else {
                var34 = -0.03944389;
            }
        } else {
            if (features[5] < 0.011497) {
                var34 = -0.06880535;
            } else {
                var34 = -0.0056244344;
            }
        }
    } else {
        if (features[1] < 0.16918) {
            if (features[5] < 0.005215) {
                var34 = 0.016387051;
            } else {
                var34 = 0.061645936;
            }
        } else {
            if (features[1] < 0.224159) {
                var34 = -0.01546215;
            } else {
                var34 = 0.012352095;
            }
        }
    }
    double var35;
    if (features[3] < -3.0902) {
        var35 = -0.046207305;
    } else {
        if (features[1] < 0.145358) {
            if (features[1] < 0.105091) {
                var35 = 0.02457878;
            } else {
                var35 = -0.035691615;
            }
        } else {
            if (features[1] < 0.176351) {
                var35 = 0.04495152;
            } else {
                var35 = -0.0013468825;
            }
        }
    }
    double var36;
    if (features[6] < 0.952014) {
        if (features[2] < 31.64) {
            if (features[6] < 0.515955) {
                var36 = 0.030739501;
            } else {
                var36 = -0.010044623;
            }
        } else {
            if (features[0] < 0.020068) {
                var36 = -0.06345297;
            } else {
                var36 = 0.0008025593;
            }
        }
    } else {
        if (features[1] < 0.176351) {
            var36 = 0.057506587;
        } else {
            if (features[0] < 0.01959) {
                var36 = 0.019539155;
            } else {
                var36 = -0.014744423;
            }
        }
    }
    double var37;
    if (features[1] < 0.145358) {
        if (features[0] < 0.023456) {
            if (features[1] < 0.13391) {
                var37 = -0.012486228;
            } else {
                var37 = -0.06280001;
            }
        } else {
            var37 = 0.021342715;
        }
    } else {
        if (features[1] < 0.176351) {
            if (features[3] < -0.3323) {
                var37 = 0.0045668366;
            } else {
                var37 = 0.051710706;
            }
        } else {
            if (features[1] < 0.241876) {
                var37 = -0.012338806;
            } else {
                var37 = 0.011745673;
            }
        }
    }
    double var38;
    if (features[4] < -0.0019) {
        if (features[4] < -0.008767) {
            if (features[4] < -0.013182) {
                var38 = -0.014041834;
            } else {
                var38 = 0.032767165;
            }
        } else {
            if (features[1] < 0.175751) {
                var38 = 0.0011080218;
            } else {
                var38 = -0.050613414;
            }
        }
    } else {
        if (features[6] < 0.551433) {
            if (features[1] < 0.189594) {
                var38 = 0.036011066;
            } else {
                var38 = 0.00057539565;
            }
        } else {
            if (features[6] < 0.692197) {
                var38 = -0.03860629;
            } else {
                var38 = 0.0050857808;
            }
        }
    }
    double var39;
    if (features[3] < -3.0902) {
        var39 = -0.036851864;
    } else {
        if (features[2] < 26.82) {
            if (features[2] < 19.93) {
                var39 = 0.018488487;
            } else {
                var39 = -0.016313048;
            }
        } else {
            if (features[3] < 1.4964) {
                var39 = 0.04114446;
            } else {
                var39 = 0.0040287497;
            }
        }
    }
    double var40;
    if (features[3] < 3.9608) {
        if (features[3] < 3.8085) {
            if (features[1] < 0.176351) {
                var40 = 0.023790313;
            } else {
                var40 = -0.0042540226;
            }
        } else {
            var40 = -0.06128586;
        }
    } else {
        if (features[5] < 0.016621) {
            if (features[4] < 0.013089) {
                var40 = 0.025886534;
            } else {
                var40 = -0.0036878572;
            }
        } else {
            var40 = 0.05603362;
        }
    }
    double var41;
    if (features[3] < -2.918) {
        var41 = -0.0438282;
    } else {
        if (features[1] < 0.150823) {
            if (features[5] < 0.00853) {
                var41 = 0.00013597123;
            } else {
                var41 = -0.038267266;
            }
        } else {
            if (features[1] < 0.176351) {
                var41 = 0.041495766;
            } else {
                var41 = -0.0009368725;
            }
        }
    }
    double var42;
    if (features[1] < 0.145358) {
        if (features[1] < 0.105091) {
            var42 = 0.03060557;
        } else {
            if (features[5] < 0.007502) {
                var42 = -0.010385055;
            } else {
                var42 = -0.04847191;
            }
        }
    } else {
        if (features[3] < -3.0902) {
            var42 = -0.03712343;
        } else {
            if (features[1] < 0.179458) {
                var42 = 0.031534415;
            } else {
                var42 = 0.0032438233;
            }
        }
    }
    double var43;
    if (features[5] < 0.006881) {
        if (features[2] < 17.89) {
            var43 = 0.01851084;
        } else {
            if (features[2] < 24.25) {
                var43 = -0.06250217;
            } else {
                var43 = -0.020462897;
            }
        }
    } else {
        if (features[0] < 0.01189) {
            if (features[1] < 0.217756) {
                var43 = 0.005770118;
            } else {
                var43 = 0.046898622;
            }
        } else {
            if (features[4] < 0.019337) {
                var43 = -0.017245939;
            } else {
                var43 = 0.0067671873;
            }
        }
    }
    double var44;
    if (features[3] < 2.4022) {
        if (features[0] < 0.01189) {
            if (features[0] < 0.007882) {
                var44 = -0.026588395;
            } else {
                var44 = 0.039923135;
            }
        } else {
            if (features[1] < 0.176062) {
                var44 = 0.0092456;
            } else {
                var44 = -0.029438844;
            }
        }
    } else {
        if (features[0] < 0.01086) {
            var44 = -0.031822175;
        } else {
            if (features[1] < 0.145358) {
                var44 = -0.017664568;
            } else {
                var44 = 0.019826788;
            }
        }
    }
    double var45;
    if (features[3] < 2.3202) {
        if (features[0] < 0.011669) {
            if (features[0] < 0.010339) {
                var45 = 0.0041577634;
            } else {
                var45 = 0.05799957;
            }
        } else {
            if (features[2] < 19.82) {
                var45 = 0.0052349004;
            } else {
                var45 = -0.035898175;
            }
        }
    } else {
        if (features[1] < 0.146961) {
            if (features[0] < 0.022297) {
                var45 = -0.041545864;
            } else {
                var45 = 0.001654372;
            }
        } else {
            if (features[2] < 30.24) {
                var45 = 0.041199557;
            } else {
                var45 = 0.0043131574;
            }
        }
    }
    double var46;
    if (features[3] < -3.0902) {
        var46 = -0.038428754;
    } else {
        if (features[0] < 0.026956) {
            if (features[3] < -2.2891) {
                var46 = 0.051010456;
            } else {
                var46 = -0.0023711387;
            }
        } else {
            if (features[0] < 0.049529) {
                var46 = 0.039487377;
            } else {
                var46 = -0.01336356;
            }
        }
    }
    double var47;
    if (features[5] < 0.007314) {
        if (features[6] < 0.490086) {
            if (features[2] < 17.28) {
                var47 = 0.042760093;
            } else {
                var47 = -0.00091916876;
            }
        } else {
            if (features[0] < 0.00842) {
                var47 = -0.011361216;
            } else {
                var47 = -0.04953239;
            }
        }
    } else {
        if (features[1] < 0.145358) {
            if (features[0] < 0.014191) {
                var47 = -0.046623845;
            } else {
                var47 = -0.00016942747;
            }
        } else {
            if (features[1] < 0.169463) {
                var47 = 0.055000287;
            } else {
                var47 = 0.0046581505;
            }
        }
    }
    double var48;
    if (features[5] < 0.007314) {
        if (features[6] < 0.490086) {
            var48 = 0.02346446;
        } else {
            if (features[3] < 1.2888) {
                var48 = -0.05748567;
            } else {
                var48 = -0.0048108804;
            }
        }
    } else {
        if (features[0] < 0.012535) {
            if (features[2] < 31.64) {
                var48 = 0.034200594;
            } else {
                var48 = -0.0019967682;
            }
        } else {
            if (features[6] < 0.819276) {
                var48 = -0.01865974;
            } else {
                var48 = 0.008097498;
            }
        }
    }
    double var49;
    if (features[1] < 0.123733) {
        if (features[1] < 0.117671) {
            var49 = 0.0029222504;
        } else {
            var49 = -0.056276817;
        }
    } else {
        if (features[2] < 17.71) {
            if (features[4] < -0.000507) {
                var49 = 0.000018431692;
            } else {
                var49 = 0.043087095;
            }
        } else {
            if (features[1] < 0.173326) {
                var49 = 0.01930309;
            } else {
                var49 = -0.004472262;
            }
        }
    }
    double var50;
    if (features[6] < 0.923753) {
        if (features[3] < 4.3589) {
            if (features[4] < 0.013925) {
                var50 = 0.005582125;
            } else {
                var50 = -0.025587356;
            }
        } else {
            var50 = 0.04164507;
        }
    } else {
        if (features[4] < 0.010501) {
            if (features[3] < 1.405) {
                var50 = 0.030204142;
            } else {
                var50 = -0.035574004;
            }
        } else {
            if (features[3] < -0.123) {
                var50 = -0.02615791;
            } else {
                var50 = 0.031102771;
            }
        }
    }
    double var51;
    if (features[2] < 21.95) {
        if (features[4] < 0.023039) {
            if (features[1] < 0.150823) {
                var51 = -0.0058535063;
            } else {
                var51 = 0.034266792;
            }
        } else {
            if (features[2] < 20.72) {
                var51 = -0.023634208;
            } else {
                var51 = 0.030261585;
            }
        }
    } else {
        if (features[4] < 0.020933) {
            if (features[5] < 0.015591) {
                var51 = -0.008341507;
            } else {
                var51 = -0.0356014;
            }
        } else {
            if (features[0] < 0.027068) {
                var51 = 0.027460469;
            } else {
                var51 = -0.028739167;
            }
        }
    }
    double var52;
    if (features[4] < 0.041695) {
        if (features[6] < 0.529138) {
            if (features[5] < 0.013537) {
                var52 = 0.039413072;
            } else {
                var52 = -0.018222036;
            }
        } else {
            if (features[3] < 2.5377) {
                var52 = -0.014660636;
            } else {
                var52 = 0.0088097835;
            }
        }
    } else {
        if (features[6] < 1.204913) {
            var52 = 0.056138318;
        } else {
            var52 = -0.011223423;
        }
    }
    double var53;
    if (features[3] < 0.6619) {
        if (features[4] < 0.00225) {
            if (features[2] < 29.04) {
                var53 = 0.034316387;
            } else {
                var53 = -0.022522967;
            }
        } else {
            if (features[2] < 29.82) {
                var53 = -0.036647122;
            } else {
                var53 = 0.012382454;
            }
        }
    } else {
        if (features[4] < 0.002672) {
            if (features[4] < -0.000344) {
                var53 = -0.00437403;
            } else {
                var53 = -0.058349874;
            }
        } else {
            if (features[4] < 0.007723) {
                var53 = 0.04834887;
            } else {
                var53 = 0.010183629;
            }
        }
    }
    double var54;
    if (features[4] < 0.010501) {
        if (features[2] < 21.08) {
            if (features[5] < 0.006765) {
                var54 = -0.015336062;
            } else {
                var54 = 0.036303934;
            }
        } else {
            if (features[5] < 0.015591) {
                var54 = -0.011165771;
            } else {
                var54 = -0.046848655;
            }
        }
    } else {
        if (features[4] < 0.017153) {
            if (features[6] < 1.244164) {
                var54 = 0.011550994;
            } else {
                var54 = 0.055055745;
            }
        } else {
            if (features[2] < 20.81) {
                var54 = -0.03848355;
            } else {
                var54 = 0.009979708;
            }
        }
    }
    double var55;
    if (features[3] < 2.5037) {
        if (features[0] < 0.01189) {
            if (features[4] < 0.016074) {
                var55 = 0.03350204;
            } else {
                var55 = -0.023081625;
            }
        } else {
            if (features[3] < -1.5542) {
                var55 = 0.010298295;
            } else {
                var55 = -0.029598022;
            }
        }
    } else {
        if (features[3] < 3.5902) {
            if (features[6] < 0.396562) {
                var55 = -0.017353322;
            } else {
                var55 = 0.029001469;
            }
        } else {
            if (features[3] < 4.3589) {
                var55 = -0.023818893;
            } else {
                var55 = 0.02876704;
            }
        }
    }
    double var56;
    if (features[1] < 0.384485) {
        if (features[1] < 0.31905) {
            if (features[1] < 0.150823) {
                var56 = -0.01919563;
            } else {
                var56 = 0.006803661;
            }
        } else {
            var56 = -0.040234845;
        }
    } else {
        if (features[5] < 0.030397) {
            var56 = 0.062444836;
        } else {
            var56 = -0.0155181885;
        }
    }
    double var57;
    if (features[2] < 17.71) {
        if (features[4] < -0.000775) {
            var57 = -0.009374004;
        } else {
            if (features[0] < 0.012537) {
                var57 = 0.012524261;
            } else {
                var57 = 0.055409398;
            }
        }
    } else {
        if (features[3] < -2.918) {
            if (features[6] < 1.137135) {
                var57 = -0.047700096;
            } else {
                var57 = -0.010171752;
            }
        } else {
            if (features[3] < -2.2761) {
                var57 = 0.039871503;
            } else {
                var57 = -0.0053518694;
            }
        }
    }
    double var58;
    if (features[3] < 2.6468) {
        if (features[3] < 1.9409) {
            if (features[3] < 1.4558) {
                var58 = -0.00576997;
            } else {
                var58 = 0.038169455;
            }
        } else {
            if (features[0] < 0.022297) {
                var58 = -0.03734296;
            } else {
                var58 = 0.030294854;
            }
        }
    } else {
        if (features[6] < 1.125862) {
            if (features[0] < 0.030516) {
                var58 = 0.04338504;
            } else {
                var58 = -0.012545506;
            }
        } else {
            if (features[4] < 0.03842) {
                var58 = -0.027879288;
            } else {
                var58 = 0.035927266;
            }
        }
    }
    double var59;
    if (features[5] < 0.005564) {
        if (features[6] < 0.496927) {
            var59 = -0.0010862182;
        } else {
            var59 = -0.046929687;
        }
    } else {
        if (features[0] < 0.009032) {
            if (features[3] < 1.7916) {
                var59 = 0.051325083;
            } else {
                var59 = 0.0034535665;
            }
        } else {
            if (features[3] < -1.2253) {
                var59 = -0.031908456;
            } else {
                var59 = 0.0048978934;
            }
        }
    }
    double var60;
    if (features[1] < 0.145358) {
        if (features[1] < 0.105091) {
            var60 = 0.03173708;
        } else {
            if (features[4] < 0.031621) {
                var60 = -0.03865571;
            } else {
                var60 = 0.0046209376;
            }
        }
    } else {
        if (features[1] < 0.173326) {
            if (features[3] < -0.8469) {
                var60 = 0.0007335296;
            } else {
                var60 = 0.04921803;
            }
        } else {
            if (features[3] < 3.161) {
                var60 = -0.007860662;
            } else {
                var60 = 0.017690212;
            }
        }
    }
    double var61;
    if (features[1] < 0.105091) {
        var61 = 0.044517517;
    } else {
        if (features[1] < 0.150823) {
            if (features[6] < 0.545508) {
                var61 = -0.0033298053;
            } else {
                var61 = -0.054356735;
            }
        } else {
            if (features[1] < 0.173326) {
                var61 = 0.04332566;
            } else {
                var61 = -0.00046131868;
            }
        }
    }
    double var62;
    if (features[3] < -1.1256) {
        if (features[0] < 0.009032) {
            var62 = 0.01959416;
        } else {
            if (features[3] < -1.7382) {
                var62 = -0.022075491;
            } else {
                var62 = -0.05379779;
            }
        }
    } else {
        if (features[5] < 0.006799) {
            if (features[1] < 0.153706) {
                var62 = 0.008076432;
            } else {
                var62 = -0.044889204;
            }
        } else {
            if (features[2] < 23.23) {
                var62 = 0.02576947;
            } else {
                var62 = -0.00069254043;
            }
        }
    }
    double var63;
    if (features[1] < 0.236536) {
        if (features[1] < 0.179853) {
            if (features[6] < 0.952014) {
                var63 = -0.0050999224;
            } else {
                var63 = 0.054188173;
            }
        } else {
            if (features[3] < 3.6948) {
                var63 = -0.02007025;
            } else {
                var63 = 0.02685295;
            }
        }
    } else {
        if (features[1] < 0.258244) {
            var63 = 0.054969855;
        } else {
            if (features[6] < 1.947073) {
                var63 = -0.005587689;
            } else {
                var63 = 0.037414126;
            }
        }
    }
    double var64;
    if (features[3] < 2.5037) {
        if (features[3] < 1.9409) {
            if (features[4] < 0.048624) {
                var64 = 0.00095026905;
            } else {
                var64 = -0.052587558;
            }
        } else {
            if (features[4] < 0.019337) {
                var64 = -0.054353602;
            } else {
                var64 = 0.002433513;
            }
        }
    } else {
        if (features[0] < 0.010643) {
            var64 = -0.038847137;
        } else {
            if (features[1] < 0.174389) {
                var64 = -0.012005975;
            } else {
                var64 = 0.030778116;
            }
        }
    }
    double var65;
    if (features[6] < 0.551433) {
        if (features[5] < 0.014896) {
            if (features[0] < 0.013235) {
                var65 = -0.000109708475;
            } else {
                var65 = 0.034187812;
            }
        } else {
            if (features[2] < 28.96) {
                var65 = 0.0033496253;
            } else {
                var65 = -0.037813157;
            }
        }
    } else {
        if (features[2] < 28.62) {
            if (features[2] < 18.2) {
                var65 = 0.011199629;
            } else {
                var65 = -0.02833145;
            }
        } else {
            if (features[2] < 31.75) {
                var65 = 0.044548977;
            } else {
                var65 = -0.008962831;
            }
        }
    }
    double var66;
    if (features[6] < 2.075328) {
        if (features[1] < 0.260367) {
            if (features[1] < 0.245359) {
                var66 = -0.0011573096;
            } else {
                var66 = 0.036872223;
            }
        } else {
            if (features[4] < 0.02874) {
                var66 = -0.002324255;
            } else {
                var66 = -0.04800488;
            }
        }
    } else {
        if (features[2] < 56.29) {
            var66 = 0.04933339;
        } else {
            var66 = 0.010671842;
        }
    }
    double var67;
    if (features[4] < -0.0019) {
        if (features[0] < 0.025186) {
            if (features[2] < 26.81) {
                var67 = -0.038979303;
            } else {
                var67 = -0.0023073244;
            }
        } else {
            var67 = 0.019181073;
        }
    } else {
        if (features[2] < 17.71) {
            if (features[4] < 0.016565) {
                var67 = 0.051708885;
            } else {
                var67 = 0.00073311286;
            }
        } else {
            if (features[2] < 18.66) {
                var67 = -0.0423935;
            } else {
                var67 = 0.0020036611;
            }
        }
    }
    double var68;
    if (features[6] < 0.649832) {
        if (features[1] < 0.174597) {
            if (features[1] < 0.14252) {
                var68 = 0.010957321;
            } else {
                var68 = 0.05381447;
            }
        } else {
            if (features[1] < 0.203572) {
                var68 = -0.03185709;
            } else {
                var68 = 0.015234346;
            }
        }
    } else {
        if (features[6] < 0.692197) {
            var68 = -0.05012874;
        } else {
            if (features[1] < 0.146961) {
                var68 = -0.03933717;
            } else {
                var68 = -0.0017579958;
            }
        }
    }
    double var69;
    if (features[3] < 4.3589) {
        if (features[3] < 3.8133) {
            if (features[3] < 3.3917) {
                var69 = -0.001307118;
            } else {
                var69 = 0.023417523;
            }
        } else {
            if (features[5] < 0.016621) {
                var69 = -0.05059458;
            } else {
                var69 = 0.00035721224;
            }
        }
    } else {
        if (features[6] < 1.442261) {
            var69 = 0.0476734;
        } else {
            var69 = -0.00884063;
        }
    }
    double var70;
    if (features[1] < 0.221014) {
        if (features[1] < 0.20686) {
            if (features[6] < 0.108291) {
                var70 = -0.043158226;
            } else {
                var70 = 0.004065468;
            }
        } else {
            if (features[4] < 0.02919) {
                var70 = -0.05321997;
            } else {
                var70 = -0.0009078785;
            }
        }
    } else {
        if (features[4] < -0.0019) {
            if (features[2] < 20.68) {
                var70 = 0.0023599297;
            } else {
                var70 = -0.041995563;
            }
        } else {
            if (features[2] < 45.6) {
                var70 = 0.02420738;
            } else {
                var70 = -0.011874995;
            }
        }
    }
    double var71;
    if (features[0] < 0.009032) {
        if (features[5] < 0.006346) {
            var71 = -0.007367146;
        } else {
            var71 = 0.041286316;
        }
    } else {
        if (features[0] < 0.010339) {
            var71 = -0.04692108;
        } else {
            if (features[0] < 0.01189) {
                var71 = 0.03242534;
            } else {
                var71 = -0.0035344418;
            }
        }
    }
    double var72;
    if (features[1] < 0.224159) {
        if (features[2] < 19.53) {
            if (features[0] < 0.012654) {
                var72 = -0.015916847;
            } else {
                var72 = 0.03253666;
            }
        } else {
            if (features[4] < 0.03354) {
                var72 = -0.018456822;
            } else {
                var72 = 0.015800111;
            }
        }
    } else {
        if (features[1] < 0.288392) {
            if (features[0] < 0.021404) {
                var72 = 0.007081073;
            } else {
                var72 = 0.06010155;
            }
        } else {
            if (features[4] < 0.032701) {
                var72 = 0.014234905;
            } else {
                var72 = -0.037879888;
            }
        }
    }
    double var73;
    if (features[3] < 3.161) {
        if (features[2] < 31.75) {
            if (features[2] < 28.6) {
                var73 = -0.004681788;
            } else {
                var73 = 0.04418887;
            }
        } else {
            if (features[4] < 0.019173) {
                var73 = -0.040058885;
            } else {
                var73 = 0.0073949257;
            }
        }
    } else {
        if (features[2] < 25.5) {
            if (features[3] < 3.5533) {
                var73 = 0.01854386;
            } else {
                var73 = -0.036609184;
            }
        } else {
            if (features[6] < 1.125862) {
                var73 = 0.037992533;
            } else {
                var73 = 0.0013458262;
            }
        }
    }
    double var74;
    if (features[5] < 0.015746) {
        if (features[2] < 23.07) {
            if (features[4] < 0.024497) {
                var74 = 0.03157155;
            } else {
                var74 = -0.018074905;
            }
        } else {
            if (features[2] < 24.18) {
                var74 = -0.052281737;
            } else {
                var74 = 0.0043008975;
            }
        }
    } else {
        if (features[2] < 28.9) {
            if (features[5] < 0.01724) {
                var74 = -0.05534145;
            } else {
                var74 = -0.014601203;
            }
        } else {
            if (features[4] < 0.041695) {
                var74 = -0.0014307396;
            } else {
                var74 = 0.047659684;
            }
        }
    }
    double var75;
    if (features[5] < 0.014191) {
        if (features[5] < 0.011768) {
            if (features[0] < 0.018875) {
                var75 = -0.008164679;
            } else {
                var75 = 0.017908474;
            }
        } else {
            if (features[0] < 0.012095) {
                var75 = 0.0043633333;
            } else {
                var75 = 0.04199548;
            }
        }
    } else {
        if (features[0] < 0.012052) {
            if (features[0] < 0.01086) {
                var75 = 0.0035844103;
            } else {
                var75 = 0.043701343;
            }
        } else {
            if (features[6] < 1.544142) {
                var75 = -0.022973713;
            } else {
                var75 = 0.004255535;
            }
        }
    }
    double var76;
    if (features[3] < 3.944) {
        if (features[3] < 3.672) {
            if (features[3] < 3.3917) {
                var76 = -0.00086449087;
            } else {
                var76 = 0.03130607;
            }
        } else {
            if (features[0] < 0.017066) {
                var76 = -0.004697358;
            } else {
                var76 = -0.04269431;
            }
        }
    } else {
        if (features[5] < 0.014635) {
            var76 = 0.00095241546;
        } else {
            var76 = 0.0526853;
        }
    }
    double var77;
    if (features[5] < 0.006802) {
        if (features[1] < 0.174615) {
            if (features[0] < 0.014679) {
                var77 = -0.017502023;
            } else {
                var77 = 0.030313004;
            }
        } else {
            var77 = -0.050452955;
        }
    } else {
        if (features[5] < 0.015746) {
            if (features[2] < 21.78) {
                var77 = 0.030242845;
            } else {
                var77 = 0.0039947196;
            }
        } else {
            if (features[2] < 28.9) {
                var77 = -0.027434263;
            } else {
                var77 = 0.012075803;
            }
        }
    }
    double var78;
    if (features[5] < 0.009407) {
        if (features[5] < 0.008662) {
            if (features[2] < 43.2) {
                var78 = 0.009115125;
            } else {
                var78 = -0.052395225;
            }
        } else {
            var78 = -0.048890833;
        }
    } else {
        if (features[0] < 0.01189) {
            if (features[4] < 0.005198) {
                var78 = -0.002820912;
            } else {
                var78 = 0.046062563;
            }
        } else {
            if (features[3] < 2.4022) {
                var78 = -0.010054868;
            } else {
                var78 = 0.021161968;
            }
        }
    }
    double var79;
    if (features[1] < 0.110579) {
        var79 = 0.04961177;
    } else {
        if (features[3] < -2.918) {
            var79 = -0.03794851;
        } else {
            if (features[3] < -2.2891) {
                var79 = 0.04254051;
            } else {
                var79 = -0.0025554923;
            }
        }
    }
    double var80;
    if (features[2] < 53.94) {
        if (features[2] < 28.62) {
            if (features[2] < 21.95) {
                var80 = 0.012517936;
            } else {
                var80 = -0.02527208;
            }
        } else {
            if (features[2] < 31.75) {
                var80 = 0.053648174;
            } else {
                var80 = 0.00032606992;
            }
        }
    } else {
        if (features[6] < 2.075328) {
            if (features[0] < 0.028247) {
                var80 = -0.057960063;
            } else {
                var80 = -0.0031866052;
            }
        } else {
            var80 = -0.00035699335;
        }
    }
    double var81;
    if (features[6] < 0.551433) {
        if (features[5] < 0.014896) {
            if (features[4] < -0.006374) {
                var81 = -0.010135754;
            } else {
                var81 = 0.036779016;
            }
        } else {
            if (features[2] < 29.3) {
                var81 = 0.017168395;
            } else {
                var81 = -0.03256923;
            }
        }
    } else {
        if (features[2] < 28.9) {
            if (features[2] < 23.23) {
                var81 = -0.0026294433;
            } else {
                var81 = -0.029640345;
            }
        } else {
            if (features[2] < 31.75) {
                var81 = 0.05522106;
            } else {
                var81 = -0.007480045;
            }
        }
    }
    double var82;
    if (features[6] < 2.075328) {
        if (features[6] < 1.66647) {
            if (features[5] < 0.006802) {
                var82 = -0.01869628;
            } else {
                var82 = 0.0023441194;
            }
        } else {
            var82 = -0.041232433;
        }
    } else {
        if (features[1] < 0.675251) {
            var82 = 0.052172005;
        } else {
            var82 = -0.026405573;
        }
    }
    double var83;
    if (features[2] < 28.9) {
        if (features[5] < 0.008231) {
            if (features[5] < 0.007314) {
                var83 = 0.00026495743;
            } else {
                var83 = 0.04454416;
            }
        } else {
            if (features[3] < 4.5687) {
                var83 = -0.016512912;
            } else {
                var83 = 0.036557492;
            }
        }
    } else {
        if (features[0] < 0.048898) {
            if (features[3] < -3.0902) {
                var83 = -0.019345602;
            } else {
                var83 = 0.019206412;
            }
        } else {
            var83 = -0.03732751;
        }
    }
    double var84;
    if (features[2] < 17.71) {
        if (features[2] < 15.84) {
            var84 = 0.007826258;
        } else {
            var84 = 0.04075051;
        }
    } else {
        if (features[1] < 0.176351) {
            if (features[3] < 3.7102) {
                var84 = 0.02354505;
            } else {
                var84 = -0.021039618;
            }
        } else {
            if (features[1] < 0.221014) {
                var84 = -0.027731797;
            } else {
                var84 = 0.0063039884;
            }
        }
    }
    double var85;
    if (features[3] < 0.5017) {
        if (features[4] < 0.00225) {
            if (features[0] < 0.01496) {
                var85 = 0.03589369;
            } else {
                var85 = -0.016860688;
            }
        } else {
            if (features[2] < 18.2) {
                var85 = 0.009403562;
            } else {
                var85 = -0.03373939;
            }
        }
    } else {
        if (features[4] < 0.002661) {
            if (features[5] < 0.011861) {
                var85 = -0.037846483;
            } else {
                var85 = 0.00265867;
            }
        } else {
            if (features[3] < 1.7916) {
                var85 = 0.044893783;
            } else {
                var85 = 0.007796327;
            }
        }
    }
    double var86;
    if (features[3] < -3.0902) {
        var86 = -0.03361179;
    } else {
        if (features[3] < -2.2761) {
            var86 = 0.04278062;
        } else {
            if (features[3] < 0.4414) {
                var86 = -0.019971948;
            } else {
                var86 = 0.0054338276;
            }
        }
    }
    double var87;
    if (features[1] < 0.146961) {
        if (features[1] < 0.105091) {
            var87 = 0.02651135;
        } else {
            if (features[2] < 45.95) {
                var87 = -0.039331224;
            } else {
                var87 = 0.019273661;
            }
        }
    } else {
        if (features[1] < 0.169463) {
            if (features[3] < -1.5542) {
                var87 = -0.009406707;
            } else {
                var87 = 0.046261277;
            }
        } else {
            if (features[1] < 0.384663) {
                var87 = -0.002774975;
            } else {
                var87 = 0.029319016;
            }
        }
    }
    double var88;
    if (features[4] < 0.044077) {
        if (features[4] < 0.030596) {
            if (features[1] < 0.276236) {
                var88 = -0.003176851;
            } else {
                var88 = 0.024709562;
            }
        } else {
            if (features[6] < 0.651915) {
                var88 = 0.008452566;
            } else {
                var88 = -0.037406664;
            }
        }
    } else {
        if (features[3] < 0.6486) {
            var88 = -0.00588733;
        } else {
            var88 = 0.041512575;
        }
    }
    double var89;
    if (features[5] < 0.015644) {
        if (features[5] < 0.009407) {
            if (features[6] < 0.506974) {
                var89 = 0.014535285;
            } else {
                var89 = -0.0174442;
            }
        } else {
            if (features[4] < 0.015568) {
                var89 = 0.03179762;
            } else {
                var89 = 0.0063513154;
            }
        }
    } else {
        if (features[4] < 0.010501) {
            if (features[5] < 0.01716) {
                var89 = -0.0584622;
            } else {
                var89 = -0.01641541;
            }
        } else {
            if (features[1] < 0.288392) {
                var89 = 0.015354077;
            } else {
                var89 = -0.01933345;
            }
        }
    }
    double var90;
    if (features[0] < 0.028045) {
        if (features[6] < 1.978757) {
            if (features[5] < 0.015644) {
                var90 = 0.0052753044;
            } else {
                var90 = -0.023278976;
            }
        } else {
            if (features[4] < 0.022325) {
                var90 = 0.045752615;
            } else {
                var90 = 0.008868328;
            }
        }
    } else {
        if (features[5] < 0.029825) {
            if (features[4] < 0.020594) {
                var90 = 0.003630596;
            } else {
                var90 = -0.059069064;
            }
        } else {
            var90 = 0.01962904;
        }
    }
    double var91;
    if (features[2] < 21.78) {
        if (features[6] < 0.952252) {
            if (features[4] < 0.018372) {
                var91 = 0.016981168;
            } else {
                var91 = -0.025289884;
            }
        } else {
            if (features[5] < 0.011497) {
                var91 = 0.0026957546;
            } else {
                var91 = 0.056160826;
            }
        }
    } else {
        if (features[2] < 26.82) {
            if (features[6] < 0.162664) {
                var91 = 0.024642669;
            } else {
                var91 = -0.027775735;
            }
        } else {
            if (features[2] < 31.75) {
                var91 = 0.02470564;
            } else {
                var91 = -0.0059622186;
            }
        }
    }
    double var92;
    if (features[1] < 0.150823) {
        if (features[1] < 0.105091) {
            var92 = 0.025400788;
        } else {
            if (features[2] < 45.95) {
                var92 = -0.037122928;
            } else {
                var92 = 0.011065139;
            }
        }
    } else {
        if (features[1] < 0.165956) {
            if (features[2] < 30.94) {
                var92 = 0.046565052;
            } else {
                var92 = 0.0085935285;
            }
        } else {
            if (features[2] < 17.71) {
                var92 = 0.03679375;
            } else {
                var92 = -0.000033377215;
            }
        }
    }
    double var93;
    if (features[1] < 0.384485) {
        if (features[3] < -3.0902) {
            var93 = -0.04441595;
        } else {
            if (features[2] < 45.6) {
                var93 = 0.0035717771;
            } else {
                var93 = -0.020615097;
            }
        }
    } else {
        if (features[3] < 0.4281) {
            var93 = 0.001922741;
        } else {
            var93 = 0.044335738;
        }
    }
    double var94;
    if (features[1] < 0.384663) {
        if (features[0] < 0.010195) {
            if (features[4] < 0.011723) {
                var94 = -0.0056586894;
            } else {
                var94 = -0.05659753;
            }
        } else {
            if (features[0] < 0.01189) {
                var94 = 0.03772105;
            } else {
                var94 = -0.00679715;
            }
        }
    } else {
        if (features[1] < 0.675251) {
            var94 = 0.04523058;
        } else {
            var94 = -0.02529164;
        }
    }
    double var95;
    if (features[3] < -2.2761) {
        if (features[3] < -2.918) {
            if (features[5] < 0.008561) {
                var95 = -0.02220698;
            } else {
                var95 = 0.011296436;
            }
        } else {
            var95 = 0.04014161;
        }
    } else {
        if (features[4] < -0.004323) {
            if (features[6] < 0.952252) {
                var95 = -0.044277493;
            } else {
                var95 = -0.0009534896;
            }
        } else {
            if (features[4] < 0.007723) {
                var95 = 0.014193207;
            } else {
                var95 = -0.008194489;
            }
        }
    }
    double var96;
    if (features[1] < 0.238412) {
        if (features[2] < 17.71) {
            if (features[0] < 0.012537) {
                var96 = -0.0030658722;
            } else {
                var96 = 0.038075514;
            }
        } else {
            if (features[2] < 25.54) {
                var96 = -0.03087302;
            } else {
                var96 = -0.0036692314;
            }
        }
    } else {
        if (features[1] < 0.257402) {
            if (features[1] < 0.245359) {
                var96 = 0.005958438;
            } else {
                var96 = 0.048220817;
            }
        } else {
            if (features[6] < 1.978757) {
                var96 = -0.009851077;
            } else {
                var96 = 0.027295057;
            }
        }
    }
    double var97;
    if (features[2] < 25.54) {
        if (features[2] < 24.9) {
            if (features[1] < 0.145017) {
                var97 = -0.038484655;
            } else {
                var97 = 0.002013873;
            }
        } else {
            var97 = -0.052935906;
        }
    } else {
        if (features[4] < 0.005167) {
            if (features[2] < 31.6) {
                var97 = 0.0074904854;
            } else {
                var97 = -0.029375216;
            }
        } else {
            if (features[1] < 0.176062) {
                var97 = 0.045990855;
            } else {
                var97 = 0.013902624;
            }
        }
    }
    double var98;
    if (features[6] < 2.103085) {
        if (features[6] < 1.667741) {
            if (features[5] < 0.03136) {
                var98 = -0.0058985953;
            } else {
                var98 = 0.032658424;
            }
        } else {
            if (features[1] < 0.363578) {
                var98 = -0.051717293;
            } else {
                var98 = -0.011230808;
            }
        }
    } else {
        if (features[1] < 0.463758) {
            var98 = 0.04415006;
        } else {
            var98 = -0.0051634745;
        }
    }
    double var99;
    if (features[5] < 0.005564) {
        if (features[2] < 23.22) {
            var99 = -0.045186058;
        } else {
            var99 = -0.009604825;
        }
    } else {
        if (features[2] < 26.82) {
            if (features[2] < 21.95) {
                var99 = 0.0064547854;
            } else {
                var99 = -0.01587479;
            }
        } else {
            if (features[2] < 31.75) {
                var99 = 0.04330204;
            } else {
                var99 = -0.0007148923;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
