document.addEventListener("DOMContentLoaded", function () {
    console.log("DEBUG: JavaScript 로드 완료, 결제 시스템 초기화 중...");

    window.selectedPayment = null;

    // ✅ HTML에서 데이터를 가져오기
    let rootPayBalance = parseInt(document.getElementById("rootpay-balance")?.value || "0", 10);
    let finalAmount = parseInt(document.getElementById("total-price")?.value || "0", 10);
    let totalMileage = parseInt(document.getElementById("total-mileage")?.value || "0", 10);
    let usedMileage = 0; // 사용한 마일리지는 처음엔 0
    let earnedMileage = parseInt(document.getElementById("earned-mileage-input")?.value || "0", 10);
    let initialTotalMileage = totalMileage; // 🔥 보유 마일리지 저장 (변하지 않도록 설정)

    console.log("DEBUG: rootPayBalance =", rootPayBalance);
    console.log("DEBUG: finalAmount =", finalAmount);
    console.log("DEBUG: totalMileage =", totalMileage);
    console.log("DEBUG: usedMileage =", usedMileage);
    console.log("DEBUG: earnedMileage =", earnedMileage);

    const rootPayBalanceElement = document.getElementById("rootpay-balance");
    const finalAmountElement = document.getElementById("final-amount");
    const usedMileageElement = document.getElementById("used-mileage");
    const finalPaymentElement = document.getElementById("final-payment");
    const popupPaymentAmount = document.getElementById("popup-payment-amount");

    const currentMileageElement = document.getElementById("current-mileage");
    const earnedMileageElement = document.getElementById("earned-mileage-display");
    const totalMileageFinalElement = document.getElementById("total-mileage-final");

    const rootpaySection = document.getElementById("rootpay-section");

    updateUI(); // 최초 UI 업데이트

    document.getElementById("apply-mileage").addEventListener("click", function () {
        let mileageInput = parseInt(document.getElementById("mileage-input").value) || 0;

        console.log("DEBUG: 사용하려는 마일리지 =", mileageInput);
        console.log("DEBUG: 현재 보유 마일리지 =", totalMileage);

        if (mileageInput > initialTotalMileage) {
            alert("보유한 마일리지보다 많이 사용할 수 없습니다.");
            return;
        }

        if (mileageInput > finalAmount) {
            alert("결제 금액을 초과하여 마일리지를 사용할 수 없습니다.");
            return;
        }

        if (mileageInput < 0) {
            alert("마일리지는 0 이상 입력해야 합니다.");
            return;
        }

        // ✅ 사용한 마일리지 업데이트 (기존 값을 유지하면서 변경)
        usedMileage = mileageInput;
        totalMileage = initialTotalMileage - usedMileage; // 🔥 항상 원래 보유 마일리지를 기준으로 계산

        // ✅ UI 업데이트
        document.getElementById("used-mileage").value = usedMileage;
        updateUI();
    });

    function updateUI() {
        console.log("DEBUG: updateUI() 실행됨!");
        console.log("DEBUG: 현재 보유 마일리지 =", totalMileage);
        console.log("DEBUG: 사용한 마일리지 =", usedMileage);
        console.log("DEBUG: 적립 마일리지 =", earnedMileage);
        console.log("DEBUG: 결제 후 보유 마일리지 =", totalMileage + earnedMileage);
        console.log("DEBUG: 최종 결제 금액 =", finalAmount - usedMileage);
    
        // ✅ HTML 요소 가져오기
        const rootPayBalanceElement = document.getElementById("rootpay-balance");
        const finalAmountElement = document.getElementById("final-amount");
        const usedMileageElement = document.getElementById("used-mileage");
        const finalPaymentElement = document.getElementById("final-payment");
        const currentMileageElement = document.getElementById("current-mileage");
        const earnedMileageElement = document.getElementById("earned-mileage");
        const totalMileageFinalElement = document.getElementById("total-mileage-final");
    
        // ✅ 요소가 없는 경우 에러 출력
        if (!finalAmountElement) console.error("ERROR: final-amount 요소 없음!");
        if (!usedMileageElement) console.error("ERROR: used-mileage 요소 없음!");
        if (!finalPaymentElement) console.error("ERROR: final-payment 요소 없음!");
        if (!currentMileageElement) console.error("ERROR: current-mileage 요소 없음!");
        if (!earnedMileageElement) console.error("ERROR: earned-mileage 요소 없음!");
        if (!totalMileageFinalElement) console.error("ERROR: total-mileage-final 요소 없음!");
    
        // ✅ 요소가 없으면 UI 업데이트 중지
        if (!rootPayBalanceElement || !finalAmountElement || !usedMileageElement || 
            !finalPaymentElement || !currentMileageElement || !earnedMileageElement || !totalMileageFinalElement) {
            console.error("ERROR: 필요한 요소가 존재하지 않습니다. UI 업데이트 중지");
            return;
        }
    
        // ✅ UI 업데이트 (보유 마일리지는 변경되지 않도록 설정)
        rootPayBalanceElement.textContent = rootPayBalance.toLocaleString();
        finalAmountElement.textContent = finalAmount.toLocaleString();
        usedMileageElement.textContent = usedMileage.toLocaleString();
    
        let updatedFinalPayment = Math.max(finalAmount - usedMileage, 0);
        finalPaymentElement.textContent = updatedFinalPayment.toLocaleString();
    
        // 🚨 보유 마일리지는 변경하지 않음!
        // 기존 보유 마일리지를 totalMileage로 변경하지 않고, 사용한 마일리지만 업데이트
        currentMileageElement.textContent = (initialTotalMileage - usedMileage); 
        earnedMileageElement.textContent = earnedMileage.toLocaleString();
        totalMileageFinalElement.textContent = (initialTotalMileage - usedMileage + earnedMileage).toLocaleString();
    
        console.log("DEBUG: 화면 업데이트 완료!");
    }
    
    
    
    
    


    function selectPayment(paymentId) {
        document.querySelectorAll('.payment-item').forEach(button => button.classList.remove('selected'));

        const selectedButton = document.getElementById(paymentId);
        if (!selectedButton) {
            console.error("ERROR: 선택된 결제 수단을 찾을 수 없습니다.");
            return;
        }

        selectedButton.classList.add('selected');
        window.selectedPayment = paymentId;

        if (paymentId === "kg-inicis") {
            rootpaySection.style.display = "none";
        } else {
            rootpaySection.style.display = "block";
        }
    }

    document.getElementById("rootpay").addEventListener("click", () => selectPayment("rootpay"));
    document.getElementById("kg-inicis").addEventListener("click", () => selectPayment("kg-inicis"));

    document.getElementById("pay-button").addEventListener("click", function () {
        if (!window.selectedPayment) {
            alert("결제 수단을 선택해주세요!");
            return;
        }

        let updatedFinalPayment = parseInt(finalPaymentElement.textContent.replace(/,/g, "") || "0", 10);
        popupPaymentAmount.textContent = updatedFinalPayment.toLocaleString();

        document.getElementById("used-mileage").value = usedMileage;

        if (window.selectedPayment === "rootpay") {
            showRootPayPopup();
        } else if (window.selectedPayment === "kg-inicis") {
            processInicisPayment(updatedFinalPayment);
        }
    });

    function processInicisPayment(amount) {
        console.log("이니시스 결제 요청 시작 (금액: " + amount + "원)");

        let buyerName = document.getElementById("username")?.value || "Guest";
        let buyerEmail = document.getElementById("email")?.value || "test@default.com";
        let buyerTel = document.getElementById("phone")?.value || "010-0000-0000";
        let buyerAddr = document.getElementById("address")?.value || "주소 정보 없음";
        let buyerPostcode = document.getElementById("postcode")?.value || "00000";

        console.log("DEBUG: 구매자 정보 확인");
        console.log("이름: ", buyerName);
        console.log("이메일: ", buyerEmail);
        console.log("전화번호: ", buyerTel);
        console.log("주소: ", buyerAddr);
        console.log("우편번호: ", buyerPostcode);

        if (typeof IMP !== 'undefined') {
            IMP.init("imp87014111");
        } else {
            console.log("IMP 객체가 정의되지 않았습니다.");
            return;
        }

        IMP.request_pay({
            pg: 'html5_inicis.INIpayTest',
            pay_method: "card",
            merchant_uid: "order_" + new Date().getTime(),
            name: "항공권 결제",
            amount: amount,
            buyer_email: buyerEmail,
            buyer_name: buyerName,
            buyer_tel: buyerTel,
            buyer_addr: buyerAddr,
            buyer_postcode: buyerPostcode,
            m_redirect_url: "https://localhost:5000/result",
        }, function (rsp) {
            if (rsp.success) {
                alert('결제 성공! 결제번호: ' + rsp.imp_uid);
            } else {
                alert('결제 실패: ' + rsp.error_msg);
            }
        });
    }
});
