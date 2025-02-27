const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', ()=>{
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

document.addEventListener("DOMContentLoaded", function () {
    const passwordForm = document.getElementById("passwordForm");
    const errorMessage = document.getElementById("error-message");
  
    passwordForm.addEventListener("submit", function (event) {
      event.preventDefault();
  
      const inputPassword = document.getElementById("password").value;
  
      // 서버의 '/cancel' 라우트로 POST 요청 (폼 데이터 전송)
      fetch('/mypage/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ password: inputPassword })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert(data.message);
          // 회원 탈퇴가 완료되면 홈 페이지(또는 원하는 페이지)로 리다이렉트
          window.location.href = '/';
        } else {
          errorMessage.textContent = data.message;
          errorMessage.style.display = "block";
        }
      })
      .catch(error => {
        console.error('오류 발생:', error);
        errorMessage.textContent = "요청 처리 중 오류가 발생했습니다.";
        errorMessage.style.display = "block";
      });
    });
  });
  