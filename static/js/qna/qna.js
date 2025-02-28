
// ✅ 탭 전환 기능
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    if (tabId === "all-questions") {
        fetchInquiryList(1);  // ✅ 전체 문의사항 로드
    } else if (tabId === "my-questions") {
        fetchMyInquiryList(1);  // ✅ 나의 문의 로드
    }
}

// ✅ 페이지당 표시할 개수 및 현재 페이지 설정
const itemsPerPage = 5;
let currentPage = 1;

// ✅ 문의사항 목록 불러오기 (Flask API 호출)
function fetchInquiryList(page = 1) {
    fetch(`/qna/api?page=${page}`)  // ✅ Flask API에서 JSON 데이터를 가져옴
        .then(response => response.json())
        .then(data => {
            displayInquiryList(data.inquiries);
            createPaginationButtons(data.total_pages, page);
        })
        .catch(error => console.error("문의사항 데이터를 불러오는 중 오류 발생:", error));
}

// ✅ 문의사항 목록 표시
function displayInquiryList(inquiries) {
    let questionList = document.getElementById("question-list");
    questionList.innerHTML = "";  // 기존 목록 삭제 후 새 데이터 삽입

    inquiries.forEach((item) => {
        let row = `
            <tr onclick="viewDetail(${item.inquiry_id})">
                <td>${item.inquiry_id}</td>
                <td><a href="/qna/${item.inquiry_id}">${item.title}</a></td>
                <td>${item.user_id}</td>
                <td>${item.created_at}</td>
            </tr>
        `;
        questionList.innerHTML += row;
    });
}

// ✅ 페이지네이션 버튼 생성
function createPaginationButtons(totalPages, currentPage) {
    let pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    // "Previous" 버튼
    let prevButton = document.createElement("button");
    prevButton.innerText = "← Previous";
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => fetchInquiryList(currentPage - 1);
    pagination.appendChild(prevButton);

    // 페이지 번호 버튼 생성
    for (let i = 1; i <= totalPages; i++) {
        let pageButton = document.createElement("button");
        pageButton.innerText = i;
        pageButton.classList.add("page-btn");
        if (i === currentPage) {
            pageButton.classList.add("active");
        }
        pageButton.onclick = () => fetchInquiryList(i);
        pagination.appendChild(pageButton);
    }

    // "Next" 버튼
    let nextButton = document.createElement("button");
    nextButton.innerText = "Next →";
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => fetchInquiryList(currentPage + 1);
    pagination.appendChild(nextButton);
}

// ✅ 문의사항 상세 페이지 이동
function viewDetail(id) {
    window.location.href = `/qna/${id}`;
}

// ✅ 페이지 로드 시 데이터 가져오기
document.addEventListener("DOMContentLoaded", () => fetchInquiryList(1));
