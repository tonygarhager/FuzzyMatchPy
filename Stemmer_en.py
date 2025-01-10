from Snowball import Stemmer, Among


class Stemmer_en(Stemmer):
    _registered = False
    g_v = "aeiouy"
    g_v_WXY = "aeiouywxY"
    g_valid_LI = "cdeghkmnrt"
    def __init__(self):
        self.i_p2 = 0
        self.i_p1 = 0
        self.a_0 = [
            Among("arsen", -1, -1),
            Among("commun", -1, -1),
            Among("gener", -1, -1)
        ]
        self.a_1 = [
            Among("'", -1, 1),
            Among("'s'", 0, 1),
            Among("'s", -1, 1)
        ]
        self.a_2 = [
            Among("ied", -1, 2),
            Among("s", -1, 3),
            Among("ies", 1, 2),
            Among("sses", 1, 1),
            Among("ss", 1, -1),
            Among("us", 1, -1)
        ]
        self.a_3 = [
            Among("", -1, 3),
            Among("bb", 0, 2),
            Among("dd", 0, 2),
            Among("ff", 0, 2),
            Among("gg", 0, 2),
            Among("bl", 0, 1),
            Among("mm", 0, 2),
            Among("nn", 0, 2),
            Among("pp", 0, 2),
            Among("rr", 0, 2),
            Among("at", 0, 1),
            Among("tt", 0, 2),
            Among("iz", 0, 1)
        ]
        self.a_4 = [
            Among("ed", -1, 2),
            Among("eed", 0, 1),
            Among("ing", -1, 2),
            Among("edly", -1, 2),
            Among("eedly", 3, 1),
            Among("ingly", -1, 2)
        ]
        self.a_5 = [
            Among("anci", -1, 3),
            Among("enci", -1, 2),
            Among("ogi", -1, 13),
            Among("li", -1, 15),
            Among("bli", 3, 12),
            Among("abli", 4, 4),
            Among("alli", 3, 8),
            Among("fulli", 3, 9),
            Among("lessli", 3, 14),
            Among("ousli", 3, 10),
            Among("entli", 3, 5),
            Among("aliti", -1, 8),
            Among("biliti", -1, 12),
            Among("iviti", -1, 11),
            Among("tional", -1, 1),
            Among("ational", 14, 7),
            Among("alism", -1, 8),
            Among("ation", -1, 7),
            Among("ization", 17, 6),
            Among("izer", -1, 6),
            Among("ator", -1, 7),
            Among("iveness", -1, 11),
            Among("fulness", -1, 9),
            Among("ousness", -1, 10)
        ]
        self.a_6 = [
            Among("icate", -1, 4),
            Among("ative", -1, 6),
            Among("alize", -1, 3),
            Among("iciti", -1, 4),
            Among("ical", -1, 4),
            Among("tional", -1, 1),
            Among("ational", 5, 2),
            Among("ful", -1, 5),
            Among("ness", -1, 5)
        ]
        self.a_7 = [
            Among("ic", -1, 1),
            Among("ance", -1, 1),
            Among("ence", -1, 1),
            Among("able", -1, 1),
            Among("ible", -1, 1),
            Among("ate", -1, 1),
            Among("ive", -1, 1),
            Among("ize", -1, 1),
            Among("iti", -1, 1),
            Among("al", -1, 1),
            Among("ism", -1, 1),
            Among("ion", -1, 2),
            Among("er", -1, 1),
            Among("ous", -1, 1),
            Among("ant", -1, 1),
            Among("ent", -1, 1),
            Among("ment", 15, 1),
            Among("ement", 16, 1)
        ]
        self.a_8 = [
            Among("e", -1, 1),
            Among("l", -1, 2)
        ]
        self.a_9 = [
            Among("succeed", -1, -1),
            Among("proceed", -1, -1),
            Among("exceed", -1, -1),
            Among("canning", -1, -1),
            Among("inning", -1, -1),
            Among("earring", -1, -1),
            Among("herring", -1, -1),
            Among("outing", -1, -1)
        ]
        self.a_10 = [
            Among("andes", -1, -1),
            Among("atlas", -1, -1),
            Among("bias", -1, -1),
            Among("cosmos", -1, -1),
            Among("dying", -1, 3),
            Among("early", -1, 9),
            Among("gently", -1, 7),
            Among("howe", -1, -1),
            Among("idly", -1, 6),
            Among("lying", -1, 4),
            Among("news", -1, -1),
            Among("only", -1, 10),
            Among("singly", -1, 11),
            Among("skies", -1, 2),
            Among("skis", -1, 1),
            Among("sky", -1, -1),
            Among("tying", -1, 5),
            Among("ugly", -1, 8)
        ]

    def r_prelude(self):
        self.b_y_found = False
        cursor = self.cursor
        self.bra = self.cursor

        # Check for the presence of "'"
        if super().eq_s("'"):
            self.ket = self.cursor
            super().slice_del()

        self.cursor = cursor
        cursor2 = self.cursor
        self.bra = self.cursor

        # Check for the presence of "y"
        if super().eq_s("y"):
            self.ket = self.cursor
            super().slice_from("Y")
            self.b_y_found = True

        self.cursor = cursor2
        cursor3 = self.cursor

        while True:
            cursor4 = self.cursor

            while True:
                cursor5 = self.cursor

                if super().in_grouping(Stemmer_en.g_v, 97, 121, False) == 0:
                    self.bra = self.cursor
                    if super().eq_s("y"):
                        break

                self.cursor = cursor5
                if self.cursor >= self.limit:
                    self.cursor = cursor4
                    self.cursor = cursor3
                    return True

                self.cursor += 1

            self.ket = self.cursor
            self.cursor = cursor5
            super().slice_from("Y")
            self.b_y_found = True

    def r_mark_regions(self):
        self.i_p1 = self.limit
        self.i_p2 = self.limit
        cursor = self.cursor
        cursor2 = self.cursor

        # Find among group a_0
        if super().find_among(self.a_0) == 0:
            self.cursor = cursor2
            num = super().out_grouping(Stemmer_en.g_v, 97, 121, True)
            if num < 0:
                self.cursor = cursor
                return True
            self.cursor += num

            num2 = super().in_grouping(Stemmer_en.g_v, 97, 121, True)
            if num2 < 0:
                self.cursor = cursor
                return True
            self.cursor += num2

        self.i_p1 = self.cursor

        num3 = super().out_grouping(Stemmer_en.g_v, 97, 121, True)
        if num3 >= 0:
            self.cursor += num3
            num4 = super().in_grouping(Stemmer_en.g_v, 97, 121, True)
            if num4 >= 0:
                self.cursor += num4
                self.i_p2 = self.cursor

        self.cursor = cursor
        return True

    def r_shortv(self):
        num = self.limit - self.cursor

        # Check conditions with `out_grouping_b` and `in_grouping_b`
        if (
                super().out_grouping_b(Stemmer_en.g_v_WXY, 89, 121, False) != 0
                or super().in_grouping_b(Stemmer_en.g_v, 97, 121, False) != 0
                or super().out_grouping_b(Stemmer_en.g_v, 97, 121, False) != 0
        ):
            self.cursor = self.limit - num
            if super().out_grouping_b(Stemmer_en.g_v, 97, 121, False) != 0:
                return False
            if super().in_grouping_b(Stemmer_en.g_v, 97, 121, False) != 0:
                return False
            if self.cursor > self.limit_backward:
                return False

        return True

    def r_R1(self):
        b = self.i_p1 <= self.cursor
        return b

    def r_R2(self):
        return self.i_p2 <= self.cursor

    def r_step_1a(self):
        num = self.limit - self.cursor
        self.ket = self.cursor

        # First find among `a_1`
        if super().find_among_b(self.a_1) == 0:
            self.cursor = self.limit - num
        else:
            self.bra = self.cursor
            super().slice_del()

        # Process `a_2`
        self.ket = self.cursor
        num2 = super().find_among_b(self.a_2)
        if num2 == 0:
            return False

        self.bra = self.cursor

        if num2 == 1:
            super().slice_from("ss")
        elif num2 == 2:
            num3 = self.limit - self.cursor
            num4 = self.cursor - 2
            if self.limit_backward <= num4 <= self.limit:
                self.cursor = num4
                super().slice_from("i")
            else:
                self.cursor = self.limit - num3
                super().slice_from("ie")
        elif num2 == 3:
            if self.cursor <= self.limit_backward:
                return False
            self.cursor -= 1
            num5 = super().out_grouping_b(Stemmer_en.g_v, 97, 121, True)
            if num5 < 0:
                return False
            self.cursor -= num5
            super().slice_del()

        return True

    def r_step_1b(self):
        self.ket = self.cursor
        num = super().find_among_b(self.a_4)
        if num == 0:
            return False
        self.bra = self.cursor

        if num == 1:
            if not self.r_R1():
                return False
            super().slice_from("ee")
        elif num == 2:
            num2 = self.limit - self.cursor
            num3 = super().out_grouping_b(Stemmer_en.g_v, 97, 121, True)
            if num3 < 0:
                return False
            self.cursor -= num3
            self.cursor = self.limit - num2
            super().slice_del()

            num4 = self.limit - self.cursor
            num = super().find_among_b(self.a_3)
            if num == 0:
                return False
            self.cursor = self.limit - num4

            if num == 1:
                cursor = self.cursor
                super().insert(self.cursor, self.cursor, "e")
                self.cursor = cursor
            elif num == 2:
                self.ket = self.cursor
                if self.cursor <= self.limit_backward:
                    return False
                self.cursor -= 1
                self.bra = self.cursor
                super().slice_del()
            elif num == 3:
                if self.cursor != self.i_p1:
                    return False
                num5 = self.limit - self.cursor
                if not self.r_shortv():
                    return False
                self.cursor = self.limit - num5
                cursor2 = self.cursor
                super().insert(self.cursor, self.cursor, "e")
                self.cursor = cursor2

        return True

    def r_step_1c(self):
        self.ket = self.cursor
        num = self.limit - self.cursor

        if not super().eq_s_b("y"):
            self.cursor = self.limit - num
            if not super().eq_s_b("Y"):
                return False

        self.bra = self.cursor

        if super().out_grouping_b(Stemmer_en.g_v, 97, 121, False) != 0:
            return False

        if self.cursor <= self.limit_backward:
            return False

        super().slice_from("i")
        return True

    def r_step_2(self):
        self.ket = self.cursor
        num = super().find_among_b(self.a_5)
        if num == 0:
            return False

        self.bra = self.cursor

        if self.r_R1() == False:
            return False

        if num == 1:
            super().slice_from("tion")
        elif num == 2:
            super().slice_from("ence")
        elif num == 3:
            super().slice_from("ance")
        elif num == 4:
            super().slice_from("able")
        elif num == 5:
            super().slice_from("ent")
        elif num == 6:
            super().slice_from("ize")
        elif num == 7:
            super().slice_from("ate")
        elif num == 8:
            super().slice_from("al")
        elif num == 9:
            super().slice_from("ful")
        elif num == 10:
            super().slice_from("ous")
        elif num == 11:
            super().slice_from("ive")
        elif num == 12:
            super().slice_from("ble")
        elif num == 13:
            if not super().eq_s_b("l"):
                return False
            super().slice_from("og")
        elif num == 14:
            super().slice_from("less")
        elif num == 15:
            if super().in_grouping_b(Stemmer_en.g_valid_LI, 99, 116, False) != 0:
                return False
            super().slice_del()

        return True

    def r_step_3(self):
        self.ket = self.cursor
        num = super().find_among_b(self.a_6)
        if num == 0:
            return False

        self.bra = self.cursor

        if not self.r_R1():
            return False

        if num == 1:
            super().slice_from("tion")
        elif num == 2:
            super().slice_from("ate")
        elif num == 3:
            super().slice_from("al")
        elif num == 4:
            super().slice_from("ic")
        elif num == 5:
            super().slice_del()
        elif num == 6:
            if not self.r_R2():
                return False
            super().slice_del()

        return True

    def r_step_4(self):
        self.ket = self.cursor
        num = super().find_among_b(self.a_7)
        if num == 0:
            return False

        self.bra = self.cursor

        if not self.r_R2():
            return False

        if num != 1:
            if num == 2:
                num2 = self.limit - self.cursor
                if not super().eq_s_b("s"):
                    self.cursor = self.limit - num2
                    if not super().eq_s_b("t"):
                        return False
                super().slice_del()
        else:
            super().slice_del()

        return True

    def r_step_5(self):
        self.ket = self.cursor
        num = super().find_among_b(self.a_8)
        if num == 0:
            return False

        self.bra = self.cursor

        if num != 1:
            if num == 2:
                if not self.r_R2():
                    return False
                if not super().eq_s_b("l"):
                    return False
                super().slice_del()
        else:
            num2 = self.limit - self.cursor
            if not self.r_R2():
                self.cursor = self.limit - num2
                if not self.r_R1():
                    return False
                num3 = self.limit - self.cursor
                if self.r_shortv():
                    return False
                self.cursor = self.limit - num3

            super().slice_del()

        return True

    def r_exception2(self):
        self.ket = self.cursor
        if super().find_among_b(self.a_9) == 0:
            return False

        self.bra = self.cursor
        return self.cursor <= self.limit_backward

    def r_exception1(self):
        self.bra = self.cursor
        num = super().find_among(self.a_10)
        if num == 0:
            return False

        self.ket = self.cursor
        if self.cursor < self.limit:
            return False

        if num == 1:
            super().slice_from("ski")
        elif num == 2:
            super().slice_from("sky")
        elif num == 3:
            super().slice_from("die")
        elif num == 4:
            super().slice_from("lie")
        elif num == 5:
            super().slice_from("tie")
        elif num == 6:
            super().slice_from("idl")
        elif num == 7:
            super().slice_from("gentl")
        elif num == 8:
            super().slice_from("ugli")
        elif num == 9:
            super().slice_from("earli")
        elif num == 10:
            super().slice_from("onli")
        elif num == 11:
            super().slice_from("singl")

        return True

    def r_postlude(self):
        if not self.b_y_found:
            return False

        while True:
            cursor = self.cursor
            while True:
                cursor2 = self.cursor
                self.bra = self.cursor
                if super().eq_s("Y"):
                    break
                self.cursor = cursor2
                if self.cursor >= self.limit:
                    self.cursor = cursor
                    return True

                self.cursor += 1

            self.ket = self.cursor
            self.cursor = cursor2
            super().slice_from("y")

    def stem(self):
        cursor = self.cursor
        if not self.r_exception1():
            self.cursor = cursor
            cursor2 = self.cursor
            num = self.cursor + 3
            if 0 <= num <= self.limit:
                self.cursor = num
                self.cursor = cursor
                self.r_prelude()
                self.r_mark_regions()
                self.limit_backward = self.cursor
                self.cursor = self.limit
                num2 = self.limit - self.cursor
                self.r_step_1a()
                self.cursor = self.limit - num2
                num3 = self.limit - self.cursor
                if not self.r_exception2():
                    self.cursor = self.limit - num3
                    num4 = self.limit - self.cursor
                    self.r_step_1b()
                    self.cursor = self.limit - num4
                    num5 = self.limit - self.cursor
                    self.r_step_1c()
                    self.cursor = self.limit - num5
                    num6 = self.limit - self.cursor
                    self.r_step_2()
                    self.cursor = self.limit - num6
                    num7 = self.limit - self.cursor
                    self.r_step_3()
                    self.cursor = self.limit - num7
                    num8 = self.limit - self.cursor
                    self.r_step_4()
                    self.cursor = self.limit - num8
                    num9 = self.limit - self.cursor
                    self.r_step_5()
                    self.cursor = self.limit - num9

                self.cursor = self.limit_backward
                cursor3 = self.cursor
                self.r_postlude()
                self.cursor = cursor3
            else:
                self.cursor = cursor2

        return True


