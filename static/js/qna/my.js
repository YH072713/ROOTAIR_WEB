document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    const itemsPerPage = 3;

    function fetchMyqna(page) {
        fetch(`/qna/api/my?page=${page}`)
            .then(response => response.json())
            .then(data => {
                displayMyqna(data.qna);
                createPaginationButtons(data.total_pages, page);
            })
            .catch(error => console.error("나의 문의 데이터를 불러오는 중 오류 발생:", error));
    }

    function displayMyqna(qna) {
        let questionList = document.getElementById("question-list");
        questionList.innerHTML = "";

        qna.forEach(inquiry => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td>${inquiry.qna_id}</td>
                <td><a href="/qna/${inquiry.qna_id}">${inquiry.subject}</a></td>
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
                fetchMyqna(currentPage);
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
                fetchMyqna(currentPage);
            };
            pagination.appendChild(nextButton);
        }
    }

    fetchMyqna(currentPage);
});
