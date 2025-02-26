// ✅ 헤더 토글 버튼 기능
const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', () => {
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

document.addEventListener("DOMContentLoaded", function() {
    // ✅ Flash 메시지 자동 제거 (5초 후)
    setTimeout(function() {
        let flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(message) {
            message.style.opacity = "0";
            setTimeout(() => message.remove(), 300); // 부드럽게 제거
        });
        
        // ✅ 새로고침 시 메시지가 남아있지 않도록 세션에서 제거
        fetch('/clear_flash', { method: 'POST' });
    }, 5000);
});


