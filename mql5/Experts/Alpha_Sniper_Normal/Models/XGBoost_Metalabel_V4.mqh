
//+------------------------------------------------------------------+
//| XGBoost Multi-Class Metalabeling Model                           |
//+------------------------------------------------------------------+
#include <Math\Stat\Math.mqh>

double meta_scaler_center[9] = {0.0014436051054620863,0.003473746291343899,0.0022902965649807027,0.0032493153858304483,0.003794698240665613,0.9060992454782028,0.0,1.3992244152462403,7.736757951043659};
double meta_scaler_scale[9] = {0.4093212262335729,0.19824956038531813,0.17681101532064677,0.17417125763670982,0.12663576069968757,0.811101662951872,1.0,13.289257378683496,33.40979185463454};

void predict_metalabel(double &f[], double &probs[]) {
    for(int i=0; i<5; i++) probs[i] = 0.5; // Base margin

    // Tree 0 for Class 0
    probs[0] += evaluate_meta_tree_0(f);
    // Tree 1 for Class 1
    probs[1] += evaluate_meta_tree_1(f);
    // Tree 2 for Class 2
    probs[2] += evaluate_meta_tree_2(f);
    // Tree 3 for Class 3
    probs[3] += evaluate_meta_tree_3(f);
    // Tree 4 for Class 4
    probs[4] += evaluate_meta_tree_4(f);
    // Tree 5 for Class 0
    probs[0] += evaluate_meta_tree_5(f);
    // Tree 6 for Class 1
    probs[1] += evaluate_meta_tree_6(f);
    // Tree 7 for Class 2
    probs[2] += evaluate_meta_tree_7(f);
    // Tree 8 for Class 3
    probs[3] += evaluate_meta_tree_8(f);
    // Tree 9 for Class 4
    probs[4] += evaluate_meta_tree_9(f);
    // Tree 10 for Class 0
    probs[0] += evaluate_meta_tree_10(f);
    // Tree 11 for Class 1
    probs[1] += evaluate_meta_tree_11(f);
    // Tree 12 for Class 2
    probs[2] += evaluate_meta_tree_12(f);
    // Tree 13 for Class 3
    probs[3] += evaluate_meta_tree_13(f);
    // Tree 14 for Class 4
    probs[4] += evaluate_meta_tree_14(f);
    // Tree 15 for Class 0
    probs[0] += evaluate_meta_tree_15(f);
    // Tree 16 for Class 1
    probs[1] += evaluate_meta_tree_16(f);
    // Tree 17 for Class 2
    probs[2] += evaluate_meta_tree_17(f);
    // Tree 18 for Class 3
    probs[3] += evaluate_meta_tree_18(f);
    // Tree 19 for Class 4
    probs[4] += evaluate_meta_tree_19(f);
    // Tree 20 for Class 0
    probs[0] += evaluate_meta_tree_20(f);
    // Tree 21 for Class 1
    probs[1] += evaluate_meta_tree_21(f);
    // Tree 22 for Class 2
    probs[2] += evaluate_meta_tree_22(f);
    // Tree 23 for Class 3
    probs[3] += evaluate_meta_tree_23(f);
    // Tree 24 for Class 4
    probs[4] += evaluate_meta_tree_24(f);
    // Tree 25 for Class 0
    probs[0] += evaluate_meta_tree_25(f);
    // Tree 26 for Class 1
    probs[1] += evaluate_meta_tree_26(f);
    // Tree 27 for Class 2
    probs[2] += evaluate_meta_tree_27(f);
    // Tree 28 for Class 3
    probs[3] += evaluate_meta_tree_28(f);
    // Tree 29 for Class 4
    probs[4] += evaluate_meta_tree_29(f);
    // Tree 30 for Class 0
    probs[0] += evaluate_meta_tree_30(f);
    // Tree 31 for Class 1
    probs[1] += evaluate_meta_tree_31(f);
    // Tree 32 for Class 2
    probs[2] += evaluate_meta_tree_32(f);
    // Tree 33 for Class 3
    probs[3] += evaluate_meta_tree_33(f);
    // Tree 34 for Class 4
    probs[4] += evaluate_meta_tree_34(f);
    // Tree 35 for Class 0
    probs[0] += evaluate_meta_tree_35(f);
    // Tree 36 for Class 1
    probs[1] += evaluate_meta_tree_36(f);
    // Tree 37 for Class 2
    probs[2] += evaluate_meta_tree_37(f);
    // Tree 38 for Class 3
    probs[3] += evaluate_meta_tree_38(f);
    // Tree 39 for Class 4
    probs[4] += evaluate_meta_tree_39(f);
    // Tree 40 for Class 0
    probs[0] += evaluate_meta_tree_40(f);
    // Tree 41 for Class 1
    probs[1] += evaluate_meta_tree_41(f);
    // Tree 42 for Class 2
    probs[2] += evaluate_meta_tree_42(f);
    // Tree 43 for Class 3
    probs[3] += evaluate_meta_tree_43(f);
    // Tree 44 for Class 4
    probs[4] += evaluate_meta_tree_44(f);
    // Tree 45 for Class 0
    probs[0] += evaluate_meta_tree_45(f);
    // Tree 46 for Class 1
    probs[1] += evaluate_meta_tree_46(f);
    // Tree 47 for Class 2
    probs[2] += evaluate_meta_tree_47(f);
    // Tree 48 for Class 3
    probs[3] += evaluate_meta_tree_48(f);
    // Tree 49 for Class 4
    probs[4] += evaluate_meta_tree_49(f);
    // Tree 50 for Class 0
    probs[0] += evaluate_meta_tree_50(f);
    // Tree 51 for Class 1
    probs[1] += evaluate_meta_tree_51(f);
    // Tree 52 for Class 2
    probs[2] += evaluate_meta_tree_52(f);
    // Tree 53 for Class 3
    probs[3] += evaluate_meta_tree_53(f);
    // Tree 54 for Class 4
    probs[4] += evaluate_meta_tree_54(f);
    // Tree 55 for Class 0
    probs[0] += evaluate_meta_tree_55(f);
    // Tree 56 for Class 1
    probs[1] += evaluate_meta_tree_56(f);
    // Tree 57 for Class 2
    probs[2] += evaluate_meta_tree_57(f);
    // Tree 58 for Class 3
    probs[3] += evaluate_meta_tree_58(f);
    // Tree 59 for Class 4
    probs[4] += evaluate_meta_tree_59(f);
    // Tree 60 for Class 0
    probs[0] += evaluate_meta_tree_60(f);
    // Tree 61 for Class 1
    probs[1] += evaluate_meta_tree_61(f);
    // Tree 62 for Class 2
    probs[2] += evaluate_meta_tree_62(f);
    // Tree 63 for Class 3
    probs[3] += evaluate_meta_tree_63(f);
    // Tree 64 for Class 4
    probs[4] += evaluate_meta_tree_64(f);
    // Tree 65 for Class 0
    probs[0] += evaluate_meta_tree_65(f);
    // Tree 66 for Class 1
    probs[1] += evaluate_meta_tree_66(f);
    // Tree 67 for Class 2
    probs[2] += evaluate_meta_tree_67(f);
    // Tree 68 for Class 3
    probs[3] += evaluate_meta_tree_68(f);
    // Tree 69 for Class 4
    probs[4] += evaluate_meta_tree_69(f);
    // Tree 70 for Class 0
    probs[0] += evaluate_meta_tree_70(f);
    // Tree 71 for Class 1
    probs[1] += evaluate_meta_tree_71(f);
    // Tree 72 for Class 2
    probs[2] += evaluate_meta_tree_72(f);
    // Tree 73 for Class 3
    probs[3] += evaluate_meta_tree_73(f);
    // Tree 74 for Class 4
    probs[4] += evaluate_meta_tree_74(f);
    // Tree 75 for Class 0
    probs[0] += evaluate_meta_tree_75(f);
    // Tree 76 for Class 1
    probs[1] += evaluate_meta_tree_76(f);
    // Tree 77 for Class 2
    probs[2] += evaluate_meta_tree_77(f);
    // Tree 78 for Class 3
    probs[3] += evaluate_meta_tree_78(f);
    // Tree 79 for Class 4
    probs[4] += evaluate_meta_tree_79(f);
    // Tree 80 for Class 0
    probs[0] += evaluate_meta_tree_80(f);
    // Tree 81 for Class 1
    probs[1] += evaluate_meta_tree_81(f);
    // Tree 82 for Class 2
    probs[2] += evaluate_meta_tree_82(f);
    // Tree 83 for Class 3
    probs[3] += evaluate_meta_tree_83(f);
    // Tree 84 for Class 4
    probs[4] += evaluate_meta_tree_84(f);
    // Tree 85 for Class 0
    probs[0] += evaluate_meta_tree_85(f);
    // Tree 86 for Class 1
    probs[1] += evaluate_meta_tree_86(f);
    // Tree 87 for Class 2
    probs[2] += evaluate_meta_tree_87(f);
    // Tree 88 for Class 3
    probs[3] += evaluate_meta_tree_88(f);
    // Tree 89 for Class 4
    probs[4] += evaluate_meta_tree_89(f);
    // Tree 90 for Class 0
    probs[0] += evaluate_meta_tree_90(f);
    // Tree 91 for Class 1
    probs[1] += evaluate_meta_tree_91(f);
    // Tree 92 for Class 2
    probs[2] += evaluate_meta_tree_92(f);
    // Tree 93 for Class 3
    probs[3] += evaluate_meta_tree_93(f);
    // Tree 94 for Class 4
    probs[4] += evaluate_meta_tree_94(f);
    // Tree 95 for Class 0
    probs[0] += evaluate_meta_tree_95(f);
    // Tree 96 for Class 1
    probs[1] += evaluate_meta_tree_96(f);
    // Tree 97 for Class 2
    probs[2] += evaluate_meta_tree_97(f);
    // Tree 98 for Class 3
    probs[3] += evaluate_meta_tree_98(f);
    // Tree 99 for Class 4
    probs[4] += evaluate_meta_tree_99(f);
    // Tree 100 for Class 0
    probs[0] += evaluate_meta_tree_100(f);
    // Tree 101 for Class 1
    probs[1] += evaluate_meta_tree_101(f);
    // Tree 102 for Class 2
    probs[2] += evaluate_meta_tree_102(f);
    // Tree 103 for Class 3
    probs[3] += evaluate_meta_tree_103(f);
    // Tree 104 for Class 4
    probs[4] += evaluate_meta_tree_104(f);
    // Tree 105 for Class 0
    probs[0] += evaluate_meta_tree_105(f);
    // Tree 106 for Class 1
    probs[1] += evaluate_meta_tree_106(f);
    // Tree 107 for Class 2
    probs[2] += evaluate_meta_tree_107(f);
    // Tree 108 for Class 3
    probs[3] += evaluate_meta_tree_108(f);
    // Tree 109 for Class 4
    probs[4] += evaluate_meta_tree_109(f);
    // Tree 110 for Class 0
    probs[0] += evaluate_meta_tree_110(f);
    // Tree 111 for Class 1
    probs[1] += evaluate_meta_tree_111(f);
    // Tree 112 for Class 2
    probs[2] += evaluate_meta_tree_112(f);
    // Tree 113 for Class 3
    probs[3] += evaluate_meta_tree_113(f);
    // Tree 114 for Class 4
    probs[4] += evaluate_meta_tree_114(f);
    // Tree 115 for Class 0
    probs[0] += evaluate_meta_tree_115(f);
    // Tree 116 for Class 1
    probs[1] += evaluate_meta_tree_116(f);
    // Tree 117 for Class 2
    probs[2] += evaluate_meta_tree_117(f);
    // Tree 118 for Class 3
    probs[3] += evaluate_meta_tree_118(f);
    // Tree 119 for Class 4
    probs[4] += evaluate_meta_tree_119(f);
    // Tree 120 for Class 0
    probs[0] += evaluate_meta_tree_120(f);
    // Tree 121 for Class 1
    probs[1] += evaluate_meta_tree_121(f);
    // Tree 122 for Class 2
    probs[2] += evaluate_meta_tree_122(f);
    // Tree 123 for Class 3
    probs[3] += evaluate_meta_tree_123(f);
    // Tree 124 for Class 4
    probs[4] += evaluate_meta_tree_124(f);
    // Tree 125 for Class 0
    probs[0] += evaluate_meta_tree_125(f);
    // Tree 126 for Class 1
    probs[1] += evaluate_meta_tree_126(f);
    // Tree 127 for Class 2
    probs[2] += evaluate_meta_tree_127(f);
    // Tree 128 for Class 3
    probs[3] += evaluate_meta_tree_128(f);
    // Tree 129 for Class 4
    probs[4] += evaluate_meta_tree_129(f);
    // Tree 130 for Class 0
    probs[0] += evaluate_meta_tree_130(f);
    // Tree 131 for Class 1
    probs[1] += evaluate_meta_tree_131(f);
    // Tree 132 for Class 2
    probs[2] += evaluate_meta_tree_132(f);
    // Tree 133 for Class 3
    probs[3] += evaluate_meta_tree_133(f);
    // Tree 134 for Class 4
    probs[4] += evaluate_meta_tree_134(f);
    // Tree 135 for Class 0
    probs[0] += evaluate_meta_tree_135(f);
    // Tree 136 for Class 1
    probs[1] += evaluate_meta_tree_136(f);
    // Tree 137 for Class 2
    probs[2] += evaluate_meta_tree_137(f);
    // Tree 138 for Class 3
    probs[3] += evaluate_meta_tree_138(f);
    // Tree 139 for Class 4
    probs[4] += evaluate_meta_tree_139(f);
    // Tree 140 for Class 0
    probs[0] += evaluate_meta_tree_140(f);
    // Tree 141 for Class 1
    probs[1] += evaluate_meta_tree_141(f);
    // Tree 142 for Class 2
    probs[2] += evaluate_meta_tree_142(f);
    // Tree 143 for Class 3
    probs[3] += evaluate_meta_tree_143(f);
    // Tree 144 for Class 4
    probs[4] += evaluate_meta_tree_144(f);
    // Tree 145 for Class 0
    probs[0] += evaluate_meta_tree_145(f);
    // Tree 146 for Class 1
    probs[1] += evaluate_meta_tree_146(f);
    // Tree 147 for Class 2
    probs[2] += evaluate_meta_tree_147(f);
    // Tree 148 for Class 3
    probs[3] += evaluate_meta_tree_148(f);
    // Tree 149 for Class 4
    probs[4] += evaluate_meta_tree_149(f);
    // Tree 150 for Class 0
    probs[0] += evaluate_meta_tree_150(f);
    // Tree 151 for Class 1
    probs[1] += evaluate_meta_tree_151(f);
    // Tree 152 for Class 2
    probs[2] += evaluate_meta_tree_152(f);
    // Tree 153 for Class 3
    probs[3] += evaluate_meta_tree_153(f);
    // Tree 154 for Class 4
    probs[4] += evaluate_meta_tree_154(f);
    // Tree 155 for Class 0
    probs[0] += evaluate_meta_tree_155(f);
    // Tree 156 for Class 1
    probs[1] += evaluate_meta_tree_156(f);
    // Tree 157 for Class 2
    probs[2] += evaluate_meta_tree_157(f);
    // Tree 158 for Class 3
    probs[3] += evaluate_meta_tree_158(f);
    // Tree 159 for Class 4
    probs[4] += evaluate_meta_tree_159(f);
    // Tree 160 for Class 0
    probs[0] += evaluate_meta_tree_160(f);
    // Tree 161 for Class 1
    probs[1] += evaluate_meta_tree_161(f);
    // Tree 162 for Class 2
    probs[2] += evaluate_meta_tree_162(f);
    // Tree 163 for Class 3
    probs[3] += evaluate_meta_tree_163(f);
    // Tree 164 for Class 4
    probs[4] += evaluate_meta_tree_164(f);
    // Tree 165 for Class 0
    probs[0] += evaluate_meta_tree_165(f);
    // Tree 166 for Class 1
    probs[1] += evaluate_meta_tree_166(f);
    // Tree 167 for Class 2
    probs[2] += evaluate_meta_tree_167(f);
    // Tree 168 for Class 3
    probs[3] += evaluate_meta_tree_168(f);
    // Tree 169 for Class 4
    probs[4] += evaluate_meta_tree_169(f);
    // Tree 170 for Class 0
    probs[0] += evaluate_meta_tree_170(f);
    // Tree 171 for Class 1
    probs[1] += evaluate_meta_tree_171(f);
    // Tree 172 for Class 2
    probs[2] += evaluate_meta_tree_172(f);
    // Tree 173 for Class 3
    probs[3] += evaluate_meta_tree_173(f);
    // Tree 174 for Class 4
    probs[4] += evaluate_meta_tree_174(f);
    // Tree 175 for Class 0
    probs[0] += evaluate_meta_tree_175(f);
    // Tree 176 for Class 1
    probs[1] += evaluate_meta_tree_176(f);
    // Tree 177 for Class 2
    probs[2] += evaluate_meta_tree_177(f);
    // Tree 178 for Class 3
    probs[3] += evaluate_meta_tree_178(f);
    // Tree 179 for Class 4
    probs[4] += evaluate_meta_tree_179(f);
    // Tree 180 for Class 0
    probs[0] += evaluate_meta_tree_180(f);
    // Tree 181 for Class 1
    probs[1] += evaluate_meta_tree_181(f);
    // Tree 182 for Class 2
    probs[2] += evaluate_meta_tree_182(f);
    // Tree 183 for Class 3
    probs[3] += evaluate_meta_tree_183(f);
    // Tree 184 for Class 4
    probs[4] += evaluate_meta_tree_184(f);
    // Tree 185 for Class 0
    probs[0] += evaluate_meta_tree_185(f);
    // Tree 186 for Class 1
    probs[1] += evaluate_meta_tree_186(f);
    // Tree 187 for Class 2
    probs[2] += evaluate_meta_tree_187(f);
    // Tree 188 for Class 3
    probs[3] += evaluate_meta_tree_188(f);
    // Tree 189 for Class 4
    probs[4] += evaluate_meta_tree_189(f);
    // Tree 190 for Class 0
    probs[0] += evaluate_meta_tree_190(f);
    // Tree 191 for Class 1
    probs[1] += evaluate_meta_tree_191(f);
    // Tree 192 for Class 2
    probs[2] += evaluate_meta_tree_192(f);
    // Tree 193 for Class 3
    probs[3] += evaluate_meta_tree_193(f);
    // Tree 194 for Class 4
    probs[4] += evaluate_meta_tree_194(f);
    // Tree 195 for Class 0
    probs[0] += evaluate_meta_tree_195(f);
    // Tree 196 for Class 1
    probs[1] += evaluate_meta_tree_196(f);
    // Tree 197 for Class 2
    probs[2] += evaluate_meta_tree_197(f);
    // Tree 198 for Class 3
    probs[3] += evaluate_meta_tree_198(f);
    // Tree 199 for Class 4
    probs[4] += evaluate_meta_tree_199(f);
    // Tree 200 for Class 0
    probs[0] += evaluate_meta_tree_200(f);
    // Tree 201 for Class 1
    probs[1] += evaluate_meta_tree_201(f);
    // Tree 202 for Class 2
    probs[2] += evaluate_meta_tree_202(f);
    // Tree 203 for Class 3
    probs[3] += evaluate_meta_tree_203(f);
    // Tree 204 for Class 4
    probs[4] += evaluate_meta_tree_204(f);
    // Tree 205 for Class 0
    probs[0] += evaluate_meta_tree_205(f);
    // Tree 206 for Class 1
    probs[1] += evaluate_meta_tree_206(f);
    // Tree 207 for Class 2
    probs[2] += evaluate_meta_tree_207(f);
    // Tree 208 for Class 3
    probs[3] += evaluate_meta_tree_208(f);
    // Tree 209 for Class 4
    probs[4] += evaluate_meta_tree_209(f);
    // Tree 210 for Class 0
    probs[0] += evaluate_meta_tree_210(f);
    // Tree 211 for Class 1
    probs[1] += evaluate_meta_tree_211(f);
    // Tree 212 for Class 2
    probs[2] += evaluate_meta_tree_212(f);
    // Tree 213 for Class 3
    probs[3] += evaluate_meta_tree_213(f);
    // Tree 214 for Class 4
    probs[4] += evaluate_meta_tree_214(f);
    // Tree 215 for Class 0
    probs[0] += evaluate_meta_tree_215(f);
    // Tree 216 for Class 1
    probs[1] += evaluate_meta_tree_216(f);
    // Tree 217 for Class 2
    probs[2] += evaluate_meta_tree_217(f);
    // Tree 218 for Class 3
    probs[3] += evaluate_meta_tree_218(f);
    // Tree 219 for Class 4
    probs[4] += evaluate_meta_tree_219(f);
    // Tree 220 for Class 0
    probs[0] += evaluate_meta_tree_220(f);
    // Tree 221 for Class 1
    probs[1] += evaluate_meta_tree_221(f);
    // Tree 222 for Class 2
    probs[2] += evaluate_meta_tree_222(f);
    // Tree 223 for Class 3
    probs[3] += evaluate_meta_tree_223(f);
    // Tree 224 for Class 4
    probs[4] += evaluate_meta_tree_224(f);
    // Tree 225 for Class 0
    probs[0] += evaluate_meta_tree_225(f);
    // Tree 226 for Class 1
    probs[1] += evaluate_meta_tree_226(f);
    // Tree 227 for Class 2
    probs[2] += evaluate_meta_tree_227(f);
    // Tree 228 for Class 3
    probs[3] += evaluate_meta_tree_228(f);
    // Tree 229 for Class 4
    probs[4] += evaluate_meta_tree_229(f);
    // Tree 230 for Class 0
    probs[0] += evaluate_meta_tree_230(f);
    // Tree 231 for Class 1
    probs[1] += evaluate_meta_tree_231(f);
    // Tree 232 for Class 2
    probs[2] += evaluate_meta_tree_232(f);
    // Tree 233 for Class 3
    probs[3] += evaluate_meta_tree_233(f);
    // Tree 234 for Class 4
    probs[4] += evaluate_meta_tree_234(f);
    // Tree 235 for Class 0
    probs[0] += evaluate_meta_tree_235(f);
    // Tree 236 for Class 1
    probs[1] += evaluate_meta_tree_236(f);
    // Tree 237 for Class 2
    probs[2] += evaluate_meta_tree_237(f);
    // Tree 238 for Class 3
    probs[3] += evaluate_meta_tree_238(f);
    // Tree 239 for Class 4
    probs[4] += evaluate_meta_tree_239(f);
    // Tree 240 for Class 0
    probs[0] += evaluate_meta_tree_240(f);
    // Tree 241 for Class 1
    probs[1] += evaluate_meta_tree_241(f);
    // Tree 242 for Class 2
    probs[2] += evaluate_meta_tree_242(f);
    // Tree 243 for Class 3
    probs[3] += evaluate_meta_tree_243(f);
    // Tree 244 for Class 4
    probs[4] += evaluate_meta_tree_244(f);
    // Tree 245 for Class 0
    probs[0] += evaluate_meta_tree_245(f);
    // Tree 246 for Class 1
    probs[1] += evaluate_meta_tree_246(f);
    // Tree 247 for Class 2
    probs[2] += evaluate_meta_tree_247(f);
    // Tree 248 for Class 3
    probs[3] += evaluate_meta_tree_248(f);
    // Tree 249 for Class 4
    probs[4] += evaluate_meta_tree_249(f);
}

