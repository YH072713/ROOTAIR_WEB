// 네비게이션 토글 기능
const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', () => {
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

// 로그인 함수
function login(user_id, password) {
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'user_id': user_id,
            'password': password
        }),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Login failed');
        }
        return response.json();
    })
    .then(data => {
        if (data.message === "Login successful") {
            window.location.href = '/edit_info';
        } else {
            throw new Error(data.error || '로그인 실패');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
}

// 페이지 로드 시 인증 상태 확인
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    if (currentPath !== '/login') {
        checkAuthAndRedirect();
    }
});

function checkAuthAndRedirect() {
    fetch('/check-auth', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Unauthorized');
        }
        return response.json();
    })
    .then(data => {
        console.log('Authentication successful:', data);
        if (window.location.pathname === '/login') {
            window.location.href = '/edit_info';
        }
    })
    .catch(error => {
        console.error('Authentication error:', error);
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    });
}

// 로그아웃 함수
function logout() {
    fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(() => {
        window.location.href = '/login';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('로그아웃 중 오류가 발생했습니다.');
    });
}

// 회원 정보 수정 페이지 접근 함수
function fetchEditInfo() {
    fetch('/edit_info', {
        method: 'GET',
        credentials: 'include'  // 쿠키를 포함하도록 설정
    })
    .then(response => {
        if (response.ok) {
            return response.text(); // HTML 또는 JSON 데이터 반환
        } else if (response.status === 401) {
            throw new Error('Unauthorized');
        } else {
            throw new Error('요청 실패');
        }
    })
    .then(html => {
        document.body.innerHTML = html; // 페이지 내용을 업데이트
    })
    .catch(error => {
        console.error('Error:', error);
        alert('인증에 실패했습니다. 다시 로그인해주세요.');
        window.location.href = '/login'; // 인증 실패 시 로그인 페이지로 이동
    });
}

// DOM 로드 후 /edit_info 요청 실행
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;

    // 로그인 페이지에서는 인증 확인을 하지 않음
    if (currentPath === '/login') {
        return;
    }

    // 다른 페이지에서는 인증 상태를 확인
    fetch('/check-auth', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Unauthorized');
        }
        return response.json();
    })
    .then(data => {
        console.log('Authentication successful:', data);
        if (currentPath === '/edit_info') {
            fetchEditInfo();
        }
    })
    .catch(error => {
        console.error('Authentication error:', error);
        window.location.href = '/login'; // 인증되지 않은 상태면 로그인 페이지로 이동
    });
});

document.addEventListener('DOMContentLoaded', function() {
    fetch('/check-auth', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Authenticated") {
            window.location.href = '/edit_info';
        }
    })
    .catch(error => console.error('Error:', error));
});

function login(user_id, password) {
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user_id, password: password }),
        credentials: 'include' // 쿠키 포함
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Login failed');
        }
        return response.json();
    })
    .then(data => {
        if (data.message === "Login successful") {
            // 로그인 성공 시 /edit_info로 리다이렉트
            window.location.href = '/edit_info';
        } else {
            throw new Error(data.error || '로그인 실패');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
}

function logout() {
    fetch('/logout', { method: 'POST', credentials: 'include' })
        .then(() => window.location.href = '/login')
        .catch(error => console.error('Error:', error));
}

function fetchEditInfo() {
    fetch('/edit_info', {
        method: 'GET',
        credentials: 'include'  // 쿠키를 포함하도록 설정
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Unauthorized');
            }
            throw new Error('요청 실패');
        }
        return response.text();
    })
    .then(html => {
        document.body.innerHTML = html; // 페이지 내용을 업데이트
    })
    .catch(error => {
        console.error('Error:', error);
        if (error.message === 'Unauthorized') {
            alert('인증에 실패했습니다. 다시 로그인해주세요.');
            window.location.href = '/login'; // 인증 실패 시 로그인 페이지로 이동
        } else {
            alert('오류가 발생했습니다: ' + error.message);
        }
    });
}

function fetchProtectedResource() {
    const token = localStorage.getItem('jwt_token'); // 또는 쿠키에서 읽기

    fetch('/protected', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}` // JWT 토큰 추가
        }
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

function refreshAccessToken() {
    fetch('/refresh', {
        method: 'POST',
        credentials: 'include' // 쿠키 포함
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to refresh token');
        }
        return response.json();
    })
    .then(data => {
        console.log('New access token:', data.access_token);
        // 새 액세스 토큰 저장 또는 사용
    })
    .catch(error => {
        console.error('Error refreshing token:', error);
        alert('세션이 만료되었습니다. 다시 로그인해주세요.');
        window.location.href = '/login';
    });
}

const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
fetch('/your-endpoint', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  credentials: 'include',
  body: JSON.stringify(data)
})