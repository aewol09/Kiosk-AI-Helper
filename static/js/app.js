// ==========================================================================
// KIOSK HELPER STATE MANAGEMENT
// ==========================================================================
let state = {
    activeScreen: 'landing', // 'landing', 'brand-select', 'simulator'
    kioskStep: 1,            // Steps 1 to 6
    cart: [],                // Array of { name, price, quantity, options }
    pendingItem: null,       // Item currently being configured in Step 2 options modal
    mistakeCount: 0,
    startTime: null,
    duration: 0,
    brand: '메가커피',
    menus: {},               // Category map loaded from server
    currentCategory: '커피', // Currently active menu tab
    voiceListening: false,
    recognition: null,       // Web Speech STT object
    ttsSpeaking: false,
    voiceTargetMenu: null    // Dynamically targeted menu card by voice command
};

// Target selectors for guidance in each step
function getGuideTargetSelector() {
    if (state.kioskStep === 1) {
        if (state.cart.length === 0) {
            if (state.voiceTargetMenu) {
                return `.menu-card[data-name="${state.voiceTargetMenu}"]`;
            }
            return '.menu-card[data-name="(ICE)아메리카노"]';
        } else {
            // Target is the Checkout button
            return '#btn-kiosk-checkout';
        }
    } else if (state.kioskStep === 2) {
        // Target is the Options commit button
        return '#btn-opt-commit';
    } else if (state.kioskStep === 3) {
        // Target is the Payment confirmation button
        return '#btn-confirm-pay';
    } else if (state.kioskStep === 4) {
        // Target is the Take-out card
        return '#btn-take-out';
    } else if (state.kioskStep === 5) {
        // Target is the Credit Card payment method card
        return '#btn-pay-card';
    } else if (state.kioskStep === 6) {
        const receiptVisible = document.getElementById('receipt-stage') && document.getElementById('receipt-stage').style.display === 'flex';
        if (receiptVisible) {
            return '#btn-receipt-finish';
        }
        // Target is the Card insertion slot button
        return '#btn-insert-card';
    }
    return null;
}

// Guideline speech bubble messages
function getGuideMessage() {
    if (state.kioskStep === 1) {
        if (state.cart.length === 0) {
            if (state.voiceTargetMenu) {
                return `1단계: 메뉴를 고를 차례입니다. 말씀하신 '${state.voiceTargetMenu}' 메뉴를 눌러보세요.`;
            }
            return "1단계: 메뉴를 고를 차례입니다. 시원한 커피인 '[ICE] 아메리카노' 메뉴를 눌러보세요.";
        } else {
            return "음료가 장바구니에 담겼습니다. 아래에 있는 주황색 '결제하기' 버튼을 눌러보세요.";
        }
    } else if (state.kioskStep === 2) {
        return "2단계: 옵션 선택 화면입니다. 더 넣고 싶은 옵션을 고른 뒤, 오른쪽 아래 '주문담기' 버튼을 누르세요.";
    } else if (state.kioskStep === 3) {
        return "3단계: 주문 내역과 금액을 확인하는 화면입니다. 내용이 맞으면 아래 오른쪽 '결제하기' 버튼을 누르세요.";
    } else if (state.kioskStep === 4) {
        return "4단계: 식사하실 곳을 고르는 화면입니다. 포장해서 가져가시려면 오른쪽 '포장하기' 버튼을 눌러보세요.";
    } else if (state.kioskStep === 5) {
        return "5단계: 결제 수단을 고르는 화면입니다. 신용카드로 계산하기 위해 왼쪽 '카드결제' 버튼을 눌러보세요.";
    } else if (state.kioskStep === 6) {
        return "6단계: 결제를 위해 카드를 넣어야 합니다. 화면 중앙의 초록색 '가상 신용카드 넣기' 버튼을 눌러보세요.";
    }
    return "";
}

// ==========================================================================
// INITIALIZATION AND ROUTING
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    setupEventListeners();
    setupSpeechRecognition();
});

