//+------------------------------------------------------------------+
//|                                     M2_XGBoost_Oracle_GBPJPY.mqh |
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
    if (features[3] < 1.9396) {
        if (features[4] < -0.913166) {
            if (features[5] < 0.00386) {
                var0 = 0.033333335;
            } else {
                var0 = -0.036842104;
            }
        } else {
            if (features[3] < -1.1325) {
                var0 = 0.0;
            } else {
                var0 = 0.05555556;
            }
        }
    } else {
        if (features[5] < 0.007413) {
            var0 = 0.071428575;
        } else {
            var0 = -0.025;
        }
    }
    double var1;
    if (features[5] < 0.003559) {
        var1 = 0.043725464;
    } else {
        if (features[1] < 0.011936) {
            if (features[4] < -0.920391) {
                var1 = -0.040095672;
            } else {
                var1 = 0.009512154;
            }
        } else {
            var1 = 0.040467665;
        }
    }
    double var2;
    if (features[3] < 1.9396) {
        if (features[1] < 0.011416) {
            if (features[5] < 0.005792) {
                var2 = 0.00036534414;
            } else {
                var2 = -0.05567524;
            }
        } else {
            var2 = 0.033029526;
        }
    } else {
        if (features[5] < 0.006037) {
            var2 = 0.06867549;
        } else {
            var2 = 0.00049264607;
        }
    }
    double var3;
    if (features[1] < 0.007186) {
        if (features[4] < -0.925224) {
            if (features[4] < -0.948748) {
                var3 = 0.027234113;
            } else {
                var3 = -0.03156556;
            }
        } else {
            var3 = 0.06421191;
        }
    } else {
        if (features[5] < 0.006125) {
            if (features[3] < -0.0298) {
                var3 = -0.02168527;
            } else {
                var3 = 0.03179687;
            }
        } else {
            if (features[2] < 23.5) {
                var3 = -0.009501883;
            } else {
                var3 = -0.053667586;
            }
        }
    }
    double var4;
    if (features[5] < 0.00545) {
        if (features[3] < 1.113) {
            if (features[3] < -2.8545) {
                var4 = 0.033591162;
            } else {
                var4 = -0.007884117;
            }
        } else {
            var4 = 0.065871015;
        }
    } else {
        if (features[3] < -2.7338) {
            var4 = -0.05041138;
        } else {
            if (features[5] < 0.013539) {
                var4 = -0.018368501;
            } else {
                var4 = 0.042614438;
            }
        }
    }
    double var5;
    if (features[6] < 0.021915) {
        if (features[0] < 0.6512) {
            if (features[2] < 23.17) {
                var5 = 0.0065512024;
            } else {
                var5 = 0.061552037;
            }
        } else {
            if (features[3] < -1.8731) {
                var5 = -0.0521692;
            } else {
                var5 = 0.026363075;
            }
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[2] < 23.5) {
                var5 = -0.0010222377;
            } else {
                var5 = -0.04224879;
            }
        } else {
            var5 = 0.021767255;
        }
    }
    double var6;
    if (features[6] < 0.022392) {
        if (features[6] < 0.016954) {
            if (features[3] < 3.2872) {
                var6 = -0.015265799;
            } else {
                var6 = 0.050561216;
            }
        } else {
            var6 = 0.05296844;
        }
    } else {
        if (features[2] < 23.47) {
            var6 = 0.0072265305;
        } else {
            if (features[0] < 0.416178) {
                var6 = -0.0553849;
            } else {
                var6 = -0.005853688;
            }
        }
    }
    double var7;
    if (features[5] < 0.003722) {
        var7 = 0.059748422;
    } else {
        if (features[4] < -0.91492) {
            if (features[4] < -0.948949) {
                var7 = 0.001092804;
            } else {
                var7 = -0.039609443;
            }
        } else {
            if (features[0] < 0.297059) {
                var7 = -0.018984444;
            } else {
                var7 = 0.057964798;
            }
        }
    }
    double var8;
    if (features[5] < 0.00545) {
        if (features[3] < 0.891) {
            if (features[0] < 0.271598) {
                var8 = -0.032867543;
            } else {
                var8 = 0.01629696;
            }
        } else {
            var8 = 0.06350435;
        }
    } else {
        if (features[4] < -0.950705) {
            var8 = 0.011026359;
        } else {
            if (features[4] < -0.913166) {
                var8 = -0.06307893;
            } else {
                var8 = -0.0067796684;
            }
        }
    }
    double var9;
    if (features[3] < 3.2872) {
        if (features[2] < 24.3) {
            if (features[3] < -0.3145) {
                var9 = 0.040446773;
            } else {
                var9 = -0.0070879995;
            }
        } else {
            if (features[4] < -0.926117) {
                var9 = -0.049482662;
            } else {
                var9 = -0.006866246;
            }
        }
    } else {
        var9 = 0.04663595;
    }
    double var10;
    if (features[5] < 0.003683) {
        var10 = 0.04552882;
    } else {
        if (features[3] < -0.4412) {
            if (features[5] < 0.008411) {
                var10 = -0.046768356;
            } else {
                var10 = 0.010115359;
            }
        } else {
            if (features[6] < 0.035843) {
                var10 = 0.027028963;
            } else {
                var10 = -0.019929862;
            }
        }
    }
    double var11;
    if (features[5] < 0.006125) {
        if (features[3] < -0.9174) {
            var11 = -0.028986413;
        } else {
            if (features[5] < 0.004266) {
                var11 = 0.0120612895;
            } else {
                var11 = 0.06335404;
            }
        }
    } else {
        if (features[5] < 0.008411) {
            if (features[0] < 0.699802) {
                var11 = -0.056620944;
            } else {
                var11 = -0.005641888;
            }
        } else {
            if (features[1] < 0.007874) {
                var11 = 0.036943328;
            } else {
                var11 = -0.031175971;
            }
        }
    }
    double var12;
    if (features[3] < -0.8758) {
        if (features[1] < 0.011235) {
            if (features[1] < 0.007874) {
                var12 = -0.0024532883;
            } else {
                var12 = -0.040857594;
            }
        } else {
            var12 = 0.015776897;
        }
    } else {
        if (features[2] < 21.63) {
            var12 = -0.010545334;
        } else {
            if (features[2] < 38.84) {
                var12 = 0.043597717;
            } else {
                var12 = -0.012013414;
            }
        }
    }
    double var13;
    if (features[6] < 0.022392) {
        if (features[0] < 0.6512) {
            var13 = 0.046708953;
        } else {
            var13 = -0.02403199;
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[2] < 30.95) {
                var13 = -0.0011880117;
            } else {
                var13 = -0.042238936;
            }
        } else {
            var13 = 0.02523495;
        }
    }
    double var14;
    if (features[1] < 0.007186) {
        if (features[0] < 0.476418) {
            var14 = 0.048269138;
        } else {
            if (features[4] < -0.950705) {
                var14 = 0.014338258;
            } else {
                var14 = -0.034518827;
            }
        }
    } else {
        if (features[1] < 0.011936) {
            if (features[2] < 23.5) {
                var14 = 0.00052499835;
            } else {
                var14 = -0.04840937;
            }
        } else {
            var14 = 0.029758615;
        }
    }
    double var15;
    if (features[5] < 0.003683) {
        var15 = 0.053578634;
    } else {
        if (features[3] < 2.367) {
            if (features[4] < -0.91492) {
                var15 = -0.02636536;
            } else {
                var15 = 0.017411293;
            }
        } else {
            if (features[2] < 27.69) {
                var15 = -0.008984939;
            } else {
                var15 = 0.0493309;
            }
        }
    }
    double var16;
    if (features[5] < 0.006125) {
        if (features[3] < 1.113) {
            if (features[5] < 0.004266) {
                var16 = -0.022633288;
            } else {
                var16 = 0.012406538;
            }
        } else {
            var16 = 0.05855853;
        }
    } else {
        if (features[0] < 0.333041) {
            if (features[0] < 0.222316) {
                var16 = -0.010057404;
            } else {
                var16 = -0.05481979;
            }
        } else {
            if (features[5] < 0.008411) {
                var16 = -0.02872831;
            } else {
                var16 = 0.03179587;
            }
        }
    }
    double var17;
    if (features[6] < 0.022392) {
        if (features[0] < 0.687278) {
            if (features[3] < 0.9387) {
                var17 = 0.04831656;
            } else {
                var17 = 0.0132483905;
            }
        } else {
            var17 = -0.012680818;
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[6] < 0.046892) {
                var17 = -0.016222132;
            } else {
                var17 = -0.056925017;
            }
        } else {
            var17 = 0.036902677;
        }
    }
    double var18;
    if (features[6] < 0.010129) {
        var18 = 0.04146711;
    } else {
        if (features[4] < -0.927063) {
            if (features[5] < 0.009694) {
                var18 = -0.042382404;
            } else {
                var18 = -0.0060143746;
            }
        } else {
            if (features[6] < 0.021443) {
                var18 = 0.05224783;
            } else {
                var18 = -0.01638181;
            }
        }
    }
    double var19;
    if (features[5] < 0.003722) {
        var19 = 0.05368188;
    } else {
        if (features[1] < 0.006337) {
            if (features[5] < 0.006886) {
                var19 = -0.008019498;
            } else {
                var19 = 0.046068113;
            }
        } else {
            if (features[1] < 0.011936) {
                var19 = -0.03449836;
            } else {
                var19 = 0.0341284;
            }
        }
    }
    double var20;
    if (features[6] < 0.022392) {
        if (features[6] < 0.01544) {
            if (features[5] < 0.00545) {
                var20 = 0.021220433;
            } else {
                var20 = -0.0316602;
            }
        } else {
            var20 = 0.05708574;
        }
    } else {
        if (features[6] < 0.068589) {
            if (features[1] < 0.007874) {
                var20 = 0.005513177;
            } else {
                var20 = -0.04442777;
            }
        } else {
            var20 = 0.01778305;
        }
    }
    double var21;
    if (features[1] < 0.011936) {
        if (features[1] < 0.008029) {
            if (features[1] < 0.002622) {
                var21 = -0.03517319;
            } else {
                var21 = 0.026297167;
            }
        } else {
            if (features[3] < -0.4412) {
                var21 = -0.056300163;
            } else {
                var21 = -0.0030203925;
            }
        }
    } else {
        var21 = 0.039206948;
    }
    double var22;
    if (features[5] < 0.00545) {
        if (features[6] < 0.010129) {
            var22 = 0.054052856;
        } else {
            if (features[2] < 25.29) {
                var22 = 0.02774023;
            } else {
                var22 = -0.0020388009;
            }
        }
    } else {
        if (features[5] < 0.008411) {
            if (features[4] < -0.925042) {
                var22 = -0.04299034;
            } else {
                var22 = -0.0022518698;
            }
        } else {
            if (features[0] < 0.314328) {
                var22 = -0.029871915;
            } else {
                var22 = 0.031746287;
            }
        }
    }
    double var23;
    if (features[5] < 0.00545) {
        if (features[3] < 1.113) {
            if (features[3] < -2.8545) {
                var23 = 0.025448;
            } else {
                var23 = -0.017548181;
            }
        } else {
            var23 = 0.051523115;
        }
    } else {
        if (features[5] < 0.009694) {
            if (features[4] < -0.925042) {
                var23 = -0.049483698;
            } else {
                var23 = -0.0065546157;
            }
        } else {
            if (features[5] < 0.014026) {
                var23 = 0.028218785;
            } else {
                var23 = -0.014222096;
            }
        }
    }
    double var24;
    if (features[1] < 0.007402) {
        if (features[0] < 0.476418) {
            var24 = 0.04386781;
        } else {
            if (features[4] < -0.950705) {
                var24 = 0.023152433;
            } else {
                var24 = -0.018898038;
            }
        }
    } else {
        if (features[1] < 0.010185) {
            if (features[3] < -0.6497) {
                var24 = -0.04837886;
            } else {
                var24 = -0.001497656;
            }
        } else {
            if (features[4] < -0.92532) {
                var24 = -0.0044707423;
            } else {
                var24 = 0.029959768;
            }
        }
    }
    double var25;
    if (features[6] < 0.010129) {
        if (features[2] < 35.83) {
            var25 = 0.04363535;
        } else {
            var25 = 0.0074114837;
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[6] < 0.044648) {
                var25 = -0.0018746222;
            } else {
                var25 = -0.05243084;
            }
        } else {
            var25 = 0.022664333;
        }
    }
    double var26;
    if (features[6] < 0.022392) {
        if (features[0] < 0.476418) {
            if (features[1] < 0.005939) {
                var26 = 0.055732936;
            } else {
                var26 = 0.010017005;
            }
        } else {
            if (features[3] < 1.113) {
                var26 = -0.04171125;
            } else {
                var26 = 0.029183438;
            }
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[1] < 0.008856) {
                var26 = -0.0075961235;
            } else {
                var26 = -0.05558039;
            }
        } else {
            var26 = 0.021977443;
        }
    }
    double var27;
    if (features[4] < -0.927752) {
        if (features[4] < -0.940584) {
            if (features[0] < 0.476418) {
                var27 = 0.03647551;
            } else {
                var27 = -0.00672622;
            }
        } else {
            var27 = -0.05101605;
        }
    } else {
        if (features[1] < 0.007402) {
            var27 = 0.053579934;
        } else {
            if (features[4] < -0.924942) {
                var27 = 0.04526123;
            } else {
                var27 = -0.016736843;
            }
        }
    }
    double var28;
    if (features[3] < 1.9396) {
        if (features[2] < 25.66) {
            if (features[5] < 0.00379) {
                var28 = -0.022459896;
            } else {
                var28 = 0.030886067;
            }
        } else {
            if (features[6] < 0.040215) {
                var28 = -0.039216053;
            } else {
                var28 = -0.0037684017;
            }
        }
    } else {
        if (features[5] < 0.006037) {
            var28 = 0.0476867;
        } else {
            var28 = -0.005466376;
        }
    }
    double var29;
    if (features[6] < 0.022392) {
        if (features[0] < 0.687278) {
            if (features[2] < 23.17) {
                var29 = 0.0015241362;
            } else {
                var29 = 0.041113134;
            }
        } else {
            var29 = -0.016357554;
        }
    } else {
        if (features[2] < 25.66) {
            if (features[2] < 20.86) {
                var29 = -0.018685654;
            } else {
                var29 = 0.03279781;
            }
        } else {
            if (features[4] < -0.925351) {
                var29 = 0.00011504422;
            } else {
                var29 = -0.047457755;
            }
        }
    }
    double var30;
    if (features[3] < 2.367) {
        if (features[2] < 30.95) {
            if (features[0] < 0.343298) {
                var30 = 0.02777191;
            } else {
                var30 = -0.0040769773;
            }
        } else {
            if (features[1] < 0.010185) {
                var30 = -0.037964188;
            } else {
                var30 = 0.019158432;
            }
        }
    } else {
        if (features[2] < 27.69) {
            var30 = 0.0076964754;
        } else {
            var30 = 0.047781106;
        }
    }
    double var31;
    if (features[4] < -0.927063) {
        if (features[4] < -0.949358) {
            if (features[0] < 0.650368) {
                var31 = -0.00998141;
            } else {
                var31 = 0.022770267;
            }
        } else {
            var31 = -0.0498896;
        }
    } else {
        if (features[5] < 0.011708) {
            if (features[4] < -0.911646) {
                var31 = 0.039455015;
            } else {
                var31 = -0.014940172;
            }
        } else {
            var31 = -0.02301124;
        }
    }
    double var32;
    if (features[1] < 0.011936) {
        if (features[6] < 0.040969) {
            if (features[4] < -0.932352) {
                var32 = -0.01016198;
            } else {
                var32 = 0.028486928;
            }
        } else {
            if (features[0] < 0.306351) {
                var32 = -0.05201697;
            } else {
                var32 = -0.003648514;
            }
        }
    } else {
        var32 = 0.03726917;
    }
    double var33;
    if (features[6] < 0.022392) {
        if (features[3] < -0.0298) {
            if (features[0] < 0.558485) {
                var33 = 0.027904138;
            } else {
                var33 = -0.03943768;
            }
        } else {
            var33 = 0.0505638;
        }
    } else {
        if (features[6] < 0.040215) {
            if (features[3] < -0.8758) {
                var33 = -0.045233324;
            } else {
                var33 = -0.008894845;
            }
        } else {
            if (features[0] < 0.177517) {
                var33 = -0.029273126;
            } else {
                var33 = 0.021434207;
            }
        }
    }
    double var34;
    if (features[5] < 0.005672) {
        if (features[3] < -0.9174) {
            var34 = -0.0020974067;
        } else {
            if (features[4] < -0.948805) {
                var34 = 0.0045344164;
            } else {
                var34 = 0.051403143;
            }
        }
    } else {
        if (features[1] < 0.007186) {
            if (features[5] < 0.007491) {
                var34 = -0.009738227;
            } else {
                var34 = 0.036999747;
            }
        } else {
            if (features[6] < 0.071677) {
                var34 = -0.038847696;
            } else {
                var34 = 0.029669628;
            }
        }
    }
    double var35;
    if (features[3] < -2.9024) {
        if (features[1] < 0.007874) {
            var35 = 0.00017075684;
        } else {
            var35 = -0.042711556;
        }
    } else {
        if (features[6] < 0.022392) {
            if (features[3] < 0.6875) {
                var35 = 0.016905125;
            } else {
                var35 = 0.053320087;
            }
        } else {
            if (features[6] < 0.034356) {
                var35 = -0.04514165;
            } else {
                var35 = 0.023436835;
            }
        }
    }
    double var36;
    if (features[4] < -0.927752) {
        if (features[6] < 0.010129) {
            var36 = 0.026493264;
        } else {
            if (features[1] < 0.003224) {
                var36 = -0.008683547;
            } else {
                var36 = -0.04497808;
            }
        }
    } else {
        if (features[1] < 0.008029) {
            if (features[2] < 36.66) {
                var36 = 0.052394863;
            } else {
                var36 = 0.015642973;
            }
        } else {
            if (features[1] < 0.011936) {
                var36 = -0.026870966;
            } else {
                var36 = 0.022957582;
            }
        }
    }
    double var37;
    if (features[1] < 0.007186) {
        if (features[0] < 0.476418) {
            if (features[1] < 0.005653) {
                var37 = 0.052758753;
            } else {
                var37 = 0.015960522;
            }
        } else {
            if (features[3] < 1.113) {
                var37 = -0.024136223;
            } else {
                var37 = 0.028587151;
            }
        }
    } else {
        if (features[2] < 20.86) {
            var37 = -0.050485004;
        } else {
            if (features[4] < -0.924942) {
                var37 = 0.02647462;
            } else {
                var37 = -0.011033059;
            }
        }
    }
    double var38;
    if (features[1] < 0.007874) {
        if (features[0] < 0.476418) {
            var38 = 0.04711929;
        } else {
            if (features[1] < 0.003224) {
                var38 = 0.012660115;
            } else {
                var38 = -0.031154558;
            }
        }
    } else {
        if (features[4] < -0.92532) {
            if (features[6] < 0.052679) {
                var38 = -0.046196185;
            } else {
                var38 = -0.0048582046;
            }
        } else {
            if (features[1] < 0.011416) {
                var38 = -0.005860222;
            } else {
                var38 = 0.029326051;
            }
        }
    }
    double var39;
    if (features[6] < 0.022392) {
        if (features[1] < 0.003595) {
            if (features[1] < 0.002349) {
                var39 = 0.023646291;
            } else {
                var39 = -0.031486765;
            }
        } else {
            if (features[6] < 0.008824) {
                var39 = 0.007826783;
            } else {
                var39 = 0.043806504;
            }
        }
    } else {
        if (features[1] < 0.011936) {
            if (features[6] < 0.046892) {
                var39 = -0.011039649;
            } else {
                var39 = -0.04976117;
            }
        } else {
            var39 = 0.0292472;
        }
    }
    double var40;
    if (features[5] < 0.00545) {
        if (features[5] < 0.004266) {
            if (features[3] < 1.113) {
                var40 = -0.015865533;
            } else {
                var40 = 0.03265207;
            }
        } else {
            var40 = 0.039945718;
        }
    } else {
        if (features[1] < 0.011936) {
            if (features[1] < 0.008856) {
                var40 = -0.005257656;
            } else {
                var40 = -0.045684557;
            }
        } else {
            var40 = 0.020759044;
        }
    }
    double var41;
    if (features[3] < 2.367) {
        if (features[4] < -0.91492) {
            if (features[5] < 0.006842) {
                var41 = -0.044211876;
            } else {
                var41 = -0.00963047;
            }
        } else {
            if (features[3] < -1.2997) {
                var41 = -0.013960621;
            } else {
                var41 = 0.027889615;
            }
        }
    } else {
        var41 = 0.03175646;
    }
    double var42;
    if (features[5] < 0.006125) {
        if (features[0] < 0.143755) {
            var42 = -0.011532645;
        } else {
            if (features[0] < 0.476418) {
                var42 = 0.04331123;
            } else {
                var42 = 0.0004185245;
            }
        }
    } else {
        if (features[5] < 0.006842) {
            var42 = -0.042593088;
        } else {
            if (features[0] < 0.333041) {
                var42 = -0.020429172;
            } else {
                var42 = 0.020976694;
            }
        }
    }
    double var43;
    if (features[4] < -0.920391) {
        if (features[5] < 0.00386) {
            var43 = 0.03157368;
        } else {
            if (features[2] < 23.5) {
                var43 = 0.010938331;
            } else {
                var43 = -0.029329;
            }
        }
    } else {
        if (features[0] < 0.143755) {
            var43 = -0.0015730776;
        } else {
            if (features[2] < 24.33) {
                var43 = 0.008827674;
            } else {
                var43 = 0.051703777;
            }
        }
    }
    double var44;
    if (features[3] < -0.4412) {
        if (features[1] < 0.011416) {
            if (features[1] < 0.006509) {
                var44 = 0.0042607053;
            } else {
                var44 = -0.04804283;
            }
        } else {
            var44 = 0.024304273;
        }
    } else {
        if (features[5] < 0.006125) {
            if (features[1] < 0.00361) {
                var44 = -0.006822175;
            } else {
                var44 = 0.055190094;
            }
        } else {
            if (features[0] < 0.375243) {
                var44 = -0.034728043;
            } else {
                var44 = 0.027361447;
            }
        }
    }
    double var45;
    if (features[3] < 1.9396) {
        if (features[3] < 0.4199) {
            if (features[3] < -2.9024) {
                var45 = -0.016569054;
            } else {
                var45 = 0.028211726;
            }
        } else {
            var45 = -0.04302347;
        }
    } else {
        if (features[2] < 27.69) {
            var45 = 0.014295078;
        } else {
            var45 = 0.047503527;
        }
    }
    double var46;
    if (features[0] < 0.375619) {
        if (features[1] < 0.006337) {
            var46 = 0.014954395;
        } else {
            if (features[3] < -0.0298) {
                var46 = -0.033233363;
            } else {
                var46 = 0.0043943366;
            }
        }
    } else {
        if (features[0] < 0.647427) {
            if (features[1] < 0.008029) {
                var46 = 0.052054938;
            } else {
                var46 = -0.00038656293;
            }
        } else {
            if (features[3] < 0.6875) {
                var46 = -0.027526617;
            } else {
                var46 = 0.022671094;
            }
        }
    }
    double var47;
    if (features[6] < 0.046892) {
        if (features[0] < 0.476418) {
            if (features[2] < 19.53) {
                var47 = -0.0134855155;
            } else {
                var47 = 0.041356664;
            }
        } else {
            if (features[1] < 0.004212) {
                var47 = 0.014785759;
            } else {
                var47 = -0.033189457;
            }
        }
    } else {
        if (features[1] < 0.010685) {
            var47 = -0.045456782;
        } else {
            var47 = 0.01140141;
        }
    }
    double var48;
    if (features[3] < 1.9396) {
        if (features[2] < 25.66) {
            if (features[3] < -0.4203) {
                var48 = 0.03125918;
            } else {
                var48 = -0.01264401;
            }
        } else {
            if (features[3] < -3.6928) {
                var48 = -0.0028482915;
            } else {
                var48 = -0.041551575;
            }
        }
    } else {
        if (features[2] < 27.69) {
            var48 = -0.0028921228;
        } else {
            var48 = 0.04237504;
        }
    }
    double var49;
    if (features[6] < 0.010129) {
        var49 = 0.041489366;
    } else {
        if (features[4] < -0.927063) {
            if (features[5] < 0.011192) {
                var49 = -0.036442265;
            } else {
                var49 = 0.008860833;
            }
        } else {
            if (features[6] < 0.022392) {
                var49 = 0.04173358;
            } else {
                var49 = -0.010380385;
            }
        }
    }
    double var50;
    if (features[6] < 0.022392) {
        if (features[5] < 0.00545) {
            var50 = 0.035182428;
        } else {
            if (features[5] < 0.006886) {
                var50 = -0.043979123;
            } else {
                var50 = 0.03872792;
            }
        }
    } else {
        if (features[6] < 0.071677) {
            if (features[5] < 0.006125) {
                var50 = 0.010141241;
            } else {
                var50 = -0.029180959;
            }
        } else {
            var50 = 0.01882623;
        }
    }
    double var51;
    if (features[0] < 0.375619) {
        if (features[4] < -0.927063) {
            var51 = -0.036179643;
        } else {
            if (features[2] < 24.65) {
                var51 = 0.016013807;
            } else {
                var51 = -0.016621687;
            }
        }
    } else {
        if (features[0] < 0.502054) {
            var51 = 0.039950162;
        } else {
            if (features[0] < 0.565474) {
                var51 = -0.024474483;
            } else {
                var51 = 0.0015509232;
            }
        }
    }
    double var52;
    if (features[3] < 2.367) {
        if (features[0] < 0.502054) {
            if (features[0] < 0.375619) {
                var52 = -0.008941895;
            } else {
                var52 = 0.037108798;
            }
        } else {
            if (features[5] < 0.008411) {
                var52 = -0.04150469;
            } else {
                var52 = -0.006454874;
            }
        }
    } else {
        if (features[5] < 0.006037) {
            var52 = 0.03356212;
        } else {
            var52 = 0.0056318487;
        }
    }
    double var53;
    if (features[4] < -0.911646) {
        if (features[3] < 2.367) {
            if (features[2] < 25.66) {
                var53 = 0.019792505;
            } else {
                var53 = -0.014897923;
            }
        } else {
            var53 = 0.034962397;
        }
    } else {
        var53 = -0.03313574;
    }
    double var54;
    if (features[5] < 0.006125) {
        if (features[4] < -0.922291) {
            if (features[5] < 0.004365) {
                var54 = 0.0190057;
            } else {
                var54 = -0.017703906;
            }
        } else {
            if (features[0] < 0.143755) {
                var54 = 0.0056892815;
            } else {
                var54 = 0.045528308;
            }
        }
    } else {
        if (features[6] < 0.01544) {
            var54 = -0.03893231;
        } else {
            if (features[6] < 0.021915) {
                var54 = 0.025044134;
            } else {
                var54 = -0.014043435;
            }
        }
    }
    double var55;
    if (features[6] < 0.042936) {
        if (features[4] < -0.932352) {
            if (features[3] < 2.367) {
                var55 = -0.018768473;
            } else {
                var55 = 0.024969278;
            }
        } else {
            if (features[0] < 0.195024) {
                var55 = 0.01237972;
            } else {
                var55 = 0.054863054;
            }
        }
    } else {
        if (features[6] < 0.071677) {
            var55 = -0.03439238;
        } else {
            var55 = 0.018670926;
        }
    }
    double var56;
    if (features[3] < 1.8869) {
        if (features[3] < 0.4199) {
            if (features[0] < 0.647427) {
                var56 = 0.017229225;
            } else {
                var56 = -0.028663475;
            }
        } else {
            var56 = -0.041460186;
        }
    } else {
        if (features[1] < 0.007186) {
            var56 = 0.038684834;
        } else {
            var56 = 0.00850002;
        }
    }
    double var57;
    if (features[3] < 2.367) {
        if (features[0] < 0.502054) {
            if (features[0] < 0.375619) {
                var57 = -0.007643635;
            } else {
                var57 = 0.035546448;
            }
        } else {
            var57 = -0.03480057;
        }
    } else {
        if (features[2] < 27.69) {
            var57 = 0.00805387;
        } else {
            var57 = 0.036710333;
        }
    }
    double var58;
    if (features[3] < 2.367) {
        if (features[0] < 0.6512) {
            if (features[0] < 0.375619) {
                var58 = -0.011747834;
            } else {
                var58 = 0.031171734;
            }
        } else {
            var58 = -0.03623501;
        }
    } else {
        var58 = 0.037925623;
    }
    double var59;
    if (features[0] < 0.687278) {
        if (features[0] < 0.195024) {
            if (features[1] < 0.009896) {
                var59 = -0.03088822;
            } else {
                var59 = 0.003886503;
            }
        } else {
            if (features[5] < 0.005792) {
                var59 = 0.03146026;
            } else {
                var59 = 0.00084334187;
            }
        }
    } else {
        var59 = -0.034616202;
    }
    double var60;
    if (features[3] < 2.367) {
        if (features[4] < -0.91492) {
            if (features[5] < 0.00386) {
                var60 = 0.018805906;
            } else {
                var60 = -0.032042928;
            }
        } else {
            if (features[3] < -1.5401) {
                var60 = -0.01724077;
            } else {
                var60 = 0.03097695;
            }
        }
    } else {
        var60 = 0.019099224;
    }
    double var61;
    if (features[3] < -1.5401) {
        if (features[4] < -0.927752) {
            var61 = -0.037027296;
        } else {
            if (features[1] < 0.008023) {
                var61 = 0.018907255;
            } else {
                var61 = -0.024651049;
            }
        }
    } else {
        if (features[2] < 28.5) {
            if (features[2] < 25.29) {
                var61 = 0.015659964;
            } else {
                var61 = -0.040817004;
            }
        } else {
            if (features[6] < 0.027441) {
                var61 = 0.038583368;
            } else {
                var61 = 0.0006791265;
            }
        }
    }
    double var62;
    if (features[3] < -0.4412) {
        if (features[1] < 0.010685) {
            if (features[1] < 0.006509) {
                var62 = -0.0018389616;
            } else {
                var62 = -0.04822784;
            }
        } else {
            var62 = 0.010244421;
        }
    } else {
        if (features[5] < 0.006125) {
            if (features[0] < 0.180657) {
                var62 = 0.0011901156;
            } else {
                var62 = 0.04892048;
            }
        } else {
            if (features[2] < 24.3) {
                var62 = 0.012158455;
            } else {
                var62 = -0.03377391;
            }
        }
    }
    double var63;
    if (features[0] < 0.138139) {
        var63 = -0.027543524;
    } else {
        if (features[4] < -0.927752) {
            if (features[4] < -0.940584) {
                var63 = 0.0066449917;
            } else {
                var63 = -0.04054931;
            }
        } else {
            if (features[3] < -2.9266) {
                var63 = -0.01220392;
            } else {
                var63 = 0.035429474;
            }
        }
    }
    double var64;
    if (features[2] < 25.66) {
        if (features[2] < 21.63) {
            var64 = -0.012252392;
        } else {
            var64 = 0.037660297;
        }
    } else {
        if (features[0] < 0.314328) {
            var64 = -0.04152668;
        } else {
            if (features[4] < -0.925678) {
                var64 = -0.011363744;
            } else {
                var64 = 0.034623824;
            }
        }
    }
    double var65;
    if (features[2] < 25.29) {
        if (features[3] < -0.3145) {
            var65 = 0.04699989;
        } else {
            if (features[3] < 1.113) {
                var65 = -0.016165374;
            } else {
                var65 = 0.02444684;
            }
        }
    } else {
        if (features[0] < 0.306351) {
            var65 = -0.0363744;
        } else {
            if (features[0] < 0.647427) {
                var65 = 0.02303216;
            } else {
                var65 = -0.012556112;
            }
        }
    }
    double var66;
    if (features[6] < 0.010129) {
        var66 = 0.027386505;
    } else {
        if (features[1] < 0.011936) {
            if (features[2] < 38.28) {
                var66 = -0.026950374;
            } else {
                var66 = 0.006969876;
            }
        } else {
            var66 = 0.020522084;
        }
    }
    double var67;
    if (features[5] < 0.006125) {
        if (features[0] < 0.476418) {
            if (features[2] < 20.18) {
                var67 = -0.012620273;
            } else {
                var67 = 0.028962756;
            }
        } else {
            var67 = -0.01196101;
        }
    } else {
        if (features[2] < 41.33) {
            if (features[5] < 0.009694) {
                var67 = -0.042336673;
            } else {
                var67 = 0.0014678696;
            }
        } else {
            var67 = 0.020288555;
        }
    }
    double var68;
    if (features[2] < 24.3) {
        if (features[3] < 0.4199) {
            var68 = 0.044629153;
        } else {
            var68 = -0.01330735;
        }
    } else {
        if (features[2] < 35.79) {
            if (features[6] < 0.042922) {
                var68 = -0.04049432;
            } else {
                var68 = -0.004662265;
            }
        } else {
            if (features[3] < 1.8869) {
                var68 = 0.003964297;
            } else {
                var68 = 0.03852536;
            }
        }
    }
    double var69;
    if (features[3] < 2.367) {
        if (features[3] < 0.4104) {
            if (features[3] < -0.4412) {
                var69 = -0.0107836705;
            } else {
                var69 = 0.031019628;
            }
        } else {
            if (features[3] < 1.4489) {
                var69 = -0.043110896;
            } else {
                var69 = -0.013395089;
            }
        }
    } else {
        var69 = 0.023162859;
    }
    double var70;
    if (features[3] < 0.4199) {
        if (features[4] < -0.926117) {
            if (features[2] < 27.27) {
                var70 = 0.011396654;
            } else {
                var70 = -0.03490576;
            }
        } else {
            if (features[3] < -1.2997) {
                var70 = 0.000632678;
            } else {
                var70 = 0.047110032;
            }
        }
    } else {
        if (features[3] < 3.2872) {
            if (features[2] < 22.39) {
                var70 = -0.010143335;
            } else {
                var70 = -0.048400592;
            }
        } else {
            var70 = 0.017381556;
        }
    }
    double var71;
    if (features[2] < 30.95) {
        if (features[5] < 0.004351) {
            var71 = -0.013327259;
        } else {
            if (features[0] < 0.558485) {
                var71 = 0.03722739;
            } else {
                var71 = -0.008415689;
            }
        }
    } else {
        if (features[0] < 0.375619) {
            var71 = -0.02777875;
        } else {
            if (features[2] < 39.05) {
                var71 = -0.018517112;
            } else {
                var71 = 0.022300903;
            }
        }
    }
    double var72;
    if (features[6] < 0.022392) {
        if (features[6] < 0.013531) {
            if (features[6] < 0.009505) {
                var72 = 0.01141905;
            } else {
                var72 = -0.033283357;
            }
        } else {
            if (features[2] < 30.46) {
                var72 = 0.0033712431;
            } else {
                var72 = 0.04193751;
            }
        }
    } else {
        if (features[1] < 0.011936) {
            if (features[0] < 0.342802) {
                var72 = -0.012931623;
            } else {
                var72 = -0.044720966;
            }
        } else {
            var72 = 0.0139037175;
        }
    }
    double var73;
    if (features[4] < -0.949925) {
        var73 = 0.028315669;
    } else {
        if (features[4] < -0.927063) {
            if (features[4] < -0.940584) {
                var73 = -0.0022740953;
            } else {
                var73 = -0.04034166;
            }
        } else {
            if (features[6] < 0.022392) {
                var73 = 0.038777836;
            } else {
                var73 = -0.0033756495;
            }
        }
    }
    double var74;
    if (features[5] < 0.008411) {
        if (features[5] < 0.005672) {
            if (features[0] < 0.375619) {
                var74 = -0.012235973;
            } else {
                var74 = 0.02423175;
            }
        } else {
            if (features[2] < 38.28) {
                var74 = -0.052208044;
            } else {
                var74 = -0.012097231;
            }
        }
    } else {
        if (features[0] < 0.314328) {
            var74 = -0.012362667;
        } else {
            if (features[0] < 0.502054) {
                var74 = 0.048154015;
            } else {
                var74 = 0.009040265;
            }
        }
    }
    double var75;
    if (features[6] < 0.022392) {
        if (features[1] < 0.002622) {
            var75 = -0.0062059173;
        } else {
            if (features[6] < 0.010731) {
                var75 = -0.002657663;
            } else {
                var75 = 0.040984984;
            }
        }
    } else {
        if (features[6] < 0.033574) {
            var75 = -0.037385598;
        } else {
            if (features[5] < 0.00687) {
                var75 = 0.018590808;
            } else {
                var75 = -0.017098347;
            }
        }
    }
    double var76;
    if (features[3] < 1.9396) {
        if (features[3] < 0.4104) {
            if (features[3] < -1.5401) {
                var76 = -0.018267803;
            } else {
                var76 = 0.016425546;
            }
        } else {
            var76 = -0.040432073;
        }
    } else {
        var76 = 0.02430213;
    }
    double var77;
    if (features[1] < 0.011936) {
        if (features[5] < 0.003683) {
            var77 = 0.021176418;
        } else {
            if (features[1] < 0.007186) {
                var77 = -0.00038571397;
            } else {
                var77 = -0.0298787;
            }
        }
    } else {
        var77 = 0.031183658;
    }
    double var78;
    if (features[5] < 0.00545) {
        if (features[4] < -0.911669) {
            if (features[0] < 0.455247) {
                var78 = 0.03160416;
            } else {
                var78 = 0.0071065277;
            }
        } else {
            var78 = -0.008362852;
        }
    } else {
        if (features[5] < 0.00776) {
            if (features[0] < 0.375619) {
                var78 = -0.036627404;
            } else {
                var78 = -0.0077472352;
            }
        } else {
            if (features[4] < -0.925678) {
                var78 = -0.01258856;
            } else {
                var78 = 0.028451115;
            }
        }
    }
    double var79;
    if (features[3] < 2.367) {
        if (features[3] < 0.4104) {
            if (features[3] < -0.4412) {
                var79 = -0.0053996136;
            } else {
                var79 = 0.031605665;
            }
        } else {
            if (features[4] < -0.91492) {
                var79 = -0.03333426;
            } else {
                var79 = 0.006111278;
            }
        }
    } else {
        var79 = 0.028798623;
    }
    double var80;
    if (features[0] < 0.502054) {
        if (features[3] < 0.2799) {
            if (features[1] < 0.008856) {
                var80 = 0.033091035;
            } else {
                var80 = 0.0045026;
            }
        } else {
            if (features[1] < 0.007186) {
                var80 = 0.008580695;
            } else {
                var80 = -0.020121088;
            }
        }
    } else {
        if (features[3] < 1.113) {
            var80 = -0.0334233;
        } else {
            var80 = 0.01806122;
        }
    }
    double var81;
    if (features[6] < 0.022392) {
        if (features[6] < 0.012362) {
            if (features[2] < 28.61) {
                var81 = 0.014284918;
            } else {
                var81 = -0.016872037;
            }
        } else {
            var81 = 0.03562342;
        }
    } else {
        if (features[2] < 23.5) {
            if (features[2] < 20.81) {
                var81 = -0.009648946;
            } else {
                var81 = 0.028537944;
            }
        } else {
            if (features[6] < 0.040215) {
                var81 = -0.040763404;
            } else {
                var81 = -0.0015826892;
            }
        }
    }
    double var82;
    if (features[5] < 0.006125) {
        if (features[3] < 1.113) {
            if (features[5] < 0.004378) {
                var82 = -0.018231152;
            } else {
                var82 = 0.01698511;
            }
        } else {
            var82 = 0.036450796;
        }
    } else {
        if (features[0] < 0.373763) {
            if (features[3] < -0.4203) {
                var82 = -0.00088766543;
            } else {
                var82 = -0.042520005;
            }
        } else {
            if (features[6] < 0.0161) {
                var82 = -0.012161541;
            } else {
                var82 = 0.016647676;
            }
        }
    }
    double var83;
    if (features[4] < -0.927063) {
        if (features[4] < -0.940584) {
            if (features[0] < 0.476418) {
                var83 = 0.017282467;
            } else {
                var83 = -0.006395632;
            }
        } else {
            var83 = -0.03921962;
        }
    } else {
        if (features[5] < 0.011708) {
            if (features[4] < -0.911646) {
                var83 = 0.032247584;
            } else {
                var83 = -0.002724546;
            }
        } else {
            var83 = -0.0193091;
        }
    }
    double var84;
    if (features[5] < 0.003683) {
        var84 = 0.032684438;
    } else {
        if (features[6] < 0.071677) {
            if (features[6] < 0.022392) {
                var84 = 0.0024305254;
            } else {
                var84 = -0.028590156;
            }
        } else {
            var84 = 0.027650688;
        }
    }
    double var85;
    if (features[3] < -1.5401) {
        if (features[0] < 0.375619) {
            var85 = -0.0337452;
        } else {
            if (features[0] < 0.476418) {
                var85 = 0.027579648;
            } else {
                var85 = -0.020789003;
            }
        }
    } else {
        if (features[3] < 0.4199) {
            if (features[3] < -0.7168) {
                var85 = 0.0061246515;
            } else {
                var85 = 0.04809235;
            }
        } else {
            if (features[3] < 2.367) {
                var85 = -0.020663252;
            } else {
                var85 = 0.011456992;
            }
        }
    }
    double var86;
    if (features[3] < 1.9396) {
        if (features[1] < 0.011936) {
            if (features[2] < 23.87) {
                var86 = 0.0044980138;
            } else {
                var86 = -0.031833913;
            }
        } else {
            var86 = 0.017893298;
        }
    } else {
        if (features[2] < 33.83) {
            var86 = -0.008757217;
        } else {
            var86 = 0.035292532;
        }
    }
    double var87;
    if (features[1] < 0.007186) {
        if (features[2] < 27.27) {
            var87 = 0.037535742;
        } else {
            if (features[2] < 36.93) {
                var87 = -0.01838649;
            } else {
                var87 = 0.019801373;
            }
        }
    } else {
        if (features[2] < 20.86) {
            var87 = -0.02893557;
        } else {
            if (features[5] < 0.011708) {
                var87 = 0.018002776;
            } else {
                var87 = -0.02045623;
            }
        }
    }
    double var88;
    if (features[6] < 0.022392) {
        if (features[6] < 0.013531) {
            if (features[6] < 0.009505) {
                var88 = 0.02311636;
            } else {
                var88 = -0.032283943;
            }
        } else {
            var88 = 0.04131898;
        }
    } else {
        if (features[6] < 0.035096) {
            var88 = -0.036318745;
        } else {
            if (features[4] < -0.921196) {
                var88 = 0.02598454;
            } else {
                var88 = -0.021027816;
            }
        }
    }
    double var89;
    if (features[3] < -1.6235) {
        if (features[3] < -3.1028) {
            var89 = -0.001048813;
        } else {
            var89 = -0.032388408;
        }
    } else {
        if (features[3] < 0.4199) {
            if (features[3] < -0.4412) {
                var89 = 0.0032773705;
            } else {
                var89 = 0.03998741;
            }
        } else {
            if (features[3] < 1.9396) {
                var89 = -0.024775818;
            } else {
                var89 = 0.013139064;
            }
        }
    }
    double var90;
    if (features[4] < -0.927063) {
        if (features[4] < -0.940584) {
            if (features[0] < 0.476418) {
                var90 = 0.018598458;
            } else {
                var90 = -0.009823992;
            }
        } else {
            var90 = -0.036997728;
        }
    } else {
        if (features[5] < 0.011708) {
            if (features[3] < 0.4199) {
                var90 = 0.03747042;
            } else {
                var90 = -0.0016561747;
            }
        } else {
            var90 = -0.018096855;
        }
    }
    double var91;
    if (features[5] < 0.008411) {
        if (features[5] < 0.006125) {
            if (features[3] < 1.113) {
                var91 = -0.008536379;
            } else {
                var91 = 0.03608063;
            }
        } else {
            if (features[2] < 38.28) {
                var91 = -0.045196183;
            } else {
                var91 = 0.0051780986;
            }
        }
    } else {
        if (features[6] < 0.044648) {
            var91 = 0.0412663;
        } else {
            var91 = -0.006126604;
        }
    }
    double var92;
    if (features[3] < 2.367) {
        if (features[4] < -0.91492) {
            if (features[5] < 0.00545) {
                var92 = 0.010621684;
            } else {
                var92 = -0.031129202;
            }
        } else {
            if (features[5] < 0.004386) {
                var92 = -0.007857996;
            } else {
                var92 = 0.032841202;
            }
        }
    } else {
        var92 = 0.025333298;
    }
    double var93;
    if (features[2] < 25.66) {
        if (features[2] < 20.86) {
            if (features[1] < 0.007389) {
                var93 = 0.016171705;
            } else {
                var93 = -0.017087383;
            }
        } else {
            var93 = 0.027102778;
        }
    } else {
        if (features[2] < 28.5) {
            var93 = -0.04240821;
        } else {
            if (features[3] < 1.4489) {
                var93 = -0.012827245;
            } else {
                var93 = 0.026003493;
            }
        }
    }
    double var94;
    if (features[0] < 0.184167) {
        if (features[2] < 23.5) {
            var94 = 0.0024759087;
        } else {
            var94 = -0.023072027;
        }
    } else {
        if (features[1] < 0.010405) {
            if (features[2] < 48.9) {
                var94 = 0.023712626;
            } else {
                var94 = -0.01716416;
            }
        } else {
            var94 = -0.0075331978;
        }
    }
    double var95;
    if (features[5] < 0.006125) {
        if (features[4] < -0.932352) {
            var95 = -0.0035898683;
        } else {
            if (features[3] < -0.9174) {
                var95 = 0.0008134965;
            } else {
                var95 = 0.036213305;
            }
        }
    } else {
        if (features[5] < 0.009694) {
            if (features[1] < 0.005615) {
                var95 = -0.012685514;
            } else {
                var95 = -0.041749228;
            }
        } else {
            if (features[5] < 0.011708) {
                var95 = 0.029233858;
            } else {
                var95 = -0.012212846;
            }
        }
    }
    double var96;
    if (features[5] < 0.006125) {
        if (features[0] < 0.343298) {
            if (features[6] < 0.026911) {
                var96 = -0.001513226;
            } else {
                var96 = 0.042865254;
            }
        } else {
            if (features[2] < 35.79) {
                var96 = -0.022588613;
            } else {
                var96 = 0.0051797293;
            }
        }
    } else {
        if (features[2] < 41.33) {
            if (features[2] < 23.5) {
                var96 = 0.005351615;
            } else {
                var96 = -0.036993433;
            }
        } else {
            var96 = 0.009481747;
        }
    }
    double var97;
    if (features[4] < -0.927063) {
        if (features[4] < -0.948748) {
            if (features[5] < 0.006842) {
                var97 = -0.0056045125;
            } else {
                var97 = 0.020019561;
            }
        } else {
            var97 = -0.037641607;
        }
    } else {
        if (features[5] < 0.011708) {
            if (features[3] < 0.4199) {
                var97 = 0.027762735;
            } else {
                var97 = -0.009266139;
            }
        } else {
            var97 = -0.01293582;
        }
    }
    double var98;
    if (features[5] < 0.006125) {
        if (features[5] < 0.004351) {
            var98 = -0.013006386;
        } else {
            if (features[0] < 0.310096) {
                var98 = 0.038454816;
            } else {
                var98 = -0.0020658378;
            }
        }
    } else {
        if (features[5] < 0.006932) {
            var98 = -0.04054389;
        } else {
            if (features[1] < 0.007874) {
                var98 = 0.019258497;
            } else {
                var98 = -0.019365277;
            }
        }
    }
    double var99;
    if (features[6] < 0.009505) {
        var99 = 0.027674237;
    } else {
        if (features[2] < 28.5) {
            if (features[2] < 25.29) {
                var99 = -0.00068570365;
            } else {
                var99 = -0.03039503;
            }
        } else {
            if (features[6] < 0.046892) {
                var99 = 0.018892927;
            } else {
                var99 = -0.006009748;
            }
        }
    }
    double var100;
    var100 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29 + var30 + var31 + var32 + var33 + var34 + var35 + var36 + var37 + var38 + var39 + var40 + var41 + var42 + var43 + var44 + var45 + var46 + var47 + var48 + var49 + var50 + var51 + var52 + var53 + var54 + var55 + var56 + var57 + var58 + var59 + var60 + var61 + var62 + var63 + var64 + var65 + var66 + var67 + var68 + var69 + var70 + var71 + var72 + var73 + var74 + var75 + var76 + var77 + var78 + var79 + var80 + var81 + var82 + var83 + var84 + var85 + var86 + var87 + var88 + var89 + var90 + var91 + var92 + var93 + var94 + var95 + var96 + var97 + var98 + var99);
    result[0] = 1.0 - var100;
    result[1] = var100;
}
