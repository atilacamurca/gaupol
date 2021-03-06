# Copyright (C) 2005-2009 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol. If not, see <http://www.gnu.org/licenses/>.

import aeidon
import codecs
_ = aeidon.i18n._


class TestModule(aeidon.TestCase):

    def test_code_to_description(self):
        code_to_description = aeidon.encodings.code_to_description
        assert code_to_description("cp1006") == _("Urdu")
        assert code_to_description("hz") == _("Chinese simplified")
        assert code_to_description("shift_jis") == _("Japanese")

    def test_code_to_description__value_error(self):
        code_to_description = aeidon.encodings.code_to_description
        self.raises(ValueError, code_to_description, "xxxxx")

    def test_code_to_long_name(self):
        code, name, description = ("cp1140", "IBM1140", _("Western"))
        long_name = aeidon.encodings.code_to_long_name(code)
        assert long_name == _("%(description)s (%(name)s)") % locals()

    def test_code_to_long_name__value_error(self):
        self.raises(ValueError, aeidon.encodings.code_to_long_name, "xxxxx")

    def test_code_to_name(self):
        code_to_name = aeidon.encodings.code_to_name
        assert code_to_name("big5hkscs") == "Big5-HKSCS"
        assert code_to_name("cp949") == "IBM949"
        assert code_to_name("mac_roman") == "MacRoman"

    def test_code_to_name__value_error(self):
        code_to_name = aeidon.encodings.code_to_name
        self.raises(ValueError, code_to_name, "xxxxx")

    def test_detect(self):
        name = aeidon.encodings.detect(self.new_subrip_file())
        assert aeidon.encodings.is_valid_code(name)

    @aeidon.deco.monkey_patch(aeidon.encodings, "translate_code")
    def test_detect__value_error(self):
        def bad_translate_code(code): raise ValueError
        aeidon.encodings.translate_code = bad_translate_code
        assert aeidon.encodings.detect(self.new_subrip_file()) is None

    def test_detect_bom__none(self):
        path = self.new_subrip_file()
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding is None

    def test_detect_bom__utf_8(self):
        path = self.new_subrip_file()
        text = open(path, "r").read()
        open(path, "w").write(codecs.BOM_UTF8 + text)
        encoding = aeidon.encodings.detect_bom(path)
        if aeidon.encodings.is_valid_code("utf_8_sig"):
            assert encoding == "utf_8_sig"

    def test_detect_bom__utf_16_be(self):
        path = self.new_subrip_file()
        text = open(path, "r").read()
        open(path, "w").write(codecs.BOM_UTF16_BE + text)
        encoding = aeidon.encodings.detect_bom(path)
        if aeidon.encodings.is_valid_code("utf_16_be"):
            assert encoding == "utf_16_be"

    def test_detect_bom__utf_16_le(self):
        path = self.new_subrip_file()
        text = open(path, "r").read()
        open(path, "w").write(codecs.BOM_UTF16_LE + text)
        encoding = aeidon.encodings.detect_bom(path)
        if aeidon.encodings.is_valid_code("utf_16_le"):
            assert encoding == "utf_16_le"

    def test_detect_bom__utf_32_be(self):
        path = self.new_subrip_file()
        text = open(path, "r").read()
        open(path, "w").write(codecs.BOM_UTF32_BE + text)
        encoding = aeidon.encodings.detect_bom(path)
        if aeidon.encodings.is_valid_code("utf_32_be"):
            assert encoding == "utf_32_be"

    def test_detect_bom__utf_32_le(self):
        path = self.new_subrip_file()
        text = open(path, "r").read()
        open(path, "w").write(codecs.BOM_UTF32_LE + text)
        encoding = aeidon.encodings.detect_bom(path)
        if aeidon.encodings.is_valid_code("utf_32_le"):
            assert encoding == "utf_32_le"

    def test_get_locale_code(self):
        code = aeidon.encodings.get_locale_code()
        assert aeidon.encodings.is_valid_code(code)

    def test_get_locale_long_name(self):
        long_name = aeidon.encodings.get_locale_long_name()
        code = aeidon.encodings.get_locale_code()
        name = aeidon.encodings.code_to_name(code)
        assert long_name == _("Current locale (%s)") % name

    def test_get_valid(self):
        assert aeidon.encodings.get_valid()
        for item in aeidon.encodings.get_valid():
            assert aeidon.encodings.is_valid_code(item[0])
            assert isinstance(item[1], basestring)
            assert isinstance(item[2], basestring)

    @aeidon.deco.monkey_patch(aeidon.encodings, "is_valid_code")
    def test_get_valid__invalid(self):
        bad_is_valid_code = lambda code: not code.startswith("cp")
        aeidon.encodings.is_valid_code = bad_is_valid_code
        assert aeidon.encodings.get_valid()

    def test_is_valid_code(self):
        assert aeidon.encodings.is_valid_code("gbk")
        assert aeidon.encodings.is_valid_code("utf_16_be")
        assert not aeidon.encodings.is_valid_code("xxxxx")

    def test_name_to_code(self):
        name_to_code = aeidon.encodings.name_to_code
        assert name_to_code("IBM037") == "cp037"
        assert name_to_code("GB2312") == "gb2312"
        assert name_to_code("PTCP154") == "ptcp154"

    def test_name_to_code__value_error(self):
        name_to_code = aeidon.encodings.name_to_code
        self.raises(ValueError, name_to_code, "XXXXX")

    def test_translate_code(self):
        translate_code = aeidon.encodings.translate_code
        assert translate_code("johab") == "johab"
        assert translate_code("UTF-8") == "utf_8"
        assert translate_code("ISO-8859-1") == "latin_1"

    def test_translate_code__value_error(self):
        translate_code = aeidon.encodings.translate_code
        self.raises(ValueError, translate_code, "xxxxx")
