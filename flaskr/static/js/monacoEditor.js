var glbEditor = null;
this.initEditor();

function initEditor() {
    require.config({
        paths: {
            'vs': "../../static/monaco-editor-0.19.3/package/min/vs"
        }
    });
    require(["vs/editor/editor.main"], function () {
        var editor = monaco.editor.create(document.getElementById('monacoEditor'), {
            value: [
                'function x() {',
                '\tconsole.log("Hello world!");',
                '}'
            ].join('\n'),
            language: 'javascript',
            theme: "vs-dark"
        });
        glbEditor = editor;
    });
}

function changeEditor() {
    var selectLanguage = document.getElementById('selectLanguage');
    var index = selectLanguage.selectedIndex;
    var value = selectLanguage.options[index].value;
    console.log(value);
}