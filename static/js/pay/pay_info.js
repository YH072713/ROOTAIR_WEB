
document.addEventListener("DOMContentLoaded", function () {
    console.log("DEBUG: 결제 정보 페이지 로드 완료");

    // ✅ GET 파라미터에서 데이터 가져오기
    const urlParams = new URLSearchParams(window.location.search);
    console.log("DEBUG: GET 파라미터 =", Object.fromEntries(urlParams.entries())); // 🔥 GET 데이터 확인

    // ✅ HTML에 데이터 표시
    document.getElementById("display_total_price").textContent = urlParams.get("total_price") || "0";

    // ✅ 폼 데이터 자동 채움 (오타 수정 및 기본값 설정)
    let form = document.getElementById("paymentInfoForm");

    form.elements["username"].value = urlParams.get("username") || "Unknown User";
    form.elements["eng_name"].value = urlParams.get("eng_name") || "N/A";  // ✅ `eng_name` 포함
    form.elements["airplane_name"].value = urlParams.get("airplane_name") || "Unknown Flight";
    form.elements["seat_class"].value = urlParams.get("seat_class") || "Economy";
    form.elements["passenger_count"].value = urlParams.get("passenger_count") || "1";
    form.elements["total_price"].value = urlParams.get("total_price") || "0";
    form.elements["email"].value = urlParams.get("email") || "example@email.com";
    form.elements["mileage_used"].value = urlParams.get("mileage_used") || "0";
});

function submitPayment() {
    let consentChecked = document.getElementById("consent").checked;
    if (!consentChecked) {
        alert("결제 정보를 제공에 동의해야 합니다.");
        return;
    }

    let formData = new FormData(document.getElementById("paymentInfoForm"));

    // ✅ `eng_name` 값이 폼에 포함되는지 확인
    console.log("DEBUG: 전송할 formData 데이터:");
    for (let pair of formData.entries()) {
        console.log(`${pair[0]} = ${pair[1]}`);
    }

    fetch("/pay/process_payment", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("DEBUG: 서버 응답 데이터 =", data);
        if (data.redirect_url) {
            // ✅ 부모 창이 존재하면 부모 창으로 리디렉트 메시지 전송
            if (window.opener) {
                window.opener.postMessage({ redirect_url: data.redirect_url }, "*");
            }
            window.close();  // ✅ 자식 창 닫기
        } else {
            alert("결제 실패: " + data.error);
        }
    })
    .catch(error => {
        console.error("ERROR: 결제 요청 실패", error);
        alert("결제 요청 중 오류가 발생했습니다.");
    });
}
