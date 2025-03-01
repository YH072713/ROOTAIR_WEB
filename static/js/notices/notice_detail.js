

// ✅ 목록으로 돌아가는 함수
function goBack() {
    window.location.href = "/notices";  // 공지사항 목록 페이지로 이동
}
document.addEventListener("DOMContentLoaded", function() {
    const deleteBtn = document.getElementById("deleteBtn");

    if (deleteBtn) {
        deleteBtn.addEventListener("click", function() {
            if (confirm("정말 삭제하시겠습니까?")) {
                const noticeId = deleteBtn.getAttribute("data-notice-id");

                fetch(`/notices/api/delete/${noticeId}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        window.location.href = data.redirect_url;
                    } else {
                        alert("삭제에 실패했습니다.");
                    }
                })
                .catch(error => {
                    console.error("삭제 오류:", error);
                    alert("오류가 발생했습니다. 다시 시도해주세요.");
                });
            }
        });
    }
});