double evaluate_meta_tree_0(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[8] < -0.935274363) {
                return -0.00378762302;
            } else {
                return 0.000504292024;
            }
        } else {
            if (f[4] < -0.0346435718) {
                return -0.000374325493;
            } else {
                return -0.0154864462;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.0265874695;
            } else {
                return 0.0952243656;
            }
        } else {
            if (f[7] < 0.637940526) {
                return 0.00719409902;
            } else {
                return 0.0350381099;
            }
        }
    }
}

double evaluate_meta_tree_1(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[0] < -1.13067496) {
                return -0.00502532721;
            } else {
                return 8.27351687e-05;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.0124951536;
            } else {
                return 0.00337167061;
            }
        }
    } else {
        if (f[1] < 2.06438828) {
            if (f[3] < -0.464442223) {
                return -0.0183184631;
            } else {
                return -0.00458804751;
            }
        } else {
            if (f[0] < 1.72220576) {
                return 0.0269601103;
            } else {
                return -0.0223463383;
            }
        }
    }
}

double evaluate_meta_tree_2(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0206093695;
            } else {
                return -0.00138632383;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00399934268;
            } else {
                return 0.0033838395;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.0244769845;
            } else {
                return -0.00853507966;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00624989765;
            } else {
                return -0.00561847584;
            }
        }
    }
}

double evaluate_meta_tree_3(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -1.10483754) {
            if (f[3] < 1.02796721) {
                return 0.00252629467;
            } else {
                return 0.0179825965;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00267232559;
            } else {
                return 0.000450889667;
            }
        }
    } else {
        if (f[2] < -1.38151884) {
            if (f[0] < 0.5810377) {
                return 0.0468789972;
            } else {
                return 0.00478951028;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00638927752;
            } else {
                return -0.000943909516;
            }
        }
    }
}

double evaluate_meta_tree_4(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.080678001;
            } else {
                return 9.09474184e-05;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00615740707;
            } else {
                return -0.00087274838;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.0300000254;
            } else {
                return 0.0997398198;
            }
        } else {
            if (f[7] < 1.193892) {
                return -5.74528422e-05;
            } else {
                return 0.0532795899;
            }
        }
    }
}

double evaluate_meta_tree_5(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[8] < -0.935274363) {
                return -0.00369567168;
            } else {
                return 0.000490643957;
            }
        } else {
            if (f[4] < -0.0346435718) {
                return -0.000382038881;
            } else {
                return -0.015235493;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.0258972105;
            } else {
                return 0.0892272815;
            }
        } else {
            if (f[7] < 0.637940526) {
                return 0.00703216204;
            } else {
                return 0.0335138626;
            }
        }
    }
}

double evaluate_meta_tree_6(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[0] < -1.13067496) {
                return -0.00488438876;
            } else {
                return 7.99486443e-05;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.0120647913;
            } else {
                return 0.00326081715;
            }
        }
    } else {
        if (f[1] < 2.06438828) {
            if (f[3] < -0.464442223) {
                return -0.0180739891;
            } else {
                return -0.00452332944;
            }
        } else {
            if (f[0] < 1.72220576) {
                return 0.0261456817;
            } else {
                return -0.0220267307;
            }
        }
    }
}

double evaluate_meta_tree_7(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0203568619;
            } else {
                return -0.00135937089;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00390554755;
            } else {
                return 0.00328542967;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.0242065322;
            } else {
                return -0.00833397172;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00610518456;
            } else {
                return -0.00547668105;
            }
        }
    }
}

double evaluate_meta_tree_8(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -1.10483754) {
            if (f[4] < 0.21967949) {
                return 0.00743121607;
            } else {
                return -0.00312822987;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00260302913;
            } else {
                return 0.000441440468;
            }
        }
    } else {
        if (f[2] < -1.13830388) {
            if (f[7] < 0.129899934) {
                return 0.0390568636;
            } else {
                return 0.0131458789;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00586787937;
            } else {
                return -0.0011547741;
            }
        }
    }
}

double evaluate_meta_tree_9(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.0788455307;
            } else {
                return 0.00579410605;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00596704846;
            } else {
                return -0.000849562522;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.0286604222;
            } else {
                return 0.0914275274;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.000278924941;
            } else {
                return 0.0510718524;
            }
        }
    }
}

double evaluate_meta_tree_10(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[7] < 2.01427317) {
                return 0.000181714349;
            } else {
                return -0.0117578311;
            }
        } else {
            if (f[4] < -0.0346435718) {
                return -0.00038295376;
            } else {
                return -0.0149885444;
            }
        }
    } else {
        if (f[5] < 1.53045237) {
            if (f[8] < -0.379841208) {
                return 0.00615895679;
            } else {
                return 0.0731893629;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00152286352;
            } else {
                return 0.0315284245;
            }
        }
    }
}

double evaluate_meta_tree_11(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[3] < -0.699636102) {
                return -0.00295318267;
            } else {
                return 0.000307663315;
            }
        } else {
            if (f[5] < 0.199363336) {
                return 0.00822043419;
            } else {
                return 0.00170728273;
            }
        }
    } else {
        if (f[8] < 0.910671234) {
            if (f[1] < 2.06438828) {
                return -0.00940242782;
            } else {
                return -0.0226108897;
            }
        } else {
            if (f[3] < 1.10518503) {
                return 0.00960699003;
            } else {
                return -0.0144401705;
            }
        }
    }
}

double evaluate_meta_tree_12(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0200964324;
            } else {
                return -0.00133250328;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00381147349;
            } else {
                return 0.0031896315;
            }
        }
    } else {
        if (f[1] < 0.0115987631) {
            if (f[0] < -0.835615456) {
                return 0.00105982367;
            } else {
                return -0.0125817554;
            }
        } else {
            if (f[5] < -0.707347035) {
                return -0.02608102;
            } else {
                return -0.0009299675;
            }
        }
    }
}

double evaluate_meta_tree_13(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -1.10483754) {
            if (f[3] < 1.02796721) {
                return 0.00224982551;
            } else {
                return 0.0173062831;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00253529777;
            } else {
                return 0.000432328088;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.486810774) {
                return 0.0298793744;
            } else {
                return 0.00812314358;
            }
        } else {
            if (f[5] < -0.759402156) {
                return 0.0210404266;
            } else {
                return 0.00177560968;
            }
        }
    }
}

double evaluate_meta_tree_14(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0707351714;
            } else {
                return -0.000415014481;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00578499539;
            } else {
                return -0.000827064447;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.02741009;
            } else {
                return 0.0844679773;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.000489455531;
            } else {
                return 0.0490073003;
            }
        }
    }
}

double evaluate_meta_tree_15(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[8] < -0.935274363) {
                return -0.00360481488;
            } else {
                return 0.000475658802;
            }
        } else {
            if (f[4] < -0.0346435718) {
                return -0.000373366609;
            } else {
                return -0.0147361895;
            }
        }
    } else {
        if (f[5] < 1.53045237) {
            if (f[8] < -0.379841208) {
                return 0.00609616004;
            } else {
                return 0.0690165162;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00150602858;
            } else {
                return 0.0302498341;
            }
        }
    }
}

double evaluate_meta_tree_16(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[0] < -1.13067496) {
                return -0.00470672827;
            } else {
                return 8.33877639e-05;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.0113471514;
            } else {
                return 0.00302327494;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.220058784) {
                return -0.0103293443;
            } else {
                return 0.0404091887;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0142477378;
            } else {
                return -0.00108128123;
            }
        }
    }
}

double evaluate_meta_tree_17(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0198370293;
            } else {
                return -0.00130433298;
            }
        } else {
            if (f[2] < -1.4817332) {
                return -0.00884785131;
            } else {
                return 0.00280398736;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.023835307;
            } else {
                return -0.00795598049;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00609451113;
            } else {
                return -0.00522048492;
            }
        }
    }
}

double evaluate_meta_tree_18(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.79142714) {
            if (f[2] < -0.027247604) {
                return -0.0252537671;
            } else {
                return -0.00455858419;
            }
        } else {
            if (f[8] < -1.10483754) {
                return 0.00427188864;
            } else {
                return -0.000913299446;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[0] < 0.721791387) {
                return 0.0489054136;
            } else {
                return 0.00695746392;
            }
        } else {
            if (f[5] < -0.555639148) {
                return 0.018741196;
            } else {
                return 0.00259741861;
            }
        }
    }
}

double evaluate_meta_tree_19(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.069617264;
            } else {
                return 0.0050173616;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00561767584;
            } else {
                return -0.000805713411;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.0262306519;
            } else {
                return 0.0785766169;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.000677585776;
            } else {
                return 0.0471438877;
            }
        }
    }
}

double evaluate_meta_tree_20(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[8] < -0.935274363) {
                return -0.00365651958;
            } else {
                return 0.000462093129;
            }
        } else {
            if (f[2] < -1.4817332) {
                return 0.0320235975;
            } else {
                return -0.0123309912;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.0219437908;
            } else {
                return 0.0765392408;
            }
        } else {
            if (f[4] < -0.159837157) {
                return -0.0225975178;
            } else {
                return 0.0209770072;
            }
        }
    }
}

double evaluate_meta_tree_21(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[3] < -0.699636102) {
                return -0.00286005205;
            } else {
                return 0.000306622096;
            }
        } else {
            if (f[5] < 0.199363336) {
                return 0.00774053112;
            } else {
                return 0.00154342153;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.382045984) {
                return -0.0128808385;
            } else {
                return 0.0338475294;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0140076084;
            } else {
                return -0.00108295737;
            }
        }
    }
}

double evaluate_meta_tree_22(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0195879377;
            } else {
                return -0.00127661158;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00375290285;
            } else {
                return 0.00302266516;
            }
        }
    } else {
        if (f[1] < 0.0115987631) {
            if (f[0] < -0.835615456) {
                return 0.00120405923;
            } else {
                return -0.0122008957;
            }
        } else {
            if (f[5] < -0.707347035) {
                return -0.0257598609;
            } else {
                return -0.000777894631;
            }
        }
    }
}

double evaluate_meta_tree_23(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -1.10483754) {
            if (f[4] < 0.21967949) {
                return 0.006892276;
            } else {
                return -0.00334037654;
            }
        } else {
            if (f[5] < -0.458790749) {
                return 0.000914594915;
            } else {
                return -0.00225440017;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.129899934) {
                return 0.0346032344;
            } else {
                return 0.0112048713;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00542804413;
            } else {
                return -0.00119337277;
            }
        }
    }
}

double evaluate_meta_tree_24(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0627921373;
            } else {
                return -0.000873230863;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00544411875;
            } else {
                return -0.000783849042;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[8] < 0.788691342) {
                return 0.0677491874;
            } else {
                return 0.00070588378;
            }
        } else {
            if (f[5] < 0.216660485) {
                return 0.0422206335;
            } else {
                return -0.00165246264;
            }
        }
    }
}

double evaluate_meta_tree_25(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[7] < 2.01427317) {
                return 0.000175000823;
            } else {
                return -0.0113280965;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00317813759;
            } else {
                return -0.0166029334;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0238239691;
            } else {
                return -0.0150535973;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.067030333;
            } else {
                return 0.0271010138;
            }
        }
    }
}

double evaluate_meta_tree_26(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[1] < -1.08474684) {
                return -0.0062331548;
            } else {
                return -0.000291457487;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.0128880162;
            } else {
                return 0.00139979401;
            }
        }
    } else {
        if (f[1] < 2.06438828) {
            if (f[3] < -0.464442223) {
                return -0.0174609795;
            } else {
                return -0.00391145563;
            }
        } else {
            if (f[0] < 1.72220576) {
                return 0.0256821644;
            } else {
                return -0.0209891181;
            }
        }
    }
}

double evaluate_meta_tree_27(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[1] < -0.949965775) {
            if (f[2] < 0.903505504) {
                return -0.00781195331;
            } else {
                return 0.011815954;
            }
        } else {
            if (f[1] < -0.832442343) {
                return 0.0158252548;
            } else {
                return 0.00117631524;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.0234755054;
            } else {
                return -0.00759697845;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00606826879;
            } else {
                return -0.00497858925;
            }
        }
    }
}

double evaluate_meta_tree_28(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.79142714) {
            if (f[2] < 1.38156605) {
                return -0.0168981478;
            } else {
                return 0.0245431047;
            }
        } else {
            if (f[8] < -1.10483754) {
                return 0.00397306262;
            } else {
                return -0.000866701768;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[0] < 0.721791387) {
                return 0.0455136262;
            } else {
                return 0.0063277497;
            }
        } else {
            if (f[5] < -0.555639148) {
                return 0.01793845;
            } else {
                return 0.0024487148;
            }
        }
    }
}

double evaluate_meta_tree_29(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.0620816909;
            } else {
                return 0.00431792857;
            }
        } else {
            if (f[0] < 1.15781617) {
                return -0.000760488037;
            } else {
                return 0.00539747719;
            }
        }
    } else {
        if (f[5] < 0.312420905) {
            if (f[8] < 0.802149236) {
                return 0.0652581006;
            } else {
                return -0.00157552829;
            }
        } else {
            if (f[4] < 0.877845049) {
                return 0.0360481888;
            } else {
                return -0.00123446085;
            }
        }
    }
}

double evaluate_meta_tree_30(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[8] < -0.935274363) {
                return -0.00341635989;
            } else {
                return 0.000451004365;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00304055866;
            } else {
                return -0.0163597409;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[8] < -0.301485926) {
                return 0.0290813651;
            } else {
                return -0.00916474406;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0637764707;
            } else {
                return 0.0260676928;
            }
        }
    }
}

double evaluate_meta_tree_31(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[0] < -1.13067496) {
                return -0.00452423608;
            } else {
                return 8.46350813e-05;
            }
        } else {
            if (f[8] < -0.160652995) {
                return 0.0214226916;
            } else {
                return 0.00357892551;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.382045984) {
                return -0.0124399187;
            } else {
                return 0.0328477062;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0135294301;
            } else {
                return -0.000912710966;
            }
        }
    }
}

double evaluate_meta_tree_32(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0193365086;
            } else {
                return -0.00126312382;
            }
        } else {
            if (f[3] < -1.38441098) {
                return -0.00712741632;
            } else {
                return 0.00267614587;
            }
        }
    } else {
        if (f[1] < 0.0115987631) {
            if (f[0] < -0.835615456) {
                return 0.00132216897;
            } else {
                return -0.0118418494;
            }
        } else {
            if (f[5] < 0.614919662) {
                return 0.00166086468;
            } else {
                return -0.00970344059;
            }
        }
    }
}

double evaluate_meta_tree_33(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[0] < -1.79142714) {
            if (f[2] < 0.0607290007) {
                return -0.0248572472;
            } else {
                return -0.00140919292;
            }
        } else {
            if (f[8] < -1.10483754) {
                return 0.00386228785;
            } else {
                return -0.00125209137;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.486810774) {
                return 0.0270195156;
            } else {
                return 0.00696211169;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00522816274;
            } else {
                return -0.00121418678;
            }
        }
    }
}

double evaluate_meta_tree_34(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.056454666;
            } else {
                return -0.00131642947;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00524323853;
            } else {
                return -0.000749865256;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.0212160423;
            } else {
                return 0.0665208697;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.0013257924;
            } else {
                return 0.0441501699;
            }
        }
    }
}

double evaluate_meta_tree_35(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[8] < -0.935274363) {
                return -0.00347131677;
            } else {
                return 0.000439736061;
            }
        } else {
            if (f[2] < -1.4817332) {
                return 0.0316636376;
            } else {
                return -0.0119166672;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0227563363;
            } else {
                return -0.0148709388;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0607556179;
            } else {
                return 0.0250401478;
            }
        }
    }
}

double evaluate_meta_tree_36(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[3] < -0.736839056) {
                return -0.00432669884;
            } else {
                return -3.15855723e-05;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.0125284214;
            } else {
                return 0.00134405494;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.220058784) {
                return -0.00964621641;
            } else {
                return 0.0362440795;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0132951578;
            } else {
                return -0.000924564141;
            }
        }
    }
}

double evaluate_meta_tree_37(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[1] < -0.949965775) {
            if (f[2] < 0.903505504) {
                return -0.00765777519;
            } else {
                return 0.0113499379;
            }
        } else {
            if (f[1] < -0.832442343) {
                return 0.0152369766;
            } else {
                return 0.00111259974;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.0231260601;
            } else {
                return -0.00726643298;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00602889666;
            } else {
                return -0.00475296704;
            }
        }
    }
}

double evaluate_meta_tree_38(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0220701229;
            } else {
                return -0.00257467129;
            }
        } else {
            if (f[8] < -1.10483754) {
                return 0.00390244718;
            } else {
                return -0.000814915751;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[1] < -0.45740661) {
                return -0.00299823168;
            } else {
                return 0.0404270068;
            }
        } else {
            if (f[5] < -0.555639148) {
                return 0.0171877258;
            } else {
                return 0.0023025074;
            }
        }
    }
}

