const app = document.querySelector(".app");
const screens = [...document.querySelectorAll(".screen")];
const helperBubble = document.getElementById("helperBubble");
const toast = document.getElementById("toast");
const settingsPanel = document.getElementById("settingsPanel");
const fontSize = document.getElementById("fontSize");
const contrastToggle = document.getElementById("contrastToggle");
const voiceToggle = document.getElementById("voiceToggle");
const missionText = document.getElementById("missionText");
const micButton = document.getElementById("micButton");
const voiceStatus = document.getElementById("voiceStatus");
const phoneNumber = document.getElementById("phoneNumber");
const receiptPrice = document.getElementById("receiptPrice");

// 메뉴 데이터
const menuData = {
  coffee: [
    { id: "ame", name: "(ICE)아메리카노", price: 2000 },
    { id: "latte", name: "(ICE)카페라떼", price: 2900 },
    { id: "cappu", name: "(ICE)카푸치노", price: 2900 },
  ],
  juice: [
    { id: "straw", name: "딸기주스", price: 3500 },
    { id: "orange", name: "오렌지주스", price: 3500 },
  ],
};

let selectedItem = null;
let shotAdded = false;

// 메뉴 렌더링 함수
function renderMenu() {
  const container = document.getElementById("menuContainer");
  if (!container) return;
  container.innerHTML = "";
  
  Object.values(menuData).flat().forEach(item => {
    const btn = document.createElement("button");
    btn.className = "menu-item";
    btn.textContent = item.name;
    btn.dataset.id = item.id;
    btn.onclick = () => selectItem(item);
    container.appendChild(btn);
  });
}

function selectItem(item) {
  selectedItem = item;
  showToast(`${item.name}이(가) 선택되었습니다.`);
  updateHelper(`${item.name}을 선택했습니다. 옵션 화면으로 이동합니다.`);
  goTo("option");
}

const guides = {
  home: "시작하기를 누르면 제가 버튼 가까이 이동하면서 차례대로 알려드릴게요.",
  cafe: "메가MGC커피 카드로 갈게요. 노란 카드를 눌러주세요.",
  voice: "마이크를 누르고 주문을 말하거나, 아래 문장을 그대로 사용해도 됩니다.",
  menu: "제가 가리키는 컵 메뉴를 눌러보세요. (ICE)아메리카노입니다.",
  option: "옵션이 필요 없으면 제가 가리키는 주문담기를 누르세요. 샷 추가도 눌러볼 수 있어요.",
  confirm: "주문 내역을 확인한 뒤, 밖으로 가져가려면 포장하기를 누르세요.",
  payment: "할인은 지나가고 카드결제로 이동합니다. 제가 가리키는 칸을 눌러주세요.",
  stamp: "번호를 누른 뒤 적립을 누르고, 오른쪽 승인 요청으로 마무리합니다.",
  complete: "끝까지 잘 따라왔습니다. 실제 결제 없이 흐름만 확인했습니다.",
};

const speech = window.speechSynthesis;
const initialScreen = new URLSearchParams(window.location.search).get("screen");
let currentScreen = screens.some((screen) => screen.id === initialScreen) ? initialScreen : "home";
let shotAdded = false;
let toastTimer;
let recognition;