function setupEventListeners() {
    // Screen transitions
    document.getElementById('btn-start').addEventListener('click', () => switchScreen('brand-select'));
    document.getElementById('btn-brand-back').addEventListener('click', () => switchScreen('landing'));
    document.getElementById('btn-brand-mega').addEventListener('click', () => {
        state.brand = '메가커피';
        switchScreen('simulator');
        startSession();
    });

    // Instructions Guide dialog
    document.getElementById('btn-show-guide').addEventListener('click', () => {
        document.getElementById('guide-modal-overlay').classList.add('active');
        speakTTS("키오스크 도우미 사용 방법 안내입니다. 천천히 읽어보신 후 아래 확인했습니다 단추를 눌러주세요.");
    });
    document.getElementById('btn-close-guide').addEventListener('click', () => {
        document.getElementById('guide-modal-overlay').classList.remove('active');
        cancelTTS();
    });

    // Kiosk simulator actions
    document.getElementById('btn-kiosk-checkout').addEventListener('click', handleKioskCheckout);
    document.getElementById('btn-opt-cancel').addEventListener('click', cancelOptions);
    document.getElementById('btn-opt-commit').addEventListener('click', commitOptions);
    document.getElementById('btn-confirm-cancel').addEventListener('click', cancelConfirm);
    document.getElementById('btn-confirm-pay').addEventListener('click', commitConfirm);
    
    // Eat-in / Take-out choices
    document.getElementById('btn-take-out').addEventListener('click', () => setEatInOption('포장'));
    document.getElementById('btn-eat-in').addEventListener('click', () => setEatInOption('매장'));
    
    // Payment method choices
    document.getElementById('btn-pay-card').addEventListener('click', setPaymentMethod);
    
    // Card simulation
    document.getElementById('btn-insert-card').addEventListener('click', insertCreditCard);
    document.getElementById('btn-receipt-finish').addEventListener('click', finishSession);

    // Sidebar translator search
    document.getElementById('sim-voice-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') processSimulatedVoice();
    });
    document.getElementById('btn-sim-voice-submit').addEventListener('click', processSimulatedVoice);

    // Sidebar microphone trigger
    document.getElementById('btn-browser-mic').addEventListener('click', toggleMic);

    // Suggested speech quick buttons
    document.querySelectorAll('.phrase-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const txt = btn.getAttribute('data-text');
            document.getElementById('sim-voice-input').value = txt;
            processSimulatedVoice();
        });
    });
}

function switchScreen(screenId) {
    state.activeScreen = screenId;
    document.querySelectorAll('.app-screen').forEach(scr => scr.classList.remove('active'));
    document.getElementById(`screen-${screenId}`).classList.add('active');

    if (screenId === 'landing') {
        loadStatistics();
        cancelTTS();
    }
}

// ==========================================================================
// SESSION STATE MACHINE
// ==========================================================================
function startSession() {
    state.kioskStep = 1;
    state.cart = [];
    state.pendingItem = null;
    state.mistakeCount = 0;
    state.startTime = new Date();
    state.voiceTargetMenu = null;
    
    fetchMenuData().then(() => {
        renderKioskStep();
    });
}

function fetchMenuData() {
    return fetch('/api/menu')
        .then(res => res.json())
        .then(data => {
            state.menus = data[state.brand] || {};
            // Default active category
            state.currentCategory = Object.keys(state.menus)[0] || '커피';
        })
        .catch(err => console.error("Error fetching menu:", err));
}

function handleKioskCheckout() {
    if (state.cart.length > 0) {
        if (state.kioskStep === 1) {
            triggerFeedback('success');
            state.kioskStep = 3; // Move to confirmation
            renderKioskStep();
        } else {
            triggerFeedback('error');
        }
    } else {
        triggerFeedback('error');
    }
}

function cancelOptions() {
    state.pendingItem = null;
    state.kioskStep = 1;
    state.voiceTargetMenu = null;
    renderKioskStep();
}

function commitOptions() {
    if (state.pendingItem) {
        triggerFeedback('success');
        // Match duplicate names & options to increase quantity
        let duplicate = state.cart.find(item => 
            item.name === state.pendingItem.name && 
            JSON.stringify(item.options) === JSON.stringify(state.pendingItem.options)
        );
        if (duplicate) {
            duplicate.quantity += 1;
        } else {
            state.cart.push(state.pendingItem);
        }
        state.pendingItem = null;
        state.kioskStep = 1;
        state.voiceTargetMenu = null;
        renderKioskStep();
    }
}

function cancelConfirm() {
    state.cart = [];
    state.kioskStep = 1;
    state.voiceTargetMenu = null;
    renderKioskStep();
}

function commitConfirm() {
    if (state.kioskStep === 3) {
        triggerFeedback('success');
        state.kioskStep = 4; // Move to Eat-in selection
        renderKioskStep();
    }
}

function setEatInOption(option) {
    if (state.kioskStep === 4) {
        triggerFeedback('success');
        state.eatInOption = option;
        state.kioskStep = 5; // Move to payment method select
        renderKioskStep();
    }
}

