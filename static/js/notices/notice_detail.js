
// 네비게이션 메뉴 토글 기능
const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', () => {
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

// ✅ 목록으로 돌아가는 함수
function goBack() {
    window.location.href = "/notices";  // 공지사항 목록 페이지로 이동
}
