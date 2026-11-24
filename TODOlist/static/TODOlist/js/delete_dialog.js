// 削除リンク(.js-delete)をクリックしたら、確認ページへ遷移せずダイアログを開く。
// <dialog>が使えない環境では何もしないので、リンクがそのまま確認ページへ遷移する。
(function () {
    'use strict';

    var dialog = document.getElementById('delete-dialog');
    if (!dialog || typeof dialog.showModal !== 'function') {
        return;
    }

    var form = dialog.querySelector('form');
    var target = document.getElementById('delete-dialog-target');
    var cancel = document.getElementById('delete-dialog-cancel');

    document.querySelectorAll('.js-delete').forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            form.action = link.href;
            target.textContent = link.dataset.deleteTitle || '';
            dialog.showModal();
        });
    });

    cancel.addEventListener('click', function () {
        dialog.close();
    });

    // 背景(::backdrop)をクリックしたら閉じる。ダイアログ内側は<form>が覆っているので、
    // event.targetがdialog自身になるのは背景をクリックしたときだけ。
    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) {
            dialog.close();
        }
    });
})();