function setPaymentMethod() {
    if (state.kioskStep === 5) {
        triggerFeedback('success');
        state.kioskStep = 6; // Move to Card slot
        renderKioskStep();
    }
}

function insertCreditCard() {
    if (state.kioskStep === 6) {
        triggerFeedback('success');
        // Finalize timing and mistakes
        const endTime = new Date();
        state.duration = Math.round((endTime - state.startTime) / 1000);

        // Render receipt values
        document.getElementById('rec-brand').textContent = state.brand;
        let menusStr = state.cart.map(item => `${item.name} ${item.quantity}개`).join(', ');
        document.getElementById('rec-menus').textContent = menusStr;
        document.getElementById('rec-duration').textContent = `${state.duration}초`;
        document.getElementById('rec-mistakes').textContent = `${state.mistakeCount}회`;

        // Save learning record to server
        fetch('/api/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brand: state.brand,
                ordered_menus: menusStr,
                duration_seconds: state.duration,
                mistake_count: state.mistakeCount
            })
        }).then(res => res.json())
        .then(() => {
            // Hide card inserter, show receipt
            document.getElementById('payment-complete-stage').style.display = 'none';
            document.getElementById('receipt-stage').style.display = 'flex';
            
            let finishMessage = `결제가 성황리에 완료되었습니다! 총 ${state.duration}초 동안 연습하셨고, 실수는 ${state.mistakeCount}회 하셨습니다. 정말 참 잘하셨습니다! 이제 화면 아래의 처음 화면으로 돌아가기 버튼을 눌러주세요.`;
            const bubbleText = document.getElementById('ai-bubble-text');
            if (bubbleText) bubbleText.textContent = finishMessage;
            const sidebarText = document.getElementById('ai-sidebar-text');
            if (sidebarText) sidebarText.textContent = finishMessage;
            speakTTS(finishMessage);
        });
    }
}

function finishSession() {
    // Reset completed screen display toggles
    document.getElementById('payment-complete-stage').style.display = 'block';
    document.getElementById('receipt-stage').style.display = 'none';
    switchScreen('landing');
}

// ==========================================================================
// RENDER INTERACTIVE WEB KIOSK LAYOUT
// ==========================================================================
function renderKioskStep() {
    // Clear and hide all kiosk subviews
    document.querySelectorAll('.kiosk-view').forEach(view => view.classList.remove('active'));
    
    // Highlight step dots
    document.querySelectorAll('.step-dot').forEach(dot => {
        dot.classList.remove('active');
        if (parseInt(dot.getAttribute('data-step')) === state.kioskStep) {
            dot.classList.add('active');
        }
    });

    const step = state.kioskStep;
    if (step === 1) {
        document.getElementById('kiosk-view-menu').classList.add('active');
        renderCategoryTabs();
        renderMenuGrid();
        renderCartPanel();
    } else if (step === 2) {
        document.getElementById('kiosk-view-options').classList.add('active');
        renderOptionsView();
    } else if (step === 3) {
        document.getElementById('kiosk-view-confirm').classList.add('active');
        renderConfirmView();
    } else if (step === 4) {
        document.getElementById('kiosk-view-eat-option').classList.add('active');
    } else if (step === 5) {
        document.getElementById('kiosk-view-payment-method').classList.add('active');
    } else if (step === 6) {
        document.getElementById('kiosk-view-payment-complete').classList.add('active');
    }

    // Trigger AI helper animation glide and speech bubble
    setTimeout(positionAICharacter, 300);
}

function renderCategoryTabs() {
    const container = document.getElementById('kiosk-category-container');
    container.innerHTML = '';

    Object.keys(state.menus).forEach(cat => {
        const btn = document.createElement('button');
        btn.className = `category-btn ${state.currentCategory === cat ? 'active' : ''}`;
        btn.textContent = cat;
        btn.addEventListener('click', () => {
            state.currentCategory = cat;
            renderCategoryTabs();
            renderMenuGrid();
        });
        container.appendChild(btn);
    });
}