double evaluate_meta_tree_39(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.0557315424;
            } else {
                return 0.00360299391;
            }
        } else {
            if (f[0] < 1.15781617) {
                return -0.000728019164;
            } else {
                return 0.00521963416;
            }
        }
    } else {
        if (f[5] < 0.312420905) {
            if (f[8] < 0.802149236) {
                return 0.0587766133;
            } else {
                return -0.00235617254;
            }
        } else {
            if (f[4] < 0.877845049) {
                return 0.0333067514;
            } else {
                return -0.00167034694;
            }
        }
    }
}

double evaluate_meta_tree_40(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[7] < 2.01427317) {
                return 0.000167999868;
            } else {
                return -0.0109286271;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00287146377;
            } else {
                return -0.0161166973;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[8] < -0.301485926) {
                return 0.0277414173;
            } else {
                return -0.0090548005;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0580933765;
            } else {
                return 0.0241284445;
            }
        }
    }
}

double evaluate_meta_tree_41(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[1] < -1.08474684) {
                return -0.00607037405;
            } else {
                return -0.000268303935;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.0121213859;
            } else {
                return 0.00130666269;
            }
        }
    } else {
        if (f[1] < 2.06438828) {
            if (f[3] < -0.464442223) {
                return -0.0169214178;
            } else {
                return -0.00339377671;
            }
        } else {
            if (f[0] < 1.72220576) {
                return 0.0251193177;
            } else {
                return -0.0202896241;
            }
        }
    }
}

double evaluate_meta_tree_42(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0191029515;
            } else {
                return -0.00125765975;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00205337419;
            } else {
                return 0.0316734016;
            }
        }
    } else {
        if (f[1] < 0.0115987631) {
            if (f[0] < -0.835615456) {
                return 0.00142908946;
            } else {
                return -0.0114877708;
            }
        } else {
            if (f[5] < -0.707347035) {
                return -0.025435403;
            } else {
                return -0.000485248718;
            }
        }
    }
}

double evaluate_meta_tree_43(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[0] < -1.79142714) {
            if (f[2] < 0.0607290007) {
                return -0.0243226662;
            } else {
                return -0.0013131554;
            }
        } else {
            if (f[8] < -1.10483754) {
                return 0.0035893512;
            } else {
                return -0.00119556696;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.129899934) {
                return 0.031505622;
            } else {
                return 0.00991021749;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00504284026;
            } else {
                return -0.00122964743;
            }
        }
    }
}

double evaluate_meta_tree_44(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0510522835;
            } else {
                return -0.0017050535;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00505651394;
            } else {
                return -0.000717569666;
            }
        }
    } else {
        if (f[5] < 0.312420905) {
            if (f[1] < 2.37942123) {
                return 0.0245680343;
            } else {
                return 0.0640636832;
            }
        } else {
            if (f[4] < 0.877845049) {
                return 0.0323379226;
            } else {
                return -0.00171243423;
            }
        }
    }
}

double evaluate_meta_tree_45(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[7] < 2.01427317) {
                return 0.000163786812;
            } else {
                return -0.0107360836;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00277017895;
            } else {
                return -0.0158866607;
            }
        }
    } else {
        if (f[5] < 1.53045237) {
            if (f[8] < -0.379841208) {
                return 0.00371351209;
            } else {
                return 0.0532841682;
            }
        } else {
            if (f[3] < 2.23530412) {
                return -3.56639102e-05;
            } else {
                return 0.025730595;
            }
        }
    }
}

double evaluate_meta_tree_46(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[3] < -0.699636102) {
                return -0.00271477457;
            } else {
                return 0.000292435579;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.0103795119;
            } else {
                return 0.00248562638;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[2] < -0.859133124) {
                return -0.0171832871;
            } else {
                return 0.0254175961;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0128403297;
            } else {
                return -0.000734294415;
            }
        }
    }
}

double evaluate_meta_tree_47(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[1] < -0.949965775) {
            if (f[2] < 0.903505504) {
                return -0.00755540887;
            } else {
                return 0.0109207621;
            }
        } else {
            if (f[1] < -0.832442343) {
                return 0.0143381655;
            } else {
                return 0.00105593214;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            return -0.0297968127;
        } else {
            if (f[2] < -1.31682527) {
                return 0.0579873323;
            } else {
                return -0.00429011555;
            }
        }
    }
}

double evaluate_meta_tree_48(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0215359405;
            } else {
                return -0.00248007406;
            }
        } else {
            if (f[5] < -0.339252353) {
                return 0.00153734547;
            } else {
                return -0.00127904012;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[1] < -0.45740661) {
                return -0.00323500717;
            } else {
                return 0.0380292721;
            }
        } else {
            if (f[0] < 1.83004999) {
                return 0.00297384686;
            } else {
                return 0.0372328497;
            }
        }
    }
}

double evaluate_meta_tree_49(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0486218594;
            } else {
                return -0.00171783089;
            }
        } else {
            if (f[0] < 1.15781617) {
                return -0.000698246469;
            } else {
                return 0.00506321713;
            }
        }
    } else {
        if (f[4] < 0.877845049) {
            if (f[2] < 0.160648212) {
                return 0.017676359;
            } else {
                return 0.057902243;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.00194407499;
            } else {
                return 0.0413897149;
            }
        }
    }
}

double evaluate_meta_tree_50(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[8] < -0.935274363) {
            if (f[5] < 2.15955353) {
                return -0.00284790155;
            } else {
                return -0.0160519164;
            }
        } else {
            if (f[0] < 0.645920277) {
                return 0.000956305594;
            } else {
                return -0.00240114727;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0215189438;
            } else {
                return -0.0148257455;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0534763746;
            } else {
                return 0.0225867238;
            }
        }
    }
}

double evaluate_meta_tree_51(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[3] < -0.736839056) {
                return -0.00415265281;
            } else {
                return -2.30098358e-05;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.0118221147;
            } else {
                return 0.00124496676;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.382045984) {
                return -0.011837109;
            } else {
                return 0.0303403642;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0125981933;
            } else {
                return -0.000596889062;
            }
        }
    }
}

double evaluate_meta_tree_52(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[7] < 0.687748313) {
                return -0.0023926883;
            } else {
                return 0.0465833656;
            }
        } else {
            if (f[2] < -1.4817332) {
                return -0.00868387986;
            } else {
                return 0.00242434326;
            }
        }
    } else {
        if (f[1] < -0.558167577) {
            if (f[2] < 0.0482802205) {
                return -0.0227449033;
            } else {
                return -0.00685350597;
            }
        } else {
            if (f[0] < -0.509635746) {
                return 0.00611541327;
            } else {
                return -0.00443040673;
            }
        }
    }
}

double evaluate_meta_tree_53(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -0.549308479) {
            if (f[4] < 0.289133519) {
                return 0.00289520551;
            } else {
                return -0.00345099228;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00325244176;
            } else {
                return 0.000477598747;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.486810774) {
                return 0.0246570911;
            } else {
                return 0.00593426684;
            }
        } else {
            if (f[5] < -0.759402156) {
                return 0.0189146046;
            } else {
                return 0.0013938729;
            }
        }
    }
}

double evaluate_meta_tree_54(double &f[]) {
    if (f[0] < 2.3796556) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0450982489;
            } else {
                return -0.00601613149;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00487054419;
            } else {
                return -0.000686108135;
            }
        }
    } else {
        if (f[8] < 0.747675538) {
            if (f[5] < 0.582937419) {
                return 0.0509042032;
            } else {
                return 0.00146232964;
            }
        } else {
            if (f[2] < 1.07075059) {
                return -0.0135116056;
            } else {
                return 0.0431161039;
            }
        }
    }
}

double evaluate_meta_tree_55(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[8] < -0.935274363) {
                return -0.00329956668;
            } else {
                return 0.000418059848;
            }
        } else {
            if (f[2] < -1.05065691) {
                return 0.0127144204;
            } else {
                return -0.0121622942;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0208089128;
            } else {
                return -0.0145969959;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0514461957;
            } else {
                return 0.0218042061;
            }
        }
    }
}

double evaluate_meta_tree_56(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[5] < -0.721313536) {
                return 0.00437574973;
            } else {
                return -0.0011542209;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.011478561;
            } else {
                return 0.00121706526;
            }
        }
    } else {
        if (f[1] < 2.06438828) {
            if (f[2] < -0.874095023) {
                return -0.0167821236;
            } else {
                return -0.00302875042;
            }
        } else {
            if (f[0] < 1.72220576) {
                return 0.0245501567;
            } else {
                return -0.0196085628;
            }
        }
    }
}

double evaluate_meta_tree_57(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[1] < -0.949965775) {
            if (f[2] < 0.903505504) {
                return -0.0073959888;
            } else {
                return 0.0105326641;
            }
        } else {
            if (f[1] < -0.832442343) {
                return 0.0138000129;
            } else {
                return 0.000997088966;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00256309495;
            } else {
                return -0.0302511547;
            }
        } else {
            if (f[8] < -0.301485926) {
                return 0.0370789021;
            } else {
                return -0.00393297384;
            }
        }
    }
}

double evaluate_meta_tree_58(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[7] < -1.303895) {
            if (f[3] < 1.01076698) {
                return 0.00214486104;
            } else {
                return 0.0176078584;
            }
        } else {
            if (f[3] < 1.96079302) {
                return -0.00105829432;
            } else {
                return -0.0202755369;
            }
        }
    } else {
        if (f[2] < -1.38151884) {
            if (f[0] < 0.5810377) {
                return 0.0355149917;
            } else {
                return 0.000567983778;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00516742654;
            } else {
                return -0.0011638857;
            }
        }
    }
}

double evaluate_meta_tree_59(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0447584912;
            } else {
                return -0.00207235757;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00473825587;
            } else {
                return -0.000734491972;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0187040418;
            } else {
                return 0.0588324033;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.00817330834;
            } else {
                return 0.0424072705;
            }
        }
    }
}

double evaluate_meta_tree_60(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[7] < 2.01427317) {
                return 0.000159567106;
            } else {
                return -0.0103499452;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00249835942;
            } else {
                return -0.0155931432;
            }
        }
    } else {
        if (f[5] < 1.53045237) {
            if (f[3] < 1.4542923) {
                return 0.0141435238;
            } else {
                return 0.0522586405;
            }
        } else {
            if (f[3] < 2.23530412) {
                return -0.000612139876;
            } else {
                return 0.0237367582;
            }
        }
    }
}

double evaluate_meta_tree_61(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[0] < -1.13067496) {
                return -0.00432851259;
            } else {
                return 8.30446807e-05;
            }
        } else {
            if (f[5] < 0.199363336) {
                return 0.00685222959;
            } else {
                return 0.000990985543;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[2] < -0.859133124) {
                return -0.0167168025;
            } else {
                return 0.0242096521;
            }
        } else {
            if (f[8] < 0.910671234) {
                return -0.0121565098;
            } else {
                return -0.000452867564;
            }
        }
    }
}

double evaluate_meta_tree_62(double &f[]) {
    if (f[7] < 0.701444626) {
        if (f[5] < -0.370376468) {
            if (f[8] < -1.21296334) {
                return -0.0188492741;
            } else {
                return -0.0012042661;
            }
        } else {
            if (f[7] < -0.635008097) {
                return 0.00508327316;
            } else {
                return 0.00087299844;
            }
        }
    } else {
        if (f[1] < 0.0115987631) {
            if (f[0] < -0.835615456) {
                return 0.00178305514;
            } else {
                return -0.010969596;
            }
        } else {
            if (f[0] < 0.0305097383) {
                return 0.00613592099;
            } else {
                return -0.00490238285;
            }
        }
    }
}

double evaluate_meta_tree_63(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0211445838;
            } else {
                return -0.00236170716;
            }
        } else {
            if (f[5] < -0.339252353) {
                return 0.00151463621;
            } else {
                return -0.00123157108;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[0] < 0.721791387) {
                return 0.0373101532;
            } else {
                return 0.00321114319;
            }
        } else {
            if (f[5] < -0.555639148) {
                return 0.0159872752;
            } else {
                return 0.00195486355;
            }
        }
    }
}

double evaluate_meta_tree_64(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.0449432731;
            } else {
                return 0.00202835444;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00457984488;
            } else {
                return -0.000714050198;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0180077832;
            } else {
                return 0.0562607758;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.00810930133;
            } else {
                return 0.0406873263;
            }
        }
    }
}

double evaluate_meta_tree_65(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[8] < -0.935274363) {
            if (f[5] < 2.15955353) {
                return -0.00270114071;
            } else {
                return -0.015733121;
            }
        } else {
            if (f[0] < 0.645920277) {
                return 0.000925568223;
            } else {
                return -0.00234242529;
            }
        }
    } else {
        if (f[4] < -0.159837157) {
            return -0.0239400472;
        } else {
            if (f[4] < 1.4961977) {
                return 0.0387030803;
            } else {
                return 0.0124515649;
            }
        }
    }
}

double evaluate_meta_tree_66(double &f[]) {
    if (f[3] < -0.699636102) {
        if (f[5] < 1.97747576) {
            if (f[5] < -0.388354152) {
                return 0.0147650493;
            } else {
                return -0.00375704211;
            }
        } else {
            if (f[4] < -1.65523922) {
                return 0.0245635677;
            } else {
                return 0.00210915459;
            }
        }
    } else {
        if (f[1] < 1.09404576) {
            if (f[0] < -1.13067496) {
                return -0.00413447432;
            } else {
                return 0.00124685187;
            }
        } else {
            if (f[4] < -1.58203208) {
                return 0.0483222343;
            } else {
                return -0.00408238219;
            }
        }
    }
}

double evaluate_meta_tree_67(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.00722969696;
            } else {
                return -0.00746773416;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00201793015;
            } else {
                return -0.0218541306;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0155378273;
            } else {
                return -0.0301147532;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0187791921;
            } else {
                return 0.000341720151;
            }
        }
    }
}

double evaluate_meta_tree_68(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[5] < -0.485459775) {
            if (f[7] < -0.611591339) {
                return 0.00790344086;
            } else {
                return 0.000345508073;
            }
        } else {
            if (f[7] < -1.78379381) {
                return 0.00869487971;
            } else {
                return -0.00168997224;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[5] < 1.97747576) {
                return 0.00297986832;
            } else {
                return 0.0162655246;
            }
        } else {
            if (f[8] < -0.0155891962) {
                return 0.0257595982;
            } else {
                return -0.0163611192;
            }
        }
    }
}

double evaluate_meta_tree_69(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0401570164;
            } else {
                return -0.00619449886;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00444315514;
            } else {
                return -0.000694462622;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0172653552;
            } else {
                return 0.053911265;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.00805725902;
            } else {
                return 0.0390433334;
            }
        }
    }
}

double evaluate_meta_tree_70(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[0] < -0.924897909) {
                return -0.00307370885;
            } else {
                return 0.000411050365;
            }
        } else {
            if (f[2] < -1.05065691) {
                return 0.0127343033;
            } else {
                return -0.0117643951;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[8] < -0.301485926) {
                return 0.0246370807;
            } else {
                return -0.00965799671;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0469140112;
            } else {
                return 0.0196926575;
            }
        }
    }
}

double evaluate_meta_tree_71(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[8] < 0.266049951) {
            if (f[1] < -1.08474684) {
                return -0.005736019;
            } else {
                return -0.000245113479;
            }
        } else {
            if (f[4] < -1.19378555) {
                return 0.0111505911;
            } else {
                return 0.00116381224;
            }
        }
    } else {
        if (f[1] < -0.090162456) {
            if (f[0] < 1.83004999) {
                return 0.0367831774;
            } else {
                return -0.00973427761;
            }
        } else {
            if (f[3] < -0.464442223) {
                return -0.0211933348;
            } else {
                return -0.00671049161;
            }
        }
    }
}

double evaluate_meta_tree_72(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[1] < -0.949965775) {
            if (f[2] < 0.903505504) {
                return -0.00712154666;
            } else {
                return 0.0104070576;
            }
        } else {
            if (f[1] < -0.832442343) {
                return 0.0128526213;
            } else {
                return 0.000931239396;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00257997424;
            } else {
                return -0.0300385039;
            }
        } else {
            if (f[8] < -0.301485926) {
                return 0.0357570052;
            } else {
                return -0.00370403263;
            }
        }
    }
}

double evaluate_meta_tree_73(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -0.549308479) {
            if (f[4] < 0.289133519) {
                return 0.00280283904;
            } else {
                return -0.003349534;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00310647534;
            } else {
                return 0.00051088765;
            }
        }
    } else {
        if (f[4] < 0.282096893) {
            if (f[2] < 0.292328924) {
                return 0.00271348981;
            } else {
                return 0.0125979157;
            }
        } else {
            if (f[2] < -1.38151884) {
                return 0.0426626168;
            } else {
                return -0.00120959501;
            }
        }
    }
}

double evaluate_meta_tree_74(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.040101327;
            } else {
                return -0.00265677646;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00428754045;
            } else {
                return -0.000674990937;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0166631788;
            } else {
                return 0.0518941246;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.0079101827;
            } else {
                return 0.037710093;
            }
        }
    }
}

double evaluate_meta_tree_75(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.72220576) {
            if (f[0] < -0.924897909) {
                return -0.00294300518;
            } else {
                return 0.000418187818;
            }
        } else {
            if (f[4] < 0.322939962) {
                return -0.00221353653;
            } else {
                return -0.0152706951;
            }
        }
    } else {
        if (f[4] < -0.159837157) {
            return -0.0237252042;
        } else {
            if (f[4] < 1.4961977) {
                return 0.0362684987;
            } else {
                return 0.0115405386;
            }
        }
    }
}

double evaluate_meta_tree_76(double &f[]) {
    if (f[3] < -0.699636102) {
        if (f[5] < 1.97747576) {
            if (f[5] < -0.388354152) {
                return 0.0143551528;
            } else {
                return -0.00367435371;
            }
        } else {
            if (f[4] < -1.65523922) {
                return 0.0235185921;
            } else {
                return 0.00204488123;
            }
        }
    } else {
        if (f[1] < 1.09404576) {
            if (f[0] < -1.13067496) {
                return -0.00400781957;
            } else {
                return 0.00120957196;
            }
        } else {
            if (f[4] < -1.58203208) {
                return 0.0461097136;
            } else {
                return -0.00396188768;
            }
        }
    }
}

double evaluate_meta_tree_77(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[5] < -0.583981514) {
            if (f[8] < -0.379841208) {
                return 0.00734164193;
            } else {
                return -0.00355430855;
            }
        } else {
            if (f[3] < -0.883044124) {
                return 0.0446876064;
            } else {
                return -0.00698655564;
            }
        }
    } else {
        if (f[7] < -0.635008097) {
            if (f[1] < 1.11387551) {
                return 0.00604522694;
            } else {
                return -0.0212748814;
            }
        } else {
            if (f[2] < 1.34327388) {
                return 0.000628272945;
            } else {
                return -0.00962974038;
            }
        }
    }
}

double evaluate_meta_tree_78(double &f[]) {
    if (f[8] < 0.945901334) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0207599849;
            } else {
                return -0.00232002488;
            }
        } else {
            if (f[7] < -1.303895) {
                return 0.00458036317;
            } else {
                return -0.000647753826;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            if (f[1] < -0.45740661) {
                return -0.00493521383;
            } else {
                return 0.0331263207;
            }
        } else {
            if (f[0] < 1.83004999) {
                return 0.00255104108;
            } else {
                return 0.0348743722;
            }
        }
    }
}

double evaluate_meta_tree_79(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0385907516;
            } else {
                return -0.00264722761;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00411556801;
            } else {
                return -0.000654617732;
            }
        }
    } else {
        if (f[5] < 0.755383968) {
            if (f[1] < 2.37942123) {
                return 0.0170220286;
            } else {
                return 0.0460054614;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.011622739;
            } else {
                return 0.0405020788;
            }
        }
    }
}

double evaluate_meta_tree_80(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[8] < -0.935274363) {
                return -0.00311453338;
            } else {
                return 0.000397611788;
            }
        } else {
            if (f[2] < -1.4817332) {
                return 0.0320241004;
            } else {
                return -0.0107326396;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0182453841;
            } else {
                return -0.0150105869;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0444010645;
            } else {
                return 0.0184688568;
            }
        }
    }
}

double evaluate_meta_tree_81(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[1] < 1.09404576) {
            if (f[1] < -1.08474684) {
                return -0.00560280168;
            } else {
                return 4.53532157e-05;
            }
        } else {
            if (f[7] < -0.882695615) {
                return 0.00779050961;
            } else {
                return -0.00823372602;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0150429262;
            } else {
                return 0.00118214765;
            }
        } else {
            if (f[5] < 0.0813811943) {
                return 0.00251555094;
            } else {
                return -0.000680133817;
            }
        }
    }
}