function goTo(id) {
  screens.forEach((screen) => screen.classList.toggle("active", screen.id === id));
  currentScreen = id;
  app.dataset.screen = id;
  
  if (id === "menu") renderMenu();
  
  updateHelper(guides[id]);
  if (id === "confirm") {
    const summaryText = document.getElementById("summaryText");
    summaryText.textContent = `${selectedItem.name} ${shotAdded ? "+ 샷 추가" : ""}`;
  }
  
  if (id === "complete") {
    receiptPrice.textContent = selectedItem ? `${(selectedItem.price + (shotAdded ? 600 : 0)).toLocaleString()}원` : "2,000원";
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateHelper(message, speak = true) {
  helperBubble.textContent = message;
  if (speak && voiceToggle.checked && speech) {
    speech.cancel();
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "ko-KR";
    utterance.rate = 0.85;
    speech.speak(utterance);
  }
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
}

function toggleShot(btn) {
  shotAdded = !shotAdded;
  btn.classList.toggle("active", shotAdded);
  const message = shotAdded
    ? "샷 추가를 선택했습니다. 금액이 600원 올라갑니다."
    : "샷 추가를 해제했습니다.";
  showToast(message);
  updateHelper(`${message} 이제 주문담기를 누르세요.`);
}

function appendNumber(value) {
  const base = phoneNumber.textContent;
  if (value === "010") {
    phoneNumber.textContent = "010-";
    return;
  }
  const digits = base.replace(/\D/g, "");
  if (digits.length >= 11) return;
  const next = `${digits}${value}`.slice(0, 11);
  phoneNumber.textContent = formatPhone(next);
}

function formatPhone(digits) {
  if (digits.length <= 3) return digits;
  if (digits.length <= 7) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
  return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`;
}

function backspacePhone() {
  const digits = phoneNumber.textContent.replace(/\D/g, "").slice(0, -1);
  phoneNumber.textContent = formatPhone(digits) || "010-";
}

function saveStamp() {
  const digits = phoneNumber.textContent.replace(/\D/g, "");
  if (digits.length < 10) {
    showToast("연습용 번호를 조금 더 입력해보세요.");
    updateHelper("번호 입력이 어렵다면 010 버튼을 누른 뒤 숫자를 천천히 눌러보세요.");
    return;
  }
  showToast("스탬프 적립 연습이 완료되었습니다.");
  updateHelper("좋습니다. 이제 오른쪽 카드 결제 창의 승인 요청을 눌러보세요.");
}

function initSpeechRecognition() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) return;

  recognition = new Recognition();
  recognition.lang = "ko-KR";
  recognition.interimResults = true;
  recognition.continuous = false;

  recognition.addEventListener("start", () => {
    micButton.classList.add("listening");
    voiceStatus.textContent = "듣고 있습니다.";
  });

  recognition.addEventListener("result", (event) => {
    const transcript = [...event.results].map((result) => result[0].transcript).join("");
    missionText.value = transcript;
    voiceStatus.textContent = transcript;
  });

  recognition.addEventListener("end", () => {
    micButton.classList.remove("listening");
    voiceStatus.textContent = "인식이 끝났습니다. 연습 시작을 누르세요.";
  });
}

document.addEventListener("click", (event) => {
  const goButton = event.target.closest("[data-go]");
  if (goButton) {
    goTo(goButton.dataset.go);
    return;
  }

  const actionButton = event.target.closest("[data-action]");
  if (!actionButton) return;

  const { action } = actionButton.dataset;
  if (action === "home") goTo("home");
  if (action === "toggle-settings") settingsPanel.classList.toggle("open");
  if (action === "show-guide") {
    updateHelper("헬피가 다음 버튼 가까이 움직입니다. 손이 가리키는 곳을 천천히 눌러주세요.");
  }
  if (action === "toggle-shot") toggleShot(actionButton);
  if (action === "explain") {
    updateHelper(actionButton.dataset.message);
    showToast(actionButton.dataset.message);
  }
  if (action === "backspace") backspacePhone();
  if (action === "save-stamp") saveStamp();
});

document.addEventListener("click", (event) => {
  const errorButton = event.target.closest("[data-error]");
  if (!errorButton) return;
  updateHelper(errorButton.dataset.error);
  showToast(errorButton.dataset.error);
});

document.querySelectorAll("[data-num]").forEach((button) => {
  button.addEventListener("click", () => appendNumber(button.dataset.num));
});

fontSize.addEventListener("change", () => {
  app.dataset.fontSize = fontSize.value;
});

contrastToggle.addEventListener("change", () => {
  app.classList.toggle("high-contrast", contrastToggle.checked);
});

voiceToggle.addEventListener("change", () => {
  if (!voiceToggle.checked && speech) speech.cancel();
});

micButton.addEventListener("click", () => {
  if (!recognition) {
    const fallback = "이 브라우저는 음성 인식을 지원하지 않습니다. 문장을 직접 확인하고 연습 시작을 눌러주세요.";
    voiceStatus.textContent = fallback;
    updateHelper(fallback, false);
    return;
  }
  recognition.start();
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (settingsPanel.classList.contains("open")) settingsPanel.classList.remove("open");
    else goTo("home");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  // data-go 버튼들에 직접 이벤트 할당
  document.querySelectorAll("[data-go]").forEach(button => {
    button.addEventListener("click", () => {
      goTo(button.dataset.go);
    });
  });

  initSpeechRecognition();
  goTo(currentScreen);
});