function renderMenuGrid() {
    const grid = document.getElementById('kiosk-menu-grid');
    grid.innerHTML = '';

    const items = state.menus[state.currentCategory] || [];
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'menu-card';
        card.setAttribute('data-name', item.name);
        
        // Graphic coffee cup placeholder using character styling
        const placeholder = document.createElement('div');
        placeholder.className = 'menu-card-img-placeholder';
        placeholder.textContent = getMenuEmoji(item.name);
        card.appendChild(placeholder);

        const nameLabel = document.createElement('span');
        nameLabel.className = 'menu-card-name';
        nameLabel.textContent = item.name;
        card.appendChild(nameLabel);

        const priceLabel = document.createElement('span');
        priceLabel.className = 'menu-card-price';
        priceLabel.textContent = `${item.price.toLocaleString()}원`;
        card.appendChild(priceLabel);

        // Click handler to select menu
        card.addEventListener('click', () => {
            // Trigger translation update on click automatically
            translateMenuItem(item.name);
            
            // Clear voice target since they clicked a menu
            state.voiceTargetMenu = null;
            
            // Validate if selecting this menu matches correct guide step
            let targetSelector = getGuideTargetSelector();
            if (targetSelector && card.matches(targetSelector)) {
                triggerFeedback('success');
                state.pendingItem = {
                    name: item.name,
                    price: item.price,
                    quantity: 1,
                    options: {
                        '텀블러': '사용 안함',
                        '샷 추가': '기본(2샷)',
                        '당도': '보통'
                    }
                };
                state.kioskStep = 2;
                renderKioskStep();
            } else {
                // If it is another menu, we update the guide target dynamically to let them practice with it!
                triggerFeedback('success');
                state.pendingItem = {
                    name: item.name,
                    price: item.price,
                    quantity: 1,
                    options: {
                        '텀블러': '사용 안함',
                        '샷 추가': '기본(2샷)',
                        '당도': '보통'
                    }
                };
                // Change guide target to match the menu item they chose!
                state.cart = []; // clear cart
                state.kioskStep = 2;
                renderKioskStep();
            }
        });

        grid.appendChild(card);
    });
}

function getMenuEmoji(name) {
    if (name.includes("아메리카노") || name.includes("에스프레소") || name.includes("화이트")) return "☕";
    if (name.includes("라떼") || name.includes("마끼아또")) return "🥛";
    if (name.includes("에이드") || name.includes("주스")) return "🍹";
    if (name.includes("티")) return "🍵";
    return "🍩";
}

function renderCartPanel() {
    const list = document.getElementById('kiosk-cart-list');
    list.innerHTML = '';

    state.cart.forEach((item, idx) => {
        const row = document.createElement('div');
        row.className = 'cart-item-row';

        const nameCol = document.createElement('div');
        nameCol.className = 'cart-item-name';
        let optText = Object.values(item.options).filter(v => v !== '사용 안함' && v !== '기본(2샷)' && v !== '보통').join(', ');
        nameCol.textContent = `${item.name}${optText ? ' [' + optText + ']' : ''}`;
        row.appendChild(nameCol);

        const qtyCol = document.createElement('div');
        qtyCol.className = 'cart-item-qty-controls';
        
        const minus = document.createElement('button');
        minus.className = 'qty-btn';
        minus.textContent = '-';
        minus.addEventListener('click', () => {
            if (item.quantity > 1) {
                item.quantity--;
            } else {
                state.cart.splice(idx, 1);
            }
            renderCartPanel();
        });
        qtyCol.appendChild(minus);

        const qtyVal = document.createElement('span');
        qtyVal.textContent = item.quantity;
        qtyCol.appendChild(qtyVal);

        const plus = document.createElement('button');
        plus.className = 'qty-btn';
        plus.textContent = '+';
        plus.addEventListener('click', () => {
            item.quantity++;
            renderCartPanel();
        });
        qtyCol.appendChild(plus);
        row.appendChild(qtyCol);

        const priceCol = document.createElement('span');
        priceCol.className = 'cart-item-price';
        priceCol.textContent = `${(item.price * item.quantity).toLocaleString()}원`;
        row.appendChild(priceCol);

        list.appendChild(row);
    });

    const totalPrice = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('kiosk-total-price').textContent = totalPrice.toLocaleString();
}

function renderOptionsView() {
    if (!state.pendingItem) return;
    document.getElementById('opt-item-name').textContent = state.pendingItem.name;

    // Reset option choices button states
    setupOptionGroupHandler('opt-choice-tumbler', '텀블러', (val) => {
        // Adjust price dynamically for tumbler discount
        if (val.includes('텀블러 사용')) {
            state.pendingItem.price = state.pendingItem.price - 300;
        } else {
            // Revert back
            state.pendingItem.price = state.pendingItem.price + 300;
        }
    });
    setupOptionGroupHandler('opt-choice-shot', '샷 추가', (val) => {
        if (val.includes('1샷 추가')) {
            state.pendingItem.price = state.pendingItem.price + 500;
        } else {
            // If they toggled back to normal or light
            // Reset options diff
        }
    });
    setupOptionGroupHandler('opt-choice-sugar', '당도');
}