double evaluate_meta_tree_82(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.00713115046;
            } else {
                return -0.00721761072;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00214725593;
            } else {
                return -0.0215043239;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.014611884;
            } else {
                return -0.0299365707;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0185353402;
            } else {
                return 0.000327974878;
            }
        }
    }
}

double evaluate_meta_tree_83(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[1] < 0.750065565) {
            if (f[5] < -0.339252353) {
                return 0.0025724275;
            } else {
                return -0.00144731649;
            }
        } else {
            if (f[7] < -0.408947945) {
                return 0.00357148168;
            } else {
                return -0.00720718969;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[8] < -0.582102537) {
                return -0.0135471523;
            } else {
                return 0.0037308035;
            }
        } else {
            if (f[8] < -0.0155891962) {
                return 0.0248180423;
            } else {
                return -0.0161048807;
            }
        }
    }
}

double evaluate_meta_tree_84(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0361158401;
            } else {
                return -0.00657948432;
            }
        } else {
            if (f[0] < 0.909485996) {
                return -0.000742556469;
            } else {
                return 0.00294984016;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0154542848;
            } else {
                return 0.0483912677;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.00771009177;
            } else {
                return 0.0349176899;
            }
        }
    }
}

double evaluate_meta_tree_85(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 0.645920277) {
            if (f[8] < -1.03339756) {
                return -0.00400776044;
            } else {
                return 0.000849209551;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.0014258821;
            } else {
                return -0.009399998;
            }
        }
    } else {
        if (f[4] < -0.159837157) {
            return -0.0237198435;
        } else {
            if (f[4] < 1.4961977) {
                return 0.0337948948;
            } else {
                return 0.0107620265;
            }
        }
    }
}

double evaluate_meta_tree_86(double &f[]) {
    if (f[3] < -0.699636102) {
        if (f[5] < 1.97747576) {
            if (f[5] < -0.388354152) {
                return 0.0140194669;
            } else {
                return -0.00358219072;
            }
        } else {
            if (f[4] < -1.65523922) {
                return 0.0225564558;
            } else {
                return 0.00197890191;
            }
        }
    } else {
        if (f[8] < -1.18002284) {
            if (f[3] < 0.655889094) {
                return 0.00835018326;
            } else {
                return -0.00224889652;
            }
        } else {
            if (f[8] < -0.575511515) {
                return -0.00277852453;
            } else {
                return 0.000755729445;
            }
        }
    }
}

double evaluate_meta_tree_87(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.24507833) {
            if (f[1] < 1.73610723) {
                return -0.0222766325;
            } else {
                return 0.0584535673;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00444857776;
            } else {
                return -0.00461171148;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[2] < 0.221994698) {
                return 0.0439296924;
            } else {
                return -0.0284369476;
            }
        } else {
            if (f[7] < -0.635008097) {
                return 0.00470307143;
            } else {
                return -0.000122133919;
            }
        }
    }
}

double evaluate_meta_tree_88(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[3] < 1.96079302) {
            if (f[3] < 1.02796721) {
                return -0.00101102039;
            } else {
                return 0.00393483834;
            }
        } else {
            if (f[7] < -1.37314141) {
                return 0.0106082773;
            } else {
                return -0.0199555121;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.129899934) {
                return 0.0282402039;
            } else {
                return 0.00794250425;
            }
        } else {
            if (f[5] < -0.759402156) {
                return 0.0176088084;
            } else {
                return 0.00111934333;
            }
        }
    }
}

double evaluate_meta_tree_89(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.0751045272) {
                return 0.0376060903;
            } else {
                return 0.000840038178;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000803107396;
            } else {
                return 0.00236303383;
            }
        }
    } else {
        if (f[5] < 0.755383968) {
            if (f[2] < -0.425015599) {
                return 0.00113088079;
            } else {
                return 0.0333898254;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.0112926243;
            } else {
                return 0.037832465;
            }
        }
    }
}

double evaluate_meta_tree_90(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[1] < -2.22324824) {
            if (f[7] < 0.164682344) {
                return -0.0247477796;
            } else {
                return 0.0127511146;
            }
        } else {
            if (f[0] < 0.645920277) {
                return 0.0004891422;
            } else {
                return -0.00209806277;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[8] < -0.301485926) {
                return 0.022083601;
            } else {
                return -0.0100673791;
            }
        } else {
            if (f[0] < -0.620916247) {
                return 0.00486794207;
            } else {
                return 0.0313307159;
            }
        }
    }
}

double evaluate_meta_tree_91(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[3] < -0.711380064) {
            if (f[5] < 1.76325357) {
                return -0.00419230061;
            } else {
                return 0.00542950863;
            }
        } else {
            if (f[8] < -1.18002284) {
                return 0.00522242906;
            } else {
                return -0.000382120692;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[7] < 0.164682344) {
                return 0.00706726778;
            } else {
                return 0.00201492477;
            }
        } else {
            if (f[3] < 1.30186212) {
                return -0.0128197419;
            } else {
                return -0.00119319593;
            }
        }
    }
}

double evaluate_meta_tree_92(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.00683260197;
            } else {
                return -0.00708711101;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00216808869;
            } else {
                return -0.0212365612;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0141180148;
            } else {
                return -0.0297350343;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0183008965;
            } else {
                return 0.000321335683;
            }
        }
    }
}

double evaluate_meta_tree_93(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[1] < 0.750065565) {
            if (f[5] < -0.339252353) {
                return 0.00250574993;
            } else {
                return -0.00140866346;
            }
        } else {
            if (f[7] < -0.408947945) {
                return 0.00351551897;
            } else {
                return -0.00704165315;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[5] < 1.97747576) {
                return 0.00268682814;
            } else {
                return 0.0152958548;
            }
        } else {
            if (f[8] < -0.0155891962) {
                return 0.0241642073;
            } else {
                return -0.0158092696;
            }
        }
    }
}

double evaluate_meta_tree_94(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0350611322;
            } else {
                return -0.00313432328;
            }
        } else {
            if (f[1] < -1.33478355) {
                return 0.00528749777;
            } else {
                return -0.000551622885;
            }
        }
    } else {
        if (f[1] < 2.37942123) {
            if (f[5] < -0.465355903) {
                return 0.0355056338;
            } else {
                return 0.00452715531;
            }
        } else {
            if (f[8] < 0.835825861) {
                return 0.0433036163;
            } else {
                return -0.00912602339;
            }
        }
    }
}

double evaluate_meta_tree_95(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[7] < 2.01427317) {
            if (f[0] < -0.924897909) {
                return -0.00291549461;
            } else {
                return 0.000394420087;
            }
        } else {
            if (f[2] < -1.05065691) {
                return 0.012783072;
            } else {
                return -0.0112854671;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.00751077104;
            } else {
                return 0.0498493277;
            }
        } else {
            if (f[0] < -0.23440364) {
                return -0.000530737394;
            } else {
                return 0.0188495163;
            }
        }
    }
}

double evaluate_meta_tree_96(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[8] < -1.61720705) {
                return 0.00641350402;
            } else {
                return -0.000398223376;
            }
        } else {
            if (f[8] < -0.160652995) {
                return 0.0201792009;
            } else {
                return 0.00295034912;
            }
        }
    } else {
        if (f[1] < 0.305820704) {
            if (f[4] < -0.382045984) {
                return -0.0113997115;
            } else {
                return 0.0289380737;
            }
        } else {
            if (f[2] < 1.24955213) {
                return -0.0101540266;
            } else {
                return 0.0121296374;
            }
        }
    }
}

double evaluate_meta_tree_97(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[4] < 1.62132287) {
            if (f[4] < 1.02172446) {
                return 0.000926500827;
            } else {
                return -0.00711676246;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00933913235;
            } else {
                return 0.0481500737;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00235005072;
            } else {
                return -0.0298727285;
            }
        } else {
            if (f[8] < -0.301485926) {
                return 0.0343598239;
            } else {
                return -0.00348262233;
            }
        }
    }
}

double evaluate_meta_tree_98(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[8] < -0.549308479) {
            if (f[4] < 0.289133519) {
                return 0.00275810389;
            } else {
                return -0.00321800634;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00297812559;
            } else {
                return 0.000527747907;
            }
        }
    } else {
        if (f[4] < 0.282096893) {
            if (f[2] < 0.47915864) {
                return 0.00293848827;
            } else {
                return 0.0137343919;
            }
        } else {
            if (f[2] < -1.38151884) {
                return 0.0394668281;
            } else {
                return -0.00131409883;
            }
        }
    }
}

double evaluate_meta_tree_99(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0328220725;
            } else {
                return -0.00665694568;
            }
        } else {
            if (f[0] < 0.909485996) {
                return -0.000700072444;
            } else {
                return 0.00282772467;
            }
        }
    } else {
        if (f[5] < 0.899194479) {
            if (f[1] < 2.37942123) {
                return 0.0141052902;
            } else {
                return 0.0411729328;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.0128021911;
            } else {
                return 0.033712782;
            }
        }
    }
}

double evaluate_meta_tree_100(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 1.56179285) {
            if (f[7] < 2.01427317) {
                return 0.000180829651;
            } else {
                return -0.00979809742;
            }
        } else {
            if (f[8] < -2.0852387) {
                return 0.0527209304;
            } else {
                return -0.00705918018;
            }
        }
    } else {
        if (f[4] < -0.159837157) {
            return -0.0234876927;
        } else {
            if (f[4] < 1.4961977) {
                return 0.0313937999;
            } else {
                return 0.00949001964;
            }
        }
    }
}

double evaluate_meta_tree_101(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[5] < -0.721313536) {
            if (f[1] < 0.806270838) {
                return 0.00514458399;
            } else {
                return -0.0113207605;
            }
        } else {
            if (f[3] < 0.0843367502) {
                return -0.00252992124;
            } else {
                return 0.000544013688;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0144651802;
            } else {
                return 0.00110835559;
            }
        } else {
            if (f[5] < 0.0813811943) {
                return 0.00240334077;
            } else {
                return -0.000675474352;
            }
        }
    }
}

double evaluate_meta_tree_102(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[5] < -0.583981514) {
            if (f[8] < -0.379841208) {
                return 0.00704944134;
            } else {
                return -0.00334810698;
            }
        } else {
            if (f[3] < -0.883044124) {
                return 0.0429885425;
            } else {
                return -0.00676134834;
            }
        }
    } else {
        if (f[7] < -0.635008097) {
            if (f[1] < 1.11387551) {
                return 0.00565589778;
            } else {
                return -0.0210387129;
            }
        } else {
            if (f[4] < -1.25697768) {
                return -0.011446978;
            } else {
                return 0.000530683086;
            }
        }
    }
}

double evaluate_meta_tree_103(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[5] < 0.593657792) {
            if (f[5] < -0.814270735) {
                return 0.0263594333;
            } else {
                return -0.0207429454;
            }
        } else {
            if (f[0] < -1.95236576) {
                return 0.0207918268;
            } else {
                return -0.0189805757;
            }
        }
    } else {
        if (f[8] < 0.945901334) {
            if (f[5] < -0.339252353) {
                return 0.0013695677;
            } else {
                return -0.00111945812;
            }
        } else {
            if (f[4] < 0.14815478) {
                return 0.00791756809;
            } else {
                return 0.000152941531;
            }
        }
    }
}

double evaluate_meta_tree_104(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0329332314;
            } else {
                return -0.00331125292;
            }
        } else {
            if (f[1] < -1.03017294) {
                return 0.0033327539;
            } else {
                return -0.000640534796;
            }
        }
    } else {
        if (f[5] < 0.687811255) {
            if (f[1] < 2.37942123) {
                return 0.0133520393;
            } else {
                return 0.04322901;
            }
        } else {
            if (f[2] < 1.15191782) {
                return -0.00759068085;
            } else {
                return 0.0312397722;
            }
        }
    }
}

double evaluate_meta_tree_105(double &f[]) {
    if (f[2] < 1.8694005) {
        if (f[7] < 2.01427317) {
            if (f[8] < -0.935274363) {
                return -0.00294568669;
            } else {
                return 0.000353583775;
            }
        } else {
            if (f[2] < -1.05065691) {
                return 0.0127360737;
            } else {
                return -0.0113546606;
            }
        }
    } else {
        if (f[1] < 0.26392144) {
            if (f[8] < 0.879919171) {
                return 0.011501357;
            } else {
                return -0.0239466112;
            }
        } else {
            if (f[0] < 0.388006359) {
                return 0.0311915725;
            } else {
                return -0.00541621866;
            }
        }
    }
}

double evaluate_meta_tree_106(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[3] < -0.711380064) {
            if (f[5] < 1.76325357) {
                return -0.00404968439;
            } else {
                return 0.00526235765;
            }
        } else {
            if (f[8] < -1.18002284) {
                return 0.0050609014;
            } else {
                return -0.000368161127;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[7] < 0.164682344) {
                return 0.006822336;
            } else {
                return 0.00191391003;
            }
        } else {
            if (f[3] < 1.30186212) {
                return -0.0126076741;
            } else {
                return -0.00117391814;
            }
        }
    }
}

double evaluate_meta_tree_107(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.0065801926;
            } else {
                return -0.00694364309;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00225487119;
            } else {
                return -0.0209380072;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0136338547;
            } else {
                return -0.0295489281;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0180347431;
            } else {
                return 0.000309949624;
            }
        }
    }
}

double evaluate_meta_tree_108(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[2] < 1.46987176) {
            if (f[5] < 0.523699343) {
                return -0.0210920032;
            } else {
                return 0.000236739623;
            }
        } else {
            if (f[4] < 0.935132205) {
                return 0.0608044527;
            } else {
                return -0.0179338381;
            }
        }
    } else {
        if (f[7] < 0.651256502) {
            if (f[1] < 0.750065565) {
                return 3.97738841e-05;
            } else {
                return -0.00391167821;
            }
        } else {
            if (f[0] < -0.989682615) {
                return 0.0130451638;
            } else {
                return 0.0019114766;
            }
        }
    }
}

double evaluate_meta_tree_109(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[1] < -1.76743913) {
            if (f[5] < 0.43784681) {
                return 0.0258901808;
            } else {
                return -0.00194132852;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000868573261;
            } else {
                return 0.0022254556;
            }
        }
    } else {
        if (f[8] < 1.07459259) {
            if (f[2] < -0.197729483) {
                return 0.00075128529;
            } else {
                return 0.0289970096;
            }
        } else {
            if (f[4] < 1.29352868) {
                return -0.0214546379;
            } else {
                return -0.00222272496;
            }
        }
    }
}

double evaluate_meta_tree_110(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 0.645920277) {
            if (f[8] < -1.03339756) {
                return -0.00380577962;
            } else {
                return 0.000802423456;
            }
        } else {
            if (f[5] < -0.792370796) {
                return 0.0139536187;
            } else {
                return -0.00235359371;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0156965237;
            } else {
                return -0.015476889;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0392890945;
            } else {
                return 0.0152852014;
            }
        }
    }
}

double evaluate_meta_tree_111(double &f[]) {
    if (f[0] < 1.63479877) {
        if (f[7] < 1.01226544) {
            if (f[5] < -0.738194823) {
                return 0.00368797965;
            } else {
                return -0.000497197791;
            }
        } else {
            if (f[8] < -0.160652995) {
                return 0.0194435306;
            } else {
                return 0.00282727228;
            }
        }
    } else {
        if (f[1] < -0.090162456) {
            if (f[0] < 1.83004999) {
                return 0.035161525;
            } else {
                return -0.00941255502;
            }
        } else {
            if (f[3] < -0.464442223) {
                return -0.0207838546;
            } else {
                return -0.00594692351;
            }
        }
    }
}

double evaluate_meta_tree_112(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.24507833) {
            if (f[1] < 1.73610723) {
                return -0.0220206082;
            } else {
                return 0.0558290556;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.004245291;
            } else {
                return -0.00438943552;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[0] < 0.451554656) {
                return 0.00294684223;
            } else {
                return 0.0632238761;
            }
        } else {
            if (f[7] < -0.635008097) {
                return 0.00436268421;
            } else {
                return -0.000105221632;
            }
        }
    }
}

double evaluate_meta_tree_113(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[7] < -1.303895) {
            if (f[3] < 1.01076698) {
                return 0.00204603234;
            } else {
                return 0.0169069674;
            }
        } else {
            if (f[3] < 1.96079302) {
                return -0.000904098793;
            } else {
                return -0.0194593836;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.486810774) {
                return 0.0220653433;
            } else {
                return 0.00403365633;
            }
        } else {
            if (f[5] < -0.759402156) {
                return 0.0167426355;
            } else {
                return 0.000957172946;
            }
        }
    }
}

double evaluate_meta_tree_114(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0302389115;
            } else {
                return -0.00683538197;
            }
        } else {
            if (f[1] < -1.14988172) {
                return 0.00375342043;
            } else {
                return -0.000607530179;
            }
        }
    } else {
        if (f[8] < 1.07459259) {
            if (f[2] < -0.197729483) {
                return 0.000723172852;
            } else {
                return 0.027982315;
            }
        } else {
            if (f[4] < 1.29352868) {
                return -0.0211889464;
            } else {
                return -0.00218026061;
            }
        }
    }
}

double evaluate_meta_tree_115(double &f[]) {
    if (f[2] < 1.8694005) {
        if (f[7] < 2.01427317) {
            if (f[0] < -0.924897909) {
                return -0.00281560211;
            } else {
                return 0.000354694901;
            }
        } else {
            if (f[2] < -1.4817332) {
                return 0.0311031323;
            } else {
                return -0.0102964127;
            }
        }
    } else {
        if (f[0] < -1.04191673) {
            if (f[8] < -0.286462218) {
                return 0.0287651662;
            } else {
                return -0.0183205456;
            }
        } else {
            if (f[0] < -0.767702758) {
                return 0.0423256271;
            } else {
                return 0.00752153713;
            }
        }
    }
}

double evaluate_meta_tree_116(double &f[]) {
    if (f[1] < 1.09404576) {
        if (f[3] < -0.699636102) {
            if (f[5] < 1.97747576) {
                return -0.00284878537;
            } else {
                return 0.00845786184;
            }
        } else {
            if (f[0] < -0.975028276) {
                return -0.00298918015;
            } else {
                return 0.00119675358;
            }
        }
    } else {
        if (f[7] < 0.740474403) {
            if (f[7] < -1.02202904) {
                return 0.0104728313;
            } else {
                return -0.00728792278;
            }
        } else {
            if (f[0] < -0.0782057941) {
                return 0.0247887187;
            } else {
                return 0.000488836551;
            }
        }
    }
}

double evaluate_meta_tree_117(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.00636160141;
            } else {
                return -0.0067839222;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00228327187;
            } else {
                return -0.0206713956;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0131804897;
            } else {
                return -0.0293609928;
            }
        } else {
            if (f[0] < -0.665902972) {
                return 0.00458778953;
            } else {
                return -0.000623728556;
            }
        }
    }
}

double evaluate_meta_tree_118(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[2] < 1.46987176) {
            if (f[5] < 0.523699343) {
                return -0.0207882077;
            } else {
                return 0.000292597571;
            }
        } else {
            if (f[4] < 0.935132205) {
                return 0.0579481684;
            } else {
                return -0.0177683085;
            }
        }
    } else {
        if (f[8] < 0.945901334) {
            if (f[7] < -1.303895) {
                return 0.00425700424;
            } else {
                return -0.000603053428;
            }
        } else {
            if (f[4] < 0.14815478) {
                return 0.00756604085;
            } else {
                return 6.0389295e-05;
            }
        }
    }
}

double evaluate_meta_tree_119(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0304714777;
            } else {
                return -0.0036579892;
            }
        } else {
            if (f[0] < 0.909485996) {
                return -0.000652899791;
            } else {
                return 0.00271711173;
            }
        }
    } else {
        if (f[5] < 1.04725361) {
            if (f[2] < -0.425015599) {
                return -0.00127325195;
            } else {
                return 0.0274338517;
            }
        } else {
            if (f[8] < 1.19285023) {
                return 0.00107660075;
            } else {
                return -0.026230162;
            }
        }
    }
}

