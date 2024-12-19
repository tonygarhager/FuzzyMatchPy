
class BooleanSettingsWrapper:
    def __init__(self, dbsettingsValue):
        self._unpackDbSettingValue(dbsettingsValue)

    def _unpackDbSettingValue(self, dbsettingsValue):
        self.builtinRecognizer = dbsettingsValue & 0x7f
        num = (dbsettingsValue & 0xFF0000) >> 16
        num ^= 1
        num ^= 2
        num ^= 4
        self.tokenizerFlags = num & 7
        num >>= 4
        num ^= 4
        self.wordCountFlags = num & 0xf