function setupOptionGroupHandler(containerId, category, priceCallback) {
    const parent = document.getElementById(containerId);
    parent.querySelectorAll('.choice-btn').forEach(btn => {
        btn.classList.remove('active');
        const val = btn.getAttribute('data-val');
        if (state.pendingItem.options[category] === val) {
            btn.classList.add('active');
        }

        // Replace click triggers
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.addEventListener('click', () => {
            const oldVal = state.pendingItem.options[category];
            const newVal = newBtn.getAttribute('data-val');
            if (oldVal !== newVal) {
                state.pendingItem.options[category] = newVal;
                if (priceCallback) priceCallback(newVal);
                renderOptionsView();
            }
        });
    });
}

function renderConfirmView() {
    const tbody = document.getElementById('confirm-items-tbody');
    tbody.innerHTML = '';

    state.cart.forEach(item => {
        const tr = document.createElement('tr');
        
        const tdName = document.createElement('td');
        tdName.style.textAlign = 'left';
        let optText = Object.values(item.options).filter(v => v !== '사용 안함' && v !== '기본(2샷)' && v !== '보통').join(', ');
        tdName.innerHTML = `<strong>${item.name}</strong>${optText ? '<div class="confirm-item-details">' + optText + '</div>' : ''}`;
        tr.appendChild(tdName);

        const tdQty = document.createElement('td');
        tdQty.textContent = `${item.quantity}개`;
        tr.appendChild(tdQty);

        const tdPrice = document.createElement('td');
        tdPrice.textContent = `${(item.price * item.quantity).toLocaleString()}원`;
        tr.appendChild(tdPrice);

        tbody.appendChild(tr);
    });

    const totalPrice = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('confirm-total-price').textContent = `${totalPrice.toLocaleString()}원`;
}

