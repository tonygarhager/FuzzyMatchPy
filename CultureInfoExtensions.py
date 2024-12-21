import locale
import win32api
import win32con
class CultureInfoExtensions:
    legacy_language_mapping = {}
    legacy_language_codes = {}
    _locale_to_group_mapping = {}

    @staticmethod
    def __init__():
        CultureInfoExtensions.legacy_language_codes["no-no"] = "nb-NO"
        CultureInfoExtensions.legacy_language_codes["no-ny"] = "nn-NO"
        CultureInfoExtensions.legacy_language_codes["no-xy"] = "nn-NO"
        CultureInfoExtensions.legacy_language_codes["es-em"] = "es-ES"
        CultureInfoExtensions.legacy_language_codes["es-xm"] = "es-ES"
        CultureInfoExtensions.legacy_language_codes["es-xy"] = "es-ES"
        CultureInfoExtensions.legacy_language_codes["es-xl"] = "es-419"
        CultureInfoExtensions.legacy_language_codes["es-cn"] = "es-CL"
        CultureInfoExtensions.legacy_language_codes["es-me"] = "es-MX"
        CultureInfoExtensions.legacy_language_codes["mt"] = "mt-MT"
        CultureInfoExtensions.legacy_language_codes["mt-01"] = "mt-MT"
        CultureInfoExtensions.legacy_language_codes["cy"] = "cy-GB"
        CultureInfoExtensions.legacy_language_codes["cy-01"] = "cy-GB"
        CultureInfoExtensions.legacy_language_codes["ga"] = "ga-IE"
        CultureInfoExtensions.legacy_language_codes["gd"] = "gd-GB"
        CultureInfoExtensions.legacy_language_codes["ga-CT"] = "gd-GB"
        CultureInfoExtensions.legacy_language_codes["iw"] = "he-IL"
        CultureInfoExtensions.legacy_language_codes["rm"] = "rm-CH"
        CultureInfoExtensions.legacy_language_codes["in"] = "id-ID"
        CultureInfoExtensions.legacy_language_codes["mn-xc"] = "mn-MN"
        CultureInfoExtensions.legacy_language_codes["ms-bx"] = "ms-BN"
        CultureInfoExtensions.legacy_language_codes["qu"] = "quz-BO"
        CultureInfoExtensions.legacy_language_codes["qu-BO"] = "quz-BO"
        CultureInfoExtensions.legacy_language_codes["qu-EC"] = "quz-EC"
        CultureInfoExtensions.legacy_language_codes["qu-PE"] = "quz-PE"
        CultureInfoExtensions.legacy_language_codes["sz"] = "se-FI"
        CultureInfoExtensions.legacy_language_codes["tl"] = "fil-PH"
        CultureInfoExtensions.legacy_language_codes["fl"] = "fil-PH"
        CultureInfoExtensions.legacy_language_codes["pt-pr"] = "pt-PT"
        CultureInfoExtensions.legacy_language_codes["zh-_c"] = "zh-CN"
        CultureInfoExtensions.legacy_language_codes["zh-_t"] = "zh-TW"
        CultureInfoExtensions.legacy_language_codes["zh-XM"] = "zh-MO"
        CultureInfoExtensions.legacy_language_codes["se"] = "se-NO"
        CultureInfoExtensions.legacy_language_codes["nep"] = "ne-NP"
        CultureInfoExtensions.legacy_language_codes["ne"] = "ne-NP"
        CultureInfoExtensions.legacy_language_codes["div"] = "dv-MV"
        CultureInfoExtensions.legacy_language_codes["mi"] = "mi-NZ"
        CultureInfoExtensions.legacy_language_codes["bo"] = "bo-CN"
        CultureInfoExtensions.legacy_language_codes["km"] = "km-KH"
        CultureInfoExtensions.legacy_language_codes["lo"] = "lo-LA"
        CultureInfoExtensions.legacy_language_codes["si"] = "si-LK"
        CultureInfoExtensions.legacy_language_codes["am"] = "am-ET"
        CultureInfoExtensions.legacy_language_codes["fy"] = "fy-NL"
        CultureInfoExtensions.legacy_language_codes["ba"] = "ba-RU"
        CultureInfoExtensions.legacy_language_codes["rw"] = "rw-RW"
        CultureInfoExtensions.legacy_language_codes["wo"] = "wo-SN"
        CultureInfoExtensions.legacy_language_codes["tk"] = "tk-TM"
        CultureInfoExtensions.legacy_language_codes["kl"] = "kl-GL"
        CultureInfoExtensions.legacy_language_codes["tg"] = "tg-Cyrl-TJ"
        CultureInfoExtensions.legacy_language_codes["ug"] = "ug-CN"
        CultureInfoExtensions.legacy_language_codes["ps"] = "ps-AF"
        CultureInfoExtensions.legacy_language_codes["br"] = "br-FR"
        CultureInfoExtensions.legacy_language_codes["oc"] = "oc-FR"
        CultureInfoExtensions.legacy_language_codes["co"] = "co-FR"
        CultureInfoExtensions.legacy_language_codes["ha"] = "ha-Latn-NG"
        CultureInfoExtensions.legacy_language_codes["yo"] = "yo-NG"
        CultureInfoExtensions.legacy_language_codes["ig"] = "ig-NG"
        CultureInfoExtensions.legacy_language_codes["sh-hr"] = "hr-HR"
        CultureInfoExtensions.legacy_language_codes["sh"] = "hr-HR"
        CultureInfoExtensions.legacy_language_codes["sh-sr"] = "sr-Latn-CS"
        CultureInfoExtensions.legacy_language_codes["sh-yu"] = "sr-Cyrl-CS"
        CultureInfoExtensions.legacy_language_codes["sr-xc"] = "sr-Cyrl-CS"
        CultureInfoExtensions.legacy_language_codes["bs"] = "bs-Latn-BA"
        CultureInfoExtensions.legacy_language_codes["sh-B1"] = "hr-BA"
        CultureInfoExtensions.legacy_language_codes["sh-B2"] = "bs-Latn-BA"
        CultureInfoExtensions.legacy_language_codes["sh-B3"] = "sr-Latn-BA"
        CultureInfoExtensions.legacy_language_codes["sh-B4"] = "sr-Cyrl-BA"
        CultureInfoExtensions.legacy_language_codes["sr-SP"] = "sr-Cyrl-CS"
        CultureInfoExtensions.legacy_language_codes["az-xc"] = "az-Cyrl-AZ"
        CultureInfoExtensions.legacy_language_codes["az-xe"] = "az-Latn-AZ"
        CultureInfoExtensions.legacy_language_codes["az-cy"] = "az-Cyrl-AZ"
        CultureInfoExtensions.legacy_language_codes["az-lt"] = "az-Latn-AZ"
        CultureInfoExtensions.legacy_language_codes["az-AZ"] = "az-Latn-AZ"
        CultureInfoExtensions.legacy_language_codes["uz-xc"] = "uz-Cyrl-UZ"
        CultureInfoExtensions.legacy_language_codes["uz-xl"] = "uz-Latn-UZ"
        CultureInfoExtensions.legacy_language_codes["uz-lt"] = "uz-Latn-UZ"
        CultureInfoExtensions.legacy_language_codes["uz-cy"] = "uz-Cyrl-UZ"
        CultureInfoExtensions.legacy_language_codes["uz-UZ"] = "uz-Latn-UZ"
        CultureInfoExtensions.legacy_language_codes["en-uk"] = "en-GB"
        CultureInfoExtensions.legacy_language_codes["en-cr"] = "en-029"
        CultureInfoExtensions.legacy_language_codes["en-cb"] = "en-029"
        CultureInfoExtensions.legacy_language_codes["en-tr"] = "en-TT"
        CultureInfoExtensions.legacy_language_codes["en-rh"] = "en-ZW"
        CultureInfoExtensions.legacy_language_codes["bn"] = "bn-IN"
        CultureInfoExtensions.legacy_language_codes["ml"] = "ml-IN"
        CultureInfoExtensions.legacy_language_codes["or"] = "or-IN"
        CultureInfoExtensions.legacy_language_codes["as"] = "as-IN"
        CultureInfoExtensions.legacy_language_codes["tn"] = "tn-ZA"
        CultureInfoExtensions.legacy_language_codes["xh"] = "xh-ZA"
        CultureInfoExtensions.legacy_language_codes["zu"] = "zu-ZA"
        CultureInfoExtensions.legacy_language_codes["ns"] = "nso-ZA"
        CultureInfoExtensions.legacy_language_codes["ns-ZA"] = "nso-ZA"

        

    @staticmethod
    def get_language_group_id(culture_name):
        pass###imp
    @staticmethod
    def get_lcid_from_locale(locale_name):
        # Use the GetLocaleInfo function to retrieve the LCID for a given culture name
        try:
            return win32api.GetLocaleInfo(win32con.LOCALE_SENGLANGUAGE, locale_name)
        except Exception as e:
            print(f"Error retrieving LCID for {locale_name}: {e}")

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

if __name__ == "__main__":
    CultureInfoExtensions.__init__()
    ret = CultureInfoExtensions.get_culture_info('en-US')
    ret = CultureInfoExtensions.get_parent_culture(ret)
    ret = CultureInfoExtensions.get_parent_culture(ret)
    print(ret)