double evaluate_meta_tree_120(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < 0.645920277) {
            if (f[0] < -0.0454454385) {
                return -0.000671630085;
            } else {
                return 0.00192719197;
            }
        } else {
            if (f[5] < -0.792370796) {
                return 0.0135280434;
            } else {
                return -0.00229672901;
            }
        }
    } else {
        if (f[7] < 0.637940526) {
            if (f[4] < 1.5452491) {
                return 0.0147983748;
            } else {
                return -0.0154481949;
            }
        } else {
            if (f[5] < 1.42658842) {
                return 0.0380104631;
            } else {
                return 0.0145639777;
            }
        }
    }
}

double evaluate_meta_tree_121(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[3] < -0.711380064) {
            if (f[5] < -0.543851018) {
                return 0.0271135308;
            } else {
                return -0.00335953734;
            }
        } else {
            if (f[8] < -1.18002284) {
                return 0.00487128971;
            } else {
                return -0.000369171845;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[7] < 0.164682344) {
                return 0.00667061051;
            } else {
                return 0.00184900034;
            }
        } else {
            if (f[7] < -0.8391307) {
                return 0.0461329482;
            } else {
                return -0.00494576292;
            }
        }
    }
}

double evaluate_meta_tree_122(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[8] < -1.21296334) {
            if (f[0] < -0.383884877) {
                return 0.000958122255;
            } else {
                return -0.0269815214;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00380497612;
            } else {
                return -0.00433032494;
            }
        }
    } else {
        if (f[2] < -1.4817332) {
            if (f[0] < 1.13732505) {
                return -0.0144553827;
            } else {
                return 0.0149610788;
            }
        } else {
            if (f[7] < -0.635008097) {
                return 0.00512624672;
            } else {
                return 0.000171188367;
            }
        }
    }
}

double evaluate_meta_tree_123(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[8] < -0.566975594) {
            if (f[4] < 0.289133519) {
                return 0.00296692434;
            } else {
                return -0.00283261249;
            }
        } else {
            if (f[5] < -0.783027411) {
                return 0.00635898998;
            } else {
                return -0.00181017572;
            }
        }
    } else {
        if (f[3] < 1.81086767) {
            if (f[8] < -0.582102537) {
                return -0.0134556191;
            } else {
                return 0.00323684956;
            }
        } else {
            if (f[4] < 1.87506628) {
                return -0.0240330976;
            } else {
                return -0.000814073079;
            }
        }
    }
}

double evaluate_meta_tree_124(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[1] < -1.76743913) {
            if (f[5] < 0.43784681) {
                return 0.0240422208;
            } else {
                return -0.00214449316;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.00082255184;
            } else {
                return 0.00214593415;
            }
        }
    } else {
        if (f[8] < 1.07459259) {
            if (f[2] < -0.197729483) {
                return 0.000543118222;
            } else {
                return 0.0262869503;
            }
        } else {
            if (f[4] < 1.29352868) {
                return -0.0209702384;
            } else {
                return -0.00217580586;
            }
        }
    }
}

double evaluate_meta_tree_125(double &f[]) {
    if (f[2] < 1.8694005) {
        if (f[7] < 2.01427317) {
            if (f[0] < -0.924897909) {
                return -0.00272533554;
            } else {
                return 0.000344441767;
            }
        } else {
            if (f[2] < -1.05065691) {
                return 0.0124709299;
            } else {
                return -0.0109218024;
            }
        }
    } else {
        if (f[7] < 1.55216515) {
            if (f[8] < 0.945901334) {
                return 0.0107960245;
            } else {
                return -0.0178109109;
            }
        } else {
            if (f[0] < 0.388006359) {
                return 0.0391954146;
            } else {
                return -0.0211810339;
            }
        }
    }
}

double evaluate_meta_tree_126(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[1] < 1.09404576) {
            if (f[1] < -1.08474684) {
                return -0.0052935034;
            } else {
                return 8.05781674e-05;
            }
        } else {
            if (f[7] < -0.882695615) {
                return 0.00746464124;
            } else {
                return -0.0078386208;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0138724586;
            } else {
                return 0.000988843967;
            }
        } else {
            if (f[5] < 1.01324117) {
                return 0.00141138874;
            } else {
                return -0.00278469152;
            }
        }
    }
}

double evaluate_meta_tree_127(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[2] < 0.903505504) {
                return -0.00423111208;
            } else {
                return 0.0133332089;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00221743598;
            } else {
                return -0.0204209741;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0127331167;
            } else {
                return -0.0291829202;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0177118313;
            } else {
                return 0.000298102706;
            }
        }
    }
}

double evaluate_meta_tree_128(double &f[]) {
    if (f[0] < -1.66689301) {
        if (f[2] < 0.0338220447) {
            if (f[5] < 1.22364473) {
                return -0.0257456191;
            } else {
                return 0.00940357149;
            }
        } else {
            if (f[5] < 0.769702196) {
                return -0.00664563989;
            } else {
                return 0.0195310805;
            }
        }
    } else {
        if (f[8] < 0.549369514) {
            if (f[8] < -1.10483754) {
                return 0.00345568778;
            } else {
                return -0.00095624564;
            }
        } else {
            if (f[4] < 0.282096893) {
                return 0.00487934565;
            } else {
                return -0.000776960107;
            }
        }
    }
}

double evaluate_meta_tree_129(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.225739405) {
                return 0.0314653814;
            } else {
                return 0.00144197454;
            }
        } else {
            if (f[1] < -1.03017294) {
                return 0.00308738835;
            } else {
                return -0.000616321631;
            }
        }
    } else {
        if (f[8] < 1.07459259) {
            if (f[2] < -0.197729483) {
                return 0.00052281341;
            } else {
                return 0.0254051425;
            }
        } else {
            if (f[4] < 1.29352868) {
                return -0.0207215529;
            } else {
                return -0.00214858586;
            }
        }
    }
}

double evaluate_meta_tree_130(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[5] < 2.26741481) {
            if (f[0] < 1.11461759) {
                return -0.00291044055;
            } else {
                return 0.00886711478;
            }
        } else {
            if (f[2] < 1.58623445) {
                return -0.0191914774;
            } else {
                return 0.0159000847;
            }
        }
    } else {
        if (f[0] < 0.645920277) {
            if (f[0] < 0.113874659) {
                return 4.93070802e-05;
            } else {
                return 0.00278114178;
            }
        } else {
            if (f[3] < -0.98748517) {
                return 0.00602065539;
            } else {
                return -0.00270826067;
            }
        }
    }
}

double evaluate_meta_tree_131(double &f[]) {
    if (f[1] < 2.06438828) {
        if (f[3] < -0.699636102) {
            if (f[5] < 1.97747576) {
                return -0.00278627011;
            } else {
                return 0.00745128794;
            }
        } else {
            if (f[3] < -0.518025935) {
                return 0.00425999006;
            } else {
                return 0.000163917721;
            }
        }
    } else {
        if (f[8] < 1.16788507) {
            if (f[2] < 0.848252594) {
                return -0.020483885;
            } else {
                return -0.000677098753;
            }
        } else {
            if (f[5] < 0.899194479) {
                return 0.0559765883;
            } else {
                return -0.00467687845;
            }
        }
    }
}

double evaluate_meta_tree_132(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[4] < 1.62132287) {
            if (f[4] < 1.02172446) {
                return 0.000868747768;
            } else {
                return -0.00703288196;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00899330433;
            } else {
                return 0.0458414815;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00225988915;
            } else {
                return -0.0297077931;
            }
        } else {
            if (f[2] < -1.34023845) {
                return -0.0291600209;
            } else {
                return -0.00244687102;
            }
        }
    }
}

double evaluate_meta_tree_133(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[5] < 0.769702196) {
                return -0.0145735247;
            } else {
                return 0.00683968281;
            }
        } else {
            if (f[7] < -1.303895) {
                return 0.00449528312;
            } else {
                return -0.000257028616;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[4] < 0.862586141) {
                return 0.00960859749;
            } else {
                return 0.0431968234;
            }
        } else {
            if (f[5] < -0.648974836) {
                return 0.053700991;
            } else {
                return -0.00562781421;
            }
        }
    }
}

double evaluate_meta_tree_134(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[1] < -1.76743913) {
            if (f[5] < 0.43784681) {
                return 0.0227351505;
            } else {
                return -0.00226420769;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000792321458;
            } else {
                return 0.00209468673;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[2] < -0.197729483) {
                return 0.000286648137;
            } else {
                return 0.0285166595;
            }
        } else {
            if (f[8] < 1.44587219) {
                return 0.000590255135;
            } else {
                return -0.0223371014;
            }
        }
    }
}

double evaluate_meta_tree_135(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[1] < -2.22324824) {
            if (f[7] < 0.164682344) {
                return -0.023936322;
            } else {
                return 0.0135252373;
            }
        } else {
            if (f[0] < 0.645920277) {
                return 0.000439830881;
            } else {
                return -0.00187414407;
            }
        }
    } else {
        if (f[4] < -0.159837157) {
            return -0.0234519094;
        } else {
            if (f[4] < 0.14815478) {
                return 0.0499124192;
            } else {
                return 0.0123158759;
            }
        }
    }
}

double evaluate_meta_tree_136(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[4] < -2.19129109) {
            if (f[1] < 0.320598692) {
                return 0.010072167;
            } else {
                return 0.0764982849;
            }
        } else {
            if (f[3] < -0.711380064) {
                return -0.0032338996;
            } else {
                return -3.03924298e-05;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[7] < 0.164682344) {
                return 0.00641266955;
            } else {
                return 0.00176710391;
            }
        } else {
            if (f[3] < 1.4542923) {
                return -0.00957872905;
            } else {
                return 0.000746333739;
            }
        }
    }
}

double evaluate_meta_tree_137(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.21296334) {
            if (f[0] < -0.383884877) {
                return -0.00198805006;
            } else {
                return -0.027067;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00420430023;
            } else {
                return -0.00419216976;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[2] < 0.221994698) {
                return 0.0401364714;
            } else {
                return -0.0283528399;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00518732145;
            } else {
                return 0.0013849145;
            }
        }
    }
}

double evaluate_meta_tree_138(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0199698564;
            } else {
                return -0.00253543607;
            }
        } else {
            if (f[7] < -1.303895) {
                return 0.00436019851;
            } else {
                return -0.00025044856;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[4] < 0.862586141) {
                return 0.00930613466;
            } else {
                return 0.0411133617;
            }
        } else {
            if (f[5] < -0.648974836) {
                return 0.0514916889;
            } else {
                return -0.0055208574;
            }
        }
    }
}

double evaluate_meta_tree_139(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0276444145;
            } else {
                return -0.00406856416;
            }
        } else {
            if (f[1] < -0.617830217) {
                return 0.00173091225;
            } else {
                return -0.00078873802;
            }
        }
    } else {
        if (f[8] < 0.835825861) {
            if (f[2] < -0.197729483) {
                return -0.000162425364;
            } else {
                return 0.0258634686;
            }
        } else {
            if (f[5] < 0.899194479) {
                return -0.00142330595;
            } else {
                return -0.0224769395;
            }
        }
    }
}

double evaluate_meta_tree_140(double &f[]) {
    if (f[8] < -1.61720705) {
        if (f[2] < -0.18213667) {
            if (f[1] < -1.12717307) {
                return 0.0319762565;
            } else {
                return -0.000975049683;
            }
        } else {
            if (f[2] < 0.647000253) {
                return -0.0185843091;
            } else {
                return 0.000331134041;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[7] < 2.01427317) {
                return 0.000108188593;
            } else {
                return -0.00973997172;
            }
        } else {
            if (f[0] < -1.04191673) {
                return -0.0147158075;
            } else {
                return 0.00958683994;
            }
        }
    }
}

double evaluate_meta_tree_141(double &f[]) {
    if (f[0] < -0.975028276) {
        if (f[1] < -0.662262738) {
            if (f[7] < 2.01427317) {
                return -0.00591214141;
            } else {
                return 0.0285199825;
            }
        } else {
            if (f[3] < -0.155514181) {
                return 0.00617371267;
            } else {
                return -0.00206292258;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[3] < -0.0844796002) {
                return -0.00013227723;
            } else {
                return 0.0146722151;
            }
        } else {
            if (f[1] < 0.966418505) {
                return 0.00051702623;
            } else {
                return -0.00302555761;
            }
        }
    }
}

double evaluate_meta_tree_142(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.0062161847;
            } else {
                return -0.00666974811;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00222664024;
            } else {
                return -0.0201441236;
            }
        }
    } else {
        if (f[0] < -0.665902972) {
            if (f[5] < 1.57331765) {
                return 0.00394886034;
            } else {
                return 0.0235713776;
            }
        } else {
            if (f[8] < -1.18002284) {
                return -0.00793683808;
            } else {
                return 0.00014436616;
            }
        }
    }
}

double evaluate_meta_tree_143(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[5] < -0.485459775) {
            if (f[7] < -0.611591339) {
                return 0.00744175678;
            } else {
                return 0.000319354353;
            }
        } else {
            if (f[3] < 0.992228925) {
                return -0.00174305961;
            } else {
                return 0.00284149568;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[5] < 1.97747576) {
                return 0.00231608585;
            } else {
                return 0.0143054416;
            }
        } else {
            if (f[8] < -0.0155891962) {
                return 0.0242099296;
            } else {
                return -0.0154085979;
            }
        }
    }
}

double evaluate_meta_tree_144(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[1] < -1.76743913) {
            if (f[5] < 0.43784681) {
                return 0.0215286892;
            } else {
                return -0.00241854903;
            }
        } else {
            if (f[0] < 0.909485996) {
                return -0.000676482043;
            } else {
                return 0.00257830857;
            }
        }
    } else {
        if (f[1] < 2.37942123) {
            if (f[5] < -0.465355903) {
                return 0.027598327;
            } else {
                return 0.00185469782;
            }
        } else {
            if (f[8] < 0.835825861) {
                return 0.0346695185;
            } else {
                return -0.0104767755;
            }
        }
    }
}

double evaluate_meta_tree_145(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[5] < 2.26741481) {
            if (f[0] < 1.11461759) {
                return -0.0028244094;
            } else {
                return 0.00870282669;
            }
        } else {
            if (f[2] < 1.58623445) {
                return -0.0188913215;
            } else {
                return 0.0155561958;
            }
        }
    } else {
        if (f[0] < 0.645920277) {
            if (f[4] < 0.27433756) {
                return -8.34789244e-05;
            } else {
                return 0.00252779806;
            }
        } else {
            if (f[3] < -0.98748517) {
                return 0.00587503705;
            } else {
                return -0.00258016004;
            }
        }
    }
}

double evaluate_meta_tree_146(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[5] < -0.83517772) {
                return 0.00557387667;
            } else {
                return -0.000404999679;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.0199941006;
            } else {
                return -0.00287955254;
            }
        }
    } else {
        if (f[5] < 0.199363336) {
            if (f[8] < -0.0556765571) {
                return 0.02885109;
            } else {
                return 0.00489105051;
            }
        } else {
            if (f[0] < -0.31426236) {
                return -0.00580650335;
            } else {
                return 0.00297847926;
            }
        }
    }
}

double evaluate_meta_tree_147(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[4] < 1.62132287) {
            if (f[4] < 1.02172446) {
                return 0.000845049624;
            } else {
                return -0.0069061364;
            }
        } else {
            if (f[3] < -0.140297294) {
                return -0.0287586004;
            } else {
                return 0.0175619591;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00219217758;
            } else {
                return -0.0295475032;
            }
        } else {
            if (f[8] < -0.319508225) {
                return 0.0414025746;
            } else {
                return -0.00309118116;
            }
        }
    }
}

double evaluate_meta_tree_148(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[3] < 1.96079302) {
            if (f[3] < 1.02796721) {
                return -0.000888779236;
            } else {
                return 0.003907267;
            }
        } else {
            if (f[5] < 2.71545076) {
                return -0.0233843382;
            } else {
                return -0.00460627256;
            }
        }
    } else {
        if (f[4] < 0.282096893) {
            if (f[2] < 0.292328924) {
                return 0.00198673829;
            } else {
                return 0.0113558872;
            }
        } else {
            if (f[0] < 1.72220576) {
                return -0.00174310058;
            } else {
                return 0.022581486;
            }
        }
    }
}

double evaluate_meta_tree_149(double &f[]) {
    if (f[0] < 1.34784722) {
        if (f[1] < -1.33478355) {
            if (f[5] < 0.989987016) {
                return 0.0101433508;
            } else {
                return -0.0072590299;
            }
        } else {
            if (f[2] < 1.8694005) {
                return -0.000690720975;
            } else {
                return 0.00945504755;
            }
        }
    } else {
        if (f[1] < 2.37942123) {
            if (f[5] < 1.53045237) {
                return 0.00634512305;
            } else {
                return -0.0119877718;
            }
        } else {
            if (f[5] < 0.675036609) {
                return 0.0357057527;
            } else {
                return -0.000847142772;
            }
        }
    }
}

double evaluate_meta_tree_150(double &f[]) {
    if (f[2] < 1.8694005) {
        if (f[7] < 2.01427317) {
            if (f[4] < 2.50719428) {
                return -3.99674573e-05;
            } else {
                return 0.0170997512;
            }
        } else {
            if (f[0] < -0.896542609) {
                return 0.0165043827;
            } else {
                return -0.0103038521;
            }
        }
    } else {
        if (f[8] < -0.264259368) {
            if (f[8] < -0.379841208) {
                return 0.00869852863;
            } else {
                return 0.0542410389;
            }
        } else {
            if (f[7] < 0.637940526) {
                return -0.0104477452;
            } else {
                return 0.0141949179;
            }
        }
    }
}

double evaluate_meta_tree_151(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[5] < -0.721313536) {
            if (f[4] < 0.235285908) {
                return 0.00566495908;
            } else {
                return -0.00487776473;
            }
        } else {
            if (f[3] < 0.0843367502) {
                return -0.00235681375;
            } else {
                return 0.000556338986;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0133615183;
            } else {
                return 0.000889378076;
            }
        } else {
            if (f[5] < 1.01324117) {
                return 0.00134414353;
            } else {
                return -0.00267897989;
            }
        }
    }
}

double evaluate_meta_tree_152(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[5] < -0.583981514) {
            if (f[2] < -0.683066666) {
                return -0.0302735809;
            } else {
                return 0.00127412006;
            }
        } else {
            if (f[3] < -0.883044124) {
                return 0.0412637331;
            } else {
                return -0.00644953037;
            }
        }
    } else {
        if (f[2] < 1.34327388) {
            if (f[4] < -1.15942764) {
                return -0.00485397549;
            } else {
                return 0.00189850817;
            }
        } else {
            if (f[7] < -0.714137852) {
                return 0.0139514804;
            } else {
                return -0.00943515263;
            }
        }
    }
}

double evaluate_meta_tree_153(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[5] < 0.593657792) {
            if (f[5] < -0.814270735) {
                return 0.0282391962;
            } else {
                return -0.0193743724;
            }
        } else {
            if (f[0] < -1.95236576) {
                return 0.0204302538;
            } else {
                return -0.018739609;
            }
        }
    } else {
        if (f[7] < 0.651256502) {
            if (f[1] < 0.750065565) {
                return 6.465552e-05;
            } else {
                return -0.00372480089;
            }
        } else {
            if (f[0] < -0.989682615) {
                return 0.0122866789;
            } else {
                return 0.00163204398;
            }
        }
    }
}

double evaluate_meta_tree_154(double &f[]) {
    if (f[0] < -2.2552712) {
        if (f[2] < 0.337951213) {
            if (f[3] < -0.699636102) {
                return 0.00841219071;
            } else {
                return 0.0362441763;
            }
        } else {
            if (f[7] < -0.734648108) {
                return 0.0217903778;
            } else {
                return -0.0136143444;
            }
        }
    } else {
        if (f[0] < 1.15781617) {
            if (f[1] < -0.617830217) {
                return 0.00166282302;
            } else {
                return -0.00103972724;
            }
        } else {
            if (f[6] < 1) {
                return 0.00420634402;
            } else {
                return 0.0406914465;
            }
        }
    }
}