// ==========================================================================
// DYNAMIC FLOATING AI BARISTA POSITIONING (COORD MATH)
// ==========================================================================
function positionAICharacter() {
    // 1. Remove glow borders from old target elements
    const oldTargets = document.querySelectorAll('.glowing-target');
    oldTargets.forEach(el => el.classList.remove('glowing-target'));

    const aiElem = document.getElementById('floating-ai');
    const bubbleText = document.getElementById('ai-bubble-text');
    const sidebarText = document.getElementById('ai-sidebar-text');
    
    // 2. Find new target elements
    const targetSelector = getGuideTargetSelector();
    let targetEl = null;
    if (targetSelector) {
        targetEl = document.querySelector(targetSelector);
    }
    
    let guideMessage = getGuideMessage();
    if (bubbleText) {
        bubbleText.textContent = guideMessage;
    }
    if (sidebarText) {
        sidebarText.textContent = guideMessage;
    }
    
    // Trigger speech synthesis
    speakTTS(guideMessage);

    if (targetEl) {
        // 3. Highlight target element
        targetEl.classList.add('glowing-target');
        
        // 4. Calculate relative coordinates to place the avatar
        const kioskContainer = document.getElementById('kiosk-container');
        const kioskRect = kioskContainer.getBoundingClientRect();
        const targetRect = targetEl.getBoundingClientRect();
        
        const relativeTop = targetRect.top - kioskRect.top;
        const relativeLeft = targetRect.left - kioskRect.left;
        
        const isReceiptStage = (targetSelector === '#btn-receipt-finish');
        const containerWidth = isReceiptStage ? 270 : 200;
        const avatarHeight = 60;
        const bubbleHeight = 68; // estimated height of speech bubble + margin
        const totalHeight = avatarHeight + bubbleHeight;
        const margin = 8;
        
        // Remove old alignment classes
        aiElem.classList.remove('align-left', 'align-right', 'align-center', 'bubble-bottom', 'bubble-side');
        
        let aiLeft = 0;
        let aiTop = 0;
        
        if (isReceiptStage) {
            // Receipt page: place helper at the bottom right corner with side-by-side bubble layout
            aiElem.classList.add('align-right', 'bubble-side');
            aiLeft = 540 - containerWidth - 10; // 260px
            aiTop = 675 - 75; // 600px (near bottom)
        } else {
            // Let's decide side to place
            let placeSide = 'right'; // 'right', 'left', 'top', 'bottom'
            
            // Check if placing on the right overflows right edge
            if (relativeLeft + targetRect.width + margin + containerWidth > 540) {
                placeSide = 'left';
            }
            
            // Check if placing on the left overflows left edge
            if (placeSide === 'left' && relativeLeft - margin - containerWidth < 0) {
                placeSide = 'top';
            }
            
            // Determine whether bubble goes on bottom
            let isBubbleBottom = (state.kioskStep >= 4);
            if (placeSide === 'top') {
                isBubbleBottom = false; // Bubble on top, avatar closest to button
            } else if (placeSide === 'bottom') {
                isBubbleBottom = true; // Avatar closest to button, bubble below
            }
            
            if (isBubbleBottom) {
                aiElem.classList.add('bubble-bottom');
            } else {
                aiElem.classList.remove('bubble-bottom');
            }
            
            if (placeSide === 'right') {
                aiElem.classList.add('align-left'); // Avatar on left of container, bubble extends right
                aiLeft = relativeLeft + targetRect.width + margin;
                if (isBubbleBottom) {
                    aiTop = relativeTop + (targetRect.height / 2) - 30;
                } else {
                    aiTop = relativeTop + (targetRect.height / 2) - 30 - bubbleHeight;
                }
            } else if (placeSide === 'left') {
                aiElem.classList.add('align-right'); // Avatar on right of container, bubble extends left
                aiLeft = relativeLeft - margin - containerWidth;
                if (isBubbleBottom) {
                    aiTop = relativeTop + (targetRect.height / 2) - 30;
                } else {
                    aiTop = relativeTop + (targetRect.height / 2) - 30 - bubbleHeight;
                }
            } else if (placeSide === 'top') {
                aiElem.classList.add('align-center');
                aiLeft = relativeLeft + (targetRect.width / 2) - (containerWidth / 2);
                aiTop = relativeTop - totalHeight - margin;
                if (aiTop < 10) {
                    placeSide = 'bottom';
                    isBubbleBottom = true;
                    aiElem.classList.add('bubble-bottom');
                }
            }
            
            if (placeSide === 'bottom') {
                aiElem.classList.add('align-center');
                aiLeft = relativeLeft + (targetRect.width / 2) - (containerWidth / 2);
                aiTop = relativeTop + targetRect.height + margin;
            }
            
            // Keep within kiosk boundaries
            if (aiTop < 10) aiTop = 10;
            if (aiTop > 675 - totalHeight - 10) aiTop = 675 - totalHeight - 10;
            if (aiLeft < 10) aiLeft = 10;
            if (aiLeft > 540 - containerWidth - 10) aiLeft = 540 - containerWidth - 10;
        }

        aiElem.style.left = `${aiLeft}px`;
        aiElem.style.top = `${aiTop}px`;
        aiElem.style.opacity = '1';
    } else {
        // Home position (bottom right corner bezel area)
        aiElem.classList.remove('align-left', 'align-right', 'bubble-bottom', 'bubble-side');
        aiElem.classList.add('align-center');
        aiElem.style.left = '330px';
        aiElem.style.top = '480px';
    }
}

// Visual screen flash success/error indicators
function triggerFeedback(type) {
    const area = document.getElementById('kiosk-body-area');
    
    const feedback = document.createElement('div');
    feedback.className = 'feedback-overlay';
    feedback.textContent = type === 'success' ? '✔️' : '❌';
    area.appendChild(feedback);

    if (type === 'error') {
        state.mistakeCount++;
        speakTTS("그 단추가 아닙니다. 반짝이는 테두리 가이드 부분을 다시 한번 누르세요!");
    }

    setTimeout(() => {
        feedback.remove();
    }, 700);
}

// ==========================================================================
// TRANSLATOR INTEGRATION
// ==========================================================================
function translateMenuItem(menuName) {
    const output = document.getElementById('translator-output');
    output.innerHTML = `<span class="translator-placeholder">설명 불러오는 중...</span>`;

    fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ menu_name: menuName })
    }).then(res => res.json())
    .then(data => {
        output.innerHTML = `
            <span class="translated-title">[ ${data.menu_name} ]</span>
            <span>${data.explanation}</span>
        `;
    }).catch(err => {
        console.error("Translation error:", err);
        output.innerHTML = `<span class="translator-placeholder">설명을 가져오지 못했습니다.</span>`;
    });
}

