#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import STYLE_MAP


class CodeHighlight():
    @staticmethod
    def getHtmlFormatter():
        return HtmlFormatter(cssclass="highlight_code",linenos='inline')

    @staticmethod
    def getLexer(language):
        if type(language) is not str:
            return None
        return get_lexer_by_name(language, stripall=True)

    @staticmethod
    def getStyleCss():
        return CodeHighlight.getHtmlFormatter().get_style_defs('.highlight_code');

    @staticmethod
    def codeTranslate(code, language):
        if type(code) is not str or type(language) is not str:
            return None
        lexer = CodeHighlight.getLexer(language)
        formatter = CodeHighlight.getHtmlFormatter()
        return highlight(code, lexer, formatter)
    



if __name__ == "__main__":
    code = r"""
    #include <iostream>
    using namespace std;

    int main()
    {
        int a,b;
        while(cin >> a >> b)
            cout << a+b << endl;
    }
    """
    print(CodeHighlight.codeTranslate(code,"cpp"))
    # print(CodeHighlight.getStyleCss())
