document.addEventListener("DOMContentLoaded", function () {
    console.log("DEBUG: JavaScript 로드 완료, 결제 시스템 초기화 중...");

    let totalAmount = parseInt(document.getElementById("final-amount").textContent.replace(/,/g, ""), 10);
    let rootpayBalance = parseInt(document.getElementById("rootpay-balance").textContent.replace(/,/g, ""), 10);
    let totalMileage = parseInt(document.getElementById("total-mileage").textContent.replace(/,/g, ""), 10);
    let earnedMileage = parseInt(document.getElementById("earned-mileage").textContent.replace(/,/g, ""), 10);
    let passengerCount = document.getElementById("passenger_count")?.value || "1";

    console.log(`DEBUG: 보유 마일리지 = ${totalMileage}, 적립 마일리지 = ${earnedMileage}, ROOT PAY 잔액 = ${rootpayBalance}, 총 금액 = ${totalAmount}`);

    const mileageInput = document.getElementById("mileage-input");
    const applyMileageButton = document.getElementById("apply-mileage");
    const usedMileageDisplay = document.getElementById("mileage-used");  
    const usedRootpayDisplay = document.getElementById("used-rootpay");
    const finalPaymentDisplay = document.getElementById("final-payment");
    const totalMileageFinalDisplay = document.getElementById("total-mileage-final");

    let mileageUsed = 0;
    let finalMileage = totalMileage + earnedMileage; 
    let selectedPayment = null;
    let paymentWindow = null; 

    if (!applyMileageButton) {
        console.error("ERROR: apply-mileage 버튼을 찾을 수 없습니다.");
        return;
    }

    // ✅ 마일리지 적용 버튼 클릭 시 최종 결제 금액 계산
    applyMileageButton.addEventListener("click", function () {
        console.log("DEBUG: 마일리지 적용 버튼 클릭됨");

        let inputMileage = parseInt(mileageInput.value, 10) || 0;

        if (inputMileage > totalMileage) {
            alert(`사용할 마일리지가 보유 마일리지(${totalMileage})를 초과할 수 없습니다.`);
            inputMileage = totalMileage; 
        }

        mileageUsed = inputMileage;

        let finalAmount = totalAmount - mileageUsed; // ✅ Root PAY 차감 없이 유지
        if (finalAmount < 0) finalAmount = 0;

        // ✅ 최종 마일리지 계산 (현재 마일리지 - 사용 마일리지 + 적립 마일리지)
        finalMileage = totalMileage - mileageUsed + earnedMileage;

        // ✅ UI 업데이트 (마일리지, 최종 결제 금액 반영)
        updateUI(mileageUsed, finalAmount, finalMileage);

        console.log(`DEBUG: 사용 마일리지 = ${mileageUsed}, 최종 결제 금액 = ${finalAmount}, 결제 후 최종 마일리지 = ${finalMileage}`);
        alert("마일리지가 적용되었습니다!");
    });

    // ✅ UI 업데이트 함수 (Root PAY 사용 금액은 결제 버튼 클릭 시 계산)
    function updateUI(mileageUsed, finalAmount, finalMileage) {
        if (usedMileageDisplay) usedMileageDisplay.textContent = mileageUsed.toLocaleString();
        if (finalPaymentDisplay) finalPaymentDisplay.textContent = finalAmount.toLocaleString();
        if (totalMileageFinalDisplay) totalMileageFinalDisplay.textContent = finalMileage.toLocaleString();
    }

    // ✅ 결제 수단 선택
    document.querySelectorAll(".payment-item").forEach(button => {
        button.addEventListener("click", function () {
            document.querySelectorAll('.payment-item').forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');
            selectedPayment = button.id;
        });
    });

    // ✅ 결제 버튼 클릭 시 처리
    document.getElementById("pay-button").addEventListener("click", function () {
        if (!selectedPayment) {
            alert("결제 수단을 선택해주세요!");
            return;
        }

        let finalPaymentAmount = parseInt(finalPaymentDisplay.textContent.replace(/,/g, ""), 10);
        let flightId = document.getElementById("flight_id")?.value;
        
        // ✅ Root PAY 결제 시 사용 금액 계산 (Root PAY 잔액보다 크면 Root PAY 전부 사용)
        let usedRootPay = finalPaymentAmount > rootpayBalance ? rootpayBalance : finalPaymentAmount;
        let remainingBalance = rootpayBalance - usedRootPay; 

        let queryParams = new URLSearchParams({
            total_price: finalPaymentAmount.toString(),
            user_id: document.getElementById("user_id")?.value || "user001",
            eng_name: document.getElementById("eng_name")?.value || "N/A",
            mileage_used: mileageUsed.toString(),
            final_mileage: finalMileage.toString(),
            used_rootpay: usedRootPay.toString(),  // ✅ 사용한 Root PAY 전송
            remaining_balance: remainingBalance.toString(),  // ✅ 결제 후 남은 Root PAY 전송
            passenger_count: passengerCount,
            flight_id: flightId
        });

        let paymentUrl = `/pay/payment_info?${queryParams.toString()}`;

        if (selectedPayment === "rootpay") {
            // ✅ 새 창으로 payment_info 열기
            paymentWindow = window.open(paymentUrl, "PaymentInfo", "width=800,height=600,resizable=yes");

            if (!paymentWindow) {
                alert("팝업 차단이 활성화되어 있습니다. 팝업을 허용해주세요.");
            } else {
                paymentWindow.focus();
            }
        } else if (selectedPayment === "kg-inicis") {
            processInicisPayment(finalPaymentAmount);
        }
    });

    // ✅ 결제 완료 후 부모 창 닫고 result로 이동
    window.addEventListener("message", function (event) {
        if (event.data && event.data.redirect_url) {
            console.log(`DEBUG: 결제 완료 → ${event.data.redirect_url}`);

            if (paymentWindow) {
                paymentWindow.close(); // ✅ 결제 창 닫기
            }

            window.location.href = event.data.redirect_url; // ✅ result 페이지로 이동
        }
    });

    // ✅ IMP(이니시스) 결제 처리
    function processInicisPayment(amount) {
        console.log("DEBUG: KG 이니시스 결제 시작 (금액: " + amount + "원)");

        let buyerEmail = document.getElementById("email")?.value || "test@default.com";
        let buyerName = document.getElementById("username")?.value || "Guest";
        let buyerTel = document.getElementById("phone")?.value || "010-0000-0000";

        console.log("DEBUG: 구매자 정보 확인", { buyerEmail, buyerName, buyerTel });

        if (typeof IMP === "undefined") {
            console.error("ERROR: IMP 객체를 찾을 수 없습니다. 결제 라이브러리가 로드되지 않았습니다.");
            alert("결제 시스템을 불러올 수 없습니다. 새로고침 후 다시 시도해주세요.");
            return;
        }

        IMP.init("imp87014111"); 

        IMP.request_pay({
            pg: "html5_inicis.INIpayTest",
            pay_method: "card",
            merchant_uid: "order_" + new Date().getTime(),
            name: "항공권 결제",
            amount: amount,
            buyer_email: buyerEmail,
            buyer_name: buyerName,
            buyer_tel: buyerTel,
            m_redirect_url: "/pay/result"  
        }, function (rsp) {
            if (rsp.success) {
                alert("결제 성공! 결제번호: " + rsp.imp_uid);
                window.location.href = "/pay/result";  
            } else {
                alert("결제 실패: " + rsp.error_msg);
            }
        });
    }
});