// ==========================================================================
// AUDIO SYSTEM (TTS ENGINE WITH WEB SPEECH SYNTHESIS)
// ==========================================================================
function speakTTS(text) {
    // 1. Cancel any active speaking sounds immediately to avoid overlap
    cancelTTS();

    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ko-KR';
        utterance.rate = 0.9; // Moderate speaking pace for seniors
        
        // Pick custom voice if available
        let voices = window.speechSynthesis.getVoices();
        let koVoice = voices.find(v => v.lang.includes('ko'));
        if (koVoice) {
            utterance.voice = koVoice;
        }

        utterance.onstart = () => { state.ttsSpeaking = true; };
        utterance.onend = () => { state.ttsSpeaking = false; };
        
        window.speechSynthesis.speak(utterance);
    } else {
        console.log("[TTS Browser fallback]:", text);
    }
}

function cancelTTS() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        state.ttsSpeaking = false;
    }
}

// ==========================================================================
// microphone SPEECH CONTROL (STT WITH WEB SPEECH RECOGNITION)
// ==========================================================================
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        state.recognition = new SpeechRecognition();
        state.recognition.continuous = false;
        state.recognition.lang = 'ko-KR';
        state.recognition.interimResults = false;
        state.recognition.maxAlternatives = 1;

        state.recognition.onstart = () => {
            state.voiceListening = true;
            const micBtn = document.getElementById('btn-browser-mic');
            micBtn.textContent = "🎙️ 말씀하세요... (듣는 중)";
            micBtn.classList.add('listening');
            document.getElementById('mic-status').textContent = "귀 기울여 듣고 있습니다...";
        };

        state.recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            document.getElementById('sim-voice-input').value = text;
            processVoiceCommand(text);
        };

        state.recognition.onerror = (event) => {
            console.error("STT error:", event.error);
            document.getElementById('mic-status').textContent = "오류가 발생했습니다. 다시 켜주세요.";
            resetMicUI();
        };

        state.recognition.onend = () => {
            resetMicUI();
        };
    } else {
        document.getElementById('btn-browser-mic').style.display = 'none';
        document.getElementById('mic-status').textContent = "브라우저가 마이크 입력을 지원하지 않습니다. 아래 예시를 쓰세요.";
    }
}

function toggleMic() {
    if (!state.recognition) return;
    if (state.voiceListening) {
        state.recognition.stop();
    } else {
        // Stop TTS before opening microphone
        cancelTTS();
        try {
            state.recognition.start();
        } catch (e) {
            console.error("STT start error:", e);
        }
    }
}

function resetMicUI() {
    state.voiceListening = false;
    const micBtn = document.getElementById('btn-browser-mic');
    micBtn.textContent = "🎙️ 마이크 켜고 말하기";
    micBtn.classList.remove('listening');
    document.getElementById('mic-status').textContent = "마이크 대기 중";
}

function processSimulatedVoice() {
    const text = document.getElementById('sim-voice-input').value.trim();
    if (text) {
        processVoiceCommand(text);
    }
}

function findMatchingMenuItem(text) {
    let bestMatch = null;
    let bestMatchCategory = null;
    let highestScore = 0;

    // Normalize input text: remove spaces and convert to lowercase
    const cleanText = text.replace(/\s+/g, '').toLowerCase();

    for (const [category, items] of Object.entries(state.menus)) {
        for (const item of items) {
            const name = item.name;
            // Normalize menu name: remove spaces, convert to lowercase
            let cleanName = name.replace(/\s+/g, '').toLowerCase();
            
            let isIceMatch = false;
            let isHotMatch = false;
            
            if (cleanName.includes('(ice)')) {
                cleanName = cleanName.replace('(ice)', '');
                if (cleanText.includes('아이스') || cleanText.includes('ice') || cleanText.includes('차가운') || cleanText.includes('차갑')) {
                    isIceMatch = true;
                }
            } else if (cleanName.includes('(hot)')) {
                cleanName = cleanName.replace('(hot)', '');
                if (cleanText.includes('핫') || cleanText.includes('hot') || cleanText.includes('따뜻한') || cleanText.includes('따뜻') || cleanText.includes('뜨거운') || cleanText.includes('뜨겁')) {
                    isHotMatch = true;
                }
            }

            // Check if cleanName is in cleanText
            if (cleanText.includes(cleanName)) {
                let score = cleanName.length; // prefer longer name matches
                
                // Add score boost if ICE/HOT matches explicitly
                if (isIceMatch && name.includes('(ICE)')) score += 10;
                if (isHotMatch && name.includes('(HOT)')) score += 10;
                
                // If no explicit ice/hot match but item is ICE, give a tiny boost (0.1) to default to ICE
                if (name.includes('(ICE)')) score += 0.1;
                
                if (score > highestScore) {
                    highestScore = score;
                    bestMatch = item;
                    bestMatchCategory = category;
                }
            }
        }
    }
    
    // Fallback check for simple keywords (e.g. "아메리카노" -> "(ICE)아메리카노")
    if (!bestMatch) {
        if (cleanText.includes('아메리카노')) {
            if (cleanText.includes('핫') || cleanText.includes('따뜻') || cleanText.includes('뜨겁')) {
                bestMatch = state.menus['커피'] ? state.menus['커피'].find(i => i.name === '(HOT)아메리카노') : null;
                bestMatchCategory = '커피';
            } else {
                bestMatch = state.menus['커피'] ? state.menus['커피'].find(i => i.name === '(ICE)아메리카노') : null;
                bestMatchCategory = '커피';
            }
        }
    }

    return bestMatch ? { item: bestMatch, category: bestMatchCategory } : null;
}

