require.config({ paths: { 'vs': "../../static/monaco-editor-0.19.3/package/min/vs" }});
require(["vs/editor/editor.main"], function() {
    var editor = monaco.editor.create(document.getElementById('monacoEditor'), {
        value: [
            'function x() {',
            '\tconsole.log("Hello world!");',
            '}'
        ].join('\n'),
        language: 'javascript',
        theme: "vs-dark",
    });
});