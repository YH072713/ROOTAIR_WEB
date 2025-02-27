document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    const itemsPerPage = 3;

    function fetchMyInquiries(page) {
        fetch(`/qna/api/my?page=${page}`)
            .then(response => response.json())
            .then(data => {
                displayMyInquiries(data.inquiries);
                createPaginationButtons(data.total_pages, page);
            })
            .catch(error => console.error("나의 문의 데이터를 불러오는 중 오류 발생:", error));
    }

    function displayMyInquiries(inquiries) {
        let questionList = document.getElementById("question-list");
        questionList.innerHTML = "";

        inquiries.forEach(inquiry => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td>${inquiry.inquiry_id}</td>
                <td><a href="/qna/${inquiry.inquiry_id}">${inquiry.subject}</a></td>
                <td>${inquiry.created_at}</td>
            `;
            questionList.appendChild(row);
        });
    }

    function createPaginationButtons(totalPages, currentPage) {
        let pagination = document.getElementById("pagination");
        pagination.innerHTML = "";

        if (currentPage > 1) {
            let prevButton = document.createElement("button");
            prevButton.innerText = "← Previous";
            prevButton.onclick = () => {
                currentPage--;
                fetchMyInquiries(currentPage);
            };
            pagination.appendChild(prevButton);
        }

        let pageIndicator = document.createElement("span");
        pageIndicator.innerText = `Page ${currentPage} of ${totalPages}`;
        pagination.appendChild(pageIndicator);

        if (currentPage < totalPages) {
            let nextButton = document.createElement("button");
            nextButton.innerText = "Next →";
            nextButton.onclick = () => {
                currentPage++;
                fetchMyInquiries(currentPage);
            };
            pagination.appendChild(nextButton);
        }
    }

    fetchMyInquiries(currentPage);
});