double evaluate_meta_tree_155(double &f[]) {
    if (f[8] < -1.61720705) {
        if (f[2] < -0.18213667) {
            if (f[1] < -1.12717307) {
                return 0.0308480095;
            } else {
                return -0.000944000203;
            }
        } else {
            if (f[2] < 0.647000253) {
                return -0.0182873588;
            } else {
                return 0.000484854216;
            }
        }
    } else {
        if (f[2] < 1.58623445) {
            if (f[7] < 2.01427317) {
                return 0.000105012943;
            } else {
                return -0.0093559064;
            }
        } else {
            if (f[0] < -1.04191673) {
                return -0.0145529835;
            } else {
                return 0.00907601975;
            }
        }
    }
}

double evaluate_meta_tree_156(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[8] < -1.61720705) {
                return 0.0056828903;
            } else {
                return -0.00038149688;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.0197212975;
            } else {
                return -0.00263178884;
            }
        }
    } else {
        if (f[5] < 0.199363336) {
            if (f[1] < -0.54158932) {
                return 0.0167261176;
            } else {
                return 0.00377310673;
            }
        } else {
            if (f[0] < -0.31426236) {
                return -0.00567020802;
            } else {
                return 0.00290940213;
            }
        }
    }
}

double evaluate_meta_tree_157(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[2] < 0.903505504) {
            if (f[2] < 0.292328924) {
                return -0.00342881563;
            } else {
                return -0.016316032;
            }
        } else {
            if (f[7] < 0.414304435) {
                return 0.0172393247;
            } else {
                return -0.0201492328;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[4] < 0.789403021) {
                return 0.0132252844;
            } else {
                return -0.0177813601;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0174333174;
            } else {
                return 0.000272522389;
            }
        }
    }
}

double evaluate_meta_tree_158(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[5] < 0.769702196) {
                return -0.013912526;
            } else {
                return 0.00679758331;
            }
        } else {
            if (f[7] < -1.303895) {
                return 0.00423509115;
            } else {
                return -0.000244698807;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[5] < 1.70352268) {
                return 0.0134284142;
            } else {
                return 0.0570864975;
            }
        } else {
            if (f[5] < -0.53068167) {
                return 0.040982198;
            } else {
                return -0.00615701405;
            }
        }
    }
}

double evaluate_meta_tree_159(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[0] < -2.2552712) {
            if (f[2] < -0.225739405) {
                return 0.0276599973;
            } else {
                return 0.000409196102;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.00065869157;
            } else {
                return 0.00201851688;
            }
        }
    } else {
        if (f[8] < 1.07459259) {
            if (f[2] < -0.197729483) {
                return 0.000120720644;
            } else {
                return 0.0220766179;
            }
        } else {
            if (f[4] < 1.29352868) {
                return -0.0205002334;
            } else {
                return -0.00164289179;
            }
        }
    }
}

double evaluate_meta_tree_160(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[5] < 2.26741481) {
            if (f[0] < 1.11461759) {
                return -0.00273013744;
            } else {
                return 0.00853914954;
            }
        } else {
            if (f[2] < 1.58623445) {
                return -0.0186586436;
            } else {
                return 0.0150621636;
            }
        }
    } else {
        if (f[0] < 0.645920277) {
            if (f[0] < 0.113874659) {
                return 8.11072596e-08;
            } else {
                return 0.00265135057;
            }
        } else {
            if (f[3] < -0.98748517) {
                return 0.00569604523;
            } else {
                return -0.00250102254;
            }
        }
    }
}

double evaluate_meta_tree_161(double &f[]) {
    if (f[0] < -0.975028276) {
        if (f[1] < -0.662262738) {
            if (f[7] < 1.31135154) {
                return -0.00606680848;
            } else {
                return 0.0108639998;
            }
        } else {
            if (f[3] < -0.155514181) {
                return 0.00605206005;
            } else {
                return -0.00198462908;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[3] < -0.0844796002) {
                return -0.000303031935;
            } else {
                return 0.0138243539;
            }
        } else {
            if (f[1] < 0.966418505) {
                return 0.000497043948;
            } else {
                return -0.00290085166;
            }
        }
    }
}

double evaluate_meta_tree_162(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.24507833) {
            if (f[1] < 1.73610723) {
                return -0.0213380028;
            } else {
                return 0.0557699278;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00392689696;
            } else {
                return -0.00404451927;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[2] < 0.221994698) {
                return 0.0381755196;
            } else {
                return -0.028159691;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.0049751536;
            } else {
                return 0.00131356984;
            }
        }
    }
}

double evaluate_meta_tree_163(double &f[]) {
    if (f[8] < 0.549369514) {
        if (f[3] < 1.96079302) {
            if (f[3] < 1.02796721) {
                return -0.00086020364;
            } else {
                return 0.00381386653;
            }
        } else {
            if (f[5] < 2.71545076) {
                return -0.0231253896;
            } else {
                return -0.00442542089;
            }
        }
    } else {
        if (f[2] < -1.09507775) {
            if (f[7] < 0.486810774) {
                return 0.0211415496;
            } else {
                return 0.0033276591;
            }
        } else {
            if (f[5] < -0.759402156) {
                return 0.015724007;
            } else {
                return 0.000727814215;
            }
        }
    }
}

double evaluate_meta_tree_164(double &f[]) {
    if (f[0] < 1.83004999) {
        if (f[1] < -1.33478355) {
            if (f[5] < -0.128686339) {
                return 0.015723791;
            } else {
                return 0.00107315322;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000880792271;
            } else {
                return 0.00196731067;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[2] < -0.197729483) {
                return -7.89371115e-05;
            } else {
                return 0.0250958446;
            }
        } else {
            if (f[8] < 1.44587219) {
                return -0.000315628771;
            } else {
                return -0.0217374973;
            }
        }
    }
}

double evaluate_meta_tree_165(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < -0.924897909) {
            if (f[3] < 0.655889094) {
                return -0.00111854018;
            } else {
                return -0.00986039825;
            }
        } else {
            if (f[1] < -1.08474684) {
                return 0.00535859214;
            } else {
                return 1.50965807e-05;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.00378720998;
            } else {
                return 0.0433889739;
            }
        } else {
            if (f[0] < -0.23440364) {
                return -0.00271932757;
            } else {
                return 0.0151969688;
            }
        }
    }
}

double evaluate_meta_tree_166(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[4] < -2.19129109) {
            if (f[1] < 0.320598692) {
                return 0.0096980473;
            } else {
                return 0.072160244;
            }
        } else {
            if (f[3] < -0.711380064) {
                return -0.00311984518;
            } else {
                return -2.99089497e-05;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[2] < -0.59138298) {
                return -0.000904737157;
            } else {
                return 0.00334224897;
            }
        } else {
            if (f[3] < 1.4542923) {
                return -0.0093450984;
            } else {
                return 0.000874113466;
            }
        }
    }
}

double evaluate_meta_tree_167(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[4] < 1.62132287) {
            if (f[4] < 1.02172446) {
                return 0.000812615268;
            } else {
                return -0.00678064767;
            }
        } else {
            if (f[3] < -0.140297294) {
                return -0.0285772365;
            } else {
                return 0.0169118345;
            }
        }
    } else {
        if (f[2] < -1.34023845) {
            return -0.0289815571;
        } else {
            if (f[2] < -1.31682527) {
                return 0.0577481166;
            } else {
                return -0.00316577894;
            }
        }
    }
}

double evaluate_meta_tree_168(double &f[]) {
    if (f[7] < 0.651256502) {
        if (f[5] < -0.311641991) {
            if (f[1] < 0.750065565) {
                return 0.00232471433;
            } else {
                return -0.0084304912;
            }
        } else {
            if (f[5] < -0.24104166) {
                return -0.00779047748;
            } else {
                return -0.000946929329;
            }
        }
    } else {
        if (f[3] < 1.81086767) {
            if (f[8] < -0.582102537) {
                return -0.0133603988;
            } else {
                return 0.00292496267;
            }
        } else {
            if (f[4] < 1.87506628) {
                return -0.0237099323;
            } else {
                return -0.000767936173;
            }
        }
    }
}

double evaluate_meta_tree_169(double &f[]) {
    if (f[0] < 1.34784722) {
        if (f[1] < -1.33478355) {
            if (f[5] < 0.989987016) {
                return 0.00935798045;
            } else {
                return -0.00719377352;
            }
        } else {
            if (f[4] < -0.251987576) {
                return -0.00171145133;
            } else {
                return 8.73182362e-05;
            }
        }
    } else {
        if (f[1] < 2.37942123) {
            if (f[5] < 1.53045237) {
                return 0.00582981389;
            } else {
                return -0.0119275628;
            }
        } else {
            if (f[5] < 0.675036609) {
                return 0.0334943458;
            } else {
                return -0.00115029083;
            }
        }
    }
}

double evaluate_meta_tree_170(double &f[]) {
    if (f[4] < -0.339147002) {
        if (f[3] < -0.952752829) {
            if (f[4] < -0.529866278) {
                return 0.00404753536;
            } else {
                return -0.00927630253;
            }
        } else {
            if (f[0] < 0.56007576) {
                return -0.000954991381;
            } else {
                return -0.00750989234;
            }
        }
    } else {
        if (f[4] < -0.121787123) {
            if (f[1] < -1.10609031) {
                return 0.0151423244;
            } else {
                return 0.00289915432;
            }
        } else {
            if (f[5] < 0.312420905) {
                return -0.00117759744;
            } else {
                return 0.00201558485;
            }
        }
    }
}

double evaluate_meta_tree_171(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[5] < -0.721313536) {
            if (f[1] < 0.806270838) {
                return 0.00468124403;
            } else {
                return -0.011129884;
            }
        } else {
            if (f[3] < 0.0843367502) {
                return -0.00228336896;
            } else {
                return 0.000542735565;
            }
        }
    } else {
        if (f[4] < -1.19378555) {
            if (f[0] < 0.095344983) {
                return 0.0137571199;
            } else {
                return 0.0011812835;
            }
        } else {
            if (f[1] < -0.153442234) {
                return 0.00254845433;
            } else {
                return -0.000288402778;
            }
        }
    }
}

double evaluate_meta_tree_172(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[5] < -0.583981514) {
            if (f[2] < -0.683066666) {
                return -0.0300781578;
            } else {
                return 0.00129992247;
            }
        } else {
            if (f[3] < -0.883044124) {
                return 0.0395866446;
            } else {
                return -0.00625925371;
            }
        }
    } else {
        if (f[2] < 1.34327388) {
            if (f[2] < -1.4817332) {
                return -0.00955229532;
            } else {
                return 0.00157211313;
            }
        } else {
            if (f[7] < -0.714137852) {
                return 0.0133529035;
            } else {
                return -0.00925014075;
            }
        }
    }
}

double evaluate_meta_tree_173(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[2] < 1.46987176) {
            if (f[5] < 0.523699343) {
                return -0.0195265785;
            } else {
                return 0.00069395965;
            }
        } else {
            if (f[4] < 0.935132205) {
                return 0.0544186309;
            } else {
                return -0.0174905341;
            }
        }
    } else {
        if (f[8] < 0.945901334) {
            if (f[5] < -0.339252353) {
                return 0.00128069555;
            } else {
                return -0.00100476469;
            }
        } else {
            if (f[2] < -1.34023845) {
                return 0.0222306177;
            } else {
                return 0.0023227823;
            }
        }
    }
}

double evaluate_meta_tree_174(double &f[]) {
    if (f[1] < -2.22324824) {
        if (f[8] < 0.129053533) {
            if (f[3] < -1.73790622) {
                return -0.0187552292;
            } else {
                return 0.0402124636;
            }
        } else {
            if (f[3] < -0.49158442) {
                return -0.0203601159;
            } else {
                return 0.0322475433;
            }
        }
    } else {
        if (f[0] < 1.15781617) {
            if (f[1] < -0.617830217) {
                return 0.00163321372;
            } else {
                return -0.00098702067;
            }
        } else {
            if (f[6] < 1) {
                return 0.00382956606;
            } else {
                return 0.038278684;
            }
        }
    }
}

double evaluate_meta_tree_175(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[5] < 2.26741481) {
            if (f[0] < -0.256470829) {
                return -0.00519616995;
            } else {
                return 4.04327147e-05;
            }
        } else {
            if (f[2] < 1.58623445) {
                return -0.0184459481;
            } else {
                return 0.0148128169;
            }
        }
    } else {
        if (f[0] < 0.645920277) {
            if (f[4] < 0.27433756) {
                return -0.000114506031;
            } else {
                return 0.00241520209;
            }
        } else {
            if (f[8] < 1.68745327) {
                return -0.00134652946;
            } else {
                return -0.0132263331;
            }
        }
    }
}

double evaluate_meta_tree_176(double &f[]) {
    if (f[0] < -0.975028276) {
        if (f[1] < -0.662262738) {
            if (f[7] < 2.01427317) {
                return -0.00560316211;
            } else {
                return 0.027055338;
            }
        } else {
            if (f[0] < -1.57202971) {
                return 0.0112631591;
            } else {
                return -0.00084773585;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[3] < -0.0844796002) {
                return -0.000266331394;
            } else {
                return 0.0133033162;
            }
        } else {
            if (f[1] < 0.966418505) {
                return 0.00048223362;
            } else {
                return -0.00279925228;
            }
        }
    }
}

double evaluate_meta_tree_177(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[8] < 0.252857864) {
            if (f[4] < -0.579055786) {
                return 0.00614176877;
            } else {
                return -0.00640113;
            }
        } else {
            if (f[0] < -1.13067496) {
                return 0.00243507768;
            } else {
                return -0.0197263956;
            }
        }
    } else {
        if (f[0] < -0.665902972) {
            if (f[5] < 1.57331765) {
                return 0.00377919781;
            } else {
                return 0.0226797741;
            }
        } else {
            if (f[8] < -1.18002284) {
                return -0.0078233676;
            } else {
                return 0.000127799736;
            }
        }
    }
}

double evaluate_meta_tree_178(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.0192815792;
            } else {
                return -0.00190029223;
            }
        } else {
            if (f[1] < -1.91067636) {
                return 0.0161754824;
            } else {
                return -7.15525457e-05;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[4] < 0.862586141) {
                return 0.008098525;
            } else {
                return 0.0377124213;
            }
        } else {
            if (f[1] < 0.409948021) {
                return 0.00733780488;
            } else {
                return -0.0177449528;
            }
        }
    }
}

double evaluate_meta_tree_179(double &f[]) {
    if (f[1] < -2.22324824) {
        if (f[8] < 0.129053533) {
            if (f[3] < -1.73790622) {
                return -0.0184808355;
            } else {
                return 0.039064955;
            }
        } else {
            if (f[3] < -0.49158442) {
                return -0.0199870281;
            } else {
                return 0.0313905701;
            }
        }
    } else {
        if (f[1] < 1.48934865) {
            if (f[1] < -0.566395581) {
                return 0.00144855538;
            } else {
                return -0.000817274384;
            }
        } else {
            if (f[5] < 0.331580073) {
                return 0.0147429099;
            } else {
                return -0.00187444594;
            }
        }
    }
}

double evaluate_meta_tree_180(double &f[]) {
    if (f[4] < 2.50719428) {
        if (f[1] < -2.22324824) {
            if (f[7] < 0.164682344) {
                return -0.0233986434;
            } else {
                return 0.0132889925;
            }
        } else {
            if (f[0] < -1.79142714) {
                return 0.00906286296;
            } else {
                return -8.03588046e-05;
            }
        }
    } else {
        if (f[3] < 0.0515333228) {
            if (f[1] < -0.749377131) {
                return 0.0211730823;
            } else {
                return -0.0268839449;
            }
        } else {
            if (f[0] < 1.44641376) {
                return 0.0303775407;
            } else {
                return -0.0113664931;
            }
        }
    }
}

double evaluate_meta_tree_181(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[5] < -0.83517772) {
                return 0.00520373229;
            } else {
                return -0.000383870385;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.0193070825;
            } else {
                return -0.00199231505;
            }
        }
    } else {
        if (f[8] < -0.160652995) {
            if (f[7] < 1.13714707) {
                return 0.048116833;
            } else {
                return 0.00625420827;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.00788418576;
            } else {
                return 0.00101412123;
            }
        }
    }
}

double evaluate_meta_tree_182(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.24507833) {
            if (f[1] < -1.76743913) {
                return 0.0545400791;
            } else {
                return -0.021068437;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00385163212;
            } else {
                return -0.00388523447;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[0] < 0.451554656) {
                return 0.00164277409;
            } else {
                return 0.0557943881;
            }
        } else {
            if (f[7] < -0.643692672) {
                return 0.00395454047;
            } else {
                return -0.00015633872;
            }
        }
    }
}

double evaluate_meta_tree_183(double &f[]) {
    if (f[7] < 0.542411983) {
        if (f[8] < -0.540752888) {
            if (f[4] < 0.289133519) {
                return 0.00277707982;
            } else {
                return -0.00268767844;
            }
        } else {
            if (f[8] < 0.289221942) {
                return -0.00265274523;
            } else {
                return 0.00112473872;
            }
        }
    } else {
        if (f[3] < -1.63246799) {
            if (f[4] < 0.708717287) {
                return 0.00533995777;
            } else {
                return 0.0508485101;
            }
        } else {
            if (f[2] < 1.46987176) {
                return 0.00204453594;
            } else {
                return -0.00711311027;
            }
        }
    }
}

double evaluate_meta_tree_184(double &f[]) {
    if (f[0] < 2.00178194) {
        if (f[1] < -1.76743913) {
            if (f[4] < -0.295399517) {
                return 0.00293176132;
            } else {
                return 0.025973523;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000654362026;
            } else {
                return 0.00187322486;
            }
        }
    } else {
        if (f[5] < 0.146123737) {
            if (f[4] < -0.59862864) {
                return -0.0182241276;
            } else {
                return 0.0229228083;
            }
        } else {
            if (f[8] < 0.747675538) {
                return 0.00793998968;
            } else {
                return -0.0139317727;
            }
        }
    }
}

double evaluate_meta_tree_185(double &f[]) {
    if (f[8] < -1.61720705) {
        if (f[2] < -0.402236015) {
            if (f[1] < -0.439924061) {
                return 0.0222711246;
            } else {
                return -0.00228445698;
            }
        } else {
            if (f[7] < 0.0121863708) {
                return -0.0117759779;
            } else {
                return 0.0348673984;
            }
        }
    } else {
        if (f[2] < 1.8694005) {
            if (f[0] < -0.937538922) {
                return -0.00251368457;
            } else {
                return 0.000341349078;
            }
        } else {
            if (f[8] < -0.264259368) {
                return 0.0229733475;
            } else {
                return 0.00403980911;
            }
        }
    }
}

double evaluate_meta_tree_186(double &f[]) {
    if (f[8] < 0.611430824) {
        if (f[4] < -2.19129109) {
            if (f[1] < 0.320598692) {
                return 0.0094688544;
            } else {
                return 0.0685839653;
            }
        } else {
            if (f[3] < -0.711380064) {
                return -0.00299863704;
            } else {
                return -3.21675216e-05;
            }
        }
    } else {
        if (f[3] < 1.17473137) {
            if (f[7] < 0.164682344) {
                return 0.0061303135;
            } else {
                return 0.00158224965;
            }
        } else {
            if (f[7] < -0.8391307) {
                return 0.0455695353;
            } else {
                return -0.00452054152;
            }
        }
    }
}

double evaluate_meta_tree_187(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[2] < 0.903505504) {
            if (f[2] < 0.292328924) {
                return -0.00322588766;
            } else {
                return -0.0159872677;
            }
        } else {
            if (f[7] < 0.414304435) {
                return 0.0167861525;
            } else {
                return -0.0196779761;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0119009856;
            } else {
                return -0.0289740153;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0171189066;
            } else {
                return 0.000248763681;
            }
        }
    }
}

double evaluate_meta_tree_188(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.019018203;
            } else {
                return -0.00179239549;
            }
        } else {
            if (f[7] < -1.303895) {
                return 0.00412328076;
            } else {
                return -0.000239403904;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[4] < 0.862586141) {
                return 0.00780003006;
            } else {
                return 0.0359179974;
            }
        } else {
            if (f[5] < -0.648974836) {
                return 0.0468094982;
            } else {
                return -0.0056100823;
            }
        }
    }
}

