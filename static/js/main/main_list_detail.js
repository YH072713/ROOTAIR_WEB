document.addEventListener("DOMContentLoaded", function () {
    const passengerCountInput = document.getElementById("passengerCount");
    const passengerTableBody = document.getElementById("passengerTableBody");
    const bookingForm = document.getElementById("bookingForm"); // ✅ form 요소 가져오기

    // URL 쿼리스트링에서 passenger_count 값을 읽어 hidden input에 적용
    const urlParams = new URLSearchParams(window.location.search);
    const passengerCountParam = urlParams.get('passenger_count');
    if (passengerCountParam) {
        passengerCountInput.value = passengerCountParam;
    }

    function updatePassengerFields(count) {
        passengerTableBody.innerHTML = ""; // 기존 입력 필드 초기화

        for (let i = 0; i < count; i++) {
            const row = document.createElement("tr");

            let nameCell = document.createElement("td");
            let nameInput = document.createElement("input");
            nameInput.setAttribute("type", "text");
            nameInput.setAttribute("name", "eng_name[]");  // ✅ 배열 형태 유지
            nameInput.setAttribute("placeholder", "여권 영문명을 입력하세요");
            nameInput.setAttribute("required", "true");
            nameCell.appendChild(nameInput);

            let genderCell = document.createElement("td");
            let genderSelect = document.createElement("select");
            genderSelect.setAttribute("name", "gender[]");
            let optionMale = document.createElement("option");
            optionMale.value = "남";
            optionMale.textContent = "남";
            let optionFemale = document.createElement("option");
            optionFemale.value = "여";
            optionFemale.textContent = "여";
            genderSelect.appendChild(optionMale);
            genderSelect.appendChild(optionFemale);
            genderCell.appendChild(genderSelect);

            let birthdateCell = document.createElement("td");
            let birthdateInput = document.createElement("input");
            birthdateInput.setAttribute("type", "text");
            birthdateInput.setAttribute("name", "birthdate[]");
            birthdateInput.setAttribute("placeholder", "YYYYMMDD");
            birthdateCell.appendChild(birthdateInput);

            row.appendChild(nameCell);
            row.appendChild(genderCell);
            row.appendChild(birthdateCell);

            passengerTableBody.appendChild(row);
        }
    }

    // 🚀 탑승객 수를 가져와 동적으로 입력칸 생성
    let passengerCount = parseInt(passengerCountInput.value) || 1;
    updatePassengerFields(passengerCount);

    // ✅ form 제출 이벤트 리스너 추가 (제출 전에 모든 input 값이 정상적으로 설정되었는지 확인)
    bookingForm.addEventListener("submit", function (event) {
        let engNames = document.querySelectorAll("input[name='eng_name[]']");
        let emptyFields = Array.from(engNames).filter(input => input.value.trim() === "");

        if (emptyFields.length > 0) {
            alert("모든 탑승객의 영문명을 입력해주세요.");
            event.preventDefault();
            return;
        }

        console.log("DEBUG: formData 전송 전 eng_name 값 =", Array.from(engNames).map(input => input.value.trim()));
    });
});
