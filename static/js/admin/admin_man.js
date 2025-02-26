// ✅ 헤더 토글 버튼 기능
const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', () => {
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

document.addEventListener("DOMContentLoaded", async function () {
    await fetchMembers();  // 페이지 로드 시 회원 목록 가져오기
});

let members = [];
const itemsPerPage = 10;
let currentPage = 1;

async function fetchMembers() {
    try {
        const response = await fetch('/admin/get_members');
        if (!response.ok) {
            throw new Error(`서버 응답 오류: ${response.status}`);
        }
        members = await response.json();
        currentPage = 1; // 데이터를 가져올 때 첫 페이지로 초기화
        displayMembers();
        displayPagination();
    } catch (error) {
        console.error('회원 데이터를 가져오는 중 오류 발생:', error);
    }
}

function displayMembers(filteredMembers = null) {
    const memberTable = document.getElementById("memberTable");
    memberTable.innerHTML = "";

    const data = filteredMembers || members; // 검색된 데이터가 있으면 그걸 사용
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedMembers = data.slice(start, end);

    paginatedMembers.forEach(member => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${member.id}</td>
            <td><input type="text" value="${member.user_id}" readonly></td>
            <td><input type="text" value="${member.username}" readonly></td>
            <td><input type="text" value="${member.phone_number}" readonly></td>
            <td><input type="text" value="${member.email}" readonly></td>
            <td><button class="delete-btn" onclick="deleteMember(${member.id})">삭제</button></td>
        `;

        memberTable.appendChild(row);
    });

    displayPagination(filteredMembers ? filteredMembers.length : members.length); // 검색 결과 페이지네이션 업데이트
}

function displayPagination(totalItems = members.length) {
    const pageNumbers = document.getElementById("pageNumbers");
    pageNumbers.innerHTML = "";

    const totalPages = Math.ceil(totalItems / itemsPerPage);

    for (let i = 1; i <= totalPages; i++) {
        const pageSpan = document.createElement("span");
        pageSpan.textContent = i;
        pageSpan.classList.add("page-btn");
        if (i === currentPage) {
            pageSpan.classList.add("active-page");
        }
        pageSpan.addEventListener("click", () => {
            currentPage = i;
            displayMembers();
            displayPagination(totalItems);  // 페이지네이션 다시 갱신
        });
        pageNumbers.appendChild(pageSpan);
    }

    document.getElementById("prevPage").style.display = currentPage > 1 ? "inline-block" : "none";
    document.getElementById("nextPage").style.display = currentPage < totalPages ? "inline-block" : "none";
}

async function deleteMember(id) {
    if (!confirm("정말 삭제하시겠습니까?")) return;

    try {
        const response = await fetch('/admin/delete_member', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            await fetchMembers();  // 삭제 후 목록 갱신
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('회원 삭제 중 오류 발생:', error);
    }
}

document.getElementById("prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        displayMembers();
        displayPagination();  // 페이지네이션 업데이트
    }
});

document.getElementById("nextPage").addEventListener("click", () => {
    const totalPages = Math.ceil(members.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayMembers();
        displayPagination();  // 페이지네이션 업데이트
    }
});

// 🔎 검색 기능 (검색 시 필터링 후 첫 페이지부터 다시 시작)
function searchMembers() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const filteredMembers = members.filter(member => 
        member.user_id.toLowerCase().includes(input) ||
        member.username.toLowerCase().includes(input) ||
        member.phone_number.toLowerCase().includes(input) ||
        member.email.toLowerCase().includes(input)
    );

    currentPage = 1; // 검색 시 첫 페이지로 이동
    displayMembers(filteredMembers);
    displayPagination(filteredMembers.length);
}
