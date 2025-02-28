
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("qnaForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // 기본 제출 동작 방지

        const formData = new FormData(form);
        
        // ✅ 체크박스 값 추가
        formData.append("isPrivate", document.getElementById("private").checked);

        fetch("/qna/api/create", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())  // ✅ JSON 응답 받기
        .then(data => {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;  // ✅ 목록 페이지로 이동
            } else {
                alert("문의 등록 실패: " + data.error);
            }
        })
        .catch(error => console.error("에러 발생:", error));
    });
});