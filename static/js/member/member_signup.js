// 헤더
const togglebtn = document.querySelector('.navbar_togglebtn');
const menu = document.querySelector('.navbar_menu');
const member = document.querySelector('.navbar_member');

togglebtn.addEventListener('click', () => {
    menu.classList.toggle('active');
    member.classList.toggle('active');
});

function searchAddress() {
    new daum.Postcode({
        oncomplete: function(data) {
            document.getElementById("postal_code").value = data.zonecode;
            document.getElementById("address").value = data.address;
            document.getElementById("add_detail").focus();
        }
    }).open();
}

function checkId() {
    const userId = $('#user_id').val();
    if (!userId) {
        $('#idCheckResult').text('아이디를 입력해주세요.');
        return;
    }

    $.ajax({
        url: '/member/check-id',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ user_id: userId }),
        success: function(response) {
            $('#idCheckResult').text(response.message);
            if (response.available) {
                $('#idCheckResult').css('color', 'green');
            } else {
                $('#idCheckResult').css('color', 'red');
            }
        },
        error: function(xhr) {
            $('#idCheckResult').text('오류가 발생했습니다.');
            $('#idCheckResult').css('color', 'red');
        }
    });
}

function signUp(event) {
    event.preventDefault();
    
    const formData = {
        email: $('#email').val(),
        username: $('#username').val(),
        user_id: $('#user_id').val(),
        password: $('#password').val(),
        password_confirm: $('#password_confirm').val(),
        postal_code: $('#postal_code').val(),
        address: $('#address').val(),
        add_detail: $('#add_detail').val(),
        phone_number: $('#phone_number').val()
    };

    fetch('/member/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Sign up successful") {
            alert("회원가입이 완료되었습니다.");
            window.location.href = "/login";
        } else {
            alert(data.error || "회원가입 중 오류가 발생했습니다.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("회원가입 중 오류가 발생했습니다.");
    });
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("signupButton").addEventListener("click", signUp);
});



document.addEventListener("DOMContentLoaded", function() {
    const signupForm = document.getElementById("signupForm");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");
    const phoneInput = document.getElementById("phone_number");
    const userIdInput = document.getElementById("user_id");
    const nameInput = document.getElementById("username");
   
    const passwordError = document.getElementById("passwordError");
    const confirmPasswordError = document.getElementById("confirmPasswordError");
    const phoneError = document.getElementById("phoneError");
    const userIdError = document.getElementById("userIdError");
    const nameError = document.getElementById("nameError");
   
    let isUserIdChecked = false; // 중복 체크 여부 확인 변수
   
    function validateField(input, regex, errorElement, errorMessage) {
        input.addEventListener("input", function() {
            if (!regex.test(input.value)) {
                errorElement.style.display = "block";
                errorElement.innerText = errorMessage;
            } else {
                errorElement.style.display = "none";
            }
        });
   
        input.addEventListener("blur", function() {
            if (input.value.trim() === "") {
                errorElement.style.display = "none";
            }
        });
    }
   
    // 🔹 비밀번호 유효성 검사
    if (passwordInput) {
        validateField(
            passwordInput, 
            /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,20}$/, 
            passwordError, 
            "비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자로 설정해야 합니다."
        );
    }
   
    // 🔹 비밀번호 확인 검사
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener("input", function() {
            confirmPasswordError.style.display = (passwordInput.value !== confirmPasswordInput.value) ? "block" : "none";
            confirmPasswordError.innerText = "비밀번호가 일치하지 않습니다.";
        });
    }
   
    // 🔹 전화번호 유효성 검사
    if (phoneInput) {
        validateField(
            phoneInput, 
            /^010-\d{4}-\d{4}$|^010\d{8}$/, 
            phoneError, 
            "전화번호 형식이 올바르지 않습니다. (예: 010-1234-5678 또는 01012345678)"
        );
    }
   
    // 🔹 아이디 유효성 검사
    if (userIdInput) {
        validateField(
            userIdInput, 
            /^[a-zA-Z0-9]{5,15}$/, 
            userIdError, 
            "아이디는 영문과 숫자로 구성된 5~15자여야 합니다."
        );
   
        // 아이디 입력 시 중복 체크 여부 초기화
        userIdInput.addEventListener("input", function() {
            isUserIdChecked = false;
            userIdCheckError.style.display = "block";
            userIdCheckError.innerText = "아이디 중복 확인을 해주세요.";
        });
    }
   
    // 🔹 이름 유효성 검사
    if (nameInput) {
        nameInput.addEventListener("input", function() {
            nameError.style.display = (nameInput.value.trim().length < 2) ? "block" : "none";
            nameError.innerText = "이름은 최소 2자 이상 입력해야 합니다.";
        });
    }
   
   
    // 🔹 폼 제출 시 모든 유효성 검사 확인 + 중복 체크 확인
    if (signupForm) {
        signupForm.addEventListener("submit", function(event) {
            if (
                passwordError.style.display === "block" ||
                confirmPasswordError.style.display === "block" ||
                userIdError.style.display === "block" ||
                phoneError.style.display === "block" ||
                nameError.style.display === "block" ||
                !isUserIdChecked
            ) {
                event.preventDefault(); // 검증 실패 시 폼 제출 방지
                if (!isUserIdChecked) {
                    userIdCheckError.style.display = "block";
                    userIdCheckError.innerText = "아이디 중복 확인을 해주세요.";
                }
            }
        });
    }
   
    
   
   });
   
        // 🔹 회원가입 라벨 중앙 정렬 유지
    const signupLabel = document.querySelector("label[for='signup']");
        if (signupLabel) {
            signupLabel.style.textAlign = "center";
        }
    