double evaluate_meta_tree_189(double &f[]) {
    if (f[0] < 1.15781617) {
        if (f[1] < -1.33478355) {
            if (f[5] < 0.989987016) {
                return 0.00874852762;
            } else {
                return -0.00705686072;
            }
        } else {
            if (f[2] < 1.8694005) {
                return -0.00068021199;
            } else {
                return 0.00945125148;
            }
        }
    } else {
        if (f[6] < 1) {
            if (f[5] < 1.53045237) {
                return 0.00498717651;
            } else {
                return -0.00961751956;
            }
        } else {
            if (f[5] < 0.582937419) {
                return 0.0484339856;
            } else {
                return -0.0104843108;
            }
        }
    }
}

double evaluate_meta_tree_190(double &f[]) {
    if (f[4] < -0.339147002) {
        if (f[3] < -0.952752829) {
            if (f[4] < -0.529866278) {
                return 0.00393380551;
            } else {
                return -0.00908640679;
            }
        } else {
            if (f[0] < 0.56007576) {
                return -0.000911264622;
            } else {
                return -0.00733102858;
            }
        }
    } else {
        if (f[4] < -0.121787123) {
            if (f[1] < -1.10609031) {
                return 0.014709319;
            } else {
                return 0.00283534755;
            }
        } else {
            if (f[5] < 0.312420905) {
                return -0.00115476002;
            } else {
                return 0.00193477422;
            }
        }
    }
}

double evaluate_meta_tree_191(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[5] < -0.83517772) {
                return 0.00503275124;
            } else {
                return -0.000374468509;
            }
        } else {
            if (f[8] < -0.775247097) {
                return 0.00430203835;
            } else {
                return -0.0176411606;
            }
        }
    } else {
        if (f[8] < -0.160652995) {
            if (f[7] < 1.13714707) {
                return 0.0459762476;
            } else {
                return 0.00611165073;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.00763197988;
            } else {
                return 0.000998209231;
            }
        }
    }
}

double evaluate_meta_tree_192(double &f[]) {
    if (f[7] < 0.71272862) {
        if (f[4] < 1.62132287) {
            if (f[4] < 1.02172446) {
                return 0.000772979518;
            } else {
                return -0.0066552232;
            }
        } else {
            if (f[3] < 2.23530412) {
                return 0.00782584678;
            } else {
                return 0.0422000699;
            }
        }
    } else {
        if (f[8] < -0.34709096) {
            if (f[8] < -0.845748901) {
                return 0.00213730591;
            } else {
                return -0.0293678641;
            }
        } else {
            if (f[8] < -0.301485926) {
                return 0.0327940099;
            } else {
                return -0.00285886647;
            }
        }
    }
}

double evaluate_meta_tree_193(double &f[]) {
    if (f[7] < 0.215811461) {
        if (f[8] < 0.297082245) {
            if (f[8] < -0.00668529188) {
                return -0.000466819009;
            } else {
                return -0.0067153112;
            }
        } else {
            if (f[4] < -1.65523922) {
                return 0.0238041487;
            } else {
                return 0.00259535457;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[5] < -0.0528584532) {
                return 0.015755957;
            } else {
                return 0.0812007189;
            }
        } else {
            if (f[2] < -0.502187014) {
                return 0.00503256824;
            } else {
                return 0.000282240071;
            }
        }
    }
}

double evaluate_meta_tree_194(double &f[]) {
    if (f[1] < 2.37942123) {
        if (f[1] < -2.22324824) {
            if (f[8] < 0.129053533) {
                return 0.0292363614;
            } else {
                return -0.00830230117;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000567145529;
            } else {
                return 0.00200221199;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[7] < -0.183636189) {
                return -0.00125855894;
            } else {
                return 0.0351446085;
            }
        } else {
            if (f[2] < 0.82174468) {
                return -0.0137806404;
            } else {
                return 0.0157775413;
            }
        }
    }
}

double evaluate_meta_tree_195(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[5] < 2.26741481) {
            if (f[0] < 1.11461759) {
                return -0.00260320376;
            } else {
                return 0.00844646525;
            }
        } else {
            if (f[2] < 1.58623445) {
                return -0.0181703065;
            } else {
                return 0.0146895451;
            }
        }
    } else {
        if (f[0] < 0.645920277) {
            if (f[0] < 0.113874659) {
                return -3.67119137e-05;
            } else {
                return 0.00252314634;
            }
        } else {
            if (f[7] < 1.193892) {
                return -0.000966091291;
            } else {
                return -0.00810741447;
            }
        }
    }
}

double evaluate_meta_tree_196(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[1] < 1.09404576) {
            if (f[1] < -1.08474684) {
                return -0.0047658952;
            } else {
                return 7.03181722e-05;
            }
        } else {
            if (f[7] < -0.882695615) {
                return 0.00760277826;
            } else {
                return -0.00720540155;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0125388345;
            } else {
                return 0.000787465659;
            }
        } else {
            if (f[5] < 1.01324117) {
                return 0.00123502396;
            } else {
                return -0.0025321315;
            }
        }
    }
}

double evaluate_meta_tree_197(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.21296334) {
            if (f[0] < -0.383884877) {
                return -0.00100509159;
            } else {
                return -0.0265170075;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00391780958;
            } else {
                return -0.00380568928;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[2] < 0.221994698) {
                return 0.0352671482;
            } else {
                return -0.0280460715;
            }
        } else {
            if (f[4] < -1.15942764) {
                return -0.00491863862;
            } else {
                return 0.00123738032;
            }
        }
    }
}

double evaluate_meta_tree_198(double &f[]) {
    if (f[5] < -0.485459775) {
        if (f[3] < 0.816725254) {
            if (f[7] < -0.611591339) {
                return 0.00714640832;
            } else {
                return 0.000492939842;
            }
        } else {
            if (f[0] < 0.107802898) {
                return -0.0124745527;
            } else {
                return 0.0625975505;
            }
        }
    } else {
        if (f[7] < 0.651256502) {
            if (f[7] < -1.78379381) {
                return 0.00764218578;
            } else {
                return -0.00134046504;
            }
        } else {
            if (f[3] < 1.81086767) {
                return 0.00222642766;
            } else {
                return -0.0130683882;
            }
        }
    }
}

double evaluate_meta_tree_199(double &f[]) {
    if (f[0] < 1.34784722) {
        if (f[1] < -1.33478355) {
            if (f[8] < 0.5306651) {
                return 0.00840198528;
            } else {
                return -0.00735663716;
            }
        } else {
            if (f[4] < -0.251987576) {
                return -0.00163680338;
            } else {
                return 0.000137188879;
            }
        }
    } else {
        if (f[8] < 0.835825861) {
            if (f[1] < 2.37942123) {
                return 0.00583825912;
            } else {
                return 0.0283029824;
            }
        } else {
            if (f[2] < 1.34327388) {
                return -0.00746411039;
            } else {
                return 0.0286896229;
            }
        }
    }
}

double evaluate_meta_tree_200(double &f[]) {
    if (f[4] < 2.50719428) {
        if (f[1] < -2.22324824) {
            if (f[7] < 0.164682344) {
                return -0.0230704527;
            } else {
                return 0.0130166253;
            }
        } else {
            if (f[0] < -1.79142714) {
                return 0.00883176085;
            } else {
                return -7.98183246e-05;
            }
        }
    } else {
        if (f[3] < 0.0515333228) {
            if (f[1] < -0.749377131) {
                return 0.0209190752;
            } else {
                return -0.0266699772;
            }
        } else {
            if (f[0] < 1.44641376) {
                return 0.0290986132;
            } else {
                return -0.0111797117;
            }
        }
    }
}

double evaluate_meta_tree_201(double &f[]) {
    if (f[0] < -0.975028276) {
        if (f[1] < -0.197903052) {
            if (f[5] < -0.714613557) {
                return 0.0133535741;
            } else {
                return -0.00459035067;
            }
        } else {
            if (f[8] < -1.61720705) {
                return 0.0522614606;
            } else {
                return 0.00190111902;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[1] < -0.566395581) {
                return 0.0207366049;
            } else {
                return 0.00334234769;
            }
        } else {
            if (f[1] < 0.0850012302) {
                return 0.00110519654;
            } else {
                return -0.000864445232;
            }
        }
    }
}

double evaluate_meta_tree_202(double &f[]) {
    if (f[0] < -0.665902972) {
        if (f[2] < -0.778128743) {
            if (f[1] < 0.436905593) {
                return -0.0134202233;
            } else {
                return 0.0409111194;
            }
        } else {
            if (f[3] < -0.898792088) {
                return 0.0223681163;
            } else {
                return 0.0023391624;
            }
        }
    } else {
        if (f[1] < -1.10609031) {
            if (f[8] < 0.129053533) {
                return -0.00391480979;
            } else {
                return -0.0294923168;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0173560996;
            } else {
                return -0.000114769595;
            }
        }
    }
}

double evaluate_meta_tree_203(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[5] < 0.593657792) {
            if (f[5] < -0.814270735) {
                return 0.0298342798;
            } else {
                return -0.0183893964;
            }
        } else {
            if (f[0] < -1.95236576) {
                return 0.0203325581;
            } else {
                return -0.0183183942;
            }
        }
    } else {
        if (f[8] < 0.945901334) {
            if (f[3] < -0.345641077) {
                return -0.00177831796;
            } else {
                return 0.000444293401;
            }
        } else {
            if (f[4] < 0.14815478) {
                return 0.00654021045;
            } else {
                return -0.000423623394;
            }
        }
    }
}

double evaluate_meta_tree_204(double &f[]) {
    if (f[0] < -2.2552712) {
        if (f[1] < -1.91067636) {
            if (f[8] < 0.71422559) {
                return 0.0277329236;
            } else {
                return -0.0277085435;
            }
        } else {
            if (f[8] < 0.179088086) {
                return -0.0129106762;
            } else {
                return 0.0347126573;
            }
        }
    } else {
        if (f[0] < 1.15781617) {
            if (f[1] < -0.617830217) {
                return 0.00149800174;
            } else {
                return -0.000895329693;
            }
        } else {
            if (f[6] < 1) {
                return 0.00335718063;
            } else {
                return 0.034752842;
            }
        }
    }
}

double evaluate_meta_tree_205(double &f[]) {
    if (f[0] < -0.908550382) {
        if (f[3] < 0.655889094) {
            if (f[3] < 0.427110851) {
                return -0.00211555022;
            } else {
                return 0.00979366805;
            }
        } else {
            if (f[2] < 1.24955213) {
                return -0.0149014611;
            } else {
                return 0.00136100943;
            }
        }
    } else {
        if (f[1] < -1.08474684) {
            if (f[8] < 2.21783733) {
                return 0.00418377668;
            } else {
                return 0.0620805435;
            }
        } else {
            if (f[0] < -0.84768188) {
                return 0.00776906917;
            } else {
                return -4.36582741e-05;
            }
        }
    }
}

double evaluate_meta_tree_206(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[4] < -2.19129109) {
                return 0.0129541503;
            } else {
                return -0.000271102268;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.0187498759;
            } else {
                return -0.000916734454;
            }
        }
    } else {
        if (f[8] < -0.160652995) {
            if (f[7] < 1.13714707) {
                return 0.0439376533;
            } else {
                return 0.00598772196;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.00737588806;
            } else {
                return 0.000983125414;
            }
        }
    }
}

double evaluate_meta_tree_207(double &f[]) {
    if (f[1] < -0.949965775) {
        if (f[2] < 0.903505504) {
            if (f[2] < 0.292328924) {
                return -0.00309755886;
            } else {
                return -0.0157311354;
            }
        } else {
            if (f[7] < 0.414304435) {
                return 0.0162211005;
            } else {
                return -0.0193574466;
            }
        }
    } else {
        if (f[1] < -0.832442343) {
            if (f[3] < 1.02796721) {
                return 0.0115194805;
            } else {
                return -0.02881594;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0166447032;
            } else {
                return 0.000232587525;
            }
        }
    }
}

double evaluate_meta_tree_208(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[2] < 0.0338220447) {
                return -0.018644575;
            } else {
                return -0.00152779487;
            }
        } else {
            if (f[1] < -1.91067636) {
                return 0.0156861395;
            } else {
                return -7.05441271e-05;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[5] < 1.70352268) {
                return 0.0114896633;
            } else {
                return 0.0509105325;
            }
        } else {
            if (f[1] < 0.409948021) {
                return 0.00690314686;
            } else {
                return -0.0174854752;
            }
        }
    }
}

double evaluate_meta_tree_209(double &f[]) {
    if (f[1] < 1.48934865) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0214790571;
            } else {
                return -0.004969317;
            }
        } else {
            if (f[1] < -0.566395581) {
                return 0.00132932712;
            } else {
                return -0.000744420802;
            }
        }
    } else {
        if (f[5] < 0.331580073) {
            if (f[2] < 0.0265336614) {
                return -0.000808115117;
            } else {
                return 0.02468119;
            }
        } else {
            if (f[2] < 1.22048283) {
                return -0.00427418342;
            } else {
                return 0.0122379428;
            }
        }
    }
}

double evaluate_meta_tree_210(double &f[]) {
    if (f[4] < -0.339147002) {
        if (f[0] < 0.56007576) {
            if (f[3] < 0.553257644) {
                return 0.000462551223;
            } else {
                return -0.009765069;
            }
        } else {
            if (f[2] < 0.903505504) {
                return -0.00531594269;
            } else {
                return 0.0443084501;
            }
        }
    } else {
        if (f[4] < -0.121787123) {
            if (f[3] < -0.126199737) {
                return 0.00635008095;
            } else {
                return 0.000135968497;
            }
        } else {
            if (f[5] < 0.312420905) {
                return -0.00112190074;
            } else {
                return 0.00188884011;
            }
        }
    }
}

double evaluate_meta_tree_211(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[5] < -0.721313536) {
            if (f[8] < 0.0950062275) {
                return 0.00505665271;
            } else {
                return -0.00592673244;
            }
        } else {
            if (f[3] < 0.0843367502) {
                return -0.00218747626;
            } else {
                return 0.000560934772;
            }
        }
    } else {
        if (f[4] < -1.19378555) {
            if (f[0] < 0.095344983) {
                return 0.0128799826;
            } else {
                return 0.00104971731;
            }
        } else {
            if (f[1] < -0.153442234) {
                return 0.0024296015;
            } else {
                return -0.000299484149;
            }
        }
    }
}

double evaluate_meta_tree_212(double &f[]) {
    if (f[0] < -0.665902972) {
        if (f[2] < -0.778128743) {
            if (f[1] < 0.436905593) {
                return -0.0131553113;
            } else {
                return 0.0391842239;
            }
        } else {
            if (f[3] < -0.898792088) {
                return 0.0215641204;
            } else {
                return 0.00228614965;
            }
        }
    } else {
        if (f[1] < -1.10609031) {
            if (f[8] < 0.129053533) {
                return -0.00371652539;
            } else {
                return -0.0293085333;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.0169447046;
            } else {
                return -0.00012378789;
            }
        }
    }
}

double evaluate_meta_tree_213(double &f[]) {
    if (f[5] < -0.485459775) {
        if (f[3] < 0.816725254) {
            if (f[7] < -0.611591339) {
                return 0.00693915738;
            } else {
                return 0.000465432327;
            }
        } else {
            if (f[0] < 0.107802898) {
                return -0.0123140067;
            } else {
                return 0.0592290759;
            }
        }
    } else {
        if (f[7] < 0.651256502) {
            if (f[3] < 0.992228925) {
                return -0.00156675617;
            } else {
                return 0.00279317773;
            }
        } else {
            if (f[2] < 1.58623445) {
                return 0.00222921162;
            } else {
                return -0.0104797035;
            }
        }
    }
}

double evaluate_meta_tree_214(double &f[]) {
    if (f[0] < 1.15781617) {
        if (f[1] < -1.33478355) {
            if (f[5] < -0.128686339) {
                return 0.0134654669;
            } else {
                return 0.000319046521;
            }
        } else {
            if (f[2] < 1.8694005) {
                return -0.000621356885;
            } else {
                return 0.00926133525;
            }
        }
    } else {
        if (f[6] < 1) {
            if (f[5] < 1.53045237) {
                return 0.00456643756;
            } else {
                return -0.00959035102;
            }
        } else {
            if (f[5] < 0.582937419) {
                return 0.0445580296;
            } else {
                return -0.011004095;
            }
        }
    }
}

double evaluate_meta_tree_215(double &f[]) {
    if (f[7] < -0.714137852) {
        if (f[7] < -0.722688854) {
            if (f[3] < -1.03086507) {
                return 0.00501081254;
            } else {
                return -0.00223585381;
            }
        } else {
            if (f[0] < -0.745684683) {
                return -0.0288451221;
            } else {
                return -0.0109856753;
            }
        }
    } else {
        if (f[7] < -0.457038403) {
            if (f[2] < -0.425015599) {
                return 0.00977281108;
            } else {
                return 0.00105623191;
            }
        } else {
            if (f[4] < 1.00404656) {
                return -0.00055107096;
            } else {
                return 0.00292891986;
            }
        }
    }
}

double evaluate_meta_tree_216(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[5] < -0.83517772) {
                return 0.00478991261;
            } else {
                return -0.00035982285;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.01849645;
            } else {
                return -0.000690290239;
            }
        }
    } else {
        if (f[2] < -0.580585599) {
            if (f[2] < -0.907948971) {
                return 0.00400529755;
            } else {
                return -0.00840873923;
            }
        } else {
            if (f[3] < 0.436915994) {
                return 0.00672123907;
            } else {
                return 9.12506293e-05;
            }
        }
    }
}

double evaluate_meta_tree_217(double &f[]) {
    if (f[5] < -0.370376468) {
        if (f[5] < -0.583981514) {
            if (f[2] < -0.683066666) {
                return -0.0298620518;
            } else {
                return 0.00139194529;
            }
        } else {
            if (f[8] < -1.28144574) {
                return -0.0289136525;
            } else {
                return -0.00468939124;
            }
        }
    } else {
        if (f[2] < 1.34327388) {
            if (f[4] < -1.15942764) {
                return -0.00443553971;
            } else {
                return 0.00169829524;
            }
        } else {
            if (f[7] < -0.714137852) {
                return 0.0123898359;
            } else {
                return -0.00904026534;
            }
        }
    }
}

double evaluate_meta_tree_218(double &f[]) {
    if (f[7] < 0.215811461) {
        if (f[8] < 0.297082245) {
            if (f[8] < -0.00668529188) {
                return -0.000433027337;
            } else {
                return -0.00654329685;
            }
        } else {
            if (f[1] < -0.184599519) {
                return 0.00858803093;
            } else {
                return -0.000279217231;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[8] < -1.8892436) {
                return -0.0158790238;
            } else {
                return 0.0801437944;
            }
        } else {
            if (f[2] < -0.502187014) {
                return 0.0048315078;
            } else {
                return 0.000235679006;
            }
        }
    }
}

double evaluate_meta_tree_219(double &f[]) {
    if (f[1] < 2.37942123) {
        if (f[0] < -2.2552712) {
            if (f[2] < 0.337951213) {
                return 0.0199011769;
            } else {
                return -0.00763540715;
            }
        } else {
            if (f[4] < -0.251987576) {
                return -0.0012979015;
            } else {
                return 0.000516480708;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[7] < -0.183636189) {
                return -0.00248084799;
            } else {
                return 0.0330311023;
            }
        } else {
            if (f[2] < 0.82174468) {
                return -0.0137030259;
            } else {
                return 0.0148575008;
            }
        }
    }
}

double evaluate_meta_tree_220(double &f[]) {
    if (f[4] < -0.339147002) {
        if (f[3] < -0.952752829) {
            if (f[4] < -0.529866278) {
                return 0.00372067955;
            } else {
                return -0.00892434828;
            }
        } else {
            if (f[0] < 0.56007576) {
                return -0.000889144547;
            } else {
                return -0.00707914401;
            }
        }
    } else {
        if (f[1] < -1.12717307) {
            if (f[2] < -1.24088204) {
                return 0.0583010614;
            } else {
                return 0.00601433869;
            }
        } else {
            if (f[7] < 0.432223588) {
                return 0.00112972176;
            } else {
                return -0.00141755841;
            }
        }
    }
}

double evaluate_meta_tree_221(double &f[]) {
    if (f[0] < -0.975028276) {
        if (f[1] < -0.197903052) {
            if (f[7] < 2.01427317) {
                return -0.00419855816;
            } else {
                return 0.0306888614;
            }
        } else {
            if (f[5] < -0.491068304) {
                return -0.0119062439;
            } else {
                return 0.00540770544;
            }
        }
    } else {
        if (f[8] < -1.61720705) {
            if (f[3] < -0.0844796002) {
                return -0.000440837583;
            } else {
                return 0.0125538809;
            }
        } else {
            if (f[8] < -0.231541455) {
                return -0.00111588545;
            } else {
                return 0.000853062083;
            }
        }
    }
}

