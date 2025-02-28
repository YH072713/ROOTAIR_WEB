const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', ()=>{
    menu.classList.toggle('active');
    member.classList.toggle('active');
});
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("qnaForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // 기본 제출 동작 방지

        const formData = new FormData(form);
        
        // ✅ 비밀글 체크 여부를 명확하게 설정 (체크 안 하면 'false' 기본값 추가)
        let isSecretValue = document.getElementById("private").checked ? "true" : "false";
        formData.set("isSecret", isSecretValue);  // 기존 append 대신 set 사용
        console.log("🔥 [DEBUG] isSecret 값:", isSecretValue);  // ✅ 디버깅 로그 추가
 
        fetch("/qna/api/create", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())  // ✅ JSON 응답 받기
        .then(data => {
            console.log("🔥 [DEBUG] API 응답:", data);
            if (data.redirect_url) {
                window.location.href = data.redirect_url;  // ✅ 목록 페이지로 이동
            } else {
                alert("문의 등록 실패: " + data.error);
            }
        })
        .catch(error => console.error("에러 발생:", error));
    });
});