function processVoiceCommand(text) {
    console.log("Voice Command Recognized:", text);
    const step = state.kioskStep;

    if (text.includes("종료") || text.includes("나가기") || text.includes("취소")) {
        if (step === 2) {
            cancelOptions();
        } else if (step === 3) {
            cancelConfirm();
        } else if (step >= 4) {
            finishSession();
        }
        return;
    }

    if (text.includes("번역") || text.includes("설명")) {
        for (let menu of ["아인슈페너", "플랫화이트", "아메리카노", "라떼", "에이드", "주스"]) {
            if (text.includes(menu)) {
                translateMenuItem(menu);
                speakTTS(`${menu}에 대해 설명해 드릴게요.`);
                return;
            }
        }
    }

    if (step === 1) {
        const match = findMatchingMenuItem(text);
        if (match) {
            state.voiceTargetMenu = match.item.name;
            state.currentCategory = match.category;
            renderCategoryTabs();
            renderMenuGrid();
            
            // Move helper to the menu card
            positionAICharacter();
            
            let guideMsg = `말씀하신 '${match.item.name}' 메뉴를 반짝이는 가이드 테두리를 보고 직접 눌러보세요.`;
            const bubbleText = document.getElementById('ai-bubble-text');
            const sidebarText = document.getElementById('ai-sidebar-text');
            if (bubbleText) bubbleText.textContent = guideMsg;
            if (sidebarText) sidebarText.textContent = guideMsg;
            
            speakTTS(guideMsg);
        } else if (text.includes("결제") || text.includes("주문")) {
            handleKioskCheckout();
        } else {
            triggerFeedback('error');
        }
    } else if (step === 2) {
        if (text.includes("담기") || text.includes("완료") || text.includes("확인")) {
            commitOptions();
        } else if (text.includes("샷")) {
            const btn = document.getElementById('btn-opt-add-shot');
            if (btn) btn.click();
        } else {
            triggerFeedback('error');
        }
    } else if (step === 3) {
        if (text.includes("결제") || text.includes("확인") || text.includes("예")) {
            commitConfirm();
        } else {
            triggerFeedback('error');
        }
    } else if (step === 4) {
        if (text.includes("포장") || text.includes("가져가")) {
            setEatInOption('포장');
        } else if (text.includes("매장") || text.includes("먹고")) {
            setEatInOption('매장');
        } else {
            triggerFeedback('error');
        }
    } else if (step === 5) {
        if (text.includes("카드") || text.includes("결제")) {
            setPaymentMethod();
        } else {
            triggerFeedback('error');
        }
    } else if (step === 6) {
        if (text.includes("카드") || text.includes("넣기") || text.includes("완료")) {
            insertCreditCard();
        } else {
            triggerFeedback('error');
        }
    }
}

// ==========================================================================
// HISTORY DATABASE RETRIEVAL
// ==========================================================================
function loadStatistics() {
    fetch('/api/history')
        .then(res => res.json())
        .then(data => {
            const stats = data.stats;
            document.getElementById('stats-total-sessions').textContent = `${stats.total_sessions}회`;
            document.getElementById('stats-avg-mistakes').textContent = `${stats.avg_mistakes}회`;
            document.getElementById('stats-avg-duration').textContent = `${stats.avg_duration}초`;
        })
        .catch(err => console.error("Error loading stats:", err));
}
