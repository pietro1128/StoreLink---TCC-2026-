
//#region CLICAR EM SUPORTE
var ativo = document.getElementById('suporte')
ativo.addEventListener('click', (setActiveNav));

function setActiveNav(btn) {
    document.querySelectorAll('.nav-btn').forEach(function (b) {
    b.classList.remove('active');
    });
    btn.classList.add('active');
}

//#endregion

function toggleTheme(btn) {
    document.body.classList.toggle('dark');
    var isDark = document.body.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (isDark) {
    btn.textContent = '☀️ Modo claro';
    } else {
    btn.textContent = '🌙 Modo escuro';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    var themeBtn = document.querySelector('.theme-toggle');
    if (themeBtn && document.body.classList.contains('dark')) {
    themeBtn.textContent = '☀️ Modo claro';
    }
});
 