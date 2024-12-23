from CultureInfoExtensions import CultureInfoExtensions

class TokenizerHelper:
    @staticmethod
    def is_cj_culture(culture_name:str) -> bool:
        return culture_name in ["zh-CHT", "zh-TW", "zh-CN", 'zh-HK', 'zh-SG', 'zh-MO', 'ja-JP']

    @staticmethod
    def uses_advanced_tokenization(culture_name:str) -> bool:
        return TokenizerHelper.is_cj_culture(culture_name)

    #AdvancedTokenization.TokenizesToWords
    @staticmethod
    def tokenizes_to_words(culture_name:str) -> bool:
        return CultureInfoExtensions.use_blank_as_word_separator(culture_name) or TokenizerHelper.uses_advanced_tokenization(culture_name)

