
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("qnaForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // 기본 제출 동작 방지

        const formData = new FormData(form);
        
        // ✅ 체크박스 값 추가
        formData.append("isPrivate", document.getElementById("private").checked);
        
        // ✅ qna_id 값을 HTML에서 가져오기
        const qnaId = form.getAttribute("data-qna-id");
        if (!qnaId) {
            alert("문의 ID를 찾을 수 없습니다.");
            return;
        }

        fetch(`/qna/api/edit/${qnaId}`, {
            method: "POST",
            body: formData
        })
        .then(response => response.json())  // ✅ JSON 응답 받기
        .then(data => {
            if (data.message) {
                alert(data.message);
                window.location.href = "/qna";
            } else {
                alert("문의 등록 실패: " + data.error);
            }
        })
        .catch(error => console.error("에러 발생:", error));
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file");
    const fileNameDisplay = document.getElementById("fileNameDisplay");

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name; // ✅ 새 파일명 표시
        } else {
            fileNameDisplay.textContent = "선택된 파일 없음";
        }
    });
});