double evaluate_meta_tree_222(double &f[]) {
    if (f[8] < 1.07459259) {
        if (f[2] < 1.34327388) {
            if (f[7] < -1.37314141) {
                return -0.00613872148;
            } else {
                return 0.00099284458;
            }
        } else {
            if (f[3] < 2.23530412) {
                return -0.00925826561;
            } else {
                return 0.0228688587;
            }
        }
    } else {
        if (f[1] < -0.432626486) {
            if (f[0] < -0.924897909) {
                return 0.000901715946;
            } else {
                return -0.0210931804;
            }
        } else {
            if (f[4] < 0.364231914) {
                return 0.00403092382;
            } else {
                return -0.00768594211;
            }
        }
    }
}

double evaluate_meta_tree_223(double &f[]) {
    if (f[3] < -0.345641077) {
        if (f[4] < 1.5452491) {
            if (f[0] < 1.27751553) {
                return -0.00218998198;
            } else {
                return 0.0117173688;
            }
        } else {
            if (f[8] < 0.0766446963) {
                return 0.0590106659;
            } else {
                return 0.00919456594;
            }
        }
    } else {
        if (f[4] < -0.251987576) {
            if (f[1] < -1.23373532) {
                return 0.0219892431;
            } else {
                return 0.00261147576;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00196003239;
            } else {
                return 0.00129477435;
            }
        }
    }
}

double evaluate_meta_tree_224(double &f[]) {
    if (f[1] < 1.48934865) {
        if (f[1] < -1.91067636) {
            if (f[3] < -1.06812358) {
                return -0.00471072458;
            } else {
                return 0.0166007318;
            }
        } else {
            if (f[1] < -0.566395581) {
                return 0.0012163216;
            } else {
                return -0.000721536286;
            }
        }
    } else {
        if (f[5] < 0.331580073) {
            if (f[2] < -0.337463975) {
                return -0.00746608106;
            } else {
                return 0.0200878829;
            }
        } else {
            if (f[2] < 1.22048283) {
                return -0.00416324055;
            } else {
                return 0.0117823742;
            }
        }
    }
}

double evaluate_meta_tree_225(double &f[]) {
    if (f[8] < -0.935274363) {
        if (f[0] < -2.2552712) {
            if (f[5] < 0.124966487) {
                return -0.0194303598;
            } else {
                return 0.0706442818;
            }
        } else {
            if (f[4] < -0.719429672) {
                return -0.00705988426;
            } else {
                return -0.0011270094;
            }
        }
    } else {
        if (f[4] < 0.97142303) {
            if (f[7] < 0.375814617) {
                return 0.000723544625;
            } else {
                return -0.00198312895;
            }
        } else {
            if (f[1] < -1.26252258) {
                return 0.033985246;
            } else {
                return 0.00225452241;
            }
        }
    }
}

double evaluate_meta_tree_226(double &f[]) {
    if (f[4] < -2.19129109) {
        if (f[1] < -0.23086971) {
            if (f[5] < 2.53329372) {
                return 0.0120654637;
            } else {
                return -0.0113915419;
            }
        } else {
            if (f[3] < -0.378293753) {
                return 0.0681038797;
            } else {
                return 0.0123703917;
            }
        }
    } else {
        if (f[3] < -0.699636102) {
            if (f[5] < -0.388354152) {
                return 0.0144864563;
            } else {
                return -0.00237118755;
            }
        } else {
            if (f[3] < -0.518025935) {
                return 0.00401879987;
            } else {
                return -1.46946641e-05;
            }
        }
    }
}

double evaluate_meta_tree_227(double &f[]) {
    if (f[0] < -0.665902972) {
        if (f[2] < -0.778128743) {
            if (f[1] < 0.436905593) {
                return -0.0128746703;
            } else {
                return 0.0375317186;
            }
        } else {
            if (f[3] < -0.898792088) {
                return 0.0207920149;
            } else {
                return 0.00223997305;
            }
        }
    } else {
        if (f[1] < -1.10609031) {
            if (f[8] < 0.129053533) {
                return -0.00356421992;
            } else {
                return -0.0291340332;
            }
        } else {
            if (f[3] < -1.54531109) {
                return -0.016680425;
            } else {
                return -0.000130785673;
            }
        }
    }
}

double evaluate_meta_tree_228(double &f[]) {
    if (f[5] < -0.47153765) {
        if (f[3] < 0.816725254) {
            if (f[7] < -0.611591339) {
                return 0.0065553668;
            } else {
                return 0.000459591945;
            }
        } else {
            if (f[4] < 1.21018171) {
                return 0.0517166071;
            } else {
                return -0.0137353865;
            }
        }
    } else {
        if (f[7] < -1.78379381) {
            if (f[3] < 1.01076698) {
                return 0.00141152879;
            } else {
                return 0.0287914518;
            }
        } else {
            if (f[7] < 0.102718167) {
                return -0.00174450374;
            } else {
                return 0.000601037755;
            }
        }
    }
}

double evaluate_meta_tree_229(double &f[]) {
    if (f[0] < 1.15781617) {
        if (f[1] < -1.33478355) {
            if (f[8] < 0.5306651) {
                return 0.00764699234;
            } else {
                return -0.00740192411;
            }
        } else {
            if (f[3] < 1.81086767) {
                return -0.000604099187;
            } else {
                return 0.00813193992;
            }
        }
    } else {
        if (f[6] < 1) {
            if (f[5] < 1.53045237) {
                return 0.00438067643;
            } else {
                return -0.00936102495;
            }
        } else {
            if (f[5] < 0.582937419) {
                return 0.0425506048;
            } else {
                return -0.0108475275;
            }
        }
    }
}

double evaluate_meta_tree_230(double &f[]) {
    if (f[7] < 2.01427317) {
        if (f[4] < 2.50719428) {
            if (f[0] < -0.896542609) {
                return -0.00222870056;
            } else {
                return 0.000331976073;
            }
        } else {
            if (f[3] < 0.0357334837) {
                return -0.0250947755;
            } else {
                return 0.0216076896;
            }
        }
    } else {
        if (f[0] < 0.469548017) {
            if (f[0] < 0.451554656) {
                return -0.00556926569;
            } else {
                return 0.0820112973;
            }
        } else {
            if (f[2] < -1.1849165) {
                return 0.021136038;
            } else {
                return -0.0197947454;
            }
        }
    }
}

double evaluate_meta_tree_231(double &f[]) {
    if (f[8] < 0.266049951) {
        if (f[1] < 1.09404576) {
            if (f[3] < -0.0787335187) {
                return -0.00158586691;
            } else {
                return 0.000955920841;
            }
        } else {
            if (f[7] < -0.882695615) {
                return 0.00741670886;
            } else {
                return -0.00691398326;
            }
        }
    } else {
        if (f[4] < -1.11105633) {
            if (f[0] < 0.095344983) {
                return 0.0117297005;
            } else {
                return 0.00056245469;
            }
        } else {
            if (f[8] < 1.19285023) {
                return 7.46736032e-06;
            } else {
                return 0.0033311327;
            }
        }
    }
}

double evaluate_meta_tree_232(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.21296334) {
            if (f[0] < -0.383884877) {
                return -0.000683662482;
            } else {
                return -0.0262447204;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00384137151;
            } else {
                return -0.003682493;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[0] < 0.451554656) {
                return 0.00109397329;
            } else {
                return 0.0514745601;
            }
        } else {
            if (f[4] < -0.20567213) {
                return 0.00264850236;
            } else {
                return -0.000721428019;
            }
        }
    }
}

double evaluate_meta_tree_233(double &f[]) {
    if (f[3] < -0.345641077) {
        if (f[4] < 1.5452491) {
            if (f[0] < 1.27751553) {
                return -0.00213286257;
            } else {
                return 0.0113696177;
            }
        } else {
            if (f[8] < 0.210432574) {
                return 0.0509447344;
            } else {
                return 0.00567678874;
            }
        }
    } else {
        if (f[4] < -0.251987576) {
            if (f[1] < -1.23373532) {
                return 0.0211817399;
            } else {
                return 0.00252116169;
            }
        } else {
            if (f[7] < 0.123049602) {
                return -0.00188927061;
            } else {
                return 0.00123940571;
            }
        }
    }
}

double evaluate_meta_tree_234(double &f[]) {
    if (f[1] < 2.37942123) {
        if (f[1] < -2.22324824) {
            if (f[8] < 0.129053533) {
                return 0.0264029037;
            } else {
                return -0.00917223748;
            }
        } else {
            if (f[1] < 0.750065565) {
                return -0.000516553409;
            } else {
                return 0.00187759881;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[7] < -0.183636189) {
                return -0.0029488178;
            } else {
                return 0.0317989774;
            }
        } else {
            if (f[2] < 0.82174468) {
                return -0.013412619;
            } else {
                return 0.0143139502;
            }
        }
    }
}

double evaluate_meta_tree_235(double &f[]) {
    if (f[7] < -0.714137852) {
        if (f[8] < -0.328133613) {
            if (f[7] < -0.882695615) {
                return 0.000941946753;
            } else {
                return -0.00453210576;
            }
        } else {
            if (f[0] < 0.276965767) {
                return -0.00940234959;
            } else {
                return 0.00155771791;
            }
        }
    } else {
        if (f[7] < -0.457038403) {
            if (f[2] < -0.425015599) {
                return 0.00941631477;
            } else {
                return 0.000990077388;
            }
        } else {
            if (f[6] < 0) {
                return -0.00635654246;
            } else {
                return 0.000110596993;
            }
        }
    }
}

double evaluate_meta_tree_236(double &f[]) {
    if (f[4] < -1.83394468) {
        if (f[7] < 0.164682344) {
            if (f[0] < -0.453184128) {
                return -0.00610713242;
            } else {
                return 0.0117647303;
            }
        } else {
            if (f[2] < 1.17002356) {
                return 0.0364804119;
            } else {
                return -0.0179617461;
            }
        }
    } else {
        if (f[0] < -0.975028276) {
            if (f[1] < -0.197903052) {
                return -0.00417593913;
            } else {
                return 0.00248928764;
            }
        } else {
            if (f[2] < -0.394173354) {
                return -0.00128595508;
            } else {
                return 0.000813295308;
            }
        }
    }
}

double evaluate_meta_tree_237(double &f[]) {
    if (f[8] < 1.07459259) {
        if (f[2] < 1.34327388) {
            if (f[7] < -1.37314141) {
                return -0.00602245843;
            } else {
                return 0.000962423277;
            }
        } else {
            if (f[3] < 2.23530412) {
                return -0.00905458536;
            } else {
                return 0.0222404525;
            }
        }
    } else {
        if (f[1] < -0.432626486) {
            if (f[0] < -0.924897909) {
                return 0.000796576322;
            } else {
                return -0.0208135564;
            }
        } else {
            if (f[3] < 0.713478565) {
                return -0.00545811746;
            } else {
                return 0.00722189248;
            }
        }
    }
}

double evaluate_meta_tree_238(double &f[]) {
    if (f[0] < -1.79142714) {
        if (f[2] < 1.46987176) {
            if (f[5] < 0.523699343) {
                return -0.0185875557;
            } else {
                return 0.00170520472;
            }
        } else {
            if (f[4] < 0.935132205) {
                return 0.0528924838;
            } else {
                return -0.0171739105;
            }
        }
    } else {
        if (f[5] < -0.47153765) {
            if (f[0] < -1.36343253) {
                return 0.0210883711;
            } else {
                return 0.00145643426;
            }
        } else {
            if (f[7] < -1.78379381) {
                return 0.00767231872;
            } else {
                return -0.000549143704;
            }
        }
    }
}

double evaluate_meta_tree_239(double &f[]) {
    if (f[0] < 1.34784722) {
        if (f[1] < -1.76743913) {
            if (f[4] < -0.295399517) {
                return 0.00142343796;
            } else {
                return 0.0229711141;
            }
        } else {
            if (f[2] < 1.8694005) {
                return -0.000415730843;
            } else {
                return 0.00908113923;
            }
        }
    } else {
        if (f[8] < 0.835825861) {
            if (f[1] < 0.929909587) {
                return 0.000329800649;
            } else {
                return 0.0126081575;
            }
        } else {
            if (f[2] < 1.46987176) {
                return -0.00722134439;
            } else {
                return 0.0345435925;
            }
        }
    }
}

double evaluate_meta_tree_240(double &f[]) {
    if (f[2] < 2.12161636) {
        if (f[0] < -0.937538922) {
            if (f[3] < 0.655889094) {
                return -0.000961921585;
            } else {
                return -0.00954533648;
            }
        } else {
            if (f[1] < -1.08474684) {
                return 0.00528870337;
            } else {
                return -1.79624167e-05;
            }
        }
    } else {
        if (f[5] < 1.33469391) {
            if (f[5] < 1.17465198) {
                return 0.0033775114;
            } else {
                return 0.0419903696;
            }
        } else {
            if (f[0] < -0.23440364) {
                return -0.00315905991;
            } else {
                return 0.0140849641;
            }
        }
    }
}

double evaluate_meta_tree_241(double &f[]) {
    if (f[4] < -2.19129109) {
        if (f[1] < -0.23086971) {
            if (f[8] < -0.609427869) {
                return -0.00742977951;
            } else {
                return 0.0140461698;
            }
        } else {
            if (f[3] < -0.378293753) {
                return 0.0641394407;
            } else {
                return 0.0117116468;
            }
        }
    } else {
        if (f[3] < -0.699636102) {
            if (f[5] < -0.388354152) {
                return 0.0140840877;
            } else {
                return -0.00229034177;
            }
        } else {
            if (f[3] < -0.518025935) {
                return 0.00393834896;
            } else {
                return -2.23314255e-05;
            }
        }
    }
}

double evaluate_meta_tree_242(double &f[]) {
    if (f[5] < -0.339252353) {
        if (f[8] < -1.24507833) {
            if (f[1] < 1.73610723) {
                return -0.0202909615;
            } else {
                return 0.057685256;
            }
        } else {
            if (f[8] < -0.401186317) {
                return 0.00355293485;
            } else {
                return -0.00359878573;
            }
        }
    } else {
        if (f[5] < -0.333165199) {
            if (f[2] < 0.221994698) {
                return 0.0327396542;
            } else {
                return -0.0279322416;
            }
        } else {
            if (f[7] < -0.643692672) {
                return 0.00374329719;
            } else {
                return -0.000192672742;
            }
        }
    }
}

double evaluate_meta_tree_243(double &f[]) {
    if (f[8] < 1.8846314) {
        if (f[0] < -1.66689301) {
            if (f[5] < 0.769702196) {
                return -0.0125233103;
            } else {
                return 0.00730414037;
            }
        } else {
            if (f[1] < -1.91067636) {
                return 0.0152343735;
            } else {
                return -6.96525894e-05;
            }
        }
    } else {
        if (f[8] < 2.21783733) {
            if (f[4] < 0.862586141) {
                return 0.00676427409;
            } else {
                return 0.0331264995;
            }
        } else {
            if (f[4] < 0.115433432) {
                return 0.012818289;
            } else {
                return -0.0115313958;
            }
        }
    }
}

double evaluate_meta_tree_244(double &f[]) {
    if (f[1] < 2.37942123) {
        if (f[0] < -2.2552712) {
            if (f[1] < -1.91067636) {
                return 0.0193924587;
            } else {
                return -0.00524609582;
            }
        } else {
            if (f[4] < -0.251987576) {
                return -0.00124880939;
            } else {
                return 0.00050975685;
            }
        }
    } else {
        if (f[5] < 0.582937419) {
            if (f[7] < -0.183636189) {
                return -0.00314247049;
            } else {
                return 0.0309630167;
            }
        } else {
            if (f[2] < 0.82174468) {
                return -0.0132083511;
            } else {
                return 0.0138162822;
            }
        }
    }
}

double evaluate_meta_tree_245(double &f[]) {
    if (f[8] < -1.61720705) {
        if (f[2] < -0.18213667) {
            if (f[1] < -1.12717307) {
                return 0.0291294139;
            } else {
                return -0.000719089934;
            }
        } else {
            if (f[2] < 0.647000253) {
                return -0.0176822599;
            } else {
                return 0.00142415217;
            }
        }
    } else {
        if (f[2] < 2.12161636) {
            if (f[0] < -0.937538922) {
                return -0.00230174558;
            } else {
                return 0.000336202182;
            }
        } else {
            if (f[5] < 1.33469391) {
                return 0.0312254466;
            } else {
                return 0.00679937238;
            }
        }
    }
}

double evaluate_meta_tree_246(double &f[]) {
    if (f[7] < 1.01226544) {
        if (f[1] < 2.06438828) {
            if (f[8] < -1.18002284) {
                return 0.0029219694;
            } else {
                return -0.000432174944;
            }
        } else {
            if (f[2] < 0.848252594) {
                return -0.0181227904;
            } else {
                return 5.12033184e-05;
            }
        }
    } else {
        if (f[8] < -0.160652995) {
            if (f[8] < -0.319508225) {
                return 0.00848189089;
            } else {
                return 0.0528080426;
            }
        } else {
            if (f[5] < -0.325752825) {
                return 0.00695677707;
            } else {
                return 0.000849277887;
            }
        }
    }
}

double evaluate_meta_tree_247(double &f[]) {
    if (f[0] < -0.665902972) {
        if (f[2] < -0.778128743) {
            if (f[1] < 0.436905593) {
                return -0.0127166659;
            } else {
                return 0.0358813442;
            }
        } else {
            if (f[3] < -0.898792088) {
                return 0.0198942591;
            } else {
                return 0.00216993014;
            }
        }
    } else {
        if (f[1] < -1.10609031) {
            if (f[8] < 0.129053533) {
                return -0.00346838683;
            } else {
                return -0.0289750826;
            }
        } else {
            if (f[4] < -1.25697768) {
                return -0.00865657628;
            } else {
                return 4.57839087e-05;
            }
        }
    }
}

double evaluate_meta_tree_248(double &f[]) {
    if (f[3] < -0.345641077) {
        if (f[4] < 1.62132287) {
            if (f[0] < 1.27751553) {
                return -0.00206512562;
            } else {
                return 0.0109787546;
            }
        } else {
            if (f[7] < 2.54269695) {
                return 0.033199992;
            } else {
                return -0.0259956103;
            }
        }
    } else {
        if (f[4] < -0.251987576) {
            if (f[1] < -1.23373532) {
                return 0.0204520561;
            } else {
                return 0.00244096993;
            }
        } else {
            if (f[3] < 1.81086767) {
                return -4.75671695e-05;
            } else {
                return -0.0112742195;
            }
        }
    }
}

double evaluate_meta_tree_249(double &f[]) {
    if (f[0] < 1.15781617) {
        if (f[1] < -0.617830217) {
            if (f[5] < 0.559665799) {
                return 0.00314566563;
            } else {
                return -0.00177331886;
            }
        } else {
            if (f[7] < -1.26540399) {
                return 0.00359926256;
            } else {
                return -0.00102298858;
            }
        }
    } else {
        if (f[6] < 1) {
            if (f[5] < 1.53045237) {
                return 0.00414467789;
            } else {
                return -0.00921028759;
            }
        } else {
            if (f[5] < 0.582937419) {
                return 0.040694505;
            } else {
                return -0.0109034115;
            }
        }
    }
}


int Get_Optimal_Barrier_Class(double &raw_features[]) {
    double scaled[9];
    for(int i=0; i<9; i++) {
        scaled[i] = (raw_features[i] - meta_scaler_center[i]) / meta_scaler_scale[i];
    }
    double probs[5];
    predict_metalabel(scaled, probs);
    
    double sum_exp = 0;
    for(int i=0; i<5; i++) sum_exp += MathExp(probs[i]);
    for(int i=0; i<5; i++) probs[i] = MathExp(probs[i]) / sum_exp;
    
    int best_class = 0;
    double max_prob = probs[0];
    for(int i=1; i<5; i++) {
        if(probs[i] > max_prob) {
            max_prob = probs[i];
            best_class = i;
        }
    }
    return best_class;
}
