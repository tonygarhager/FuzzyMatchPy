import locale
import json
from StringUtils import StringUtils

class CultureInfoExtensions:
    legacy_language_mapping = {}
    legacy_language_codes = {}
    _locale_to_group_mapping = {}
    _region_qualified_culture_mapping = {}
    _lcid_map = {}
    romance_languages = {
				"fr",
				"es",
				"pt",
				"it",
				"ro",
				"gl",
				"ca"
			}
    use_blank_as_word_separator_exceptions = {
				"th",
				"km",
				"ja",
				"chs",
				"cht",
				"zh"
			}
    use_blank_as_sentence_separator_languages = {
				"th",
				"km"
			}

    with open('lcid.json', 'r', encoding='utf-8') as filelcid:
        _lcid_map = json.load(filelcid)

    legacy_language_codes["no-no"] = "nb-NO"
    legacy_language_codes["no-ny"] = "nn-NO"
    legacy_language_codes["no-xy"] = "nn-NO"
    legacy_language_codes["es-em"] = "es-ES"
    legacy_language_codes["es-xm"] = "es-ES"
    legacy_language_codes["es-xy"] = "es-ES"
    legacy_language_codes["es-xl"] = "es-419"
    legacy_language_codes["es-cn"] = "es-CL"
    legacy_language_codes["es-me"] = "es-MX"
    legacy_language_codes["mt"] = "mt-MT"
    legacy_language_codes["mt-01"] = "mt-MT"
    legacy_language_codes["cy"] = "cy-GB"
    legacy_language_codes["cy-01"] = "cy-GB"
    legacy_language_codes["ga"] = "ga-IE"
    legacy_language_codes["gd"] = "gd-GB"
    legacy_language_codes["ga-CT"] = "gd-GB"
    legacy_language_codes["iw"] = "he-IL"
    legacy_language_codes["rm"] = "rm-CH"
    legacy_language_codes["in"] = "id-ID"
    legacy_language_codes["mn-xc"] = "mn-MN"
    legacy_language_codes["ms-bx"] = "ms-BN"
    legacy_language_codes["qu"] = "quz-BO"
    legacy_language_codes["qu-BO"] = "quz-BO"
    legacy_language_codes["qu-EC"] = "quz-EC"
    legacy_language_codes["qu-PE"] = "quz-PE"
    legacy_language_codes["sz"] = "se-FI"
    legacy_language_codes["tl"] = "fil-PH"
    legacy_language_codes["fl"] = "fil-PH"
    legacy_language_codes["pt-pr"] = "pt-PT"
    legacy_language_codes["zh-_c"] = "zh-CN"
    legacy_language_codes["zh-_t"] = "zh-TW"
    legacy_language_codes["zh-XM"] = "zh-MO"
    legacy_language_codes["se"] = "se-NO"
    legacy_language_codes["nep"] = "ne-NP"
    legacy_language_codes["ne"] = "ne-NP"
    legacy_language_codes["div"] = "dv-MV"
    legacy_language_codes["mi"] = "mi-NZ"
    legacy_language_codes["bo"] = "bo-CN"
    legacy_language_codes["km"] = "km-KH"
    legacy_language_codes["lo"] = "lo-LA"
    legacy_language_codes["si"] = "si-LK"
    legacy_language_codes["am"] = "am-ET"
    legacy_language_codes["fy"] = "fy-NL"
    legacy_language_codes["ba"] = "ba-RU"
    legacy_language_codes["rw"] = "rw-RW"
    legacy_language_codes["wo"] = "wo-SN"
    legacy_language_codes["tk"] = "tk-TM"
    legacy_language_codes["kl"] = "kl-GL"
    legacy_language_codes["tg"] = "tg-Cyrl-TJ"
    legacy_language_codes["ug"] = "ug-CN"
    legacy_language_codes["ps"] = "ps-AF"
    legacy_language_codes["br"] = "br-FR"
    legacy_language_codes["oc"] = "oc-FR"
    legacy_language_codes["co"] = "co-FR"
    legacy_language_codes["ha"] = "ha-Latn-NG"
    legacy_language_codes["yo"] = "yo-NG"
    legacy_language_codes["ig"] = "ig-NG"
    legacy_language_codes["sh-hr"] = "hr-HR"
    legacy_language_codes["sh"] = "hr-HR"
    legacy_language_codes["sh-sr"] = "sr-Latn-CS"
    legacy_language_codes["sh-yu"] = "sr-Cyrl-CS"
    legacy_language_codes["sr-xc"] = "sr-Cyrl-CS"
    legacy_language_codes["bs"] = "bs-Latn-BA"
    legacy_language_codes["sh-B1"] = "hr-BA"
    legacy_language_codes["sh-B2"] = "bs-Latn-BA"
    legacy_language_codes["sh-B3"] = "sr-Latn-BA"
    legacy_language_codes["sh-B4"] = "sr-Cyrl-BA"
    legacy_language_codes["sr-SP"] = "sr-Cyrl-CS"
    legacy_language_codes["az-xc"] = "az-Cyrl-AZ"
    legacy_language_codes["az-xe"] = "az-Latn-AZ"
    legacy_language_codes["az-cy"] = "az-Cyrl-AZ"
    legacy_language_codes["az-lt"] = "az-Latn-AZ"
    legacy_language_codes["az-AZ"] = "az-Latn-AZ"
    legacy_language_codes["uz-xc"] = "uz-Cyrl-UZ"
    legacy_language_codes["uz-xl"] = "uz-Latn-UZ"
    legacy_language_codes["uz-lt"] = "uz-Latn-UZ"
    legacy_language_codes["uz-cy"] = "uz-Cyrl-UZ"
    legacy_language_codes["uz-UZ"] = "uz-Latn-UZ"
    legacy_language_codes["en-uk"] = "en-GB"
    legacy_language_codes["en-cr"] = "en-029"
    legacy_language_codes["en-cb"] = "en-029"
    legacy_language_codes["en-tr"] = "en-TT"
    legacy_language_codes["en-rh"] = "en-ZW"
    legacy_language_codes["bn"] = "bn-IN"
    legacy_language_codes["ml"] = "ml-IN"
    legacy_language_codes["or"] = "or-IN"
    legacy_language_codes["as"] = "as-IN"
    legacy_language_codes["tn"] = "tn-ZA"
    legacy_language_codes["xh"] = "xh-ZA"
    legacy_language_codes["zu"] = "zu-ZA"
    legacy_language_codes["ns"] = "nso-ZA"
    legacy_language_codes["ns-ZA"] = "nso-ZA"
    # InitializeLanguageGroupMapping()
    _locale_to_group_mapping[1027] = 'WesternEurope'
    _locale_to_group_mapping[3] = 'WesternEurope'
    _locale_to_group_mapping[1030] = 'WesternEurope'
    _locale_to_group_mapping[6] = 'WesternEurope'
    _locale_to_group_mapping[1031] = 'WesternEurope'
    _locale_to_group_mapping[7] = 'WesternEurope'
    _locale_to_group_mapping[1033] = 'WesternEurope'
    _locale_to_group_mapping[9] = 'WesternEurope'
    _locale_to_group_mapping[1034] = 'WesternEurope'
    _locale_to_group_mapping[10] = 'WesternEurope'
    _locale_to_group_mapping[1035] = 'WesternEurope'
    _locale_to_group_mapping[11] = 'WesternEurope'
    _locale_to_group_mapping[1036] = 'WesternEurope'
    _locale_to_group_mapping[12] = 'WesternEurope'
    _locale_to_group_mapping[1039] = 'WesternEurope'
    _locale_to_group_mapping[15] = 'WesternEurope'
    _locale_to_group_mapping[1040] = 'WesternEurope'
    _locale_to_group_mapping[16] = 'WesternEurope'
    _locale_to_group_mapping[1043] = 'WesternEurope'
    _locale_to_group_mapping[19] = 'WesternEurope'
    _locale_to_group_mapping[1044] = 'WesternEurope'
    _locale_to_group_mapping[20] = 'WesternEurope'
    _locale_to_group_mapping[1046] = 'WesternEurope'
    _locale_to_group_mapping[22] = 'WesternEurope'
    _locale_to_group_mapping[1047] = 'WesternEurope'
    _locale_to_group_mapping[23] = 'WesternEurope'
    _locale_to_group_mapping[1053] = 'WesternEurope'
    _locale_to_group_mapping[29] = 'WesternEurope'
    _locale_to_group_mapping[1057] = 'WesternEurope'
    _locale_to_group_mapping[33] = 'WesternEurope'
    _locale_to_group_mapping[1069] = 'WesternEurope'
    _locale_to_group_mapping[45] = 'WesternEurope'
    _locale_to_group_mapping[1070] = 'WesternEurope'
    _locale_to_group_mapping[46] = 'WesternEurope'
    _locale_to_group_mapping[1072] = 'WesternEurope'
    _locale_to_group_mapping[48] = 'WesternEurope'
    _locale_to_group_mapping[1073] = 'WesternEurope'
    _locale_to_group_mapping[49] = 'WesternEurope'
    _locale_to_group_mapping[1074] = 'WesternEurope'
    _locale_to_group_mapping[50] = 'WesternEurope'
    _locale_to_group_mapping[1075] = 'WesternEurope'
    _locale_to_group_mapping[51] = 'WesternEurope'
    _locale_to_group_mapping[1076] = 'WesternEurope'
    _locale_to_group_mapping[52] = 'WesternEurope'
    _locale_to_group_mapping[1077] = 'WesternEurope'
    _locale_to_group_mapping[53] = 'WesternEurope'
    _locale_to_group_mapping[1078] = 'WesternEurope'
    _locale_to_group_mapping[54] = 'WesternEurope'
    _locale_to_group_mapping[1080] = 'WesternEurope'
    _locale_to_group_mapping[56] = 'WesternEurope'
    _locale_to_group_mapping[1082] = 'WesternEurope'
    _locale_to_group_mapping[58] = 'WesternEurope'
    _locale_to_group_mapping[1083] = 'WesternEurope'
    _locale_to_group_mapping[59] = 'WesternEurope'
    _locale_to_group_mapping[1085] = 'WesternEurope'
    _locale_to_group_mapping[61] = 'WesternEurope'
    _locale_to_group_mapping[1086] = 'WesternEurope'
    _locale_to_group_mapping[62] = 'WesternEurope'
    _locale_to_group_mapping[1089] = 'WesternEurope'
    _locale_to_group_mapping[65] = 'WesternEurope'
    _locale_to_group_mapping[1106] = 'WesternEurope'
    _locale_to_group_mapping[82] = 'WesternEurope'
    _locale_to_group_mapping[1109] = 'WesternEurope'
    _locale_to_group_mapping[85] = 'WesternEurope'
    _locale_to_group_mapping[1110] = 'WesternEurope'
    _locale_to_group_mapping[86] = 'WesternEurope'
    _locale_to_group_mapping[1112] = 'WesternEurope'
    _locale_to_group_mapping[88] = 'WesternEurope'
    _locale_to_group_mapping[1116] = 'WesternEurope'
    _locale_to_group_mapping[92] = 'WesternEurope'
    _locale_to_group_mapping[1117] = 'WesternEurope'
    _locale_to_group_mapping[93] = 'WesternEurope'
    _locale_to_group_mapping[1118] = 'WesternEurope'
    _locale_to_group_mapping[94] = 'WesternEurope'
    _locale_to_group_mapping[1122] = 'WesternEurope'
    _locale_to_group_mapping[98] = 'WesternEurope'
    _locale_to_group_mapping[1124] = 'WesternEurope'
    _locale_to_group_mapping[100] = 'WesternEurope'
    _locale_to_group_mapping[1126] = 'WesternEurope'
    _locale_to_group_mapping[102] = 'WesternEurope'
    _locale_to_group_mapping[1127] = 'WesternEurope'
    _locale_to_group_mapping[103] = 'WesternEurope'
    _locale_to_group_mapping[1128] = 'WesternEurope'
    _locale_to_group_mapping[104] = 'WesternEurope'
    _locale_to_group_mapping[1129] = 'WesternEurope'
    _locale_to_group_mapping[105] = 'WesternEurope'
    _locale_to_group_mapping[1130] = 'WesternEurope'
    _locale_to_group_mapping[106] = 'WesternEurope'
    _locale_to_group_mapping[1131] = 'WesternEurope'
    _locale_to_group_mapping[107] = 'WesternEurope'
    _locale_to_group_mapping[1132] = 'WesternEurope'
    _locale_to_group_mapping[108] = 'WesternEurope'
    _locale_to_group_mapping[1134] = 'WesternEurope'
    _locale_to_group_mapping[110] = 'WesternEurope'
    _locale_to_group_mapping[1135] = 'WesternEurope'
    _locale_to_group_mapping[111] = 'WesternEurope'
    _locale_to_group_mapping[1136] = 'WesternEurope'
    _locale_to_group_mapping[112] = 'WesternEurope'
    _locale_to_group_mapping[1137] = 'WesternEurope'
    _locale_to_group_mapping[113] = 'WesternEurope'
    _locale_to_group_mapping[1138] = 'WesternEurope'
    _locale_to_group_mapping[114] = 'WesternEurope'
    _locale_to_group_mapping[1139] = 'WesternEurope'
    _locale_to_group_mapping[115] = 'WesternEurope'
    _locale_to_group_mapping[1140] = 'WesternEurope'
    _locale_to_group_mapping[116] = 'WesternEurope'
    _locale_to_group_mapping[1141] = 'WesternEurope'
    _locale_to_group_mapping[117] = 'WesternEurope'
    _locale_to_group_mapping[1142] = 'WesternEurope'
    _locale_to_group_mapping[118] = 'WesternEurope'
    _locale_to_group_mapping[1143] = 'WesternEurope'
    _locale_to_group_mapping[119] = 'WesternEurope'
    _locale_to_group_mapping[1145] = 'WesternEurope'
    _locale_to_group_mapping[121] = 'WesternEurope'
    _locale_to_group_mapping[1146] = 'WesternEurope'
    _locale_to_group_mapping[122] = 'WesternEurope'
    _locale_to_group_mapping[1148] = 'WesternEurope'
    _locale_to_group_mapping[124] = 'WesternEurope'
    _locale_to_group_mapping[1150] = 'WesternEurope'
    _locale_to_group_mapping[126] = 'WesternEurope'
    _locale_to_group_mapping[1153] = 'WesternEurope'
    _locale_to_group_mapping[129] = 'WesternEurope'
    _locale_to_group_mapping[1154] = 'WesternEurope'
    _locale_to_group_mapping[130] = 'WesternEurope'
    _locale_to_group_mapping[1155] = 'WesternEurope'
    _locale_to_group_mapping[131] = 'WesternEurope'
    _locale_to_group_mapping[1156] = 'WesternEurope'
    _locale_to_group_mapping[132] = 'WesternEurope'
    _locale_to_group_mapping[1158] = 'WesternEurope'
    _locale_to_group_mapping[134] = 'WesternEurope'
    _locale_to_group_mapping[1159] = 'WesternEurope'
    _locale_to_group_mapping[135] = 'WesternEurope'
    _locale_to_group_mapping[1160] = 'WesternEurope'
    _locale_to_group_mapping[136] = 'WesternEurope'
    _locale_to_group_mapping[1169] = 'WesternEurope'
    _locale_to_group_mapping[145] = 'WesternEurope'
    _locale_to_group_mapping[2051] = 'WesternEurope'
    _locale_to_group_mapping[2055] = 'WesternEurope'
    _locale_to_group_mapping[2057] = 'WesternEurope'
    _locale_to_group_mapping[2058] = 'WesternEurope'
    _locale_to_group_mapping[2060] = 'WesternEurope'
    _locale_to_group_mapping[2064] = 'WesternEurope'
    _locale_to_group_mapping[2067] = 'WesternEurope'
    _locale_to_group_mapping[2068] = 'WesternEurope'
    _locale_to_group_mapping[2070] = 'WesternEurope'
    _locale_to_group_mapping[2072] = 'WesternEurope'
    _locale_to_group_mapping[24] = 'WesternEurope'
    _locale_to_group_mapping[2073] = 'WesternEurope'
    _locale_to_group_mapping[25] = 'WesternEurope'
    _locale_to_group_mapping[2077] = 'WesternEurope'
    _locale_to_group_mapping[2080] = 'WesternEurope'
    _locale_to_group_mapping[32] = 'WesternEurope'
    _locale_to_group_mapping[2094] = 'WesternEurope'
    _locale_to_group_mapping[2098] = 'WesternEurope'
    _locale_to_group_mapping[2107] = 'WesternEurope'
    _locale_to_group_mapping[2108] = 'WesternEurope'
    _locale_to_group_mapping[60] = 'WesternEurope'
    _locale_to_group_mapping[2110] = 'WesternEurope'
    _locale_to_group_mapping[2141] = 'WesternEurope'
    _locale_to_group_mapping[2143] = 'WesternEurope'
    _locale_to_group_mapping[95] = 'WesternEurope'
    _locale_to_group_mapping[2145] = 'WesternEurope'
    _locale_to_group_mapping[97] = 'WesternEurope'
    _locale_to_group_mapping[2151] = 'WesternEurope'
    _locale_to_group_mapping[2155] = 'WesternEurope'
    _locale_to_group_mapping[2163] = 'WesternEurope'
    _locale_to_group_mapping[3079] = 'WesternEurope'
    _locale_to_group_mapping[3081] = 'WesternEurope'
    _locale_to_group_mapping[3082] = 'WesternEurope'
    _locale_to_group_mapping[3084] = 'WesternEurope'
    _locale_to_group_mapping[3131] = 'WesternEurope'
    _locale_to_group_mapping[3153] = 'WesternEurope'
    _locale_to_group_mapping[81] = 'WesternEurope'
    _locale_to_group_mapping[3179] = 'WesternEurope'
    _locale_to_group_mapping[4103] = 'WesternEurope'
    _locale_to_group_mapping[4105] = 'WesternEurope'
    _locale_to_group_mapping[4106] = 'WesternEurope'
    _locale_to_group_mapping[4108] = 'WesternEurope'
    _locale_to_group_mapping[4155] = 'WesternEurope'
    _locale_to_group_mapping[4191] = 'WesternEurope'
    _locale_to_group_mapping[5127] = 'WesternEurope'
    _locale_to_group_mapping[5129] = 'WesternEurope'
    _locale_to_group_mapping[5130] = 'WesternEurope'
    _locale_to_group_mapping[5132] = 'WesternEurope'
    _locale_to_group_mapping[5179] = 'WesternEurope'
    _locale_to_group_mapping[6153] = 'WesternEurope'
    _locale_to_group_mapping[6154] = 'WesternEurope'
    _locale_to_group_mapping[6156] = 'WesternEurope'
    _locale_to_group_mapping[6203] = 'WesternEurope'
    _locale_to_group_mapping[7177] = 'WesternEurope'
    _locale_to_group_mapping[7178] = 'WesternEurope'
    _locale_to_group_mapping[7180] = 'WesternEurope'
    _locale_to_group_mapping[7227] = 'WesternEurope'
    _locale_to_group_mapping[8201] = 'WesternEurope'
    _locale_to_group_mapping[8202] = 'WesternEurope'
    _locale_to_group_mapping[8204] = 'WesternEurope'
    _locale_to_group_mapping[8251] = 'WesternEurope'
    _locale_to_group_mapping[9225] = 'WesternEurope'
    _locale_to_group_mapping[9226] = 'WesternEurope'
    _locale_to_group_mapping[9228] = 'WesternEurope'
    _locale_to_group_mapping[9275] = 'WesternEurope'
    _locale_to_group_mapping[10249] = 'WesternEurope'
    _locale_to_group_mapping[10250] = 'WesternEurope'
    _locale_to_group_mapping[10252] = 'WesternEurope'
    _locale_to_group_mapping[11273] = 'WesternEurope'
    _locale_to_group_mapping[11274] = 'WesternEurope'
    _locale_to_group_mapping[11276] = 'WesternEurope'
    _locale_to_group_mapping[12297] = 'WesternEurope'
    _locale_to_group_mapping[12298] = 'WesternEurope'
    _locale_to_group_mapping[12300] = 'WesternEurope'
    _locale_to_group_mapping[13321] = 'WesternEurope'
    _locale_to_group_mapping[13322] = 'WesternEurope'
    _locale_to_group_mapping[13324] = 'WesternEurope'
    _locale_to_group_mapping[14345] = 'WesternEurope'
    _locale_to_group_mapping[14346] = 'WesternEurope'
    _locale_to_group_mapping[14348] = 'WesternEurope'
    _locale_to_group_mapping[15369] = 'WesternEurope'
    _locale_to_group_mapping[15370] = 'WesternEurope'
    _locale_to_group_mapping[15372] = 'WesternEurope'
    _locale_to_group_mapping[16393] = 'WesternEurope'
    _locale_to_group_mapping[16394] = 'WesternEurope'
    _locale_to_group_mapping[17417] = 'WesternEurope'
    _locale_to_group_mapping[17418] = 'WesternEurope'
    _locale_to_group_mapping[18441] = 'WesternEurope'
    _locale_to_group_mapping[18442] = 'WesternEurope'
    _locale_to_group_mapping[19465] = 'WesternEurope'
    _locale_to_group_mapping[19466] = 'WesternEurope'
    _locale_to_group_mapping[20490] = 'WesternEurope'
    _locale_to_group_mapping[21514] = 'WesternEurope'
    _locale_to_group_mapping[22538] = 'WesternEurope'
    _locale_to_group_mapping[23562] = 'WesternEurope'
    _locale_to_group_mapping[65663] = 'WesternEurope'
    _locale_to_group_mapping[127] = 'WesternEurope'
    _locale_to_group_mapping[66567] = 'WesternEurope'
    _locale_to_group_mapping[1029] = 'CentralEurope'
    _locale_to_group_mapping[5] = 'CentralEurope'
    _locale_to_group_mapping[1038] = 'CentralEurope'
    _locale_to_group_mapping[14] = 'CentralEurope'
    _locale_to_group_mapping[1045] = 'CentralEurope'
    _locale_to_group_mapping[21] = 'CentralEurope'
    _locale_to_group_mapping[1048] = 'CentralEurope'
    _locale_to_group_mapping[1050] = 'CentralEurope'
    _locale_to_group_mapping[26] = 'CentralEurope'
    _locale_to_group_mapping[1051] = 'CentralEurope'
    _locale_to_group_mapping[27] = 'CentralEurope'
    _locale_to_group_mapping[1052] = 'CentralEurope'
    _locale_to_group_mapping[28] = 'CentralEurope'
    _locale_to_group_mapping[1060] = 'CentralEurope'
    _locale_to_group_mapping[36] = 'CentralEurope'
    _locale_to_group_mapping[1068] = 'CentralEurope'
    _locale_to_group_mapping[44] = 'CentralEurope'
    _locale_to_group_mapping[1090] = 'CentralEurope'
    _locale_to_group_mapping[66] = 'CentralEurope'
    _locale_to_group_mapping[1091] = 'CentralEurope'
    _locale_to_group_mapping[67] = 'CentralEurope'
    _locale_to_group_mapping[2074] = 'CentralEurope'
    _locale_to_group_mapping[4122] = 'CentralEurope'
    _locale_to_group_mapping[5146] = 'CentralEurope'
    _locale_to_group_mapping[6170] = 'CentralEurope'
    _locale_to_group_mapping[9242] = 'CentralEurope'
    _locale_to_group_mapping[11290] = 'CentralEurope'
    _locale_to_group_mapping[66574] = 'CentralEurope'
    _locale_to_group_mapping[1061] = 'Baltic'
    _locale_to_group_mapping[37] = 'Baltic'
    _locale_to_group_mapping[1062] = 'Baltic'
    _locale_to_group_mapping[38] = 'Baltic'
    _locale_to_group_mapping[1063] = 'Baltic'
    _locale_to_group_mapping[39] = 'Baltic'
    _locale_to_group_mapping[1032] = 'Greek'
    _locale_to_group_mapping[8] = 'Greek'
    _locale_to_group_mapping[1026] = 'Cyrillic'
    _locale_to_group_mapping[2] = 'Cyrillic'
    _locale_to_group_mapping[1049] = 'Cyrillic'
    _locale_to_group_mapping[1058] = 'Cyrillic'
    _locale_to_group_mapping[34] = 'Cyrillic'
    _locale_to_group_mapping[1059] = 'Cyrillic'
    _locale_to_group_mapping[35] = 'Cyrillic'
    _locale_to_group_mapping[1064] = 'Cyrillic'
    _locale_to_group_mapping[40] = 'Cyrillic'
    _locale_to_group_mapping[1071] = 'Cyrillic'
    _locale_to_group_mapping[47] = 'Cyrillic'
    _locale_to_group_mapping[1087] = 'Cyrillic'
    _locale_to_group_mapping[63] = 'Cyrillic'
    _locale_to_group_mapping[1088] = 'Cyrillic'
    _locale_to_group_mapping[64] = 'Cyrillic'
    _locale_to_group_mapping[1092] = 'Cyrillic'
    _locale_to_group_mapping[68] = 'Cyrillic'
    _locale_to_group_mapping[1104] = 'Cyrillic'
    _locale_to_group_mapping[80] = 'Cyrillic'
    _locale_to_group_mapping[1133] = 'Cyrillic'
    _locale_to_group_mapping[109] = 'Cyrillic'
    _locale_to_group_mapping[1157] = 'Cyrillic'
    _locale_to_group_mapping[133] = 'Cyrillic'
    _locale_to_group_mapping[2092] = 'Cyrillic'
    _locale_to_group_mapping[2115] = 'Cyrillic'
    _locale_to_group_mapping[3098] = 'Cyrillic'
    _locale_to_group_mapping[7194] = 'Cyrillic'
    _locale_to_group_mapping[8218] = 'Cyrillic'
    _locale_to_group_mapping[10266] = 'Cyrillic'
    _locale_to_group_mapping[12314] = 'Cyrillic'
    _locale_to_group_mapping[1055] = 'Turkish'
    _locale_to_group_mapping[31] = 'Turkish'
    _locale_to_group_mapping[1041] = 'Japanese'
    _locale_to_group_mapping[17] = 'Japanese'
    _locale_to_group_mapping[263185] = 'Japanese'
    _locale_to_group_mapping[1042] = 'Korean'
    _locale_to_group_mapping[18] = 'Korean'
    _locale_to_group_mapping[1028] = 'TraditionalChinese'
    _locale_to_group_mapping[4] = 'TraditionalChinese'
    _locale_to_group_mapping[1144] = 'TraditionalChinese'
    _locale_to_group_mapping[120] = 'TraditionalChinese'
    _locale_to_group_mapping[3076] = 'TraditionalChinese'
    _locale_to_group_mapping[5124] = 'TraditionalChinese'
    _locale_to_group_mapping[136196] = 'TraditionalChinese'
    _locale_to_group_mapping[197636] = 'TraditionalChinese'
    _locale_to_group_mapping[263172] = 'TraditionalChinese'
    _locale_to_group_mapping[265220] = 'TraditionalChinese'
    _locale_to_group_mapping[267268] = 'TraditionalChinese'
    _locale_to_group_mapping[2052] = 'SimplifiedChinese'
    _locale_to_group_mapping[4100] = 'SimplifiedChinese'
    _locale_to_group_mapping[133124] = 'SimplifiedChinese'
    _locale_to_group_mapping[135172] = 'SimplifiedChinese'
    _locale_to_group_mapping[329732] = 'SimplifiedChinese'
    _locale_to_group_mapping[331780] = 'SimplifiedChinese'
    _locale_to_group_mapping[1054] = 'Thai'
    _locale_to_group_mapping[30] = 'Thai'
    _locale_to_group_mapping[1037] = 'Hebrew'
    _locale_to_group_mapping[13] = 'Hebrew'
    _locale_to_group_mapping[1025] = 'Arabic'
    _locale_to_group_mapping[1] = 'Arabic'
    _locale_to_group_mapping[1056] = 'Arabic'
    _locale_to_group_mapping[1065] = 'Arabic'
    _locale_to_group_mapping[41] = 'Arabic'
    _locale_to_group_mapping[1114] = 'Arabic'
    _locale_to_group_mapping[90] = 'Arabic'
    _locale_to_group_mapping[1119] = 'Arabic'
    _locale_to_group_mapping[1123] = 'Arabic'
    _locale_to_group_mapping[99] = 'Arabic'
    _locale_to_group_mapping[1125] = 'Arabic'
    _locale_to_group_mapping[101] = 'Arabic'
    _locale_to_group_mapping[1152] = 'Arabic'
    _locale_to_group_mapping[128] = 'Arabic'
    _locale_to_group_mapping[1164] = 'Arabic'
    _locale_to_group_mapping[140] = 'Arabic'
    _locale_to_group_mapping[1170] = 'Arabic'
    _locale_to_group_mapping[146] = 'Arabic'
    _locale_to_group_mapping[2049] = 'Arabic'
    _locale_to_group_mapping[2118] = 'Arabic'
    _locale_to_group_mapping[70] = 'Arabic'
    _locale_to_group_mapping[2137] = 'Arabic'
    _locale_to_group_mapping[89] = 'Arabic'
    _locale_to_group_mapping[3073] = 'Arabic'
    _locale_to_group_mapping[4097] = 'Arabic'
    _locale_to_group_mapping[5121] = 'Arabic'
    _locale_to_group_mapping[6145] = 'Arabic'
    _locale_to_group_mapping[7169] = 'Arabic'
    _locale_to_group_mapping[8193] = 'Arabic'
    _locale_to_group_mapping[9217] = 'Arabic'
    _locale_to_group_mapping[10241] = 'Arabic'
    _locale_to_group_mapping[11265] = 'Arabic'
    _locale_to_group_mapping[12289] = 'Arabic'
    _locale_to_group_mapping[13313] = 'Arabic'
    _locale_to_group_mapping[14337] = 'Arabic'
    _locale_to_group_mapping[15361] = 'Arabic'
    _locale_to_group_mapping[16385] = 'Arabic'
    _locale_to_group_mapping[1066] = 'Vietnamese'
    _locale_to_group_mapping[42] = 'Vietnamese'
    _locale_to_group_mapping[1081] = 'Indic'
    _locale_to_group_mapping[57] = 'Indic'
    _locale_to_group_mapping[1093] = 'Indic'
    _locale_to_group_mapping[69] = 'Indic'
    _locale_to_group_mapping[1094] = 'Indic'
    _locale_to_group_mapping[1095] = 'Indic'
    _locale_to_group_mapping[71] = 'Indic'
    _locale_to_group_mapping[1096] = 'Indic'
    _locale_to_group_mapping[72] = 'Indic'
    _locale_to_group_mapping[1097] = 'Indic'
    _locale_to_group_mapping[73] = 'Indic'
    _locale_to_group_mapping[1098] = 'Indic'
    _locale_to_group_mapping[74] = 'Indic'
    _locale_to_group_mapping[1099] = 'Indic'
    _locale_to_group_mapping[75] = 'Indic'
    _locale_to_group_mapping[1100] = 'Indic'
    _locale_to_group_mapping[76] = 'Indic'
    _locale_to_group_mapping[1101] = 'Indic'
    _locale_to_group_mapping[77] = 'Indic'
    _locale_to_group_mapping[1102] = 'Indic'
    _locale_to_group_mapping[78] = 'Indic'
    _locale_to_group_mapping[1103] = 'Indic'
    _locale_to_group_mapping[79] = 'Indic'
    _locale_to_group_mapping[1105] = 'Indic'
    _locale_to_group_mapping[1107] = 'Indic'
    _locale_to_group_mapping[83] = 'Indic'
    _locale_to_group_mapping[1108] = 'Indic'
    _locale_to_group_mapping[84] = 'Indic'
    _locale_to_group_mapping[1111] = 'Indic'
    _locale_to_group_mapping[87] = 'Indic'
    _locale_to_group_mapping[1113] = 'Indic'
    _locale_to_group_mapping[1115] = 'Indic'
    _locale_to_group_mapping[91] = 'Indic'
    _locale_to_group_mapping[1121] = 'Indic'
    _locale_to_group_mapping[2117] = 'Indic'
    _locale_to_group_mapping[2121] = 'Indic'
    _locale_to_group_mapping[2128] = 'Indic'
    _locale_to_group_mapping[2144] = 'Indic'
    _locale_to_group_mapping[96] = 'Indic'
    _locale_to_group_mapping[3152] = 'Indic'
    _locale_to_group_mapping[1079] = 'Georgian'
    _locale_to_group_mapping[55] = 'Georgian'
    _locale_to_group_mapping[66615] = 'Georgian'
    _locale_to_group_mapping[1067] = 'Armenian'
    _locale_to_group_mapping[43] = 'Armenian'
    # InitializeRegionQualifiedCultureMappingUsingCreateSpecificCulture
    _region_qualified_culture_mapping["swc"] = '{sw-CD}'
    _region_qualified_culture_mapping[""] = '{}'
    _region_qualified_culture_mapping["aa"] = '{aa-ET}'
    _region_qualified_culture_mapping["af"] = '{af-ZA}'
    _region_qualified_culture_mapping["agq"] = '{agq-CM}'
    _region_qualified_culture_mapping["ak"] = '{ak-GH}'
    _region_qualified_culture_mapping["am"] = '{am-ET}'
    _region_qualified_culture_mapping["ar"] = '{ar-SA}'
    _region_qualified_culture_mapping["arn"] = '{arn-CL}'
    _region_qualified_culture_mapping["as"] = '{as-IN}'
    _region_qualified_culture_mapping["asa"] = '{asa-TZ}'
    _region_qualified_culture_mapping["ast"] = '{ast-ES}'
    _region_qualified_culture_mapping["az"] = '{az-Latn-AZ}'
    _region_qualified_culture_mapping["az-Cyrl"] = '{az-Cyrl-AZ}'
    _region_qualified_culture_mapping["az-Latn"] = '{az-Latn-AZ}'
    _region_qualified_culture_mapping["ba"] = '{ba-RU}'
    _region_qualified_culture_mapping["bas"] = '{bas-CM}'
    _region_qualified_culture_mapping["be"] = '{be-BY}'
    _region_qualified_culture_mapping["bem"] = '{bem-ZM}'
    _region_qualified_culture_mapping["bez"] = '{bez-TZ}'
    _region_qualified_culture_mapping["bg"] = '{bg-BG}'
    _region_qualified_culture_mapping["bin"] = '{bin-NG}'
    _region_qualified_culture_mapping["bm"] = '{bm-Latn-ML}'
    _region_qualified_culture_mapping["bm-Latn"] = '{bm-Latn-ML}'
    _region_qualified_culture_mapping["bn"] = '{bn-BD}'
    _region_qualified_culture_mapping["bo"] = '{bo-CN}'
    _region_qualified_culture_mapping["br"] = '{br-FR}'
    _region_qualified_culture_mapping["brx"] = '{brx-IN}'
    _region_qualified_culture_mapping["bs"] = '{bs-Latn-BA}'
    _region_qualified_culture_mapping["bs-Cyrl"] = '{bs-Cyrl-BA}'
    _region_qualified_culture_mapping["bs-Latn"] = '{bs-Latn-BA}'
    _region_qualified_culture_mapping["byn"] = '{byn-ER}'
    _region_qualified_culture_mapping["ca"] = '{ca-ES}'
    _region_qualified_culture_mapping["ccp"] = '{ccp-Cakm-BD}'
    _region_qualified_culture_mapping["ccp-Cakm"] = '{ccp-Cakm-BD}'
    _region_qualified_culture_mapping["ce"] = '{ce-RU}'
    _region_qualified_culture_mapping["ceb"] = '{ceb-Latn-PH}'
    _region_qualified_culture_mapping["ceb-Latn"] = '{ceb-Latn-PH}'
    _region_qualified_culture_mapping["cgg"] = '{cgg-UG}'
    _region_qualified_culture_mapping["chr"] = '{chr-Cher-US}'
    _region_qualified_culture_mapping["chr-Cher"] = '{chr-Cher-US}'
    _region_qualified_culture_mapping["co"] = '{co-FR}'
    _region_qualified_culture_mapping["cs"] = '{cs-CZ}'
    _region_qualified_culture_mapping["cu"] = '{cu-RU}'
    _region_qualified_culture_mapping["cy"] = '{cy-GB}'
    _region_qualified_culture_mapping["da"] = '{da-DK}'
    _region_qualified_culture_mapping["dav"] = '{dav-KE}'
    _region_qualified_culture_mapping["de"] = '{de-DE}'
    _region_qualified_culture_mapping["dje"] = '{dje-NE}'
    _region_qualified_culture_mapping["dsb"] = '{dsb-DE}'
    _region_qualified_culture_mapping["dua"] = '{dua-CM}'
    _region_qualified_culture_mapping["dv"] = '{dv-MV}'
    _region_qualified_culture_mapping["dyo"] = '{dyo-SN}'
    _region_qualified_culture_mapping["dz"] = '{dz-BT}'
    _region_qualified_culture_mapping["ebu"] = '{ebu-KE}'
    _region_qualified_culture_mapping["ee"] = '{ee-GH}'
    _region_qualified_culture_mapping["el"] = '{el-GR}'
    _region_qualified_culture_mapping["en"] = '{en-US}'
    _region_qualified_culture_mapping["eo"] = '{eo-001}'
    _region_qualified_culture_mapping["es"] = '{es-ES}'
    _region_qualified_culture_mapping["et"] = '{et-EE}'
    _region_qualified_culture_mapping["eu"] = '{eu-ES}'
    _region_qualified_culture_mapping["ewo"] = '{ewo-CM}'
    _region_qualified_culture_mapping["fa"] = '{fa-IR}'
    _region_qualified_culture_mapping["ff"] = '{ff-Latn-SN}'
    _region_qualified_culture_mapping["ff-Latn"] = '{ff-Latn-SN}'
    _region_qualified_culture_mapping["fi"] = '{fi-FI}'
    _region_qualified_culture_mapping["fil"] = '{fil-PH}'
    _region_qualified_culture_mapping["fo"] = '{fo-FO}'
    _region_qualified_culture_mapping["fr"] = '{fr-FR}'
    _region_qualified_culture_mapping["fur"] = '{fur-IT}'
    _region_qualified_culture_mapping["fy"] = '{fy-NL}'
    _region_qualified_culture_mapping["ga"] = '{ga-IE}'
    _region_qualified_culture_mapping["gd"] = '{gd-GB}'
    _region_qualified_culture_mapping["gl"] = '{gl-ES}'
    _region_qualified_culture_mapping["gn"] = '{gn-PY}'
    _region_qualified_culture_mapping["gsw"] = '{gsw-CH}'
    _region_qualified_culture_mapping["gu"] = '{gu-IN}'
    _region_qualified_culture_mapping["guz"] = '{guz-KE}'
    _region_qualified_culture_mapping["gv"] = '{gv-IM}'
    _region_qualified_culture_mapping["ha"] = '{ha-Latn-NG}'
    _region_qualified_culture_mapping["ha-Latn"] = '{ha-Latn-NG}'
    _region_qualified_culture_mapping["haw"] = '{haw-US}'
    _region_qualified_culture_mapping["he"] = '{he-IL}'
    _region_qualified_culture_mapping["hi"] = '{hi-IN}'
    _region_qualified_culture_mapping["hr"] = '{hr-HR}'
    _region_qualified_culture_mapping["hsb"] = '{hsb-DE}'
    _region_qualified_culture_mapping["hu"] = '{hu-HU}'
    _region_qualified_culture_mapping["hy"] = '{hy-AM}'
    _region_qualified_culture_mapping["ia"] = '{ia-001}'
    _region_qualified_culture_mapping["ibb"] = '{ibb-NG}'
    _region_qualified_culture_mapping["id"] = '{id-ID}'
    _region_qualified_culture_mapping["ig"] = '{ig-NG}'
    _region_qualified_culture_mapping["ii"] = '{ii-CN}'
    _region_qualified_culture_mapping["is"] = '{is-IS}'
    _region_qualified_culture_mapping["it"] = '{it-IT}'
    _region_qualified_culture_mapping["iu"] = '{iu-Latn-CA}'
    _region_qualified_culture_mapping["iu-Cans"] = '{iu-Cans-CA}'
    _region_qualified_culture_mapping["iu-Latn"] = '{iu-Latn-CA}'
    _region_qualified_culture_mapping["ja"] = '{ja-JP}'
    _region_qualified_culture_mapping["jgo"] = '{jgo-CM}'
    _region_qualified_culture_mapping["jmc"] = '{jmc-TZ}'
    _region_qualified_culture_mapping["jv"] = '{jv-Latn-ID}'
    _region_qualified_culture_mapping["jv-Java"] = '{jv-Java-ID}'
    _region_qualified_culture_mapping["jv-Latn"] = '{jv-Latn-ID}'
    _region_qualified_culture_mapping["ka"] = '{ka-GE}'
    _region_qualified_culture_mapping["kab"] = '{kab-DZ}'
    _region_qualified_culture_mapping["kam"] = '{kam-KE}'
    _region_qualified_culture_mapping["kde"] = '{kde-TZ}'
    _region_qualified_culture_mapping["kea"] = '{kea-CV}'
    _region_qualified_culture_mapping["khq"] = '{khq-ML}'
    _region_qualified_culture_mapping["ki"] = '{ki-KE}'
    _region_qualified_culture_mapping["kk"] = '{kk-KZ}'
    _region_qualified_culture_mapping["kkj"] = '{kkj-CM}'
    _region_qualified_culture_mapping["kl"] = '{kl-GL}'
    _region_qualified_culture_mapping["kln"] = '{kln-KE}'
    _region_qualified_culture_mapping["km"] = '{km-KH}'
    _region_qualified_culture_mapping["kn"] = '{kn-IN}'
    _region_qualified_culture_mapping["ko"] = '{ko-KR}'
    _region_qualified_culture_mapping["kok"] = '{kok-IN}'
    _region_qualified_culture_mapping["kr"] = '{kr-NG}'
    _region_qualified_culture_mapping["kr-Latn"] = '{kr-Latn-NG}'
    _region_qualified_culture_mapping["ks"] = '{ks-Arab-IN}'
    _region_qualified_culture_mapping["ks-Arab"] = '{ks-Arab-IN}'
    _region_qualified_culture_mapping["ks-Deva"] = '{ks-Deva-IN}'
    _region_qualified_culture_mapping["ksb"] = '{ksb-TZ}'
    _region_qualified_culture_mapping["ksf"] = '{ksf-CM}'
    _region_qualified_culture_mapping["ksh"] = '{ksh-DE}'
    _region_qualified_culture_mapping["ku"] = '{ku-Arab-IQ}'
    _region_qualified_culture_mapping["ku-Arab"] = '{ku-Arab-IQ}'
    _region_qualified_culture_mapping["kw"] = '{kw-GB}'
    _region_qualified_culture_mapping["ky"] = '{ky-KG}'
    _region_qualified_culture_mapping["la"] = '{la-001}'
    _region_qualified_culture_mapping["lag"] = '{lag-TZ}'
    _region_qualified_culture_mapping["lb"] = '{lb-LU}'
    _region_qualified_culture_mapping["lg"] = '{lg-UG}'
    _region_qualified_culture_mapping["lkt"] = '{lkt-US}'
    _region_qualified_culture_mapping["ln"] = '{ln-CD}'
    _region_qualified_culture_mapping["lo"] = '{lo-LA}'
    _region_qualified_culture_mapping["lrc"] = '{lrc-IR}'
    _region_qualified_culture_mapping["lt"] = '{lt-LT}'
    _region_qualified_culture_mapping["lu"] = '{lu-CD}'
    _region_qualified_culture_mapping["luo"] = '{luo-KE}'
    _region_qualified_culture_mapping["luy"] = '{luy-KE}'
    _region_qualified_culture_mapping["lv"] = '{lv-LV}'
    _region_qualified_culture_mapping["mas"] = '{mas-KE}'
    _region_qualified_culture_mapping["mer"] = '{mer-KE}'
    _region_qualified_culture_mapping["mfe"] = '{mfe-MU}'
    _region_qualified_culture_mapping["mg"] = '{mg-MG}'
    _region_qualified_culture_mapping["mgh"] = '{mgh-MZ}'
    _region_qualified_culture_mapping["mgo"] = '{mgo-CM}'
    _region_qualified_culture_mapping["mi"] = '{mi-NZ}'
    _region_qualified_culture_mapping["mk"] = '{mk-MK}'
    _region_qualified_culture_mapping["ml"] = '{ml-IN}'
    _region_qualified_culture_mapping["mn"] = '{mn-MN}'
    _region_qualified_culture_mapping["mn-Cyrl"] = '{mn-MN}'
    _region_qualified_culture_mapping["mn-Mong"] = '{mn-Mong-CN}'
    _region_qualified_culture_mapping["mni"] = '{mni-IN}'
    _region_qualified_culture_mapping["moh"] = '{moh-CA}'
    _region_qualified_culture_mapping["mr"] = '{mr-IN}'
    _region_qualified_culture_mapping["ms"] = '{ms-MY}'
    _region_qualified_culture_mapping["mt"] = '{mt-MT}'
    _region_qualified_culture_mapping["mua"] = '{mua-CM}'
    _region_qualified_culture_mapping["my"] = '{my-MM}'
    _region_qualified_culture_mapping["mzn"] = '{mzn-IR}'
    _region_qualified_culture_mapping["naq"] = '{naq-NA}'
    _region_qualified_culture_mapping["nb"] = '{nb-NO}'
    _region_qualified_culture_mapping["nd"] = '{nd-ZW}'
    _region_qualified_culture_mapping["nds"] = '{nds-DE}'
    _region_qualified_culture_mapping["ne"] = '{ne-NP}'
    _region_qualified_culture_mapping["nl"] = '{nl-NL}'
    _region_qualified_culture_mapping["nmg"] = '{nmg-CM}'
    _region_qualified_culture_mapping["nn"] = '{nn-NO}'
    _region_qualified_culture_mapping["nnh"] = '{nnh-CM}'
    _region_qualified_culture_mapping["no"] = '{nb-NO}'
    _region_qualified_culture_mapping["nqo"] = '{nqo-GN}'
    _region_qualified_culture_mapping["nr"] = '{nr-ZA}'
    _region_qualified_culture_mapping["nso"] = '{nso-ZA}'
    _region_qualified_culture_mapping["nus"] = '{nus-SS}'
    _region_qualified_culture_mapping["nyn"] = '{nyn-UG}'
    _region_qualified_culture_mapping["oc"] = '{oc-FR}'
    _region_qualified_culture_mapping["om"] = '{om-ET}'
    _region_qualified_culture_mapping["or"] = '{or-IN}'
    _region_qualified_culture_mapping["os"] = '{os-GE}'
    _region_qualified_culture_mapping["pa"] = '{pa-IN}'
    _region_qualified_culture_mapping["pa-Arab"] = '{pa-Arab-PK}'
    _region_qualified_culture_mapping["pa-Guru"] = '{pa-IN}'
    _region_qualified_culture_mapping["pap"] = '{pap-029}'
    _region_qualified_culture_mapping["pl"] = '{pl-PL}'
    _region_qualified_culture_mapping["prg"] = '{prg-001}'
    _region_qualified_culture_mapping["prs"] = '{prs-AF}'
    _region_qualified_culture_mapping["ps"] = '{ps-AF}'
    _region_qualified_culture_mapping["pt"] = '{pt-BR}'
    _region_qualified_culture_mapping["quc"] = '{quc-Latn-GT}'
    _region_qualified_culture_mapping["quc-Latn"] = '{quc-Latn-GT}'
    _region_qualified_culture_mapping["quz"] = '{quz-BO}'
    _region_qualified_culture_mapping["rm"] = '{rm-CH}'
    _region_qualified_culture_mapping["rn"] = '{rn-BI}'
    _region_qualified_culture_mapping["ro"] = '{ro-RO}'
    _region_qualified_culture_mapping["rof"] = '{rof-TZ}'
    _region_qualified_culture_mapping["ru"] = '{ru-RU}'
    _region_qualified_culture_mapping["rw"] = '{rw-RW}'
    _region_qualified_culture_mapping["rwk"] = '{rwk-TZ}'
    _region_qualified_culture_mapping["sa"] = '{sa-IN}'
    _region_qualified_culture_mapping["sah"] = '{sah-RU}'
    _region_qualified_culture_mapping["saq"] = '{saq-KE}'
    _region_qualified_culture_mapping["sbp"] = '{sbp-TZ}'
    _region_qualified_culture_mapping["sd"] = '{sd-Arab-PK}'
    _region_qualified_culture_mapping["sd-Arab"] = '{sd-Arab-PK}'
    _region_qualified_culture_mapping["sd-Deva"] = '{sd-Deva-IN}'
    _region_qualified_culture_mapping["se"] = '{se-NO}'
    _region_qualified_culture_mapping["seh"] = '{seh-MZ}'
    _region_qualified_culture_mapping["ses"] = '{ses-ML}'
    _region_qualified_culture_mapping["sg"] = '{sg-CF}'
    _region_qualified_culture_mapping["shi"] = '{shi-Tfng-MA}'
    _region_qualified_culture_mapping["shi-Latn"] = '{shi-Latn-MA}'
    _region_qualified_culture_mapping["shi-Tfng"] = '{shi-Tfng-MA}'
    _region_qualified_culture_mapping["si"] = '{si-LK}'
    _region_qualified_culture_mapping["sk"] = '{sk-SK}'
    _region_qualified_culture_mapping["sl"] = '{sl-SI}'
    _region_qualified_culture_mapping["sma"] = '{sma-SE}'
    _region_qualified_culture_mapping["smj"] = '{smj-SE}'
    _region_qualified_culture_mapping["smn"] = '{smn-FI}'
    _region_qualified_culture_mapping["sms"] = '{sms-FI}'
    _region_qualified_culture_mapping["sn"] = '{sn-Latn-ZW}'
    _region_qualified_culture_mapping["sn-Latn"] = '{sn-Latn-ZW}'
    _region_qualified_culture_mapping["so"] = '{so-SO}'
    _region_qualified_culture_mapping["sq"] = '{sq-AL}'
    _region_qualified_culture_mapping["sr"] = '{sr-Latn-RS}'
    _region_qualified_culture_mapping["sr-Cyrl"] = '{sr-Cyrl-RS}'
    _region_qualified_culture_mapping["sr-Latn"] = '{sr-Latn-RS}'
    _region_qualified_culture_mapping["ss"] = '{ss-ZA}'
    _region_qualified_culture_mapping["ssy"] = '{ssy-ER}'
    _region_qualified_culture_mapping["st"] = '{st-ZA}'
    _region_qualified_culture_mapping["sv"] = '{sv-SE}'
    _region_qualified_culture_mapping["sw"] = '{sw-KE}'
    _region_qualified_culture_mapping["syr"] = '{syr-SY}'
    _region_qualified_culture_mapping["ta"] = '{ta-IN}'
    _region_qualified_culture_mapping["te"] = '{te-IN}'
    _region_qualified_culture_mapping["teo"] = '{teo-UG}'
    _region_qualified_culture_mapping["tg"] = '{tg-Cyrl-TJ}'
    _region_qualified_culture_mapping["tg-Cyrl"] = '{tg-Cyrl-TJ}'
    _region_qualified_culture_mapping["th"] = '{th-TH}'
    _region_qualified_culture_mapping["ti"] = '{ti-ER}'
    _region_qualified_culture_mapping["tig"] = '{tig-ER}'
    _region_qualified_culture_mapping["tk"] = '{tk-TM}'
    _region_qualified_culture_mapping["tn"] = '{tn-ZA}'
    _region_qualified_culture_mapping["to"] = '{to-TO}'
    _region_qualified_culture_mapping["tr"] = '{tr-TR}'
    _region_qualified_culture_mapping["ts"] = '{ts-ZA}'
    _region_qualified_culture_mapping["tt"] = '{tt-RU}'
    _region_qualified_culture_mapping["twq"] = '{twq-NE}'
    _region_qualified_culture_mapping["tzm"] = '{tzm-Latn-DZ}'
    _region_qualified_culture_mapping["tzm-Arab"] = '{tzm-Arab-MA}'
    _region_qualified_culture_mapping["tzm-Latn"] = '{tzm-Latn-DZ}'
    _region_qualified_culture_mapping["tzm-Tfng"] = '{tzm-Tfng-MA}'
    _region_qualified_culture_mapping["ug"] = '{ug-CN}'
    _region_qualified_culture_mapping["uk"] = '{uk-UA}'
    _region_qualified_culture_mapping["ur"] = '{ur-PK}'
    _region_qualified_culture_mapping["uz"] = '{uz-Latn-UZ}'
    _region_qualified_culture_mapping["uz-Arab"] = '{uz-Arab-AF}'
    _region_qualified_culture_mapping["uz-Cyrl"] = '{uz-Cyrl-UZ}'
    _region_qualified_culture_mapping["uz-Latn"] = '{uz-Latn-UZ}'
    _region_qualified_culture_mapping["vai"] = '{vai-Vaii-LR}'
    _region_qualified_culture_mapping["vai-Latn"] = '{vai-Latn-LR}'
    _region_qualified_culture_mapping["vai-Vaii"] = '{vai-Vaii-LR}'
    _region_qualified_culture_mapping["ve"] = '{ve-ZA}'
    _region_qualified_culture_mapping["vi"] = '{vi-VN}'
    _region_qualified_culture_mapping["vo"] = '{vo-001}'
    _region_qualified_culture_mapping["vun"] = '{vun-TZ}'
    _region_qualified_culture_mapping["wae"] = '{wae-CH}'
    _region_qualified_culture_mapping["wal"] = '{wal-ET}'
    _region_qualified_culture_mapping["wo"] = '{wo-SN}'
    _region_qualified_culture_mapping["xh"] = '{xh-ZA}'
    _region_qualified_culture_mapping["xog"] = '{xog-UG}'
    _region_qualified_culture_mapping["yav"] = '{yav-CM}'
    _region_qualified_culture_mapping["yi"] = '{yi-001}'
    _region_qualified_culture_mapping["yo"] = '{yo-NG}'
    _region_qualified_culture_mapping["zgh"] = '{zgh-Tfng-MA}'
    _region_qualified_culture_mapping["zgh-Tfng"] = '{zgh-Tfng-MA}'
    _region_qualified_culture_mapping["zh"] = '{zh-CN}'
    _region_qualified_culture_mapping["zh-Hans"] = '{zh-CN}'
    _region_qualified_culture_mapping["zh-Hant"] = '{zh-HK}'
    _region_qualified_culture_mapping["zu"] = '{zu-ZA}'
    _region_qualified_culture_mapping["zh-CHS"] = '{zh-CN}'
    _region_qualified_culture_mapping["zh-CHT"] = '{zh-HK}'

    @staticmethod
    def get_language_group_name(culture_name):
        return CultureInfoExtensions.get_language_group_id(culture_name)

    @staticmethod
    def get_language_group_id(culture_name):
        lcid = CultureInfoExtensions.get_lcid_from_culture_name(culture_name)
        if CultureInfoExtensions._locale_to_group_mapping.get(lcid, None) is not None:
            return CultureInfoExtensions._locale_to_group_mapping[lcid]
        return 'Unknown'

    @staticmethod
    def get_lcid_from_culture_name(culture_name):
        if culture_name == '':
            return 127
        # Use LOCALE_NAME to retrieve the LCID
        if CultureInfoExtensions._lcid_map.get(culture_name, None) is not None:
            return CultureInfoExtensions._lcid_map[culture_name]
        return -1

    @staticmethod
    def get_parent_culture(culture_name):
        # Split culture name to get the language part (before the hyphen)
        if '-' in culture_name:
            parent_culture = culture_name.split('-')[0]
            return parent_culture
        return ''

    @staticmethod
    def check_locale(culture_name):
        try:
            # Try to set the locale to the given culture name
            locale.setlocale(locale.LC_ALL, culture_name)
            return True
        except locale.Error:
            return False

    @staticmethod
    def get_culture_info(name, return_null_for_unknown=False):
        ret = ''
        if name is None:
            return None

        if len(name) == 0:
            ret = 'InvariantCulture'
            return ret

        try:
            lcid = int(name)
            return CultureInfoExtensions.get_culture_info_from_lcid(lcid)##imp
        except ValueError:
            pass

        if CultureInfoExtensions.legacy_language_mapping.get(name) is not None:
            return CultureInfoExtensions.legacy_language_mapping[name]

        if CultureInfoExtensions.check_locale(name):
            return name

        if CultureInfoExtensions.legacy_language_mapping.get(name) is not None:
            return CultureInfoExtensions.legacy_language_mapping[name]

        text = name.lower()
        if CultureInfoExtensions.legacy_language_codes.get(text) is not None:
            ret = CultureInfoExtensions.legacy_language_codes[text]
        elif text.endswith("-01"):
            name2 = text[:len(text) - 3]
            name2 = CultureInfoExtensions.get_region_qualified_culture(name2)
            ret = name2
        else:
            ret = name

        CultureInfoExtensions.legacy_language_mapping[text] = ret

        return ret

    @staticmethod
    def use_blank_as_word_separator(culture_name:str) -> bool:
        return not StringUtils.get_iso_language_code(culture_name) in CultureInfoExtensions.use_blank_as_word_separator_exceptions

if __name__ == "__main__":
    CultureInfoExtensions.__init__()
    ret = CultureInfoExtensions.get_culture_info('en-US')
    ret = CultureInfoExtensions.get_parent_culture(ret)
    ret = CultureInfoExtensions.get_parent_culture(ret)
    ret = CultureInfoExtensions.get_language_group_id('th')
    print(ret)